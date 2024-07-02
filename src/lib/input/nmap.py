from xml.etree import ElementTree
from pathlib import Path

def parse_xml(xml_file: Path):
    tree = ElementTree.parse(xml_file)
    root = tree.getroot()
    for member in root.attrib:
        print(f"{member}: {root.attrib[member]}")

if __name__ == "__main__":
    parse_xml(Path("nmap-output.xml"))
