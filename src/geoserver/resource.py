from geoserver.support import ResourceInfo, atom_link

class FeatureType(ResourceInfo):
  resource_type = "featureType"

  def __init__(self, node, store=None):
    self.href = atom_link(node)
    self.store = store
    self.update()

  def update(self):
    ResourceInfo.update(self)
    self.abstract = self.metadata.find("abstract")
    self.abstract = self.abstract.text if self.abstract is not None else None

  def encode(self, builder):
    builder.start("abstract", dict())
    builder.data(self.abstract)
    builder.end("abstract")

  def get_url(self, service_url):
    return self.href

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)

class Coverage(ResourceInfo):
  resource_type = "coverage"

  def __init__(self, node, store=None):
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
