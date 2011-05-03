from geoserver import workspace
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
        self.href = atom_link(node)

        self.name = None
        """
        A short identifier for this store, unique only within the workspace
        """

        self.enabled = False
        """ Should resources from this datastore be served? """

        self.workspace = workspace
        """ What workspace is the datastore a part of? """

        self.connection_parameters = dict()
        """ 
        The connection parameters for this store, used by GeoServer to
        connect to the underlying storage.
        """

        self.featuretypelist_url = None
        """
        The FeatureType resources provided by this datastore
        """

        self.update()

    def update(self):
        ResourceInfo.update(self)
        enabled = self.metadata.find("enabled")
        ws = self.metadata.find("workspace")
        connection_parameters = self.metadata.findall("connectionParameters/entry")
        feature_types = self.metadata.find("featureTypes")

        if enabled is not None and enabled.text == "true":
            self.enabled = True

        self.workspace = workspace.Workspace(self.catalog, ws) if ws is not None else None
        self.connection_parameters = dict((entry.attrib['key'], entry.text) for entry in connection_parameters) 
        self.featuretypelist_url = atom_link(feature_types)

    def encode(self, builder):
        builder.start("name", dict())
        builder.data(self.name)
        builder.end("name")

        builder.start("enabled", dict())
        if self.enabled:
            builder.data("true")
        else:
            builder.data("false")
        builder.end("enabled")

        builder.start("connectionParameters", dict())
        for k, v in self.connection_parameters.iteritems():
            builder.start("entry", dict(key=k))
            builder.data(v)
            builder.end("entry")
        builder.end("connectionParameters")

    def delete(self): 
        raise NotImplementedError()

    def get_resources(self):
        doc = self.catalog.get_xml(self.featuretypelist_url)
        return [FeatureType(self.catalog, n, self) for n in doc.findall("featureType")]

    def __repr__(self):
        wsname = self.workspace.name if self.workspace is not None else None
        return "DataStore[%s:%s]" % (wsname, self.name)

class UnsavedDataStore(DataStore):
    def __init__(self, catalog, name, workspace):
        self.name = name
        self.workspace = workspace
        self.href = catalog.service_url + "/workspaces/" + workspace.name + "/datastores/" + name + ".xml"
        self.connection_parameters = dict()
        self.enabled = True

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
        ws = self.metadata.find('workspace')
        data_url = self.metadata.find('url')
        coverages = self.metadata.find('coverages')

        if enabled is not None and enabled.text == 'true':
            self.enabled = True
        else:
            self.enabled = False

        self.type = type.text if type is not None else None
        self.workspace = workspace.Workspace(self.catalog, ws) if ws is not None else None
        self.data_url = data_url.text if data_url is not None else None
        self.coveragelist_url = atom_link(coverages)

    def encode(self, builder):
        builder.start("name", dict())
        builder.data(self.name)
        builder.end("name")

        builder.start("type", dict())
        builder.data(self.type)
        builder.end("type")

        builder.start("enabled", dict())
        if self.enabled:
            builder.data("true")
        else:
            builder.data("false")
        builder.end("enabled")

    def get_resources(self):
        doc = self.catalog.get_xml(self.coveragelist_url)
        return [Coverage(self.catalog, n, self) for n in doc.findall("coverage")]

    def __repr__(self):
        wsname = self.workspace.name if self.workspace is not None else None
        return "CoverageStore[%s:%s]" % (wsname, self.name)
