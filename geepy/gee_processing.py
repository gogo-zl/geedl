import ee
import json
import urllib.request
from .gee_params import *
from .gee_utils import *

def rm_landsat_cloud(image):
    """
    对 Landsat 影像应用云掩膜处理。

    Args:
        image (ee.Image): 输入的 Landsat 影像。
    
    Returns:
        ee.Image: 经过云掩膜处理的影像，移除了云和云影像素。
    """
    qa = image.select('QA_PIXEL')
    cloud_mask = qa.bitwiseAnd(1 << 3).eq(0)  # 云标志
    cloud_shadow_mask = qa.bitwiseAnd(1 << 4).eq(0)  # 云影标志
    return image.updateMask(cloud_mask.And(cloud_shadow_mask))


def rm_modis_cloud(image):
    """
    对 MODIS 影像应用严格的云掩膜处理。

    Args:
        image (ee.Image): 输入的 MODIS 影像。
    
    Returns:
        ee.Image: 经过云掩膜处理的影像，移除了云和云影像素。
    """
    qa = image.select('StateQA')
    # 清晰像素（Bits 0-1）
    cloud_state_clear = qa.bitwiseAnd(3).eq(0)
    # 无云影（Bit 2）
    no_cloud_shadow = qa.bitwiseAnd(1 << 2).eq(0)
    # 无内部云（Bit 10）
    no_internal_cloud = qa.bitwiseAnd(1 << 10).eq(0)
    return image.updateMask(cloud_state_clear.And(no_cloud_shadow).And(no_internal_cloud))


def rm_MCD43A4_cloud(image):
    """
    Apply quality control (QC) mask to the MCD43A4 image for all 7 bands using the quality bands.
    
    Args:
        image (ee.Image): Input MODIS MCD43A4 image.
    
    Returns:
        ee.Image: Image with bad quality pixels masked out for all 7 bands.
    """
    # Extract the quality control bands for each of the 7 bands
    qc_band1 = image.select('BRDF_Albedo_Band_Mandatory_Quality_Band1')
    qc_band2 = image.select('BRDF_Albedo_Band_Mandatory_Quality_Band2')
    qc_band3 = image.select('BRDF_Albedo_Band_Mandatory_Quality_Band3')
    qc_band4 = image.select('BRDF_Albedo_Band_Mandatory_Quality_Band4')
    qc_band5 = image.select('BRDF_Albedo_Band_Mandatory_Quality_Band5')
    qc_band6 = image.select('BRDF_Albedo_Band_Mandatory_Quality_Band6')
    qc_band7 = image.select('BRDF_Albedo_Band_Mandatory_Quality_Band7')
    
    # Create a mask for good quality (Bit 0 = 0 means good quality)
    # good_quality_mask = (
    #     qc_band1.eq(0)  # Band 1 good quality
    #     .And(qc_band2.eq(0))  # Band 2 good quality
    #     .And(qc_band3.eq(0))  # Band 3 good quality
    #     .And(qc_band4.eq(0))  # Band 4 good quality
    #     .And(qc_band5.eq(0))  # Band 5 good quality
    #     .And(qc_band6.eq(0))  # Band 6 good quality
    #     .And(qc_band7.eq(0))  # Band 7 good quality
    # )
    good_quality_mask = (
        qc_band2.eq(0)
    )

    
    # Apply the mask to the entire image (only keep good quality pixels)
    image = image.updateMask(good_quality_mask)
    
    return image



def add_spectral_indices(image, indices, keep_original=True):
    """
    为单张影像计算并添加指定的光谱指数。

    Args:
        image (ee.Image): 输入影像。
        indices (list): 要计算的光谱指数列表（如 ["NDVI", "EVI"]）。
        keep_original (bool): 是否保留原始影像波段。
            - True: 返回包含原始波段和计算的指数。
            - False: 返回仅包含计算的指数。

    Returns:
        ee.Image: 包含计算结果的影像。
    """
    spectral_indices = fetch_json(SPECTRAL_INDICES_URL)["SpectralIndices"]
    constants = fetch_json(CONSTANTS_URL)
    constant_values = {key: value["default"] for key, value in constants.items() if value["default"] is not None}
    result_image = image

    for index in indices:
        if index not in spectral_indices:
            raise ValueError(f"指数 {index} 不存在于 JSON 文件中。")

        formula = spectral_indices[index]["formula"]
        bands = spectral_indices[index]["bands"]

        # 构建公式的参数字典：映射波段或常数
        params = {
            symbol: image.select(BAND_MAPPING[symbol]) if symbol in BAND_MAPPING
            else image.constant(constant_values[symbol]) for symbol in bands
        }

        # 添加计算结果到影像
        result_image = result_image.addBands(image.expression(formula, params).rename(index))

    return result_image if keep_original else result_image.select(indices)


def add_spectral_indices_to_collection(imgcol, indices, keep_original=True):
    """
    为影像集合中的每个影像计算并添加指定的光谱指数。

    Args:
        imgcol (ee.ImageCollection): 输入的影像集合。
        indices (list): 要计算的光谱指数列表（如 ["NDVI", "EVI"]）。
        keep_original (bool): 是否保留原始影像波段。
            - True: 返回包含原始波段和计算的指数的集合。
            - False: 返回仅包含计算的指数的集合。

    Returns:
        ee.ImageCollection: 包含计算结果的影像集合。
    """
    return imgcol.map(lambda img: add_spectral_indices(img, indices, keep_original))


def calculate_terrain_features(region, resolution, resample_method='bilinear'):
    """
    计算给定区域的地形特征，包括海拔、高程和坡度。

    参数:
    region (ee.Geometry): 感兴趣区域。
    resolution (int): 重采样的目标分辨率。
    resample_method (str): 使用的重采样方法。默认是 'bilinear'。

    返回:
    ee.Image: 包含地形特征（海拔、高程、坡度）的图像，重采样到指定分辨率。
    """
    # 加载SRTM数据（30米分辨率）
    srtm = ee.Image('USGS/SRTMGL1_003')
    
    # 计算坡度和高程
    slope = ee.Terrain.slope(srtm)
    aspect = ee.Terrain.aspect(srtm)
    
    # 将地形特征（海拔、高程、坡度）组合成一个图像
    terrain_image = srtm.addBands(slope).addBands(aspect).rename(['elevation', 'slope', 'aspect'])
    
    # 重采样到指定分辨率
    terrain_image_resampled = terrain_image.resample(resample_method)  # 选择重采样方法
    terrain_image_resampled = terrain_image_resampled.reproject(
        crs=srtm.projection(),
        scale=resolution  # 设置目标分辨率
    ).clip(region)  # 裁剪到指定区域
    
    return terrain_image_resampled


def merge_images(collection, interval, aggregation_method='median'):
    """
    对时序影像集合进行每 interval 天的合成，可选择合成方法（均值、中值等）。
    
    Args:
        collection (ee.ImageCollection): 时序影像集合。
        interval (int): 合成时间间隔（天）。
        aggregation_method (str): 合成方法，'mean' 或 'median'。默认 'median'。
        
    Returns:
        ee.ImageCollection: 合成后的影像集合。
    """
    start_date = ee.Date(collection.sort('system:time_start').first().get('system:time_start'))
    end_date = ee.Date(collection.sort('system:time_start').aggregate_max('system:time_start'))
    time_range = ee.List.sequence(start_date.millis(), end_date.millis(), interval * 24 * 60 * 60 * 1000)

    def merge_function(start_millis):
        start = ee.Date(start_millis)
        end = start.advance(interval, 'day')
        subset = collection.filterDate(start, end)
        
        if aggregation_method == 'mean':
            aggregated_image = subset.mean()
        elif aggregation_method == 'median':
            aggregated_image = subset.median()
        elif aggregation_method == 'min':
            aggregated_image = subset.min()  
        elif aggregation_method == 'max':
            aggregated_image = subset.max()
        else:
            raise ValueError(f"Unsupported aggregation method: {aggregation_method}")
        
        return aggregated_image.set('system:time_start', start.millis())

    merged_collection = time_range.map(merge_function)

    return ee.ImageCollection(merged_collection)




__all__ = [
    "rm_landsat_cloud",
    "rm_modis_cloud",
    "rm_MCD43A4_cloud",
    "add_spectral_indices",
    "add_spectral_indices_to_collection",
    "calculate_terrain_features",
    "merge_images"
]