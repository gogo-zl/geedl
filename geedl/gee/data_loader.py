import ee
from .para import *
from .data_processing import *

class DataLoader:
    def __init__(self, dataset, date_range, roi, bands=None, remove_cloud=True, normalize=True):
        self.dataset = dataset
        self.date_range = date_range
        self.roi = roi
        self.bands = bands
        self.remove_cloud = remove_cloud
        self.normalize = normalize
        self.cloud_function = None
        self.dataset_ids = DATASET_IDS  # Assuming this is defined globally

    def set_cloud_function(self):
        """
        Set the cloud masking function based on the dataset.
        """
        if self.dataset == 'Landsat':
            self.cloud_function = rm_landsat_cloud  # Landsat cloud mask function
        elif self.dataset == 'MODIS':
            self.cloud_function = rm_modis_cloud  # MODIS cloud mask function
        else:
            raise ValueError(f"Unsupported dataset: {self.dataset}")

    def process_image(self, img, series):
        """
        Process an image by selecting bands and applying normalization.
        """
        img = img.select(ORIGINAL_BANDS[series], RENAMED_BANDS[series])

        # If user specifies bands, select them; otherwise keep all renamed bands
        if self.bands:
            img = img.select(self.bands)
        
        # Apply normalization
        if self.normalize:
            if self.dataset == 'Landsat':
                img = img.multiply(0.0000275).add(-0.2)  # Landsat normalization
            elif self.dataset == 'MODIS':
                img = img.multiply(0.0001)  # MODIS normalization
        
        # Retain system properties
        return img.copyProperties(img, ['system:time_start', 'system:time_end', 'system:index'])

    def get_image_collection(self, series):
        """
        Get the image collection for a specific series.
        """
        collection = (ee.ImageCollection(self.dataset_ids[series])
                      .filterBounds(self.roi)
                      .filterDate(self.date_range[0], self.date_range[1]))

        if self.remove_cloud:
            collection = collection.map(self.cloud_function)

        return collection.map(lambda img: self.process_image(img, series))


class LandsatProcessor(DataLoader):
    def __init__(self, date_range, roi, bands=None, remove_cloud=True, normalize=True, landsat_series=None):
        super().__init__('Landsat', date_range, roi, bands, remove_cloud, normalize)
        self.landsat_series = landsat_series or ['L5', 'L7', 'L8', 'L9']
        self.set_cloud_function()

    def process_series(self, series):
        """
        Process a single Landsat series.
        """
        return self.get_image_collection(series)


class MODISProcessor(DataLoader):
    def __init__(self, date_range, roi, bands=None, remove_cloud=True, normalize=True):
        super().__init__('MODIS', date_range, roi, bands, remove_cloud, normalize)
        self.set_cloud_function()

    def process_series(self):
        """
        Process MODIS series (MOD09A1).
        """
        return self.get_image_collection('MOD09A1')


def get_any_year_data(date_range, roi, dataset='Landsat', remove_cloud=True, normalize=True, bands=None, landsat_series=None):
    """
    Get the image collection for the specified time range and region for Landsat or MODIS datasets.
    
    Args:
        date_range (list): Start and end dates, e.g., ['2020-01-01', '2020-12-31'].
        roi (ee.Geometry): Region of interest.
        dataset (str): Dataset type ('Landsat' or 'MODIS').
        remove_cloud (bool): Whether to remove clouds from the images.
        normalize (bool): Whether to normalize the images.
        bands (list): User-defined bands.
        landsat_series (list): Landsat series, e.g., ['L5', 'L7'].
        
    Returns:
        ee.ImageCollection: Processed image collection.
    """
    if dataset == 'Landsat':
        processor = LandsatProcessor(date_range, roi, bands, remove_cloud, normalize, landsat_series)
    elif dataset == 'MODIS':
        processor = MODISProcessor(date_range, roi, bands, remove_cloud, normalize)
    else:
        raise ValueError(f"Unsupported dataset: {dataset}")
    
    # Process and merge the collections
    if dataset == 'MODIS':
        return processor.process_series()
    
    collections = [processor.process_series(series) for series in processor.landsat_series]
    merged_collection = ee.ImageCollection(collections).flatten().sort('system:time_start')
    return merged_collection


__all__ = [
    "get_any_year_data",   # Main function to get the image data
    "LandsatProcessor",    # Class for processing Landsat data
    "MODISProcessor",      # Class for processing MODIS data
    "DataLoader"           # Base class for data loading and processing
]