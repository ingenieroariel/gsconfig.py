from geoserver.support import ResourceInfo, atom_link
from geoserver.layer import Layer
class LayerGroup(ResourceInfo):
    """
    Represents a layer group in geoserver 
    """
    def __init__(self,catalog,node):
        self.catalog = catalog
        self.href  = atom_link(node)
        self.name  = None
        self.update()

    def update(self): 
        ResourceInfo.update(self)
        self.name = self.metadata.find("name").text
        self.layers = [ Layer(x) for x in self.metadata.findall("layers/layer")] 
        self.styles = self.metadata.find("styles/style")
        self.bounds = self.metadata.find("bounds") 

    def __str__(self):
        return "<LayerGroup %s>" % self.name

    __repr__ = __str__
