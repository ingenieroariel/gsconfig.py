from geoserver.support import ResourceInfo, getJSON
from geoserver.resource import FeatureType, Coverage

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

class CoverageStore(ResourceInfo):
  resourceType = 'coverageStore'

  def __init__(self, params, workspace=None):
    self.name = params["name"]
    self.workspace = workspace if workspace is not None else Workspace(params["workspace"]["name"], params["workspace"]["href"])

    if "href" in params:
      self.href = params["href"]
      self.update()
    else:
      self.type = params.get("type","")
      self.enabled = params.get("enabled","")
      self.data_url = params.get("url","")
      self.coverage_url = params.get("coverages","")

  def update(self):
    ResourceInfo.update(self)
    self.data_url = self.metadata.get("url","")
    self.coverage_url = self.metadata.get("coverages","")

  def getResources(self):
    response = getJSON(self.coverage_url)
    types = response["coverages"]["coverage"]
    return [Coverage(cov, self) for cov in types]

  def __repr__(self):
    return "CoverageStore[%s:%s]" % (self.workspace.name, self.name)

