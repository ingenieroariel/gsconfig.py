from geoserver.support import ResourceInfo, atom_link, atom_link_xml, bbox, bbox_xml, FORCE_NATIVE, FORCE_DECLARED, REPROJECT
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

class FeatureType(ResourceInfo):
  resource_type = "featureType"

  def __init__(self, catalog, node, store=None):
    self.catalog = catalog
    self.href = atom_link(node)

    self.store = store
    """The store containing this featuretype"""

    self.title = None
    """
    A short label for this featuretype, suitable for use in legends and
    layer lists
    """

    self.abstract = None
    """A natural-language description of the data in this featuretype"""

    self.keywords = None
    """A list of keywords identifying topics related to this featuretype"""

    self.native_bbox = None
    """
    A tuple of numbers identifying the extent of data in this featuretype, in
    the projection used to actually store the data.  The format is (minx, maxx,
    miny, maxy).
    """

    self.latlon_bbox = None
    """
    A tuple of number identifying the extent of data in this featuretype, in
    latitude/longitude.  The format is (minx, maxx, miny, maxy).
    """

    self.projection = None
    """
    A string identifying the coordinate system used for the data in this
    featuretype.
    """

    self.projection_policy = None
    """
    Identifies the way that GeoServer will interpret the projection setting for
    this featuretype.  Must be one of FORCE_DECLARED, FORCE_NATIVE, or
    REPROJECT (provided in the geoserver.catalog module.
    """

    self.enabled = True
    """
    Should GeoServer expose layers using this data?
    """

    self.extra_config = dict()
    """
    Extra key/value pair storage, for use by GeoServer extensions.
    """

    self.attributes = []
    """A list of names of the fields in this featuretype, as strings."""

    self.metadata_links = []
    """
    A list of the metadata links for this featuretype, as (mimetype,
    metadatatype, url) tuples
    """

    self.update()

  def update(self):
    ResourceInfo.update(self)
    title = self.metadata.find("title")
    abstract = self.metadata.find("abstract")
    keywords = self.metadata.findall("keywords/string")
    projection = self.metadata.find("srs")
    projection_policy = self.metadata.find("projectionPolicy")
    enabled = self.metadata.find("enabled")
    md_links = self.metadata.findall("metadataLinks/metadataLink")

    self.title = title.text if title is not None else None
    self.abstract = abstract.text if abstract is not None else None
    self.projection = projection.text if projection is not None else None

    if projection_policy is not None and projection_policy.text in [REPROJECT, FORCE_NATIVE, FORCE_DECLARED]:
        self.projection_policy = projection_policy.text
    else:
        self.projection_policy = None

    if enabled is not None and enabled.text == "true":
        self.enabled = True
    else: 
        self.enabled = False

    self.keywords = [word.text for word in keywords]
    self.latlon_bbox = bbox(self.metadata.find("latLonBoundingBox"))
    self.native_bbox = bbox(self.metadata.find("nativeBoundingBox"))
    self.extra_config = dict((entry.attrib["key"], entry.text) for entry in self.metadata.findall("metadata/entry"))
    self.attributes = [att.text for att in self.metadata.findall("attributes/attribute/name")]
    self.metadata_links = [md_link(n) for n in self.metadata.findall("metadataLinks/metadataLink")]

  def encode(self, builder):
    builder.start("name", dict())
    builder.data(self.name)
    builder.end("name")

    builder.start("title", dict())
    builder.data(self.title)
    builder.end("title")

    builder.start("abstract", dict())
    builder.data(self.abstract)
    builder.end("abstract")

    builder.start("keywords", dict())
    for kw in self.keywords:
        builder.start("string", dict())
        builder.data(kw)
        builder.end("string")
    builder.end("keywords")

    builder.start("nativeBoundingBox", dict())
    bbox_xml(builder, self.native_bbox)
    builder.end("nativeBoundingBox")

    builder.start("latLonBoundingBox", dict())
    bbox_xml(builder, self.latlon_bbox)
    builder.end("latLonBoundingBox")

    # builder.start("nativeCRS", {'class': 'projected'})
    # builder.data(self.native_crs)
    # builder.end("nativeCRS")

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
        builder.start("entry", {"key": k})
        builder.data(v)
        builder.end("entry")
    builder.end("metadata")

    builder.start("store", {"class": "coverageStore"})
    builder.start("name", dict())
    builder.data(self.store.name)
    builder.end("name")
    atom_link_xml(builder, self.store.href)
    builder.end("store")

    if self.projection_policy is not None:
        builder.start("projectionPolicy", dict())
        builder.data(self.projection_policy)
        builder.end("projectionPolicy")

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

    # builder.start("attributes")
    # for att in self.attributes:
    #     builder.start("attribute", dict())
    #     builder.start("name", dict())
    #     builder.data(att)
    #     builder.end("name")
    #     builder.end("attribute")
    # builder.end("attributes")
    

    """
    Removes a featureType from the GeoServer Catalog.  This is a dumb
    method, ie it does not remove any dependent resources in GeoServer. 
    To remove all dependent resource call delete_all
    """
    self.catalog.delete(self)


  def delete(self):
    """
    Removes a feature from the GeoServer Catalog. Must remove 
    """
    pass 



  def delete_all(self): 
    """
    Remove a featureType and all of the dependent resources in GeoServer. 
    """
    pass 


  def get_url(self, service_url):
    return self.href

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)

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
    self.keywords = [kw.text for kw in doc.findall("keywords/string")]
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

    builder.start("description", dict())
    builder.data(self.abstract)
    builder.end("description")

    builder.start("keywords", dict())
    for kw in self.keywords:
        builder.start("string", dict())
        builder.data(kw)
        builder.end("string")
    builder.end("keywords")

    builder.start("nativeBoundingBox", dict())
    bbox_xml(builder, self.native_bbox)
    builder.end("nativeBoundingBox")

    builder.start("latLonBoundingBox", dict())
    bbox_xml(builder, self.latlon_bbox)
    builder.end("latLonBoundingBox")

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

    builder.start("defaultInterpolationMethod", dict())
    builder.data(self.default_interpolation_method)
    builder.end("defaultInterpolationMethod")

    builder.start("interpolationMethods", dict())
    for method in self.interpolation_methods:
        builder.start("string", dict())
        builder.data(method)
        builder.end("string")
    builder.end("interpolationMethods")

    builder.start("requestSRS", dict())
    builder.start("string", dict())
    builder.data(self.request_srs)
    builder.end("string")
    builder.end("requestSRS")

    builder.start("responseSRS", dict())
    builder.start("string", dict())
    builder.data(self.response_srs)
    builder.end("string")
    builder.end("responseSRS")

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)
