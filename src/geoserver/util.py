from os.path import exists

known_exts = ['shp', 'shx', 'dbf', 'prj']

def shapefile_and_friends(base):
  def expand(ext):
    return '%s.%s' % (base, ext)

  return dict((ext, expand(ext)) for ext in known_exts if exists(expand(ext)))
