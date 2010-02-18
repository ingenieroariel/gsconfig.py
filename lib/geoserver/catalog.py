from pprint import pprint as pp
from urllib2 import urlopen, HTTPError
import httplib2
import json
import re

from geoserver.resource import FeatureType, Coverage
from geoserver.store import DataStore, CoverageStore
from geoserver.style import Style
from geoserver.support import getJSON
from geoserver.workspace import Workspace

class AmbiguousRequestError(Exception):
  pass 

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

  """
  saves an object to the REST service

  gets the object's REST location and the json from the object,
  then POSTS the request.
  """
  def save(self, object, username="admin", password="geoserver"):

    url = object.getUrl(self.service_url)
    objectJson = object.serialize()

    headers = {
        "Content-type": "text/json",
        "Accept": "text/json"
    }

    http = httplib2.Http()
    http.add_credentials(username,password) #factor out these credentials
    response = http.request(url, "PUT", objectJson, headers)

    #file = open("request","w")
    #file.write("Method: " + "PUT" +"\n")
    #file.write("Url: " + url + "\n")
    #file.write("Body: " + objectJson + "\n")
    #file.write("\n")
    #file.write("Response (printed from Python response represenation): " + response.__repr__())

    return response

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

