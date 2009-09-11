from geoserver.support import getJSON

class Style:
  def __init__(self, params):
    self.name = params["name"]
    self.href = params["href"]
    self.update()

  def update(self):
    response = getJSON(self.href)
    self.name = response["style"]["name"]
    self.filename = response["style"]["filename"]

  def __repr__(self):
    return "Style[%s]" % self.name


