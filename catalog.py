import json
from pprint import pprint as pp
from urllib2 import urlopen, HTTPError

def getJSON(url):
  response = urlopen(url).read()
  try:
    return json.loads(response)
  except:
    print response
    raise

class AmbiguousRequestError(Exception):
  pass 

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

class Style:
  def __init__(self, params):
    self.name = params["name"]
    self.href = params["href"]
    self.update()

  def update(self):
    response = getJSON(self.href)
    self.name = response["style"]["name"]
    self.filename = response["style"]["filename"]

  def __repr__(self):
    return "Style[%s]" % self.name

class Workspace: 
  def __init__(self, name, href):
    self.name = name
    self.href = href

  def __repr__(self):
    return "%s @ %s" % (self.name, self.href)

class DataStore:
  def __init__(self, params, workspace=None):
    self.name = params["name"]
    self.workspace = workspace if workspace is not None else Workspace(params["workspace"]["name"], params["workspace"]["href"])

    if "href" in params:
      self.href = params["href"]
      self.update()
    else:
      self.enabled = params["enabled"]
      self.connection_parameters = params["connectionParameters"]["entry"]
      self.feature_type_url = params["featureTypes"]

  def update(self):
    response = getJSON(self.href)
    params = response["dataStore"]
    self.enabled = params["enabled"]
    self.connection_parameters = params["connectionParameters"]["entry"]
    self.feature_type_url = params["featureTypes"]

  def getResources(self):
    response = getJSON(self.feature_type_url)
    types = response["featureTypes"]["featureType"]
    return [FeatureType(ft, self) for ft in types]

  def __repr__(self):
    return "DataStore[%s:%s]" % (self.workspace.name, self.name)

class ResourceInfo:
  resourceType = 'abstractResourceType'

  def update(self):
    self.response = getJSON(self.href)
    self.params = params = self.response[self.resourceType]
    import pdb; pdb.set_trace()
    self.title = params[u'title']
    self.srs = params[u'srs']
    self.name = params[u'name']
    self.keyword = params[u'keywords']
    self.abstract = params[u'abstract']

  def getAbstract(self):
    return self.abstract

class FeatureType(ResourceInfo):
  resourceType = 'featureType'

  def __init__(self, params, store=None):
    self.name = params["name"]
    self.href = params["href"]
    self.store = store
    self.update()

  def update(self):
    ResourceInfo.update(self)

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)

class CoverageStore(ResourceInfo):
  resourceType = 'coverageStore'

  def __init__(self, params, workspace=None):
    self.name = params["name"]
    self.workspace = workspace if workspace is not None else Workspace(params["workspace"]["name"], params["workspace"]["href"])

    if "href" in params:
      self.href = params["href"]
      self.update()
    else:
      self.type = params["type"]
      self.enabled = params["enabled"]
      self.data_url = params["url"]
      self.coverage_url = params["coverages"]

  def update(self):
    ResourceInfo.update(self)
    self.enabled = self.params["enabled"]
    self.coverage_url = self.params["coverages"]
    self.data_url = self.params["url"]

  def getResources(self):
    response = getJSON(self.coverage_url)
    types = response["coverages"]["coverage"]
    return [Coverage(cov, self) for cov in types]

  def __repr__(self):
    return "CoverageStore[%s:%s]" % (self.workspace.name, self.name)

class Coverage:
  def __init__(self, params, store=None):
    self.name = params["name"]
    self.href = params["href"]
    self.store = store
  
  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)

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
    self.service_url = url

  def add(self, object):
    raise NotImplementedError()

  def remove(self, object):
    raise NotImplementedError()

  def save(self, object):
    raise NotImplementedError()

  def getStore(self, name, workspace=None):
    if workspace is None:
      workspaces = self.getWorkspaces()
      stores = [self.getStore(workspace=ws, name=name) for ws in workspaces]
      stores = filter(lambda x: x is not None, stores)
      if len(stores) == 0:
        return None
      elif len(stores) > 1:
        raise AmbiguousRequestError("%s does not uniquely identify a store" % name)
      else:
        return stores[0]
    else:
      dsUrl = "%s/workspaces/%s/datastores/%s.json" % (self.service_url, workspace.name, name)
      csUrl = "%s/workspaces/%s/coveragestores/%s.json" % (self.service_url, workspace.name, name)

      try:
        store = getJSON(dsUrl)
        return DataStore(store["dataStore"], workspace)
      except HTTPError, e:
        try:
          store = getJSON(csUrl)
          return CoverageStore(store["coverageStore"], workspace)
        except HTTPError, e2:
          return None

    raise NotImplementedError()

  def getStores(self, workspace=None):
    if workspace is not None:
      stores = []
      dsUrl = "%s/workspaces/%s/datastores.json" % (self.service_url, workspace.name)
      csUrl = "%s/workspaces/%s/coveragestores.json" % (self.service_url, workspace.name)

      try: 
        response = getJSON(dsUrl)
        dsList = response["dataStores"]
        if not isinstance(dsList, basestring):
          dsList = dsList["dataStore"]
          stores.extend([DataStore(store, workspace) for store in dsList])
      except HTTPError, e:
        print e
        pass

      try: 
        response = getJSON(csUrl)
        csList = response["coverageStores"]
        if not isinstance(csList, basestring): 
          csList = csList["coverageStore"]
          stores.extend([CoverageStore(store, workspace) for store in csList])
      except HTTPError, e:
        pass

      return stores
    else:
      stores = []
      for ws in self.getWorkspaces():
        a = self.getStores(ws)
        stores.extend(a)

      return stores

  def getResource(self, name, store=None, workspace=None):
    if store is not None:
      candidates = filter(lambda x: x.name == name, store.getResources())
      if len(candidates) == 0:
        return None
      elif len(candidates) > 1:
        raise AmbiguousRequestError
      else:
        return candidates[0]

    if workspace is not None:
      for store in self.getStores(workspace):
        resource = self.getResource(name, store)
        if resource is not None:
          return resource
      return None

    for ws in self.getWorkspaces():
      resource = self.getResource(name, workspace=ws)
      if resource is not None:
        return resource
    return None

  def getResources(self, store=None, workspace=None, namespace=None):
    if store is not None:
      return store.getResources()
    if workspace is not None:
      resources = []
      for store in self.getStores(workspace):
        resources.extend(self.getResources(store))
      return resources
    resources = []
    for ws in self.getWorkspaces():
      resources.extend(self.getResources(workspace=ws))
    return resources

  def getLayer(self, id=None, name=None):
    raise NotImplementedError()

  def getLayers(self, resource=None, style=None):
    description = getJSON("%s/layers.json" % self.service_url)
    return [Layer(l) for l in description["layers"]["layer"]]

  def getMaps(self):
    raise NotImplementedError()

  def getMap(self, id=None, name=None):
    raise NotImplementedError()

  def getLayerGroup(self, id=None, name=None):
    raise NotImplementedError()

  def getLayerGroups(self):
    raise NotImplementedError()

  def getStyle(self, name):
    candidates = filter(lambda x: x.name == name, self.getStyles())
    if len(candidates) == 0:
      return None
    elif len(candidates) > 1:
      raise AmbiguousRequestError
    else:
      return candidates[0]

  def getStyles(self):
    description = getJSON("%s/styles.json" % self.service_url)
    return [Style(s) for s in description["styles"]["style"]]
    return description
  
  def getNamespace(self, id=None, prefix=None, uri=None):
    raise NotImplementedError()

  def getDefaultNamespace(self):
    raise NotImplementedError()

  def setDefaultNamespace(self):
    raise NotImplementedError()

  def getWorkspaces(self):
    description = getJSON("%s/workspaces.json" % self.service_url)
    return [Workspace(ws["name"], ws["href"]) for ws in description["workspaces"]["workspace"]]

  def getWorkspace(self, name):
    href = "%s/workspaces/%s.json" % (self.service_url, name)
    response = getJSON(href)
    ws = response["workspace"]
    return Workspace(ws["name"], href)

  def getDefaultWorkspace(self):
    return self.getWorkspace("default")

  def setDefaultWorkspace(self):
    raise NotImplementedError()

