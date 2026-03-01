# geedl/local/basic/management.py

import os
from .helper import get_wbt


wbt = get_wbt()

def mosaic_to_new_raster(input_rasters, output_location, raster_dataset_name_with_extension, mosaic_method="FIRST"):
    """
    仿 ArcGIS "镶嵌到新栅格" (Mosaic To New Raster) 工具。
    
    参数:
        input_rasters (list): 输入栅格文件路径列表。
        output_location (str): 输出目录路径。
        raster_dataset_name_with_extension (str): 带扩展名的输出文件名（如 'result.tif'）。
        mosaic_method (str): 镶嵌方法。支持: "FIRST", "LAST", "MINIMUM", "MAXIMUM", "MEAN", "BLEND"。
                             默认值为 "FIRST"。
    """
    
    # 1. 构造完整的输出路径
    output_path = os.path.join(output_location, raster_dataset_name_with_extension)
    
    # 2. 将输入的列表转换为 Whitebox 要求的分号分隔字符串
    # WhiteboxTools 的 inputs 参数接受 "file1.tif;file2.tif;file3.tif" 格式
    input_str = ";".join(input_rasters)
    
    # 3. 映射 ArcGIS 的 mosaic_method 到 Whitebox 的参数
    # ArcGIS: FIRST, LAST, MINIMUM, MAXIMUM, MEAN, BLEND
    # Whitebox: 'mosaic' (即first/last), 'min', 'max', 'mean', 'blend'
    method_map = {
        "FIRST": "mosaic",
        "LAST": "mosaic", # Whitebox 的 mosaic 默认处理重叠部分
        "MINIMUM": "min",
        "MAXIMUM": "max",
        "MEAN": "mean",
        "BLEND": "blend"
    }
    
    wbt_method = method_map.get(mosaic_method.upper(), "mosaic")
    
    # 4. 调用 Whitebox 引擎执行操作
    print(f"正在将 {len(input_rasters)} 个栅格镶嵌至: {output_path}")
    result = wbt.mosaic(
        inputs=input_str, 
        output=output_path, 
        method=wbt_method
    )
    
    if result == 0:
        print("镶嵌成功！")
        return output_path
    else:
        print("镶嵌过程中出现错误。")
        return None
    

def clip_raster_by_mask(in_raster, in_template_dataset, out_raster, nodata_value=None):
    """
    仿 ArcGIS "裁剪" (Clip) 工具。
    注意：此函数使用矢量多边形对栅格进行裁剪。
    
    参数:
        in_raster (str): 待裁剪的输入栅格路径。
        in_template_dataset (str): 用作裁剪边界的矢量文件路径 (.shp)。
        out_raster (str): 输出栅格路径。
        nodata_value (float): 裁剪后外部区域的填充值。
    """
    return wbt.clip_raster_to_polygon(
        i=in_raster, 
        polygons=in_template_dataset, 
        output=out_raster,
        maintain_dimensions=True # 保持原有的栅格行列结构
    )

def project_raster(in_raster, out_raster, out_coor_system):
    """
    仿 ArcGIS "投影栅格" (Project Raster) 工具。
    
    参数:
        in_raster (str): 输入栅格。
        out_raster (str): 输出栅格。
        out_coor_system (str): 目标坐标系的 EPSG 代码或 WKT 字符串。
    """
    # Whitebox 使用 reproject 函数
    return wbt.reproject_raster(
        i=in_raster, 
        output=out_raster, 
        crs=str(out_coor_system)
    )

def resample(in_raster, out_raster, cell_size, resampling_type="NEAREST"):
    """
    仿 ArcGIS "重采样" (Resample) 工具。
    
    参数:
        cell_size (float): 新的像元大小。
        resampling_type (str): 方法，支持 "NEAREST", "BILINEAR", "BICUBIC"。
    """
    method_map = {
        "NEAREST": "nn",
        "BILINEAR": "bilinear",
        "BICUBIC": "cc"
    }
    return wbt.resample(
        i=in_raster, 
        output=out_raster, 
        cell_size=cell_size, 
        method=method_map.get(resampling_type.upper(), "nn")
    )