from xml.etree.ElementTree import TreeBuilder, XML, tostring
from tempfile import mkstemp
from urllib2 import urlopen, HTTPPasswordMgr, HTTPBasicAuthHandler, install_opener, build_opener
from zipfile import ZipFile

class ResourceInfo(object):
  resource_type = 'abstractResourceType'

  def update(self):
    self.metadata = get_xml(self.href)
    self.name = self.metadata.find('name').text

  def serialize(self):
    builder = TreeBuilder()
    builder.start(self.resource_type, dict())
    self.encode(builder)
    builder.end(self.resource_type)
    return tostring(builder.close())

  def encode(self, builder):
    """
    Add appropriate XML nodes to this object.  The builder will be passed in
    ready to go, with the appropriate top-level node already added.
    """
    pass

def prepare_shapefile_bundle(name, data):
  """Create a ZIP archive with a shapefile and accompanying metadata for upload\
 to GeoServer. GeoServer expects all files in the top directory level of the\
 ZIP archive, with the basename the same as that of the layer to be created.\
 The first argument to this function provides that expected layer name, and the\
 second should be a dict mapping Shapefile file extensions to filesystem paths,\
 or to file-like objects.  The function geoserver.util.shapefile_and_friends\
 can generate such a dict for actual files.  This actually creates a temporary\
 file, which client code should delete after use."""

  handle, f = mkstemp() # we don't use the file handle directly. should we?
  zip = ZipFile(f, 'w')
  for ext, stream in data.iteritems():
    fname = "%s.%s" % (name, ext)
    if (isinstance(stream, basestring)):
      zip.write(stream, fname)
    else:
      zip.writestr(fname, stream.read())
  zip.close()
  return f

def get_xml(url):
  password_manager = HTTPPasswordMgr()
  password_manager.add_password(
    realm='GeoServer Realm',
    uri='http://localhost:8080/geoserver/',
    user='admin',
    passwd='geoserver'
  )

  handler = HTTPBasicAuthHandler(password_manager)
  install_opener(build_opener(handler))
  
  response = urlopen(url).read()
  try:
    return XML(response)
  except:
    print "%s => \n%s" % (url, response)

def atom_link(node):
  return node.find("{http://www.w3.org/2005/Atom}link").get("href")
