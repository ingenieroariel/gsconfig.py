from geoserver.support import ResourceInfo, xml_property, write_string, \
        atom_link, atom_link_xml, bbox, bbox_xml, \
        FORCE_NATIVE, FORCE_DECLARED, REPROJECT
from xml.etree.ElementTree import tostring

def md_link(node):
    """Extract a metadata link tuple from an xml node"""
    mimetype = node.find("type")
    mdtype = node.find("metadataType")
    content = node.find("content")
    if None in [mimetype, mdtype, content]:
        return None
    else:
        return (mimetype.text, mdtype.text, content.text)

def featuretype_from_index(catalog, store, node):
    name = node.find("name")
    return FeatureType(catalog, store, name.text)

class FeatureType(ResourceInfo):
    resource_type = "featureType"

    def __init__(self, catalog, store, name):
        super(FeatureType, self).__init__()
  
        assert isinstance(store, ResourceInfo)
        assert isinstance(name, basestring)
        
        self.catalog = catalog
        self.store = store
        self.name = name

    @property
    def href(self):
        return "%s/workspaces/%s/datastores/%s/featuretypes/%s.xml" % (
                self.catalog.service_url,
                self.workspace.name,
                self.store.name,
                self.name
                )

    title = xml_property("title", "title")
    abstract = xml_property("abstract", "abstract")

    writers = dict(
                title = write_string("title"),
                abstract = write_string("abstract")
            )

class CoverageDimension(object):
    def __init__(self, name, description, range):
        self.name = name
        self.description = description
        self.range = range

def coverage_dimension(node):
    name = node.find("name")
    name = name.text if name is not None else None
    description = node.find("description")
    description = description.text if description is not None else None
    min = node.find("range/min")
    max = node.find("range/max")
    range = None
    if None not in [min, max]:
        range = float(min.text), float(max.text)
    if None not in [name, description]:
        return CoverageDimension(name, description, range)
    else:
        return None # should we bomb out more spectacularly here?

def coverage_dimension_xml(builder, dimension):
    builder.start("coverageDimension", dict())
    builder.start("name", dict())
    builder.data(dimension.name)
    builder.end("name")

    builder.start("description", dict())
    builder.data(dimension.description)
    builder.end("description")

    if dimension.range is not None:
        builder.start("range", dict())
        builder.start("min", dict())
        builder.data(str(dimension.range[0]))
        builder.end("min")
        builder.start("max", dict())
        builder.data(str(dimension.range[1]))
        builder.end("max")
        builder.end("range")

    builder.end("coverageDimension")

class Coverage(ResourceInfo):
  resource_type = "coverage"

  def __init__(self, catalog, node, store=None):
    self.catalog = catalog

    self.href = atom_link(node)

    self.store = store
    """The store containing this coverage"""

    self.title = None
    """
    A short label for this coverage, suitable for use in legends and
    layer lists
    """

    self.abstract = None
    """A natural-language description of the data in this coverage"""

    self.keywords = None
    """A list of keywords identifying topics related to this coverage"""

    self.native_bbox = None
    """
    A tuple of numbers identifying the extent of data in this coverage, in
    the projection used to actually store the data.  The format is (minx, maxx,
    miny, maxy).
    """

    self.latlon_bbox = None
    """
    A tuple of number identifying the extent of data in this coverage, in
    latitude/longitude.  The format is (minx, maxx, miny, maxy).
    """

    self.projection = None
    """
    A string identifying the coordinate system used for the data in this
    coverage.
    """

    self.enabled = True
    """
    Should GeoServer expose layers using this data?
    """

    self.extra_config = dict()
    """
    Extra key/value pair storage, for use by GeoServer extensions.
    """

    self.dimensions = []
    """A list of names of the channels in this coverage, as strings."""

    self.native_format = None
    """A string identifying the format used to store this coverage"""

    self.grid = None
    """Information about the resolution and range of the pixels in this raster"""

    self.supported_formats = []
    """
    A list of strings identifying formats that may be used to respond to
    queries against this coverage
    """

    self.default_interpolation_method = None
    """
    A string identifying the interpolation method that will be used if none is
    specified in a query against this coverage
    """

    self.interpolation_methods = []
    """
    A list of strings identifying interpolation methods that may be used to
    respond to queries against this coverage
    """

    self.metadata_links = []
    """
    A list of the metadata links for this featuretype, as (mimetype,
    metadatatype, url) tuples
    """

    self.request_srs = None
    """ ??? """

    self.response_srs = None
    """ ??? """

    self.update()

  def get_url(self, service_url):
    return self.href

  def update(self):
    ResourceInfo.update(self)
    doc = self.metadata
    title = doc.find("title")
    abstract = doc.find("description")
    projection = doc.find("srs")
    enabled = doc.find("enabled")
    native_format = doc.find("nativeFormat")
    default_interpolation_method = doc.find("defaultInterpolationMethod")
    request_srs = doc.find("requestSRS/string")
    response_srs = doc.find("responseSRS/string")

    if title is None:
        print self.href
        print tostring(doc)

    self.title = title.text if title is not None else None
    self.abstract = abstract.text if abstract is not None else None
    self.keywords = [(kw.text or None) for kw in doc.findall("keywords/string")]
    self.native_bbox = bbox(doc.find("nativeBoundingBox"))
    self.latlon_bbox = bbox(doc.find("latLonBoundingBox"))
    self.projection = projection.text if projection is not None else None
    self.enabled = enabled.text == "true" if enabled is not None else False
    self.extra_config = dict((entry.attrib['key'], entry.text) for entry in doc.findall("metadata/entry"))
    self.dimensions = [coverage_dimension(d) for d in doc.findall("dimensions/coverageDimension")]
    self.native_format = native_format.text if native_format is not None else None
    self.grid = None # TODO: i guess this merits a little class of its own
    self.supported_formats = [format.text for format in doc.findall("supportedFormats/string")]
    self.default_interpolation_method = default_interpolation_method.text if default_interpolation_method is not None else None
    self.interpolation_methods = [method.text for method in doc.findall("interpolationMethods/string")]
    self.request_srs = request_srs.text if request_srs is not None else None
    self.response_srs = response_srs.text if response_srs is not None else None
    self.metadata_links = [md_link(n) for n in self.metadata.findall("metadataLinks/metadataLink")]

  def encode(self, builder):
    builder.start("title", dict())
    builder.data(self.title)
    builder.end("title")

    if self.abstract is not None:
        builder.start("description", dict())
        builder.data(self.abstract)
        builder.end("description")

    builder.start("keywords", dict())
    for kw in self.keywords:
        builder.start("string", dict())
        builder.data(kw)
        builder.end("string")
    builder.end("keywords")

    if self.native_bbox is not None:
        builder.start("nativeBoundingBox", dict())
        bbox_xml(builder, self.native_bbox)
        builder.end("nativeBoundingBox")

    if self.latlon_bbox is not None:
        builder.start("latLonBoundingBox", dict())
        bbox_xml(builder, self.latlon_bbox)
        builder.end("latLonBoundingBox")

    if self.projection is not None:
        builder.start("srs", dict())
        builder.data(self.projection)
        builder.end("srs")

    builder.start("enabled", dict())
    if self.enabled:
        builder.data("true")
    else:
        builder.data("false")
    builder.end("enabled")

    builder.start("metadata", dict())
    for k, v in self.extra_config.iteritems():
        builder.start("entry", {'key': k})
        builder.data(v)
        builder.end("entry")
    builder.end("metadata")

    builder.start("dimensions", dict())
    for dim in self.dimensions:
        coverage_dimension_xml(builder, dim)
    builder.end("dimensions")

    builder.start("nativeFormat", dict())
    builder.data(self.native_format)
    builder.end("nativeFormat")

    builder.start("supportedFormats", dict())
    for format in self.supported_formats:
        builder.start("string", dict())
        builder.data(format)
        builder.end("string")
    builder.end("supportedFormats")

    # TODO: Grid should probably be its own object type
    # builder.start("grid", {'dimension': '2'})
    # builder.data(self.grid)
    # builder.end("grid")

    if self.default_interpolation_method is not None:
        builder.start("defaultInterpolationMethod", dict())
        builder.data(self.default_interpolation_method)
        builder.end("defaultInterpolationMethod")

    builder.start("interpolationMethods", dict())
    for method in self.interpolation_methods:
        builder.start("string", dict())
        builder.data(method)
        builder.end("string")
    builder.end("interpolationMethods")

    if self.request_srs is not None:
        builder.start("requestSRS", dict())
        builder.start("string", dict())
        builder.data(self.request_srs)
        builder.end("string")
        builder.end("requestSRS")

    if self.response_srs is not None:
        builder.start("responseSRS", dict())
        builder.start("string", dict())
        builder.data(self.response_srs)
        builder.end("string")
        builder.end("responseSRS")

    builder.start("metadataLinks", dict())
    for link in self.metadata_links:
        mimetype, mdtype, url = link
        builder.start("metadataLink", dict())
        builder.start("type", dict())
        builder.data(mimetype)
        builder.end("type")
        builder.start("metadataType", dict())
        builder.data(mdtype)
        builder.end("metadataType")
        builder.start("content", dict())
        builder.data(url)
        builder.end("content")
        builder.end("metadataLink")
    builder.end("metadataLinks")

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)
