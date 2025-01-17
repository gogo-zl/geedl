import geemap

def create_map(center=[0, 0], zoom=2):
    """创建地图"""
    Map = geemap.Map(center=center, zoom=zoom)
    print("🗺️ 地图已创建")
    return Map