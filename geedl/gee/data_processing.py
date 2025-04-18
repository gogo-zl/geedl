# **File**: quality_control.py
# 处理影像数据和图像处理操作，不关心 GEE 资产的管理

from .para import *
from .notebook_utils import *
import ee

# -------------------------
# Remove Cloud Functions
# -------------------------

def rm_landsat_cloud(image):
    """
    Apply cloud masking to Landsat imagery.

    Args:
        image (ee.Image): Input Landsat image.
    
    Returns:
        ee.Image: The cloud-masked Landsat image with clouds and cloud shadow pixels removed.
    """
    qa = image.select('QA_PIXEL')  # Quality control band for Landsat
    cloud_mask = qa.bitwiseAnd(1 << 3).eq(0)  # Cloud bit flag
    cloud_shadow_mask = qa.bitwiseAnd(1 << 4).eq(0)  # Cloud shadow bit flag
    return image.updateMask(cloud_mask.And(cloud_shadow_mask))


def rm_modis_cloud(image):
    """
    Apply cloud masking to MODIS imagery.

    Args:
        image (ee.Image): Input MODIS image.
    
    Returns:
        ee.Image: The cloud-masked MODIS image with clouds and cloud shadows removed.
    """
    qa = image.select('StateQA')  # Quality control band for MODIS
    cloud_state_clear = qa.bitwiseAnd(3).eq(0)  # Clear state (Bits 0-1)
    no_cloud_shadow = qa.bitwiseAnd(1 << 2).eq(0)  # No cloud shadow (Bit 2)
    no_internal_cloud = qa.bitwiseAnd(1 << 10).eq(0)  # No internal cloud (Bit 10)
    return image.updateMask(cloud_state_clear.And(no_cloud_shadow).And(no_internal_cloud))


def rm_MCD43A4_cloud(image):
    """
    [Unused]Apply quality control (QC) mask to MCD43A4 image for all 7 bands using the quality bands.

    Args:
        image (ee.Image): Input MODIS MCD43A4 image.
    
    Returns:
        ee.Image: The cloud-masked MCD43A4 image with bad quality pixels masked out for all 7 bands.
    """
    # Extract the quality control bands for each of the 7 bands
    qc_band2 = image.select('BRDF_Albedo_Band_Mandatory_Quality_Band2')  # Select the second quality control band
    
    # Create a mask for good quality (Bit 0 = 0 means good quality)
    good_quality_mask = qc_band2.eq(0)  # Keep pixels with good quality
    
    # Apply the mask to the entire image (only keep good quality pixels)
    return image.updateMask(good_quality_mask)


# -----------------------------
# Spectral Indices Calculation
# -----------------------------

def add_spectral_indices(image, indices, keep_original=True):
    """
    Calculate and add the specified spectral indices to a single image.

    Args:
        image (ee.Image): The input image.
        indices (list): List of spectral indices to compute (e.g., ["NDVI", "EVI"]).
        keep_original (bool): Whether to keep the original image bands.
            - True: Returns an image with both original bands and computed indices.
            - False: Returns an image containing only the computed indices.

    Returns:
        ee.Image: The image with the computed spectral indices.
    """
    # Fetch the spectral indices and constants data from the JSON file
    
    spectral_indices = json_fetch(SPECTRAL_INDICES_URL)["SpectralIndices"]
    constants = json_fetch(CONSTANTS_URL)
    constant_values = {key: value["default"] for key, value in constants.items() if value["default"] is not None}

    result_image = image  # Start with the original image

    for index in indices:
        if index not in spectral_indices:
            raise ValueError(f"Index {index} is not present in the JSON file.")

        formula = spectral_indices[index]["formula"]
        bands = spectral_indices[index]["bands"]

        # Create a dictionary of parameters for the formula, mapping bands or constants
        params = {
            symbol: image.select(BAND_MAPPING[symbol]) if symbol in BAND_MAPPING
            else image.constant(constant_values[symbol]) for symbol in bands
        }

        # Add the computed index as a new band in the image
        result_image = result_image.addBands(image.expression(formula, params).rename(index))

    return result_image if keep_original else result_image.select(indices)


def add_spectral_indices_to_collection(imgcol, indices, keep_original=True):
    """
    Calculate and add the specified spectral indices to each image in an image collection.

    Args:
        imgcol (ee.ImageCollection): The input image collection.
        indices (list): List of spectral indices to compute (e.g., ["NDVI", "EVI"]).
        keep_original (bool): Whether to keep the original image bands.
            - True: Returns an image collection with both original bands and computed indices.
            - False: Returns an image collection containing only the computed indices.

    Returns:
        ee.ImageCollection: The image collection with the computed spectral indices.
    """
    return imgcol.map(lambda img: add_spectral_indices(img, indices, keep_original))


# ----------------------------
# Terrain Analysis Functions
# ----------------------------

def calculate_terrain_features(region, resolution, resample_method='bilinear'):
    """
    Calculate terrain features (elevation, slope, and aspect) for a given region.

    Args:
        region (ee.Geometry): The region of interest for terrain feature calculation.
        resolution (int): The target resolution for resampling (in meters).
        resample_method (str): Resampling method to use. Default is 'bilinear'.

    Returns:
        ee.Image: An image containing the terrain features (elevation, slope, aspect),
                  resampled to the specified resolution and clipped to the region.
    """
    # Load SRTM data (30m resolution)
    srtm = ee.Image('USGS/SRTMGL1_003')

    # Calculate slope and aspect
    slope = ee.Terrain.slope(srtm)
    aspect = ee.Terrain.aspect(srtm)

    # Combine terrain features (elevation, slope, aspect) into one image
    terrain_image = srtm.addBands(slope).addBands(aspect).rename(['elevation', 'slope', 'aspect'])

    # Resample to the specified resolution
    terrain_image_resampled = terrain_image.resample(resample_method)  # Apply resampling method
    terrain_image_resampled = terrain_image_resampled.reproject(
        crs=srtm.projection(),
        scale=resolution  # Set the target resolution
    ).clip(region)  # Clip the image to the region of interest

    return terrain_image_resampled





__all__ = [
    "rm_landsat_cloud", 
    "rm_modis_cloud", 
    "rm_MCD43A4_cloud", 
    "add_spectral_indices", 
    "add_spectral_indices_to_collection", 
    "calculate_terrain_features", 
]

