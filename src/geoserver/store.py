from geoserver.resource import FeatureType, Coverage
from geoserver.support import ResourceInfo, get_xml, atom_link
from geoserver.workspace import Workspace

class DataStore:

  resource_type = 'dataStore'
  def __init__(self,catalog,node, workspace=None):
    self.name = node.find("name").text
    self.catalog = catalog
    if workspace is not None:
        self.workspace = workspace
    else:
        ws = node.find("workspace/name").text
        href = node.find("workspace/{http://www.w3.org/2005/Atom}link").get("href")
        self.workspace = Workspace(self.catalog,ws, href)

    link = node.find("{http://www.w3.org/2005/Atom}link")
    if link is not None and "href" in link.attrib:
      self.href = link.attrib["href"]
      self.update()
    else:
     self.enabled = node.find("enabled") == "true"
     self.connection_parameters = [
          (entry.get("key"), entry.text) for entry in node.findall("connectionParameters/entry")
      ]
     self.feature_type_url = atom_link(node.find("featureTypes"))

  def update(self):
    node = get_xml(self.href)
    self.enabled = node.find("enabled") == "true"
    self.connection_parameters = [
        (entry.get("key"), entry.text) for entry in node.findall("connectionParameters/entry")
    ]
    self.feature_type_url = atom_link(node.find("featureTypes"))

  def delete(self): 
    raise NotImplementedError()

  def get_resources(self):
    node = get_xml(self.feature_type_url)
    types = node.findall("featureType")
    return [FeatureType(self.catalog,ft, self) for ft in types]

  def __repr__(self):
    return "DataStore[%s:%s]" % (self.workspace.name, self.name)

class CoverageStore(ResourceInfo):
  resource_type = 'coverageStore'

  def __init__(self,catalog,node, workspace=None):
    self.catalog  = catalog 
    self.name = node.find("name").text
    if workspace is not None:
        self.workspace = workspace
    else:
        name = node.find("name").text
        href = atom_link(node.find("workspace"))
        self.workspace = Workspace(self.catalog,name, href)

    link = node.find("{http://www.w3.org/2005/Atom}link")
    if link is not None and "href" in link.attrib:
      self.href = link.attrib["href"]
      self.update()
    else:
      self.type = node.find("type").text
      self.enabled = node.find("enabled").text == "true"
      self.data_url = node.find("url").text
      self.coverage_url = atom_link(node.find("coverages"))

  def update(self):
    ResourceInfo.update(self)
    self.data_url = self.metadata.find("url").text
    self.coverage_url = atom_link(self.metadata.find("coverages"))
  
  def delete(self):
    print self

  def get_resources(self):
    response = get_xml(self.coverage_url)
    types = response.findall("coverage")
    return [Coverage(self.catalog,cov, self) for cov in types]

  def __repr__(self):
    return "CoverageStore[%s:%s]" % (self.workspace.name, self.name)

