# gee_image_loader.py

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
        bands (list): 用户自定义的波段选择。默认根据数据类型自动选择。
        landsat_series (list): 指定 Landsat 系列，例如 ['L8', 'L9']，默认全部系列 ['L5', 'L7', 'L8', 'L9']。

    Returns:
        ee.ImageCollection: 处理后的影像集合。
    """
    validate_inputs(date_range, roi)
    
    # 设置默认波段选择和数据集键
    if dataset == 'Landsat':
        if bands is None:
            bands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
        if landsat_series is None:
            landsat_series = ['L5', 'L7', 'L8', 'L9']  # 默认处理所有 Landsat 系列
        else:
            invalid_series = [s for s in landsat_series if s not in ['L5', 'L7', 'L8', 'L9']]
            if invalid_series:
                raise ValueError(f"Invalid Landsat series: {invalid_series}")
        cloud_function = rmLandsatCloud  # 使用 Landsat 去云函数
    elif dataset == 'MODIS':
        if bands is None:
            bands = ['red', 'nir', 'blue', 'green', 'mir', 'swir1', 'swir2']
        series_keys = ['MOD09A1']
        cloud_function = rmMODISCloud  # 使用 MODIS 去云函数
    else:
        raise ValueError(f"Unsupported dataset: {dataset}")

    # 定义处理逻辑
    def process_series(series):
        print(f"Processing {dataset} series: {series}")
        collection = (ee.ImageCollection(datasetIDs[series])
                      .filterBounds(roi)
                      .filterDate(date_range[0], date_range[1]))
        if remove_cloud:
            collection = collection.map(cloud_function)  # 根据数据集动态选择去云函数

        # 保留影像的关键系统属性
        def preserve_properties(img):
            return (img.select(originalBands[series], renamedBands[series])
                    .select(bands)
                    .multiply(0.0000275).add(-0.2)
                    .copyProperties(img, ['system:time_start', 'system:time_end', 'system:index']))

        # 应用保留属性的处理逻辑
        collection = collection.map(preserve_properties)

        return collection

    # 处理逻辑分支
    if dataset == 'MODIS':
        # 如果是 MODIS 数据，直接返回处理后的集合
        return process_series('MOD09A1')
    elif dataset == 'Landsat':
        # 用户选择的 Landsat 系列
        collections = [process_series(series) for series in landsat_series]

        # 合并 Landsat 系列数据
        merged_collection = collections[0]
        for collection in collections[1:]:
            merged_collection = merged_collection.merge(collection)
        merged_collection = merged_collection.sort('system:time_start')
 
        # 添加注释：后续可以在这里实现 Landsat 不同系列之间的矫正
        # TODO: Add inter-series correction logic for Landsat (e.g., harmonization between L7 and L8)
        
        return merged_collection




__all__ = ["get_any_year_data"]
