from geoserver.support import ResourceInfo, atom_link, bbox, FORCE_NATIVE, FORCE_DECLARED, REPROJECT

class FeatureType(ResourceInfo):
  resource_type = "featureType"

  def __init__(self,catalog,node, store=None):
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
    self.native_bbox = (self.metadata.find("nativeBoundingBox"))
    self.extra_config = dict((entry.attrib["key"], entry.text) for entry in self.metadata.findall("metadata/entry"))
    self.attributes = [att.text for att in self.metadata.findall("attributes/attribute/name")]

  def encode(self, builder):
    builder.start("abstract", dict())
    builder.data(self.abstract)
    builder.end("abstract")

  def delete(self):
    """
    Removes a featureType from the GeoServer Catalog. Must remove 
    Removing a featureType from GeoServer takes three steps: 
        1. Remove the featureType's layer
        2. If the featureType is in a layer group remove it. 
        3. Remove the 
    """
    # deletes layer 
    layer_url = "%s/layers/%s" % (self.catalog.service_url,self.name)
    delete(layer_url)
    # deletes featureType
    feature_url = self.href.replace(".xml","")
    delete(feature_url)

  def get_url(self, service_url):
    return self.href

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)

class Coverage(ResourceInfo):
  resource_type = "coverage"

  def __init__(self,catalog,node, store=None):
    self.catalog = catalog
    self.href = atom_link(node)
    self.store = store
    self.update()

  def get_url(self, service_url):
    return self.href

  def update(self):
    ResourceInfo.update(self)
    self.abstract = self.metadata.find("description")
    self.abstract = self.abstract.text if self.abstract is not None else None

  def encode(self, builder):
    builder.start("description", dict())
    builder.data(self.abstract)
    builder.end("description")

  def __repr__(self):
    return "%s :: %s" % (self.store, self.name)
