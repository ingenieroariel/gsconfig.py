from geoserver.support import ResourceInfo, atom_link

class Workspace(ResourceInfo): 
    resource_type = "workspace"

    def __init__(self, catalog, name, href):
        self.catalog = catalog
        self.href = href

        self.name = None

        self.datastores = []

        self.coveragestores = []

        self.update()

    def update(self):
        ResourceInfo.update(self)
        datastores = self.metadata.find("dataStores")
        coveragestores = self.metadata.find("coverageStores")

        self.datastore_url = atom_link(datastores)
        self.coveragestore_url = atom_link(coveragestores)

    def __repr__(self):
        return "%s @ %s" % (self.name, self.href)
