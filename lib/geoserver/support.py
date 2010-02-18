import json
from urllib2 import urlopen, HTTPPasswordMgr, HTTPBasicAuthHandler, install_opener, build_opener

class ResourceInfo(object):
  resourceType = 'abstractResourceType'

  def update(self):
    self.response = getJSON(self.href)
    self.metadata = params = self.response[self.resourceType]
    self.name = params[u'name']

  def serialize(self):
    return json.dumps({self.resourceType : self.metadata})

  def get(self, key):
    return self.metadata.get(key)

  def set(self, key, value):
    self.metadata[key] = value

def getJSON(url):
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
    return json.loads(response)
  except:
    print response
    raise
