import xml.etree.ElementTree as ET

def is_managed(xml_filepath: str) -> bool:
    """ Return True if the MODS for the passed FOXML file (at <xml_filepath>) is managed, False otherwise."""

    # Define the namespace mapping
    namespaces = {
        "foxml": "info:fedora/fedora-system:def/foxml#",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    # Parse the XML file
    tree = ET.parse(xml_filepath)
    root = tree.getroot()

    # Find the <foxml:datastream> element using the namespace prefix
    datastream_element = root.find(".//foxml:datastream", namespaces)

    if datastream_element is not None:
        # Get the value of the CONTROL_GROUP attribute
        control_group = datastream_element.get("CONTROL_GROUP")

        # Check if the value is "M"
        return control_group == "M"

    return False

# Example XML file path for testing
xml_filepath = "/home/hassan/collection_utilities/foxml_scripts/foxml.xml"

result = is_managed(xml_filepath)
print(result)  # Output: True or False
