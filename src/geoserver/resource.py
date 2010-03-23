from geoserver.support import ResourceInfo, atom_link, atom_link_xml, bbox, bbox_xml, FORCE_NATIVE, FORCE_DECLARED, REPROJECT

class FeatureType(ResourceInfo):
  resource_type = "featureType"

  def __init__(self, node, store=None):
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

    self.update()

  def update(self):
    ResourceInfo.update(self)
    title = self.metadata.find("title")
    abstract = self.metadata.find("abstract")
    keywords = self.metadata.findall("keywords/string")
    projection = self.metadata.find("srs")
    projection_policy = self.metadata.find("projectionPolicy")
    enabled = self.metadata.find("enabled")

    if title is not None:
        self.title = title.text
    else:
        self.title = None

    if abstract is not None:
        self.abstract = abstract.text
    else:
        self.abstract = None

    if projection is not None:
        self.projection = projection.text
    else:
        self.projection = None

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

    builder.start("projectionPolicy", dict())
    builder.data(self.projection_policy)
    builder.end("projectionPolicy")

    # builder.start("attributes")
    # for att in self.attributes:
    #     builder.start("attribute", dict())
    #     builder.start("name", dict())
    #     builder.data(att)
    #     builder.end("name")
    #     builder.end("attribute")
    # builder.end("attributes")
    
  def get_url(self, service_url):
    return self.href

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)

class Coverage(ResourceInfo):
  resource_type = "coverage"

  def __init__(self, node, store=None):
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
    request_srs = doc.find("requestSRS")
    response_srs = doc.find("responseSRS")

    self.title = title.text if title is not None else None
    self.abstract = abstract.text if abstract is not None else None
    self.keywords = [kw.text for kw in doc.findall("keywords/string")]
    self.native_bbox = bbox(doc.find("nativeBoundingBox"))
    self.latlon_bbox = bbox(doc.find("latLonBoundingBox"))
    self.projection = projection.text if projection is not None else None
    self.enabled = enabled.text == True if enabled is not None else False
    self.extra_config = dict((entry.attrib['key'], entry.text) for entry in doc.findall("metadata/entry"))
    self.dimensions = [d.text for d in doc.findall("dimensions/coverageDimension/name")]
    self.native_format = native_format.text if native_format is not None else None
    self.grid = None # TODO: i guess this merits a little class of its own
    self.supported_formats = [format.text for format in doc.findall("supportedFormats/string")]
    self.default_interpolation_method = default_interpolation_method.text if default_interpolation_method is not None else None
    self.interpolation_methods = [method.text for method in doc.findall("interpolationMethods/string")]
    self.request_srs = request_srs.text if request_srs is not None else None
    self.response_srs = response_srs.text if response_srs is not None else None

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
        builder.start("coverageDimension", dict())
        builder.start("name", dict())
        builder.data(dim)
        builder.end("name")
        # Add more details about dimensions
        builder.end("coverageDimension")
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

    if self.request_srs is not None:
        builder.start("requestSRS", dict())
        builder.data(self.request_srs)
        builder.end("requestSRS")

    if self.response_srs is not None:
        builder.start("responseSRS", dict())
        builder.data(self.response_srs)
        builder.end("responseSRS")

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)
