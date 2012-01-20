from geoserver.support import ResourceInfo, atom_link, xml_property
import re

class Style(ResourceInfo):
    def __init__(self, catalog, name):
        super(Style, self).__init__()
        assert isinstance(name, basestring)

        self.catalog = catalog
        self.name = name
        self._sld_dom = None

    @property
    def href(self):
        return "%s/styles/%s.xml" % (self.catalog.service_url, self.name)

    def body_href(self):
        return "%s/styles/%s.sld" % (self.catalog.service_url, self.name)

    filename = xml_property("filename")

    def _get_sld_dom(self):
        if self._sld_dom is None:
            self._sld_dom = self.catalog.get_xml(self.body_href())
        return self._sld_dom

    @property
    def sld_title(self):
        user_style = self._get_sld_dom().find("{http://www.opengis.net/sld}NamedLayer/{http://www.opengis.net/sld}UserStyle")
        title_node = user_style.find("{http://www.opengis.net/sld}Title")
        return title_node.text if title_node is not None else None

    @property
    def sld_name(self):
        user_style = self._get_sld_dom().find("{http://www.opengis.net/sld}NamedLayer/{http://www.opengis.net/sld}UserStyle")
        name_node = user_style.find("{http://www.opengis.net/sld}Name")
        return name_node.text if name_node is not None else None

    @property
    def sld_body(self):
        response, content = self.catalog.http.request(self.body_href())
        return content

    def update_body(self, body):
        headers = { "Content-Type": "application/vnd.ogc.sld+xml" }
        response, content = self.catalog.http.request(
                self.body_href(), "PUT", body, headers)

# class Style(ResourceInfo):
#   def __init__(self,catalog, node):
#     self.catalog = catalog
#     self.name = node.find("name").text    
#     self.href = atom_link(node)
#     self.update()
# 
#   def update(self):
#     ResourceInfo.update(self)
#     self.name = self.metadata.find("name").text
#     self.filename = self.metadata.find("filename").text
#     # Get the raw sld
#     sld_url = self.href.replace(".xml", ".sld")
#     sld_xml = self.catalog.get_xml(sld_url)
#     # Obtain the user style node where title and name are located
#     user_style = sld_xml.find("{http://www.opengis.net/sld}NamedLayer/{http://www.opengis.net/sld}UserStyle")
#     # Extract name and title nodes from user_style
#     name_node = user_style.find("{http://www.opengis.net/sld}Name")
#     title_node = user_style.find("{http://www.opengis.net/sld}Title")
#     # Store the text value of sld name and title if present
#     self.sld_name = name_node.text if hasattr(name_node, 'text') else None
#     self.sld_title = title_node.text if hasattr(title_node, 'text') else None
# 
#   def body_href(self):
#       style_container = re.sub(r"/rest$", "/styles", self.catalog.service_url)
#       return "%s/%s" % (style_container, self.filename)
# 
#   def __repr__(self):
#     return "Style[%s]" % self.name
