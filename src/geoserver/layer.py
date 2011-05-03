from geoserver.support import ResourceInfo, atom_link, atom_link_xml
from geoserver.style import Style
from geoserver.resource import FeatureType, Coverage 

class Layer(ResourceInfo): 
  resource_type = "layer"

  def __init__(self,catalog,node):
    self.href = atom_link(node)
    self.name = None
    self.catalog = catalog
    """The name of this layer"""

    self.attribution = None
    """Natural-language identification of the provider of the data for this layer"""

    self.attribution_link = None
    """
    A URL to follow for more information about the provider of this layer's
    data
    """

    self.attribution_logo = None
    """
    The URL to a logo image or other associated graphic for the provider of
    this layer's data.
    """

    self.attribution_logo_size = None
    """
    The size (width, height) of the logo image for the attribution, if it exists.
    """

    self.attribution_logo_type = None
    """
    The MIME type of the logo image for the attribution, if it exists.
    """

    self.enabled = True
    """Should GeoServer expose this layer?"""

    self.default_style = None
    """The default style to use when rendering this layer."""

    self.styles = []
    """
    The styles (other than the default) which should be advertised as
    applicable to this layer
    """

    self.update()

  def update(self):
    ResourceInfo.update(self)
    name = self.metadata.find("name")
    attribution = self.metadata.find("attribution")
    enabled = self.metadata.find("enabled")
    default_style = self.metadata.find("defaultStyle")
    styles = self.metadata.findall("styles/style")

    self.name = name.text if name is not None else name
    
    if attribution is not None:
      title = attribution.find("title")
      href = attribution.find("href")
      logo_url = attribution.find("logoURL")
      logo_width = attribution.find("logoWidth")
      logo_height = attribution.find("logoHeight")
      logo_type = attribution.find("logoType")

      self.attribution = title.text if title is not None else None
      self.attribution_link = href.text if href is not None else None
      self.attribution_logo = logo_url.text if logo_url is not None else None
      self.attribution_type = logo_type.text if None not in [logo_url, logo_type] else None

      if None not in [logo_url, logo_width, logo_height]:
        self.attribution_size = (int(logo_width.text), int(logo_height.text))
      else:
        self.attribution_size = None

    else:
        self.attribution = None
        self.attribution_logo = None
        self.attribution_link = None
        self.attribution_size = None
        self.attribution_type = None

    if enabled is not None and enabled.text == "true":
        self.enabled = True
    else:
        self.enabled = False

    if default_style is not None:
        self.default_style = Style(self.catalog, default_style)
    else:
        self.default_style = None

    self.styles = [Style(self.catalog, s) for s in styles]

    resource = self.metadata.find("resource")
    if resource is not None and "class" in resource.attrib:
        if resource.attrib["class"] == "featureType":
            self.resource = FeatureType(self.catalog, resource)
        elif resource.attrib["class"] == "coverage":
            self.resource = Coverage(self.catalog, resource)

  def encode(self, builder):
      if self.name is not None:
          builder.start("name", dict())
          builder.data(self.name)
          builder.end("name")
      builder.start("attribution", dict())
      if self.attribution is not None:
          builder.start("title", dict())
          builder.data(self.attribution)
          builder.end("title")
      if self.attribution_link is not None:
          builder.start("href", dict())
          builder.data(self.attribution_link)
          builder.end("href")
      if self.attribution_logo is not None:
          builder.start("logoUrl", dict())
          builder.data(self.attribution_logo)
          builder.end("logoUrl")
      if self.attribution_logo_size is not None:
          builder.start("logoWidth", dict())
          builder.data(self.attribution_logo_size[0])
          builder.end("logoWidth")
          builder.start("logoHeight", dict())
          builder.data(self.attribution_logo_size[1])
          builder.end("logoHeight")
      if self.attribution_type is not None:
          builder.start("logoType", dict())
          builder.data(self.attribution_type)
          builder.end("logoType")
      builder.end("attribution")
      builder.start("enabled", dict())
      if self.enabled:
          builder.data("true")
      else:
          builder.data("false")
      builder.end('enabled')
      if self.default_style is not None:
          builder.start("defaultStyle", dict())
          builder.start("name", dict())
          builder.data(self.default_style.name)
          builder.end("name")
          atom_link_xml(builder, self.default_style.href)
          builder.end("defaultStyle")
      builder.start("styles", dict())
      for style in self.styles:
          builder.start("style", dict())
          builder.start("name", dict())
          builder.data(style.name)
          builder.end("name")
          atom_link_xml(builder, self.default_style.href)
          builder.end("style")
      builder.end("styles")

  def get_url(self, service_url):
      return self.href

  def __repr__(self):
    return "Layer[%s]" % self.name
