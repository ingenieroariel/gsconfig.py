from datetime import datetime, timedelta
from geoserver.layer import Layer
from geoserver.store import DataStore, CoverageStore
from geoserver.style import Style
from geoserver.support import prepare_upload_bundle
from geoserver.layergroup import LayerGroup
from geoserver.workspace import Workspace
from os import unlink
import httplib2 
from xml.etree.ElementTree import XML

class UploadError(Exception):
    pass

class ConflictingDataError(Exception):
    pass

class AmbiguousRequestError(Exception):
    pass 

class Catalog(object):
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
    if self.service_url.endswith("/"):
        self.service_url = self.service_url.strip("/")
    self.http = httplib2.Http()
    self.username = username
    self.password = password
    self.http.add_credentials(self.username, self.password)
    self._cache = dict()

  def add(self, object):
    raise NotImplementedError()

  def remove(self, object):
    raise NotImplementedError()

  def delete(self,object):
    """
    send a delete request 
    XXX [more here]   
    """
    url = object.get_url(self.service_url)
    headers = {
      "Content-type": "application/xml",
      "Accept": "application/xml"
    } 
    response = self.http.request(url, "DELETE", headers=headers)
    self._cache.clear()
    return response

  
  def get_xml(self, url):
    cached_response = self._cache.get(url)

    def is_valid(cached_response):
        return cached_response is not None and datetime.now() - cached_response[0] < timedelta(seconds=5)

    if is_valid(cached_response):
        return XML(cached_response[1])
    else:
        response, content = self.http.request(url)
        if response.status == 200:
            self._cache[url] = (datetime.now(), content)
            return XML(content)
        else:
            return None

  def save(self, object):
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
    self._cache.clear()
    return response

  def get_store(self, name, workspace=None):
      stores = [s for s in self.get_stores(workspace) if s.name == name]
      if len(stores) == 0:
          return None
      elif len(stores) > 1:
          raise AmbiguousRequestError("%s does not uniquely identify a layer" % name)
      else:
          return stores[0]

  def get_stores(self, workspace=None):
      if workspace is not None:
          ds_list = self.get_xml(workspace.datastore_url)
          cs_list = self.get_xml(workspace.coveragestore_url)
          datastores = [DataStore(self, n) for n in ds_list.findall("dataStore")]
          coveragestores = [CoverageStore(self, n) for n in cs_list.findall("coverageStore")]
          return datastores + coveragestores
      else:
          stores = []
          for ws in self.get_workspaces():
              a = self.get_stores(ws)
              stores.extend(a)
          return stores

  def create_featurestore(self, name, data, workspace=None, overwrite=False):
    if overwrite == False and self.get_store(name, workspace) is not None:
        fullname = "%s :: %s" % (workspace.name, name) if workspace is not None else name
        raise ConflictingDataError("There is already a store named %s" % fullname)
    if workspace is None:
      workspace = self.get_default_workspace()
    ds_url = "%s/workspaces/%s/datastores/%s/file.shp" % (self.service_url, workspace.name, name)
    # PUT /workspaces/<ws>/datastores/<ds>/file.shp
    headers = {
      "Content-type": "application/zip",
      "Accept": "application/xml"
    }
    zip = prepare_upload_bundle(name, data)
    message = open(zip).read()
    try:
      headers, response = self.http.request(ds_url, "PUT", message, headers)
      self._cache.clear()
      if headers.status != 201:
          raise UploadError(response)
    finally:
      unlink(zip)

  def create_coveragestore(self, name, data, workspace=None, overwrite=False):
    if overwrite == False and self.get_store(name, workspace) is not None:
        fullname = "%s :: %s" % (workspace.name, name) if workspace is not None else name
        raise ConflictingDataError("There is already a store named %s" % fullname)
    if workspace is None:
      workspace = self.get_default_workspace()
    headers = {
      "Content-type": "image/tiff",
      "Accept": "application/xml"
    }

    zip = None
    ext = "geotiff"

    if isinstance(data, dict):
      zip = prepare_upload_bundle(name, data)
      message = open(zip).read()
      if "tfw" in data:
        headers['Content-type'] = 'application/zip'
        ext = "worldimage"
    elif isinstance(data, basestring):
      message = open(data).read()
    else:
      message = data.read()

    cs_url = "%s/workspaces/%s/coveragestores/%s/file.%s" % (self.service_url, workspace.name, name, ext)
    try:
      headers, response = self.http.request(cs_url, "PUT", message, headers)
      self._cache.clear()
      if headers.status != 201:
          raise UploadError(response)
    finally:
      if zip is not None:
        unlink(zip)

  def get_resource(self, name, store=None, workspace=None):
    if store is not None:
      candidates = filter(lambda x: x.name == name, self.get_resources(store))
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

  def get_layer(self, name=None):
    layers = [l for l in self.get_layers() if l.name == name]
    if len(layers) == 0:
      return None
    elif len(layers) > 1:
      raise AmbiguousRequestError("%s does not uniquely identify a layer" % name)
    else:
      return layers[0]

  def get_layers(self, resource=None, style=None):
    description = self.get_xml("%s/layers.xml" % self.service_url)
    lyrs = [Layer(self, l) for l in description.findall("layer")]
    if resource is not None:
      lyrs = [l for l in lyrs if l.resource.href == resource.href]
    # TODO: Filter by style
    return lyrs

  def get_maps(self):
    raise NotImplementedError()

  def get_map(self, id=None, name=None):
    raise NotImplementedError()

  def get_layergroup(self, id=None, name=None):
    group = self.get_xml("%s/layergroups/%s.xml" % (self.service_url, name))    
    return LayerGroup(self, group.find("name").text)

  def get_layergroups(self):
    groups = self.get_xml("%s/layergroups.xml" % self.service_url)
    return [LayerGroup(self,group) for group in groups.findall("layerGroup")]

  def get_style(self, name):
    candidates = filter(lambda x: x.name == name, self.get_styles())
    if len(candidates) == 0:
      return None
    elif len(candidates) > 1:
      raise AmbiguousRequestError()
    else:
      return candidates[0]

  def get_styles(self):
    description = self.get_xml("%s/styles.xml" % self.service_url)
    return [Style(self,s) for s in description.findall("style")]

  def create_style(self, name, data, overwrite = False):
    if overwrite == False and self.get_style(name) is not None:
      raise ConflictingDataError("There is already a style named %s" % name)

    headers = {
      "Content-type": "application/vnd.ogc.sld+xml",
      "Accept": "application/xml"
    }

    if overwrite:
      style_url = "%s/styles/%s.sld" % (self.service_url, name)
      headers, response = self.http.request(style_url, "PUT", data, headers)
    else:
      style_url = "%s/styles" % (self.service_url)
      headers, response = self.http.request(style_url, "POST", data, headers)

    self._cache.clear()
    if headers.status < 200 or headers.status > 299: raise UploadError(response)
  
  def get_namespace(self, id=None, prefix=None, uri=None):
    raise NotImplementedError()

  def get_default_namespace(self):
    raise NotImplementedError()

  def set_default_namespace(self):
    raise NotImplementedError()

  def get_workspaces(self):
    description = self.get_xml("%s/workspaces.xml" % self.service_url)
    return [Workspace(self, node) for node in description.findall("workspace")]

  def get_workspace(self, name):
    candidates = filter(lambda x: x.name == name, self.get_workspaces())
    if len(candidates) == 0:
      return None
    elif len(candidates) > 1:
      raise AmbiguousRequestError()
    else:
      return candidates[0]

  def get_default_workspace(self):
      return Workspace(self, XML("""
          <workspace>
              <atom:link xmlns:atom="%s" href="%s/workspaces/default.xml"></atom:link>
          </workspace>
      """ % ("http://www.w3.org/2005/Atom", self.service_url)
      ))

  def set_default_workspace(self):
    raise NotImplementedError()
