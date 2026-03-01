from datetime import datetime
from IPython import get_ipython
import urllib.request
import json


# ------------------------
# Jupyter Notebook Hooks
# ------------------------

def jup_log_start(info=None):
    """
    Record the start time of the code cell execution.

    Args:
        info (str, optional): Optional additional information to mark the execution (default is None).

    Returns:
        datetime: The start time of the execution.
    """
    start_time = datetime.now()
    print(f"\nStart Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    return start_time

def jup_register_hook():
    """
    Register a hook in Jupyter Notebook to automatically record time before each cell execution.

    Returns:
        bool: True if hook is successfully registered, False otherwise.
    """
    ipython = get_ipython()
    if ipython:
        ipython.events.register('pre_run_cell', jup_log_start)
        return True
    else:
        print("This environment is not Jupyter Notebook, hook cannot be registered.")
        return False




# ------------------------
# Data Fetching
# ------------------------

def json_fetch(url):
    """
    Fetch JSON data from the given URL.

    Args:
        url (str): The URL of the JSON file to be fetched.

    Returns:
        dict: The parsed JSON data as a Python dictionary.

    Raises:
        RuntimeError: If there is an error while fetching or decoding the JSON file.
    """
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        raise RuntimeError(f"Error fetching JSON from {url}: {e}")
    

__all__ = [
    "jup_log_start", 
    "jup_register_hook", 
    "json_fetch",
]