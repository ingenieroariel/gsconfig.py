from geoserver.layer import Layer
from geoserver.store import DataStore, CoverageStore
from geoserver.style import Style
from geoserver.support import get_xml, prepare_shapefile_bundle
from geoserver.workspace import Workspace

from os import unlink
from urllib2 import HTTPError
import httplib2

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

  def __init__(self, url, username="admin", password="geoserver"):
    self.service_url = url
    self.http = httplib2.Http()
    self.http.add_credentials(username, password)

  def add(self, object):
    raise NotImplementedError()

  def remove(self, object):
    raise NotImplementedError()

  def save(self, object, username="admin", password="geoserver"):
    """
    saves an object to the REST service

    gets the object's REST location and the XML from the object,
    then POSTS the request.
    """
    url = object.get_url(self.service_url)
    message = object.serialize()
    headers = {
      "Content-type": "application/xml",
      "Accept": "application/xml"
    }
    response = self.http.request(url, "PUT", message, headers)
    return response

  def get_store(self, name, workspace=None):
    if workspace is None:
      workspaces = self.get_workspaces()
      stores = [self.get_store(workspace=ws, name=name) for ws in workspaces]
      stores = filter(lambda x: x is not None, stores)
      if len(stores) == 0:
        return None
      elif len(stores) > 1:
        raise AmbiguousRequestError("%s does not uniquely identify a store" % name)
      else:
        return stores[0]
    else:
      ds_url = "%s/workspaces/%s/datastores/%s.xml" % (self.service_url, workspace.name, name)
      cs_url = "%s/workspaces/%s/coveragestores/%s.xml" % (self.service_url, workspace.name, name)

      try:
        store = get_xml(ds_url)
        return DataStore(store, workspace)
      except HTTPError:
        try:
          store = get_xml(cs_url)
          return CoverageStore(store, workspace)
        except HTTPError:
          return None

    raise NotImplementedError()

  def get_stores(self, workspace=None):
    if workspace is not None:
      stores = []
      ds_url = "%s/workspaces/%s/datastores.xml" % (self.service_url, workspace.name)
      cs_url = "%s/workspaces/%s/coveragestores.xml" % (self.service_url, workspace.name)
      try: 
        response = get_xml(ds_url)
        ds_list = response.findall("dataStore")
        stores.extend([DataStore(store, workspace) for store in ds_list])
      except HTTPError, e:
        print e
        pass
      try: 
        response = get_xml(cs_url)
        cs_list = response.findall("coverageStore")
        stores.extend([CoverageStore(store, workspace) for store in cs_list])
      except HTTPError, e:
        pass
      return stores
    else:
      stores = []
      for ws in self.get_workspaces():
        a = self.get_stores(ws)
        stores.extend(a)
      return stores

  def create_featurestore(self, name, data, workspace=None):
    if workspace is None:
      workspace = self.get_default_workspace()
    ds_url = "%s/workspaces/%s/datastores/%s/file.shp" % (self.service_url, workspace.name, name)
    # PUT /workspaces/<ws>/datastores/<ds>/file.shp
    headers = {
      "Content-type": "application/zip",
      "Accept": "application/xml"
    }
    zip = prepare_shapefile_bundle(name, data)
    message = open(zip).read()
    try:
      response = self.http.request(ds_url, "PUT", message, headers)
    except Exception, e:
      print e

    unlink(zip)

  def get_resource(self, name, store=None, workspace=None):
    if store is not None:
      candidates = filter(lambda x: x.name == name, store.get_resources())
      if len(candidates) == 0:
        return None
      elif len(candidates) > 1:
        raise AmbiguousRequestError
      else:
        return candidates[0]

    if workspace is not None:
      for store in self.get_stores(workspace):
        resource = self.get_resource(name, store)
        if resource is not None:
          return resource
      return None

    for ws in self.get_workspaces():
      resource = self.get_resource(name, workspace=ws)
      if resource is not None:
        return resource
    return None

  def get_resources(self, store=None, workspace=None, namespace=None):
    if store is not None:
      return store.get_resources()
    if workspace is not None:
      resources = []
      for store in self.get_stores(workspace):
        resources.extend(self.get_resources(store))
      return resources
    resources = []
    for ws in self.get_workspaces():
      resources.extend(self.get_resources(workspace=ws))
    return resources

  def get_layer(self, id=None, name=None):
    raise NotImplementedError()

  def get_layers(self, resource=None, style=None):
    description = get_xml("%s/layers.xml" % self.service_url)
    return [Layer(l) for l in description["layers"]["layer"]]

  def get_maps(self):
    raise NotImplementedError()

  def get_map(self, id=None, name=None):
    raise NotImplementedError()

  def get_layergroup(self, id=None, name=None):
    raise NotImplementedError()

  def get_layergroups(self):
    raise NotImplementedError()

  def get_style(self, name):
    candidates = filter(lambda x: x.name == name, self.get_styles())
    if len(candidates) == 0:
      return None
    elif len(candidates) > 1:
      raise AmbiguousRequestError()
    else:
      return candidates[0]

  def get_styles(self):
    description = get_xml("%s/styles.xml" % self.service_url)
    return [Style(s) for s in description.findall("style")]
  
  def get_namespace(self, id=None, prefix=None, uri=None):
    raise NotImplementedError()

  def get_default_namespace(self):
    raise NotImplementedError()

  def set_default_namespace(self):
    raise NotImplementedError()

  def get_workspaces(self):
    description = get_xml("%s/workspaces.xml" % self.service_url)
    def extract_ws(node):
        name = node.find("name").text
        href = node.find("{http://www.w3.org/2005/Atom}link").get("href")
        return Workspace(name, href)
    return [extract_ws(node) for node in description.findall("workspace")]

  def get_workspace(self, name):
    href = "%s/workspaces/%s.xml" % (self.service_url, name)
    ws  = get_xml(href)
    name = ws.find("name").text
    # href = ws.find("{http://www.w3.org/2005/Atom}link").get("href").text
    return Workspace(name, href)

  def get_default_workspace(self):
    return self.get_workspace("default")

  def set_default_workspace(self):
    raise NotImplementedError()
