from geoserver.support import ResourceInfo, atom_link

class Style(ResourceInfo):
  def __init__(self,catalog, node):
    self.catalog = catalog
    self.name = node.find("name").text    
    self.href = atom_link(node)
    self.update()

  def update(self):
    ResourceInfo.update(self)
    self.name = self.metadata.find("name").text
    self.filename = self.metadata.find("filename").text
    # Get the raw sld
    sld_url = self.href.replace(".xml", ".sld")
    sld_xml = self.catalog.get_xml(sld_url)
    # Obtain the user style node where title and name are located
    user_style = sld_xml.find("{http://www.opengis.net/sld}NamedLayer/{http://www.opengis.net/sld}UserStyle")
    # Extract name and title nodes from user_style
    name_node = user_style.find("{http://www.opengis.net/sld}Name")
    title_node = user_style.find("{http://www.opengis.net/sld}Title")
    # Store the text value of sld name and title if present
    self.sld_name = name_node.text if hasattr(name_node, 'text') else None
    self.sld_title = title_node.text if hasattr(title_node, 'text') else None

  def __repr__(self):
    return "Style[%s]" % self.name
