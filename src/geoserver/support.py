from xml.etree.ElementTree import TreeBuilder, XML, tostring
from urllib2 import urlopen, HTTPPasswordMgr, HTTPBasicAuthHandler, install_opener, build_opener
import httplib2

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


def get(url,username=None,password=None): 

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
      return response
  except:
      print "%s => \n%s" % (url, response)


def get_xml(url):
  """
  XXX remove hard coded username and password 
  """
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

def delete(url):
  """
  delete method
  XXX remove httplib2 
  """
  h = httplib2.Http(".cache")
  h.add_credentials('admin', 'geoserver')
  try:
    h.request(url,"DELETE")
  except:
    print "something went wrong"

def atom_link(node):
    return node.find("{http://www.w3.org/2005/Atom}link").get("href")
