import ee
import importlib
import geepy
from datetime import datetime
from IPython import get_ipython
import urllib.request
import json


#######################################################################
######################################## 日志和执行控制相关
#######################################################################

def log_execution_start(info=None):
    """
    记录代码单元执行的开始时间。

    Args:
        info (str, optional): 可选的附加信息，用于标记该次运行（默认值为 None）。

    Returns:
        datetime: 返回当前的起始时间。
    """
    start_time = datetime.now()
    print(f"\nStart Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    return start_time  # 建议添加返回值方便调试


def register_jupyter_hook():
    """
    注册 Jupyter Notebook 钩子，用于在代码单元运行前自动记录时间。

    Returns:
        bool: 如果成功注册返回 True，否则返回 False。
    """
    ipython = get_ipython()
    if ipython:
        ipython.events.register('pre_run_cell', log_execution_start)
        return True
    else:
        print("当前环境非 Jupyter Notebook，无法注册钩子！")
        return False




#######################################################################
######################################## 动态加载模块
#######################################################################
def reload_package():
    """
    强制重新加载 geepy 包及其所有子模块，适用于开发者模式安装时更新后的动态加载。
    """
    for submodule in list(geepy.__dict__.values()):
        if hasattr(submodule, "__name__") and submodule.__name__.startswith("geepy."):
            importlib.reload(submodule)
    importlib.reload(geepy)




#######################################################################
######################################## 网络资源加载
#######################################################################

def fetch_json(url):
    """
    从指定 URL 加载 JSON 文件。
    
    Args:
        url (str): JSON 文件的 URL。
    
    Returns:
        dict: 解析后的 JSON 数据。
    """
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        raise RuntimeError(f"无法加载 JSON 文件：{url}\n错误信息：{e}")


#######################################################################
######################################## 网格生成工具
#######################################################################

def generate_rect_grid(study_area, grid_width=1.5, grid_height=1.5):
    """
    在给定的研究区内生成指定大小的矩形网格。

    Args:
        study_area (ee.FeatureCollection): 研究区。
        grid_width (float): 网格宽度（经度方向，单位：度）。
        grid_height (float): 网格高度（纬度方向，单位：度）。

    Returns:
        ee.FeatureCollection: 裁剪后的网格。
    """
    bounds = study_area.bounds()
    coords = bounds.coordinates().get(0)

    min_lon = ee.List(ee.List(coords).get(0)).get(0)
    max_lon = ee.List(ee.List(coords).get(1)).get(0)
    min_lat = ee.List(ee.List(coords).get(0)).get(1)
    max_lat = ee.List(ee.List(coords).get(2)).get(1)

    # 生成经度和纬度列表
    lon_list = ee.List.sequence(min_lon, max_lon, grid_width)
    lat_list = ee.List.sequence(min_lat, max_lat, grid_height)

    # 构建网格
    grid = lon_list.map(
        lambda lon: lat_list.map(
            lambda lat: ee.Feature(
                ee.Geometry.Rectangle(
                    [lon, lat, ee.Number(lon).add(grid_width), ee.Number(lat).add(grid_height)]
                )
            )
        )
    ).flatten()

    # 转换为 FeatureCollection 并裁剪到研究区
    grid_fc = ee.FeatureCollection(grid)
    return grid_fc.filterBounds(study_area)


def generate_hex_grid(study_area, radius=1.5):
    """
    在给定的研究区内生成指定大小的六边形网格

    Args:
        study_area (ee.FeatureCollection): 研究区。
        radius (float): 六边形边到中心的距离（单位：度）。

    Returns:
        ee.FeatureCollection: 裁剪后的六边形网格。
    """
    bounds = study_area.bounds()
    coords = bounds.coordinates().get(0)

    xmin = ee.Number(ee.List(ee.List(coords).get(0)).get(0))
    ymin = ee.Number(ee.List(ee.List(coords).get(0)).get(1))
    xmax = ee.Number(ee.List(ee.List(coords).get(2)).get(0))
    ymax = ee.Number(ee.List(ee.List(coords).get(2)).get(1))

    # 将 Python float 转换为 ee.Number
    radius = ee.Number(radius)
    sqrt_3 = ee.Number(3).sqrt()
    r_half = radius.divide(2)
    r_half_sqrt_3 = r_half.multiply(sqrt_3)
    step_x = radius.multiply(3)
    step_y = radius.multiply(sqrt_3)

    xx1 = ee.List.sequence(xmin, xmax.add(radius), step_x)
    yy1 = ee.List.sequence(ymin, ymax.add(radius), step_y)

    xx2 = ee.List.sequence(xmin.subtract(radius.multiply(1.5)), xmax.add(radius), step_x)
    yy2 = ee.List.sequence(ymin.add(r_half_sqrt_3), ymax.add(radius), step_y)

    def hex(x, y):
        point1_x = ee.Number(x).subtract(radius)
        point2_x = ee.Number(x).subtract(r_half)
        point3_x = ee.Number(x).add(r_half)
        point4_x = ee.Number(x).add(radius)

        point1_y = ee.Number(y).add(r_half_sqrt_3)
        point2_y = ee.Number(y)
        point3_y = ee.Number(y).subtract(r_half_sqrt_3)

        polygon = ee.Geometry.Polygon(
            [[[point1_x, point2_y],
              [point2_x, point3_y],
              [point3_x, point3_y],
              [point4_x, point2_y],
              [point3_x, point1_y],
              [point2_x, point1_y]]]
        )
        return ee.Feature(polygon)

    cell1 = xx1.map(
        lambda x: yy1.map(lambda y: hex(x, y))
    ).flatten()

    cell2 = xx2.map(
        lambda x: yy2.map(lambda y: hex(x, y))
    ).flatten()

    # 将嵌套的列表扁平化并创建 FeatureCollection
    hex_grid = ee.FeatureCollection(cell1.cat(cell2))
    return hex_grid.filterBounds(study_area)


#######################################################################
######################################## 影像处理小工具
#######################################################################

def get_image_collection_dates(imgcol):
    """
    打印影像集合中每个影像的开始时间，并转换为 'yyyy-MM-dd' 的日期格式。

    Args:
        imgcol (ee.ImageCollection): 输入的影像集合。

    Returns:
        list: 包含所有影像开始时间的字符串列表，格式为 'yyyy-MM-dd'。
    """
    def format_start_date(image):
        # 获取影像的开始时间属性并格式化为 'yyyy-MM-dd'
        start_date = ee.Date(image.get('system:time_start')).format('yyyy-MM-dd')
        return ee.Feature(None, {'date': start_date})  # 创建一个包含日期的 Feature

    # 将影像集合映射为日期集合
    date_features = imgcol.map(format_start_date)

    # 提取日期并打印
    dates = date_features.aggregate_array('date').getInfo()
    print("Start dates of images in the collection:")
    # for date in dates:
    #     print(date)

    return dates

# 删除GEE的Folder 和 IMGCOL资产
def delete_asset_folder(asset_path):
    """
    Recursively delete all child assets under a GEE folder or ImageCollection,
    then delete the folder itself.

    Args:
        asset_path (str): Full asset path 
    """
    try:
        children = ee.data.listAssets(asset_path).get('assets', [])
        if not children:
            print(f"No children found in: {asset_path}")
        else:
            for asset in children:
                ee.data.deleteAsset(asset['name'])
                print(f"Deleted: {asset['name']}")
        ee.data.deleteAsset(asset_path)
        print(f"Deleted folder: {asset_path}")
    except Exception as e:
        print(f"Error deleting assets under {asset_path}:\n{e}")


def ensure_asset_exists(asset_path, asset_type='IMAGE_COLLECTION'):
    """Check if an Earth Engine asset exists; create if not."""
    parent = '/'.join(asset_path.split('/')[:-1])
    assets = ee.data.listAssets(parent).get('assets', [])
    existing_names = [a['name'] for a in assets]

    if asset_path in existing_names:
        print(f"Asset exists: {asset_path}")
    else:
        ee.data.createAsset({'type': asset_type}, asset_path)
        print(f"Created asset: {asset_path}")


def copy_imagecollection(src_ic_path, dst_ic_path):
    """
    Copy all images from one Earth Engine ImageCollection to another using ee.data.

    Args:
        src_ic_path (str): Source ImageCollection asset path.
        dst_ic_path (str): Target ImageCollection asset path (must already exist).
    """
    # 创建目标目录（如果不存在）
    ensure_asset_exists(dst_ic_path, asset_type='IMAGE_COLLECTION')

    # 列出源目录下的所有图像
    assets = ee.data.listAssets(src_ic_path).get('assets', [])
    if not assets:
        print(f"No assets found in source: {src_ic_path}")
        return

    for asset in assets:
        if asset['type'] != 'IMAGE':
            continue
        img_name = asset['name'].split('/')[-1]
        src_img_path = asset['name']
        dst_img_path = f"{dst_ic_path}/{img_name}"

        try:
            ee.data.copyAsset(src_img_path, dst_img_path)
            print(f"Copied: {img_name}")
        except Exception as e:
            print(f"Failed to copy {img_name}: {e}")

# 明确需要导出的函数
__all__ = [
    "log_execution_start",
    "register_jupyter_hook",
    "get_image_collection_dates",
    "reload_package",
    "generate_rect_grid",
    "generate_hex_grid",
    "fetch_json", 
    "delete_asset_folder", 
    "ensure_asset_exists", 
    "copy_imagecollection"
]
