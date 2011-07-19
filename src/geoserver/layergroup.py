from geoserver.support import ResourceInfo, xml_property

def _maybe_text(n):
    if n is None:
        return None
    else:
        return n.text

def _layer_list(node):
    if node is not None:
       return [_maybe_text(n.find("name")) for n in node.findall("layer")]

def _style_list(node):
    if node is not None:
       return [_maybe_text(n.find("name")) for n in node.findall("style")]

def _write_layers(builder, layers):
    builder.start("layers", dict())
    for l in layers:
        builder.start("layer", dict())
        if l is not None:
            builder.start("name", dict())
            builder.data(l)
            builder.end("name")
        builder.end("layer")
    builder.end("layers")

def _write_styles(builder, styles):
    builder.start("styles", dict())
    for s in styles:
        builder.start("style", dict())
        if s is not None:
            builder.start("name", dict())
            builder.data(s)
            builder.end("name")
        builder.end("style")
    builder.end("styles")

class LayerGroup(ResourceInfo):
    resource_type = "layerGroup"
    save_method = "PUT"

    """
    Represents a layer group in geoserver 
    """
    def __init__(self, catalog, name):
        super(LayerGroup, self).__init__()

        assert isinstance(name, basestring)

        self.catalog = catalog
        self.name = name

    @property
    def href(self):
        return "%s/layergroups/%s.xml" % (self.catalog.service_url, self.name)

    styles = xml_property("styles", _style_list)
    layers = xml_property("layers", _layer_list)

    writers = dict(
              styles = _write_styles,
              layers = _write_layers
            )

    def __str__(self):
        return "<LayerGroup %s>" % self.name

    __repr__ = __str__
