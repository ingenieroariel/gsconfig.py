from geoserver.support import get_xml
from geoserver.layer import FeatureType

class LayerGroup(object):
    """
    Represents a layer group in geoserver 
    """
    def __init__(self,catalog,name):
        self.catalog = catalog
        self.name = name 

    @property
    def layers(self):
        """
        Returns a list of the layers in a layer group
        """
        url = get_xml("%s/layergroups/%s.xml" % (self.catalog.service_url,self.name))
        layers = url.find("layers")
        return [layer.find("name").text for layer in layers]

    @property
    def styles(self):
        return "styles" 

    @property
    def bounds(self):
        return "bounds"

    def __str__(self):
        return "<LayerGroup %s>" % self.name
