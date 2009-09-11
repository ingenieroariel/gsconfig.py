import json
from urllib2 import urlopen, HTTPError

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
  response = urlopen(url).read()
  try:
    return json.loads(response)
  except:
    print response
    raise


