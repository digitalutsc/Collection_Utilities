import zipfile
import os
import re
import xml.etree.ElementTree as ET
from io import BytesIO


def get_read_stream_zip_file(target_filename: str, zip_ref: zipfile.ZipFile) -> BytesIO:
    """ Searches for a specific filename inside a ZipFile object (including nested zip files) and returns a read stream to the first matching file found. """
    for name in zip_ref.namelist():
        if re.search(r'\.zip$', name) is not None:
            # We have a nested zip within the main zip
            with zip_ref.open(name) as nested_zip_file:
                # Read the whole nested zip entry into memory
                zfiledata = BytesIO(nested_zip_file.read())
                with zipfile.ZipFile(zfiledata, 'r') as nested_zip_ref:
                    nested_result = get_XML_tree_zip_file(
                        target_filename,
                        nested_zip_ref
                    )
                if nested_result:
                    return nested_result
        else:
            filename = os.path.basename(name)
            if target_filename in filename:
                return zip_ref.open(name)


def get_XML_tree_zip_file(target_filename: str, zip_ref: zipfile.ZipFile) -> ET.ElementTree:
    """ Searches for a specific filename inside a ZipFile object (including nested zip files) and returns an ElementTree object of the first matching file found. """
    # Get the read stream for the target file
    target_file = get_read_stream_zip_file(target_filename, zip_ref)
    if target_file:
        # Return the ElementTree object for the target file
        return ET.parse(target_file)


def setup_namespaces():
    """ Sets up the namespaces for the XML tree. """
    ET.register_namespace("dc", 'http://purl.org/dc/elements/1.1/')
    ET.register_namespace("foxml", 'info:fedora/fedora-system:def/foxml#')
    ET.register_namespace('audit', 'info:fedora/fedora-system:def/audit#')
    ET.register_namespace('fedora', 'info:fedora/fedora-system:def/relations-external#')
    ET.register_namespace('fedora-model', 'info:fedora/fedora-system:def/model#')
    ET.register_namespace('islandora', 'http://islandora.ca/ontology/relsext#')
    ET.register_namespace('oai_dc', 'http://www.openarchives.org/OAI/2.0/oai_dc/')
    ET.register_namespace('Policy', 'urn:oasis:names:tc:xacml:1.0:policy')
    ET.register_namespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
