import geoserver.workspace as ws
from geoserver.resource import featuretype_from_index, coverage_from_index
from geoserver.support import ResourceInfo, atom_link, xml_property, \
        write_bool

def datastore_from_index(catalog, workspace, node):
    name = node.find("name")
    return DataStore(catalog, workspace, name.text)

def coveragestore_from_index(catalog, workspace, node):
    name = node.find("name")
    return CoverageStore(catalog, workspace, name.text)

class DataStore(ResourceInfo):
    resource_type = "dataStore"

    def __init__(self, catalog, workspace, name):
        super(DataStore, self).__init__()

        assert isinstance(workspace, ws.Workspace)
        assert isinstance(name, basestring)
        self.catalog = catalog
        self.workspace = workspace
        self.name = name

    @property
    def href(self):
        return "%s/workspaces/%s/datastores/%s.xml" % (self.catalog.service_url, self.workspace.name, self.name)

    enabled = xml_property("enabled", lambda x: x.text == "true")

    writers = dict(enabled=write_bool("enabled"))

    def get_resources(self):
        res_url = "%s/workspaces/%s/datastores/%s/featuretypes.xml" % (
                   self.catalog.service_url,
                   self.workspace.name,
                   self.name
                )
        xml = self.catalog.get_xml(res_url)
        def ft_from_node(node):
            return featuretype_from_index(self.catalog, self.workspace, self, node)

        return [ft_from_node(node) for node in xml.findall("featureType")]

class UnsavedDataStore(DataStore):
    save_method = "POST"

    def __init__(self, catalog, name, workspace):
        self.name = name
        self.workspace = workspace
        self.href = catalog.service_url + "/workspaces/" + workspace.name + "/datastores/"
        self.connection_parameters = dict()
        self.enabled = True

class CoverageStore(ResourceInfo):
    resource_type = 'coverageStore'

    def __init__(self, catalog, workspace, name):
        super(CoverageStore, self).__init__()

        assert isinstance(workspace, ws.Workspace)
        assert isinstance(name, basestring)

        self.catalog = catalog
        self.workspace = workspace
        self.name = name

    @property
    def href(self):
        return "%s/workspaces/%s/coveragestores/%s.xml" % (self.catalog.service_url, self.workspace.name, self.name)

    def get_resources(self):
        res_url = "%s/workspaces/%s/coveragestores/%s/coverages.xml" % (
                  self.catalog.service_url,
                  self.workspace.name,
                  self.name
                )

        xml = self.catalog.get_xml(res_url)

        def cov_from_node(node):
            name = node.find("name")
            return coverage_from_index(self.catalog, self.workspace, self, node)

        return [cov_from_node(node) for node in xml.findall("coverage")]

class UnsavedCoverageStore(CoverageStore):
    save_method = "POST"

    def __init__(self, catalog, name, workspace):
        self.name = name
        self.workspace = workspace
        self.href = catalog.service_url + "/workspaces/" + workspace.name + "/coveragestores/"
        self.type = "GeoTIFF"
        self.enabled = True
        self.data_url = "file:data/"
