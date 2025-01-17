import ee

def initialize_gee():
    """初始化 GEE"""
    try:
        ee.Initialize()
        print("✅ GEE 初始化成功！")
    except Exception as e:
        ee.Authenticate()
        ee.Initialize()
        print("🔑 GEE 已认证并初始化成功！")
print('eeeee')
