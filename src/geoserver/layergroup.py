from geoserver.support import get_xml
from geoserver.layer import FeatureType

class LayerGroup(object):
    """
    Represents a layer group in geoserver 
    """
    def __init__(self,catalog,name):
        self.catalog = catalog
        self.name = name
        self.xmlNode = get_xml("%s/layergroups/%s.xml" % (self.catalog.service_url,self.name))  

    @property
    def layers(self):
        """
        Returns a list of the layers in a layer group
        """
        layers = self.xmlNode.find("layers")
        return [layer.find("name").text for layer in layers]

    @property
    def styles(self):
        styles = self.xmlNode.find("styles")
        return [style.find("name") for style in styles] 

    @property
    def bounds(self):
        """
        Make this more useful
        """
        bounds = self.xmlNode.find("bounds")
        minx = bounds.find("minx").text
        miny = bounds.find("miny").text
        maxx = bounds.find("maxx").text
        maxy = bounds.find("maxy").text
        return [minx,miny,maxx,maxy]

    def __str__(self):
        return "<LayerGroup %s>" % self.name
