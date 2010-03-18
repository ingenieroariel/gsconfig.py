from urllib2 import HTTPError
from geoserver.support import atom_link, get_xml
from geoserver.style import Style
from geoserver.resource import FeatureType, Coverage

class Layer: 
  def __init__(self, node):
    self.name = node.find("name").text
    self.href = atom_link(node)
    self.update()

  def update(self):
    try: 
      layer = get_xml(self.href)
      self.name = layer.find("name").text
      self.attribution = layer.find("attribution").text
      self.enabled = layer.find("enabled").text == "true"
      self.default_style = Style(layer.find("defaultStyle"))
      resource = layer.find("resource")
      if resource and "class" in resource.attrib:
        if resource.attrib["class"] == "featureType":
          self.resource = FeatureType(resource)
        elif resource.attrib["class"] == "coverage":
          self.resource = Coverage(resource)
    except HTTPError, e:
      print e.geturl()

  def __repr__(self):
    return "Layer[%s]" % self.name
