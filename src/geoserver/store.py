import geoserver.workspace as ws
from geoserver.resource import FeatureType, Coverage
from geoserver.support import ResourceInfo, atom_link

def datastore_from_index(catalog, workspace, node):
    name = node.find("name")
    return DataStore(catalog, workspace, name.text)

class DataStore(ResourceInfo):
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

    def get_resources(self):
        res_url = "%s/workspaces/%s/datastores/%s/featuretypes.xml" % (
                   self.catalog.service_url,
                   self.workspace.name,
                   self.name
                )
        xml = self.catalog.get_xml(res_url)
        def ft_from_node(node):
            name = node.find("name")
            return FeatureType(self.catalog, node, self)

        return [ft_from_node(node) for node in xml.findall("featureType")]

class CoverageStore(ResourceInfo):
    """
    XXX
    """
    resource_type = 'coverageStore'

    def __init__(self, catalog, node, workspace=None):
        self.catalog = catalog 

        self.href = atom_link(node)

        self.name = None

        self.type = None

        self.enabled = False

        self.workspace = workspace

        self.data_url = None

        self.coveragelist_url = None

        self.update()

        ## if workspace is not None:
        ##     self.workspace = workspace
        ## else:
        ##     name = node.find("name").text
        ##     href = atom_link(node.find("workspace"))
        ##     self.workspace = Workspace(self.catalog,name, href)

        ## link = node.find("{http://www.w3.org/2005/Atom}link")
        ## if link is not None and "href" in link.attrib:
        ##     self.href = link.attrib["href"]
        ##     self.update()
        ## else:
        ##     self.type = node.find("type").text
        ##     self.enabled = node.find("enabled").text == "true"
        ##     self.data_url = node.find("url").text
        ##     self.coverage_url = atom_link(node.find("coverages"))

    def update(self):
        ResourceInfo.update(self)
        type = self.metadata.find('type')
        enabled = self.metadata.find('enabled')
        workspace = self.metadata.find('workspace')
        data_url = self.metadata.find('url')
        coverages = self.metadata.find('coverages')

        if enabled is not None and enabled.text == 'true':
            self.enabled = True
        else:
            self.enabled = False

        self.type = type.text if type is not None else None
        self.workspace = ws.workspace_from_index(self.catalog, workspace) if workspace is not None else None
        self.data_url = data_url.text if data_url is not None else None
        self.coveragelist_url = atom_link(coverages)

    def get_resources(self):
        doc = self.catalog.get_xml(self.coveragelist_url)
        return [Coverage(self.catalog, n, self) for n in doc.findall("coverage")]

    def __repr__(self):
        wsname = self.workspace.name if self.workspace is not None else None
        return "CoverageStore[%s:%s]" % (wsname, self.name)
