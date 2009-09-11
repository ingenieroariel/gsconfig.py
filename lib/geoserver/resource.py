from geoserver.support import ResourceInfo

class FeatureType(ResourceInfo):
  resourceType = 'featureType'

  def __init__(self, params, store=None):
    self.href = params.get("href","")
    self.store = store
    self.update()

  def getUrl(self, service_url):
    return self.href

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)

class Coverage:
  def __init__(self, params, store=None):
    self.name = params["name"]
    self.href = params["href"]
    self.store = store
  
  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)
