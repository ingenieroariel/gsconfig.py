from geoserver.resource import FeatureType, Coverage
from geoserver.support import ResourceInfo, atom_link

class DataStore(ResourceInfo):
    """
    XXX represents a Datastore in GeoServer
    """
    resource_type = 'dataStore'

    def __init__(self, catalog, node, workspace=None):
        # self.name = node.find("name").text
        self.catalog = catalog
        self.href = node.get('href')

        self.name = None
        """
        A short identifier for this store, unique only within the workspace
        """

        self.enabled = False
        """ Should resources from this datastore be served? """

        self.workspace = None
        """ What workspace is the datastore a part of? """

        self.connection_parameters = dict()
        """ 
        The connection parameters for this store, used by GeoServer to
        connect to the underlying storage.
        """

        self.feature_types = list()
        """
        The FeatureType resources provided by this datastore
        """

        # if workspace is not None:
        #     self.workspace = workspace
        # else:
        #     ws = node.find("workspace/name").text
        #     href = node.find("workspace/{http://www.w3.org/2005/Atom}link").get("href")
        #     self.workspace = Workspace(self.catalog,ws, href)
        # link = node.find("{http://www.w3.org/2005/Atom}link")
        # if link is not None and "href" in link.attrib:
        #     self.href = link.attrib["href"]
        #     self.update()
        # self.enabled = node.find("enabled") == "true"
        # self.connection_parameters = [
        #      (entry.get("key"), entry.text) for entry in node.findall("connectionParameters/entry")
        # ]
        # self.feature_type_url = atom_link(node.find("featureTypes"))

    def update(self):
        ResourceInfo.update(self)
        enabled = self.metadata.find("enabled")
        workspace = self.metadata.find("workspace")
        connection_parameters = self.metadata.findall("connectionParameters/entry")
        feature_types = self.metadata.findall("featureTypes/{http://www.w3.org/2005/Atom}link")

        if enabled is not None and enabled.text == "true":
            self.enabled = True
        else: 
            self.enabled = False

        # self.workspace = Workspace(workspace) if workspace is not None else None
        self.connection_parameters = dict((entry.attrib['key'], entry.text) for entry in connection_parameters) 
        self.feature_types = [FeatureType(self.catalog, ft) for ft in feature_types]

    def delete(self): 
        raise NotImplementedError()

    def get_resources(self):
        return self.feature_types

    def __repr__(self):
        return "DataStore[%s:%s]" % (self.workspace.name, self.name)


class CoverageStore(ResourceInfo):
    """
    XXX 
    """
    resource_type = 'coverageStore'

    def __init__(self,catalog,node, workspace=None):
        self.catalog = catalog 

        self.href = atom_link(node)

        self.name = None

        self.type = None

        self.enabled = False

        self.workspace = None

        self.data_url = None

        self.coverages = None

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
        self.data_url = data_url.text if data_url is not None else None
        self.coverages = [Coverage(self.catalog, n) for n in coverages]

    def get_resources(self):
        return self.coverages

    def __repr__(self):
        return "CoverageStore[%s:%s]" % (self.workspace.name, self.name)
