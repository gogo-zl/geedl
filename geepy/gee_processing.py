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


__all__ = [
    "rm_landsat_cloud",
    "rm_modis_cloud",
    "add_spectral_indices",
    "add_spectral_indices_to_collection",
]