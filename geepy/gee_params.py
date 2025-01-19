import ee



datasetIDs = {
    'L9': "LANDSAT/LC09/C02/T1_L2", 
    'L8': "LANDSAT/LC08/C02/T1_L2", 
    'L7': "LANDSAT/LE07/C02/T1_L2",
    'L5': "LANDSAT/LT05/C02/T1_L2",
    'MOD09A1': "MODIS/061/MOD09A1",
}

originalBands = {
    'L9': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'], 
    'L8': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'], 
    'L7': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7'],
    'L5': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7'],
    'MOD09A1': ['sur_refl_b01', 'sur_refl_b02', 'sur_refl_b03', 'sur_refl_b04', 'sur_refl_b05', 'sur_refl_b06', 'sur_refl_b07']
}

renamedBands = {
    'L9': ['ub', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'], 
    'L8': ['ub', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'], 
    'L7': ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
    'L5': ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
    'MOD09A1': ['red', 'nir', 'blue', 'green', 'mir', 'swir1', 'swir2']
}

# 新增的输入验证函数
def validate_inputs(date_range, roi):
    """
    验证用户输入的参数是否合法。
    """
    if not isinstance(date_range, list) or len(date_range) != 2:
        raise ValueError("date_range must be a list with two elements: [start_date, end_date].")
    if not isinstance(roi, ee.Geometry):
        raise ValueError("roi must be an ee.Geometry object.")

__all__ = ["datasetIDs", "originalBands", "renamedBands", "validate_inputs"]