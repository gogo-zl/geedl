# geedl/local/basic/analysis.py

from .helper import get_wbt
import os

wbt = get_wbt()

def aspect(in_raster, out_raster):
    """
    仿 ArcGIS "坡向" (Aspect) 工具。
    """
    return wbt.aspect(dem=in_raster, output=out_raster)

def hillshade(in_dem, out_raster, azimuth=315.0, altitude=45.0):
    """
    仿 ArcGIS "山体阴影" (Hillshade) 工具。
    """
    return wbt.hillshade(
        dem=in_dem, 
        output=out_raster, 
        azimuth=azimuth, 
        altitude=altitude
    )

def reclassify(in_raster, out_raster, reclass_field, remap):
    """
    仿 ArcGIS "重分类" (Reclassify) 工具。
    
    参数:
        remap (str): 重分类规则，Whitebox 格式通常为 "new_val;lower;upper"。
                     这里可以根据需求进一步封装简化。
    """
    # 这里我们直接调用 whitebox 的 reclassify
    return wbt.reclassify(
        i=in_raster, 
        output=out_raster, 
        reclass_vals=remap
    )

def extract_values_to_points(in_raster, in_point_features, out_point_features):
    """
    仿 ArcGIS "值提取至点" (Extract Values to Points) 工具。
    """
    return wbt.extract_raster_values_at_points(
        inputs=in_raster, 
        points=in_point_features, 
        output=out_point_features
    )