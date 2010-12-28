from geoserver.support import ResourceInfo, atom_link, atom_link_xml, \
        xml_property, write_bool, write_string
from geoserver.style import Style
from geoserver.resource import FeatureType, Coverage 

from collections import namedtuple

class _attribution(object):
    def __init__(self, title, width, height):
        self.title = title
        self.width = width
        self.height = height

def _read_attribution(node):
    title = node.find("title")
    width = node.find("logoWidth")
    height = node.find("logoHeight")

    if title is not None:
        title = title.text
    if width is not None:
        width = width.text
    if height is not None:
        height = height.text

    return _attribution(title, width, height)

def _write_attribution(builder, attr):
    builder.start("attribution", dict())
    if attr.title is not None:
        builder.start("title", dict())
        builder.data(attr.title)
        builder.end("title")
    if attr.width is not None:
        builder.start("logoWidth", dict())
        builder.data(attr.width)
        builder.end("logoWidth")
    if attr.height is not None:
        builder.start("logoHeight", dict())
        builder.data(attr.height)
        builder.end("logoHeight")
    builder.end("attribution")

class Layer(ResourceInfo):
    def __init__(self, catalog, name):
        super(Layer, self).__init__()
        self.catalog = catalog
        self.name = name

    resource_type = "layer"

    @property
    def href(self):
        return "%s/layers/%s.xml" % (self.catalog.service_url, self.name)

    attribution_object = xml_property("attribution", _read_attribution)
    enabled = xml_property("enabled", lambda x: x.text == "true")
    
    def _get_attr_text(self):
        return self.attribution_object.title

    def _set_attr_text(self, text):
        self.dirty["attribution"] = _attribution(
                    text,
                    self.attribution_object.width,
                    self.attribution_object.height
                    )
        assert self.attribution_object.title == text

    attribution = property(_get_attr_text, _set_attr_text)

    writers = dict(
            attribution = _write_attribution,
            enabled = write_bool("enabled")
            )
