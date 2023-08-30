import zipfile
import xml.etree.ElementTree as ET
from zip_utils import *
import re

# This dictionary contains the namespaces used in the FOXML files
FOXML_NAMESPACES = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'foxml': 'info:fedora/fedora-system:def/foxml#',
    'ns2': 'info:fedora/fedora-system:def/audit#',
    'ns3': "http://www.loc.gov/mods/v3",
    'ns4': 'info:fedora/fedora-system:def/relations-external#',
    'ns5': 'info:fedora/fedora-system:def/model#',
    'ns6': 'http://islandora.ca/ontology/relsext#',
    'ns7': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'ns8': 'http://islandora.ca/ontology/relsext#',
    'ns9': 'urn:oasis:names:tc:xacml:1.0:policy',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'mods': "http://www.loc.gov/mods/v3" 
}


def setup_namespaces() -> None:
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
    ET.register_namespace('', 'http://www.loc.gov/mods/v3')


def get_xml_tree_from_zip(target_filename: str, zip_ref: zipfile.ZipFile) -> tuple[BytesIO, ET.ElementTree]:
    """
    Search for a specific filename within a ZipFile object, including nested zip files.

    This function searches for the specified file name within the provided ZipFile object,
    including any nested zip files. If the file is found, it returns an ElementTree object
    representing the XML content of the first matching file.

    Args:
        - target_filename (str): The name of the file to search for within the zip_ref.
        - zip_ref (zipfile.ZipFile): The ZipFile object to search within.

    Returns:
        tuple[BytesIO, ET.ElementTree]: A tuple containing the read stream for the file and the
                                        ElementTree object representing the XML content of the file.

    Raises:
        FileNotFoundError: If the target_filename is not found in the zip file.
        ET.ParseError: If the target_filename is found, but the content is not valid XML.
    """

    # Get the read stream for the target file and parse it into an ElementTree
    file_read_stream = get_read_stream_zip_file(target_filename, zip_ref)
    if not file_read_stream:
        raise FileNotFoundError(f"File {target_filename} not found in zip file.")
    return file_read_stream, ET.parse(file_read_stream)

def is_foxml_managed(foxml_root: ET.ElementTree) -> bool:
    """
    Determine whether the MODS datastream is managed within a FOXML document.

    This function examines the provided <foxml_root> of a FOXML document to determine if the
    MODS datastream is managed (controlled by the repository) or not.

    Args:
        - foxml_root (ET.ElementTree): The root ElementTree of the FOXML document.

    Returns:
        bool: True if the MODS datastream is managed ("M" control group), False otherwise.

    Raises:
        ValueError: If the MODS datastream lacks a CONTROL_GROUP attribute.
    """
    
    # Find the <foxml:datastream> element with ID="MODS"
    datastream_element = foxml_root.find(".//foxml:datastream[@ID='MODS']", FOXML_NAMESPACES)
    if datastream_element is not None:
        # Get the value of the CONTROL_GROUP attribute
        control_group = datastream_element.get("CONTROL_GROUP")
        if control_group is None:
            # No CONTROL_GROUP attribute, but this is a required attribute
            raise ValueError("The MODS datastream does not have a CONTROL_GROUP attribute.")
        # Check if the value is "M" ("Managed"")
        return control_group == "M"
    return False


def set_control_group_inline(datastream_element: ET.Element) -> None:
    """
    Set the CONTROL_GROUP attribute of a MODS datastream element to "X" (Inline XML) within a FOXML document.

    This function modifies the provided <datastream_element> of a FOXML document to set the CONTROL_GROUP
    attribute of the MODS datastream to "X", indicating that the datastream content is inline XML
    within the document.

    Args:
        - datastream_element (ET.Element): The <foxml:datastream> element to be modified.

    Raises:
        ValueError: If the provided datastream_element lacks a CONTROL_GROUP attribute.
    """

    # Get the value of the CONTROL_GROUP attribute
    control_group = datastream_element.get("CONTROL_GROUP")
    if control_group is None:
        # No CONTROL_GROUP attribute, but this is a required attribute
        raise ValueError("The MODS datastream does not have a CONTROL_GROUP attribute.")
    # Change the CONTROL_GROUP attribute to "X" ("Inline XML")
    datastream_element.set("CONTROL_GROUP", "X")


def remove_content_location_from_mods_record(mods_record: ET.Element) -> None:
    """
    Remove the contentLocation element from a MODS record.

    This function modifies the provided <mods_record> element by removing the contentLocation element
    from it.

    Args:
        - mods_record (ET.Element): The <foxml:datastreamVersion> element representing the MODS record.
    """
    # Find the <foxml:contentLocation> element
    content_location = mods_record.find(".//foxml:contentLocation", FOXML_NAMESPACES)
    if content_location is not None:
        # Remove the contentLocation element from the MODS record
        mods_record.remove(content_location)


def add_xml_content_to_mods_record(mods_record: ET.Element, bag_archive: zipfile.ZipFile) -> None:
    """
    Add XML content to a MODS record within a FOXML document using an xmlContent element.

    This function takes a provided MODS record as an <ET.Element>, creates a new <foxml:xmlContent>
    element, and appends it as the last child of the MODS record. It then opens the MODS file specified
    in the datastream element (e.g., MODS.0) within the provided bag_archive ZipFile and generates
    the XML tree for it. Finally, the XML tree is merged into the xmlContent element.

    Args:
        - mods_record (ET.Element): The MODS record as an ElementTree element.
        - bag_archive (zipfile.ZipFile): The ZipFile containing the BagIt archive.

    Raises:
        FileNotFoundError: If the specified MODS file is not found in the bag_archive.
        ET.ParseError: If the specified MODS file is found, but the content is not valid XML.
    """

    # Create a new <foxml:xmlContent> element in the MODS record
    xml_content = ET.Element("xmlContent")
    # Set the xmlContent element as the last child of the MODS record
    mods_record.append(xml_content)
    # Open the MODS file specified in the datastream element (e.g. MODS.0) and generate the XML tree for it
    _, mods_tree = get_xml_tree_from_zip(mods_record.get("ID"), bag_archive)
    # Surround the MODS tree with a <mods> element
    # Define the <mods> element with its namespaces (we do this separately as ET ignores it when creating the tree for MODS)
    mods_element = ET.Element(
        "mods",
        attrib={
            "xmlns": "http://www.loc.gov/mods/v3",
            "xmlns:mods": "http://www.loc.gov/mods/v3",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
        },
    )
    # Create a new <mods> element and append the MODS tree to it
    xml_content.append(mods_element)
    mods_element.extend(mods_tree.getroot())


def replace_managed_mods_with_inline(datastream_element: ET.Element, bag_archive: zipfile.ZipFile) -> None:
    """
    Replace managed MODS records with inline XML content within a datastream element.

    This function locates all the <foxml:datastreamVersion> elements with LABEL="MODS Record"
    within the provided datastream_element. For each found MODS record, it removes the
    contentLocation element. Then, it creates a new <foxml:xmlContent> element in the MODS record 
    containing the MODS XML from the specified MODS file within the bag_archive ZipFile, effectively 
    making the record inline.

    Args:
        - datastream_element (ET.Element): The datastream element containing MODS records.
        - bag_archive (zipfile.ZipFile): The ZipFile containing the BagIt archive.

    Raises:
        FileNotFoundError: If the specified MODS file is not found in the bag_archive.
        ET.ParseError: If the specified MODS file is found, but the content is not valid XML.
    """

    # Find all the <foxml:datastreamVersion> with LABEL="MODS Record"
    mods_records = [elem for elem in datastream_element.findall(".//foxml:datastreamVersion", FOXML_NAMESPACES) if elem.get('LABEL', '').startswith('MODS')]
    # Loop over each one and make them inline
    for mods_record in mods_records:
        # Remove the contentLocation element from the MODS record
        remove_content_location_from_mods_record(mods_record)
        # Create a new <foxml:xmlContent> element in the MODS record containing the MODS XML
        add_xml_content_to_mods_record(mods_record, bag_archive)


def replace_managed_mods_with_inline_in_foxml(foxml_tree: ET.ElementTree, bag_archive: zipfile.ZipFile) -> None:
    """
    Replace managed MODS records with inline XML content within a FOXML document.

    This function locates all the <foxml:datastream> elements with ID="MODS" within the provided
    foxml_tree. For each found MODS record, it removes the contentLocation element. Then, it creates
    a new <foxml:xmlContent> element in the MODS record containing the MODS XML from the specified
    MODS file within the bag_archive ZipFile, effectively making the record inline.

    Args:
        - foxml_tree (ET.ElementTree): The FOXML document as an ElementTree.
        - bag_archive (zipfile.ZipFile): The ZipFile containing the BagIt archive.

    Raises:
        FileNotFoundError: If the specified MODS file is not found in the bag_archive.
        ET.ParseError: If the specified MODS file is found, but the content is not valid XML.
    """

    # Find the <foxml:datastream> element with ID="MODS"
    mods_datastream = foxml_tree.find(".//foxml:datastream[@ID='MODS']", FOXML_NAMESPACES)
    # Update the CONTROL_GROUP attribute value to "X", as MODS are now inline effective immediatly.
    set_control_group_inline(mods_datastream)
    # Replace the managed MODS records with inline XML content
    replace_managed_mods_with_inline(mods_datastream, bag_archive)


def process_foxml_tree(foxml_tree: ET.ElementTree, atomzip_archive: zipfile.ZipFile) -> None:
    """
    Process a FOXML document.

    This function takes a provided FOXML document as an ElementTree and converts all managed MODS
    records to inline XML content, if they were not already inline.

    Args:
        - foxml_tree (ET.ElementTree): The FOXML document as an ElementTree.
        - atomzip_archive (zipfile.ZipFile): The ZipFile containing the BagIt archive.

    Raises:
        FileNotFoundError: If any of the specified MODS files are not found in the bag_archive.
        ET.ParseError: If any of the specified MODS files are found, but the content is not valid XML.
    """
    if is_foxml_managed(foxml_tree):
        replace_managed_mods_with_inline_in_foxml(foxml_tree, atomzip_archive)
