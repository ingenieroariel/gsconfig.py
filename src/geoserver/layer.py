from urllib2 import HTTPError
from geoserver.support import get_xml
from geoserver.style import Style
from geoserver.resource import FeatureType, Coverage, delete

class Layer: 
  def __init__(self, params):
    self.name = params["name"]
    self.href = params["href"]
    self.update()

  def update(self):
    try: 
      layer = get_xml(self.href)["layer"]
      self.name = layer["name"]
      self.attribution = layer["attribution"]
      self.enabled = layer["enabled"]
      self.default_style = Style(layer["defaultStyle"])
      if layer["resource"]["@class"] == "featureType":
        self.resource = FeatureType(layer["resource"])
      elif layer["resource"]["@class"] == "coverage":
        self.resource = Coverage(layer["resource"])
    except HTTPError, e:
      print e.geturl()

  def delete(self): 
    url = self.href.replace(".xml","")
    delete(url)

  def __repr__(self):
    return "Layer[%s]" % self.name
