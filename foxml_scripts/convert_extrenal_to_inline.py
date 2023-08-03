import xml.etree.ElementTree as ET
from colorama import Fore
import sys
import zipfile
from rich.progress import track


def is_managed(xml_filepath: str) -> bool:
    """Return True if the MODS for the passed FOXML file (at <xml_filepath>) are managed, False otherwise."""

    # Define the namespace mapping
    namespaces = {
        "foxml": "info:fedora/fedora-system:def/foxml#",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    # Parse the XML file
    tree = ET.parse(xml_filepath)
    root = tree.getroot()

    # Find the <foxml:datastream> element with ID="MODS" using the namespace prefix
    datastream_element = root.find(".//foxml:datastream[@ID='MODS']", namespaces)

    if datastream_element is not None:
        # Get the value of the CONTROL_GROUP attribute
        control_group = datastream_element.get("CONTROL_GROUP")

        # Check if the value is "M"
        return control_group == "M"

    return False

namespaces = {
        "foxml": "info:fedora/fedora-system:def/foxml#",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

additional_namespaces = {
    "mods": "http://www.loc.gov/mods/v3",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xlink": "http://www.w3.org/1999/xlink",
}


# Read the original XML file
original_file = "/home/dsu/collection_utilities/foxml_scripts/foxml.xml"

# Create a new XML tree from the original content
tree = ET.parse(original_file)
root = tree.getroot()


# Find the <foxml:datastream> element with ID="MODS"
datastream = root.find(".//foxml:datastream[@ID='MODS']", namespaces=namespaces)

if datastream is not None:
    control_group = datastream.get("CONTROL_GROUP")
else:
    print(Fore.RED, f"There are no MODS in {original_file}. Stopping.")
    sys.exit(0)

# Update the CONTROL_GROUP attribute value to "X", as MODS are now inline effective immediatly.
datastream.set("CONTROL_GROUP", "X")

# Read the XML content from another file
additional_file = "/home/dsu/collection_utilities/foxml_scripts/MODS.0.xml"
with open(additional_file, "r") as f:
    additional_content = f.read()

# Find the <foxml:datastreamVersion> element with ID="MODS.0"
datastream_version = root.find(".//foxml:datastreamVersion[@ID='MODS.0']", namespaces=namespaces)

# Find the <foxml:contentLocation> element and remove it from <foxml:datastreamVersion> with ID="MODS.0"
content_location_mods = datastream_version.find(".//foxml:contentLocation", namespaces=namespaces)
if content_location_mods is not None:
    datastream_version.remove(content_location_mods)

# Parse the additional content and insert elements without the ns3 prefix
additional_root = ET.fromstring(additional_content)

for elem in additional_root.iter():
    # Remove the namespace prefix from the tag if present
    if '}' in elem.tag:
        elem.tag = elem.tag.split('}', 1)[1]

    # Remove the ns3 prefix from attributes if present
    for key, value in elem.attrib.items():
        if '}' in value:
            elem.attrib[key] = value.split('}', 1)[1]

# Wrap the additional XML content in <foxml:xmlContent>
xml_content_element = ET.Element("{info:fedora/fedora-system:def/foxml#}xmlContent")
# Define the <mods> element with its namespaces
mods_element = ET.Element(
    "mods",
    attrib={
        "xmlns": "http://www.loc.gov/mods/v3",
        "xmlns:mods": "http://www.loc.gov/mods/v3",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
    },
)
xml_content_element.append(mods_element)

mods_element.extend(additional_root)

# Insert the <foxml:xmlContent> element to the datastream_version
datastream_version.append(xml_content_element)

# Write the new XML tree to a new file
new_file = "modified.xml"

# Register the namespaces to preserve the original prefixes
ET.register_namespace("foxml", "info:fedora/fedora-system:def/foxml#")
ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

# Ensure that the original namespace prefix is used in the output file
ET._namespace_map["info:fedora/fedora-system:def/foxml#"] = "foxml"

tree.write(new_file, encoding="utf-8", xml_declaration=True)

print("Modified XML content written to:", new_file)







