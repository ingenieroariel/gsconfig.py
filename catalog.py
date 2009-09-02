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
    pass

  def remove(self, object):
    pass

  def save(self, object):
    pass

  def getStore(self, id=None, workspace=None, name=None):
    pass

  def getStores(self, workspace=None):
    pass

  def getResource(self, id=None, namespace=None, name=None, store=None):
    pass

  def getResources(self, namespace=None, store=None):
    pass

  def getLayer(self, id=None, name=None):
    pass

  def getLayers(self, resource=None, style=None):
    pass

  def getMaps(self):
    pass

  def getMap(self, id=None, name=None):
    pass

  def getLayerGroup(self, id=None, name=None):
    pass

  def getLayerGroups(self):
    pass

  def getStyle(self, id=None, name=None):
    pass

  def getStyles(self):
    pass
  
  def getNamespace(self, id=None, prefix=None, uri=None):
    pass

  def getDefaultNamespace(self):
    pass

  def setDefaultNamespace(self):
    pass

  def getWorkspace(self, id=None, name=None):
    pass

  def getDefaultWorkspace(self):
    pass

  def setDefaultWorkspace(self):
    pass

