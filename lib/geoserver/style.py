from geoserver.support import ResourceInfo, atom_link

class Style(ResourceInfo):
  def __init__(self, node):
    self.name = node.find("name").text
    self.href = atom_link(node)
    self.update()

  def update(self):
    ResourceInfo.update(self)
    self.name = self.metadata.find("name").text
    self.filename = self.metadata.find("filename").text

  def __repr__(self):
    return "Style[%s]" % self.name
