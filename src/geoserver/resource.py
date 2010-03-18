from geoserver.support import ResourceInfo, atom_link, delete


class FeatureType(ResourceInfo):
  resource_type = "featureType"

  def __init__(self,catalog,node, store=None):
    self.catalog = catalog
    self.href = atom_link(node)
    self.store = store
    self.update()

  def update(self):
    ResourceInfo.update(self)
    self.abstract = self.metadata.find("abstract").text

  def encode(self, builder):
    builder.start("abstract", dict())
    builder.data(self.abstract)
    builder.end("abstract")

  def delete(self):
    """
    Removes a featureType from the GeoServer Catalog. Must remove 
    Removing a featureType from GeoServer takes three steps: 
        1. Remove the featureType's layer
        2. If the featureType is in a layer group remove it. 
        3. Remove the 
    """
    # deletes layer 
    layer_url = "%s/layers/%s" % (self.catalog.service_url,self.name)
    delete(layer_url)
    # deletes featureType
    feature_url = self.href.replace(".xml","")
    delete(feature_url)

  def get_url(self, service_url):
    return self.href

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)

class Coverage(ResourceInfo):
  resource_type = "coverage"

  def __init__(self,catalog,node, store=None):
    self.catalog = catalog
    self.href = atom_link(node)
    self.store = store
    self.update()

  def get_url(self, service_url):
    return self.href

  def update(self):
    ResourceInfo.update(self)
    self.abstract = self.metadata.find("description").text

  def encode(self, builder):
    builder.start("description", dict())
    builder.data(self.abstract)
    builder.end("description")

  
  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)
