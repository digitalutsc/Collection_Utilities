import zipfile
import os
from io import BytesIO
from typing import Optional


def get_read_stream_zip_file(target_filename: str, zip_ref: zipfile.ZipFile) -> Optional[BytesIO]:
    """
    Search for a specified filename within a ZipFile object, including nested zip files,
    and retrieve a read stream to the first matching file encountered.

    Args:
        target_filename (str): The filename to locate within the zip_ref.
        zip_ref (zipfile.ZipFile): The ZipFile object to search within.

    Returns:
        Optional[BytesIO]: A read stream to the first identified matching file, or None if not found.
    """
    nested_zip_list = []
    for name in zip_ref.namelist():
        if '.zip' in name:
            # Skip nested zips here and process them later if needed
            nested_zip_list.append(name)

        filename = os.path.basename(name)
        if target_filename in filename:
            return zip_ref.open(name)
    
    # Now process nested zip files, if any
    for name in nested_zip_list:
        if '.zip' in name:
            with zip_ref.open(name) as nested_zip_file:
                nested_zip_data = nested_zip_file.read()
                with zipfile.ZipFile(BytesIO(nested_zip_data), 'r') as nested_zip_ref:
                    nested_result = get_read_stream_zip_file(target_filename, nested_zip_ref)
                    if nested_result:
                        return nested_result
