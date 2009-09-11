class Layer: 
  def __init__(self, params):
    self.name = params["name"]
    self.href = params["href"]
    self.update()

  def update(self):
    try: 
      layer = getJSON(self.href)["layer"]
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

  def __repr__(self):
    return "Layer[%s]" % self.name


