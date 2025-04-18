# gee_utils.py
# 工具函数，用于操作 GEE 平台上的数据、资产，帮助管理 GEE 数据集

import ee

# ------------------------
# Feacol Functions
# ------------------------

def generate_rect_grid(study_area, grid_width=1.5, grid_height=1.5):
    """
    Generate a rectangular grid within the given study area.

    Args:
        study_area (ee.FeatureCollection): The region of interest (study area).
        grid_width (float): The grid cell width (longitude direction) in degrees (default is 1.5).
        grid_height (float): The grid cell height (latitude direction) in degrees (default is 1.5).

    Returns:
        ee.FeatureCollection: The generated grid, clipped to the study area.
    """
    bounds = study_area.bounds()
    coords = bounds.coordinates().get(0)

    min_lon = ee.List(ee.List(coords).get(0)).get(0)
    max_lon = ee.List(ee.List(coords).get(1)).get(0)
    min_lat = ee.List(ee.List(coords).get(0)).get(1)
    max_lat = ee.List(ee.List(coords).get(2)).get(1)

    lon_list = ee.List.sequence(min_lon, max_lon, grid_width)
    lat_list = ee.List.sequence(min_lat, max_lat, grid_height)

    grid = lon_list.map(
        lambda lon: lat_list.map(
            lambda lat: ee.Feature(
                ee.Geometry.Rectangle(
                    [lon, lat, ee.Number(lon).add(grid_width), ee.Number(lat).add(grid_height)]
                )
            )
        )
    ).flatten()

    grid_fc = ee.FeatureCollection(grid)
    return grid_fc.filterBounds(study_area)


def generate_hex_grid(study_area, radius=1.5):
    """
    Generate a hexagonal grid within the given study area.

    Args:
        study_area (ee.FeatureCollection): The region of interest (study area).
        radius (float): The distance from the center to the edge of the hexagon (default is 1.5 degrees).

    Returns:
        ee.FeatureCollection: The generated hexagonal grid, clipped to the study area.
    """
    bounds = study_area.bounds()
    coords = bounds.coordinates().get(0)

    xmin = ee.Number(ee.List(ee.List(coords).get(0)).get(0))
    ymin = ee.Number(ee.List(ee.List(coords).get(0)).get(1))
    xmax = ee.Number(ee.List(ee.List(coords).get(2)).get(0))
    ymax = ee.Number(ee.List(ee.List(coords).get(2)).get(1))

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

    hex_grid = ee.FeatureCollection(cell1.cat(cell2))
    return hex_grid.filterBounds(study_area)


# ------------------------
# Image Collection Functions
# ------------------------

def imgCol_date(imgcol):
    """
    Print the start date of each image in the image collection, formatted as 'yyyy-MM-dd'.

    Args:
        imgcol (ee.ImageCollection): The input image collection.

    Returns:
        list: A list of start dates for all images in the collection, formatted as 'yyyy-MM-dd'.
    """
    def format_start_date(image):
        # Get the start time attribute of the image and format it as 'yyyy-MM-dd'
        start_date = ee.Date(image.get('system:time_start')).format('yyyy-MM-dd')
        return ee.Feature(None, {'date': start_date})  # Create a feature with the date

    # Map the image collection to date features
    date_features = imgcol.map(format_start_date)

    # Extract the dates and print them
    dates = date_features.aggregate_array('date').getInfo()
    print("Start dates of images in the collection:")
    for date in dates:
        print(date)

    return dates


def imgCol_merge(collection, interval, aggregation_method='median'):
    """
    Merge a time series image collection into aggregated images based on a given time interval.

    Args:
        collection (ee.ImageCollection): The input time series image collection.
        interval (int): The time interval for merging (in days).
        aggregation_method (str): The aggregation method, can be 'mean', 'median', 'min', or 'max'. Default is 'median'.

    Returns:
        ee.ImageCollection: The merged image collection with aggregated images.
    """
    # Get the start and end dates of the collection
    start_date = ee.Date(collection.sort('system:time_start').first().get('system:time_start'))
    end_date = ee.Date(collection.sort('system:time_start').aggregate_max('system:time_start'))
    time_range = ee.List.sequence(start_date.millis(), end_date.millis(), interval * 24 * 60 * 60 * 1000)

    def merge_function(start_millis):
        start = ee.Date(start_millis)
        end = start.advance(interval, 'day')
        subset = collection.filterDate(start, end)

        # Apply the aggregation method
        if aggregation_method == 'mean':
            aggregated_image = subset.mean()
        elif aggregation_method == 'median':
            aggregated_image = subset.median()
        elif aggregation_method == 'min':
            aggregated_image = subset.min()
        elif aggregation_method == 'max':
            aggregated_image = subset.max()
        else:
            raise ValueError(f"Unsupported aggregation method: {aggregation_method}")

        return aggregated_image.set('system:time_start', start.millis())

    # Map the merge function over the time range and return the merged collection
    merged_collection = time_range.map(merge_function)

    return ee.ImageCollection(merged_collection)


# ------------------------
# Class 
# ------------------------

class GEEAssetManager:
    def __init__(self, root_path):
        """
        Initialize the GEEAssetManager with the root directory path.

        Args:
            root_path (str): The root path of the GEE asset directory.
        """
        self.root_path = root_path  # Store the root directory path

    def _get_full_path(self, sub_path):
        """
        Combine the root path with the specified sub-path.

        Args:
            sub_path (str): The sub-path (folder or asset) within the root directory.

        Returns:
            str: The full asset path.
        """
        return f"{self.root_path}/{sub_path}"

    def _confirm_action(self, action_name, skip_confirmation=False):
        """
        Private method for two-step confirmation before performing an action.

        Args:
            action_name (str): The name of the action to be performed.
            skip_confirmation (bool): If True, skip the confirmation steps and execute the action directly.

        Returns:
            bool: True if the action is confirmed and executed, False if aborted.
        """
        # Print the action to be confirmed
        print(f"Action to be performed: {action_name}")
        confirmation = input(f"Type 'yes' to confirm the action or 'no' to cancel: ").strip().lower()

        # If skip_confirmation is True, directly perform the action
        if skip_confirmation or confirmation == 'yes':
            return True
        else:
            print(f"Action {action_name} was cancelled.")
            return False

    def _ensure_asset_exists(self, sub_path, asset_type='IMAGE_COLLECTION'):
        """
        Private method to check if the specified GEE asset exists; do not print anything.

        Args:
            sub_path (str): The relative path of the asset or folder to check or create.
            asset_type (str): The type of the asset, default is 'IMAGE_COLLECTION'.

        Returns:
            bool: True if the asset exists, False if it does not exist.
        """
        full_path = self._get_full_path(sub_path)  # Get the full path by combining root path and sub-path
        parent = '/'.join(full_path.split('/')[:-1])
        assets = ee.data.listAssets(parent).get('assets', [])
        existing_names = [a['name'] for a in assets]

        # Return True if the asset exists, False otherwise
        return full_path in existing_names

    def delete_asset_folder(self, sub_path):
        """
        Recursively delete all child assets under a specified GEE folder or ImageCollection,
        then delete the folder itself after confirmation.

        Args:
            sub_path (str): The relative path of the folder or ImageCollection to delete.
        """
        full_path = self._get_full_path(sub_path)  # Get the full path by combining root path and sub-path
        action_name = f"Delete Folder and Assets: {full_path}"
        
        if self._confirm_action(action_name, skip_confirmation=False):
            try:
                print(f"Deleting assets under {full_path}...")
                children = ee.data.listAssets(full_path).get('assets', [])
                if not children:
                    print(f"No children found in: {full_path}")
                else:
                    for asset in children:
                        ee.data.deleteAsset(asset['name'])
                        print(f"Deleted: {asset['name']}")
                ee.data.deleteAsset(full_path)
                print(f"Deleted folder: {full_path}")
            except Exception as e:
                print(f"Error deleting assets under {full_path}:\n{e}")
        else:
            print("Deletion process was cancelled by the user.")

    def copy_imagecollection(self, src_full_path, dst_sub_path, asset_type='IMAGE_COLLECTION'):
        """
        Copy all images from one Earth Engine ImageCollection to another, with flexible asset types.

        Args:
            src_full_path (str): The relative **FULL** path of the source ImageCollection asset (can be public or private).
            dst_sub_path (str): The relative path of the target ImageCollection or folder asset (must already exist).
            asset_type (str): The type of the asset to create at the destination (default is 'IMAGE_COLLECTION', can be 'folder').
        """
        src_full_path = src_full_path  # Get the full source path
        dst_full_path = self._get_full_path(dst_sub_path)  # Get the full destination path

        # Action name and message
        action_name = f"Copy Image Collection from {src_full_path} to {dst_full_path}"
        print_message = f"Successfully copied image collection from {src_full_path} to {dst_full_path}"

        # Confirm action
        if self._confirm_action(action_name, skip_confirmation=False):
            # Ensure the destination path exists, create it if necessary
            if not self._ensure_asset_exists(dst_sub_path, asset_type=asset_type):
                # If asset type is folder, create a folder; if IMAGE_COLLECTION, create an image collection
                if asset_type == 'FOLDER':
                    ee.data.createAsset({'type': 'FOLDER'}, dst_full_path)
                else:
                    ee.data.createAsset({'type': 'IMAGE_COLLECTION'}, dst_full_path)

            # List all the assets in the source directory
            assets = ee.data.listAssets(src_full_path).get('assets', [])
            
            if not assets:
                print(f"No assets found in source: {src_full_path}")
                return

            # Copy each image to the destination
            for asset in assets:
                if asset['type'] != 'IMAGE':  # Only copy 'IMAGE' type assets
                    continue
                img_name = asset['name'].split('/')[-1]  # Get image name
                src_img_path = asset['name']  # Source image path
                dst_img_path = f"{dst_full_path}/{img_name}"  # Destination image path

                try:
                    ee.data.copyAsset(src_img_path, dst_img_path)  # Perform the copy operation
                    print(f"Copied: {img_name}")
                except Exception as e:
                    print(f"Failed to copy {img_name}: {e}")
            print(print_message)
        else:
            print("Copy operation was cancelled by the user.")



__all__ = [
    "generate_rect_grid", 
    "generate_hex_grid", 
    "imgCol_date", 
    "imgCol_merge", 
    "GEEAssetManager"
]