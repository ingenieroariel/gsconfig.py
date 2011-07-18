from geoserver.support import ResourceInfo, atom_link
from geoserver.layer import Layer

class LayerGroup(ResourceInfo):
    """
    Represents a layer group in geoserver 
    """
    def __init__(self, catalog, name):
        self.catalog = catalog
        assert isinstance(name, basestring)
        self.name = name

    @property
    def href(self):
        return "%s/layergroups/%s.xml" % (self.catalog.service_url, self.name)

    def __str__(self):
        return "<LayerGroup %s>" % self.name

    __repr__ = __str__
