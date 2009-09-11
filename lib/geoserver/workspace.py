class Workspace: 
  def __init__(self, name, href):
    self.name = name
    self.href = href

  def __repr__(self):
    return "%s @ %s" % (self.name, self.href)

