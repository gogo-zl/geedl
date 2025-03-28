import ee
from .gee_params import *
from .gee_processing import *

def get_any_year_data(date_range, roi, dataset='Landsat', remove_cloud=True, normalize=True, bands=None, landsat_series=None):
    """
    获取指定时间范围和区域的影像集合（支持 Landsat 和 MODIS 数据）。

    Args:
        date_range (list): 包含起始和结束日期的列表，例如 ['2020-01-01', '2020-12-31']。
        roi (ee.Geometry): 感兴趣区域 (Region of Interest)。
        dataset (str): 数据类型（'Landsat' 或 'MODIS'），默认为 'Landsat'。
        remove_cloud (bool): 是否对影像进行云掩膜处理，默认 True。
        normalize (bool): 是否对影像进行归一化处理，默认 True。
        bands (list): 用户自定义的波段选择，默认为 None，表示使用默认波段。
        landsat_series (list): 指定 Landsat 系列，例如 ['L8', 'L9']，默认全部系列 ['L5', 'L7', 'L8', 'L9']。

    Returns:
        ee.ImageCollection: 处理后的影像集合。
    """
    validate_inputs(date_range, roi)

    # 设置默认参数
    if dataset == 'Landsat':
        bands = bands or ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
        landsat_series = landsat_series or ['L5', 'L7', 'L8', 'L9']
        invalid_series = [s for s in landsat_series if s not in DATASET_IDS]
        if invalid_series:
            raise ValueError(f"Invalid Landsat series: {invalid_series}")
        cloud_function = rm_landsat_cloud
    elif dataset == 'MODIS':
        bands = bands or ['red', 'nir', 'blue', 'green', 'mir', 'swir1', 'swir2']
        cloud_function = rm_modis_cloud
    else:
        raise ValueError(f"Unsupported dataset: {dataset}")

    def process_series(series):
        """
        处理单个数据系列。
        """
        collection = (ee.ImageCollection(DATASET_IDS[series])
                      .filterBounds(roi)
                      .filterDate(date_range[0], date_range[1]))
        if remove_cloud:
            collection = collection.map(cloud_function)

        def process_image(img):
            """
            对影像进行选择、归一化，并保留系统属性。
            """
            img = img.select(ORIGINAL_BANDS[series], RENAMED_BANDS[series]).select(bands)
            if normalize:
                if dataset == 'Landsat':
                    img = img.multiply(0.0000275).add(-0.2)
                elif dataset == 'MODIS':
                    img = img.multiply(0.0001)
            return img.copyProperties(img, ['system:time_start', 'system:time_end', 'system:index'])

        return collection.map(process_image)

    if dataset == 'MODIS':
        return process_series('MOD09A1')

    if dataset == 'Landsat':
        collections = [process_series(series) for series in landsat_series]
        merged_collection = ee.ImageCollection(collections).flatten().sort('system:time_start')
        return merged_collection


def load_modis_data(date_range, roi, series='MOD09A1', remove_cloud=True, normalize=True):
    """
    加载并处理 MODIS 数据集（MOD09A1 或 MCD43A4），包括云掩膜、归一化等处理。

    Args:
        roi (ee.Geometry): 感兴趣区域。
        date_range (list): 日期范围，如 ['2020-01-01', '2020-12-31']。
        series (str): 数据系列，'MOD09A1' 或 'MCD43A4'。
        normalize (bool): 是否进行归一化，默认为 True。
        remove_cloud (bool): 是否去云，默认为 True。

    Returns:
        ee.ImageCollection: 处理后的 MODIS 数据集合。
    """

    # 根据数据系列选择云掩膜函数
    if series == 'MOD09A1':
        cloud_function = rm_modis_cloud  # 假设已经定义了云掩膜函数
    elif series == 'MCD43A4':
        cloud_function = rm_MCD43A4_cloud  # MCD43A4 不需要额外的云掩膜

    def process_series(series):
        """
        处理单个数据系列（加载、过滤、云掩膜、归一化等）。
        """
        # 通过 filterBounds 限制区域，避免加载整个全球数据
        collection = (ee.ImageCollection(DATASET_IDS[series])
                      .filterDate(date_range[0], date_range[1])
                      .filterBounds(roi))  # 需要传入 roi 进行区域限制

        # 如果需要去云，应用云掩膜函数
        if remove_cloud and cloud_function:
            collection = collection.map(cloud_function)

        def process_image(img):
            """
            对单张影像进行波段选择和归一化处理。
            """
            # 选择波段并进行归一化
            img2 = img.select(ORIGINAL_BANDS[series], RENAMED_BANDS[series])
            if normalize:
                img2 = img2.multiply(0.0001)  # 假设 MODIS 数据需要归一化
            # 保留影像的系统属性（如时间信息）
            img2 = img2.copyProperties(img, ['system:time_start', 'system:time_end', 'system:index'])
            return img2

        return collection.map(process_image)

    # 处理 MOD09A1 或 MCD43A4 数据系列
    return process_series(series)


__all__ = ["get_any_year_data",
           "load_modis_data"]