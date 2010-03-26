from geoserver.support import ResourceInfo, atom_link

class Workspace(ResourceInfo): 
    resource_type = "workspace"

    def __init__(self, catalog, node):
        self.catalog = catalog
        self.href = atom_link(node)

        self.datastores = []

        self.coveragestores = []

        self.update()

    def update(self):
        ResourceInfo.update(self)

        enabled = self.metadata.find("enabled")
        datastores = self.metadata.find("dataStores")
        coveragestores = self.metadata.find("coverageStores")

        if enabled is not None and enabled.text == 'true':
            enabled = True
        else:
            enabled = False

        self.datastore_url = atom_link(datastores)
        self.coveragestore_url = atom_link(coveragestores)

    def __repr__(self):
        return "%s @ %s" % (self.name, self.href)
