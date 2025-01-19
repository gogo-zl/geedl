

def rmLandsatCloud(image):
    """
    对 Landsat 影像应用云掩膜处理。

    Args:
        image (ee.Image): 输入的 Landsat 影像。
    
    Returns:
        ee.Image: 应用云掩膜后的影像。
    """
    # 获取 QA_PIXEL 波段
    qa = image.select('QA_PIXEL')

    # 第 3 位：云标志（0 = 无云, 1 = 有云）
    cloud_mask = qa.bitwiseAnd(1 << 3).eq(0)

    # 第 4 位：云影标志（0 = 无云影, 1 = 有云影）
    cloud_shadow_mask = qa.bitwiseAnd(1 << 4).eq(0)

    # 组合掩膜：仅保留无云且无云影的像素
    mask_all = cloud_mask.And(cloud_shadow_mask)

    # 应用掩膜
    return image.updateMask(mask_all)


def rmMODISCloud(image):
    """
    对 MODIS 影像应用云掩膜处理（基于 StateQA 的位 10）。

    Args:
        image (ee.Image): 输入的 MODIS 影像。
    
    Returns:
        ee.Image: 应用云掩膜后的影像。
    """
    # 获取 StateQA 波段
    qa = image.select('StateQA')
    
    # 提取位 10 信息（Bit 10: Internal cloud algorithm flag）
    # 0 = No cloud, 1 = Cloud
    cloud_mask = qa.bitwiseAnd(1 << 10).eq(0)
    
    # 应用云掩膜
    return image.updateMask(cloud_mask)


__all__ = ["rmLandsatCloud", "rmMODISCloud"]