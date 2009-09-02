class Catalog:
  """
  The GeoServer catalog represents all of the information in the GeoServer
  configuration.  This includes:
  - Stores of geospatial data
  - Resources, or individual coherent datasets within stores
  - Styles for resources
  - Layers, which combine styles with resources to create a visible map layer
  - LayerGroups, which alias one or more layers for convenience
  - Workspaces, which provide logical grouping of Stores
  - Maps, which provide a set of OWS services with a subset of the server's 
    Layers
  - Namespaces, which provide unique identifiers for resources
  """
  def __init__(self, url):
    pass

  def add(self, object):
    raise NotImplementedError()

  def remove(self, object):
    raise NotImplementedError()

  def save(self, object):
    raise NotImplementedError()

  def getStore(self, id=None, workspace=None, name=None):
    raise NotImplementedError()

  def getStores(self, workspace=None):
    raise NotImplementedError()

  def getResource(self, id=None, namespace=None, name=None, store=None):
    raise NotImplementedError()

  def getResources(self, namespace=None, store=None):
    raise NotImplementedError()

  def getLayer(self, id=None, name=None):
    raise NotImplementedError()

  def getLayers(self, resource=None, style=None):
    raise NotImplementedError()

  def getMaps(self):
    raise NotImplementedError()

  def getMap(self, id=None, name=None):
    raise NotImplementedError()

  def getLayerGroup(self, id=None, name=None):
    raise NotImplementedError()

  def getLayerGroups(self):
    raise NotImplementedError()

  def getStyle(self, id=None, name=None):
    raise NotImplementedError()

  def getStyles(self):
    raise NotImplementedError()
  
  def getNamespace(self, id=None, prefix=None, uri=None):
    raise NotImplementedError()

  def getDefaultNamespace(self):
    raise NotImplementedError()

  def setDefaultNamespace(self):
    raise NotImplementedError()

  def getWorkspace(self, id=None, name=None):
    raise NotImplementedError()

  def getDefaultWorkspace(self):
    raise NotImplementedError()

  def setDefaultWorkspace(self):
    raise NotImplementedError()

