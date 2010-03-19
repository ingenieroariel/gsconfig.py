from urllib2 import HTTPError
from geoserver.support import ResourceInfo, atom_link, get_xml
from geoserver.style import Style
from geoserver.resource import FeatureType, Coverage

class Layer(ResourceInfo): 
  resource_type = "layers"

  def __init__(self, node):
    self.name = node.find("name").text
    self.href = atom_link(node)
    self.update()

  def update(self):
    ResourceInfo.update(self)
    name = self.metadata.find("name")
    attribution = self.metadata.find("attribution")
    enabled = self.metadata.find("enabled")
    default_style = self.metadata.find("defaultStyle")

    if name is not None:
      self.name = name.text
    else:
      self.name = None
    
    if attribution is not None:
      self.attribution = attribution.text
    else:
      self.attribution = None

    if enabled is not None and enabled.text == "true":
      self.enabled = True
    else:
      self.enabled = False

    if default_style is not None:
      self.default_style = Style(default_style)
    else:
      self.default_style = None

    resource = self.metadata.find("resource")
    if resource and "class" in resource.attrib:
      if resource.attrib["class"] == "featureType":
        self.resource = FeatureType(resource)
      elif resource.attrib["class"] == "coverage":
        self.resource = Coverage(resource)

  def __repr__(self):
    return "Layer[%s]" % self.name
