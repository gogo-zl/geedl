# para.py

SPECTRAL_INDICES_URL = "https://raw.githubusercontent.com/awesome-spectral-indices/awesome-spectral-indices/main/output/spectral-indices-dict.json"
CONSTANTS_URL = "https://raw.githubusercontent.com/awesome-spectral-indices/awesome-spectral-indices/main/output/constants.json"

DATASET_IDS = {
    'L9': "LANDSAT/LC09/C02/T1_L2", 
    'L8': "LANDSAT/LC08/C02/T1_L2", 
    'L7': "LANDSAT/LE07/C02/T1_L2",
    'L5': "LANDSAT/LT05/C02/T1_L2",
    'MOD09A1': "MODIS/061/MOD09A1",
    'MCD43A4': "MODIS/061/MCD43A4"
}

ORIGINAL_BANDS = {
    'L9': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'], 
    'L8': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'], 
    'L7': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7'],
    'L5': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7'],
    'MOD09A1': ['sur_refl_b01', 'sur_refl_b02', 'sur_refl_b03', 'sur_refl_b04', 'sur_refl_b05', 'sur_refl_b06', 'sur_refl_b07'],
    'MCD43A4': ['Nadir_Reflectance_Band1', 'Nadir_Reflectance_Band2', 'Nadir_Reflectance_Band3', 'Nadir_Reflectance_Band4', 'Nadir_Reflectance_Band5', 'Nadir_Reflectance_Band6', 'Nadir_Reflectance_Band7']
}

RENAMED_BANDS = {
    'L9': ['ub', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'], 
    'L8': ['ub', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'], 
    'L7': ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
    'L5': ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],
    'MOD09A1': ['red', 'nir', 'blue', 'green', 'mir', 'swir1', 'swir2'],
    'MCD43A4': ['red', 'nir', 'blue', 'green', 'mir', 'swir1', 'swir2']
}

BAND_MAPPING = {
    'B': 'blue',
    'G': 'green',
    'R': 'red',
    'N': 'nir',
    'S1': 'swir1',
    'S2': 'swir2',
    'M': 'mir',
    'UB': 'ub'
}


__all__ = [
    "SPECTRAL_INDICES_URL",  # The URL to fetch spectral indices data (e.g., NDVI, EVI)
    "CONSTANTS_URL",         # The URL to fetch constants related to spectral indices
    "DATASET_IDS",           # A dictionary of dataset IDs for different satellite data (Landsat, MODIS)
    "ORIGINAL_BANDS",        # A dictionary mapping datasets to their original band names (before renaming)
    "RENAMED_BANDS",         # A dictionary mapping datasets to their renamed band names (after renaming)
    "BAND_MAPPING"           # A mapping of band abbreviations to full names (e.g., 'B' -> 'blue', 'G' -> 'green')
]