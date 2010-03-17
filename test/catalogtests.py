import unittest
from geoserver.catalog import Catalog
from geoserver.util import shapefile_and_friends

class CatalogTests(unittest.TestCase):
  def setUp(self):
    self.cat = Catalog("http://localhost:8080/geoserver/rest")

  def testWorkspaces(self):
    self.assertEqual(7, len(self.cat.get_workspaces()))
    self.assertEqual("nurc", self.cat.get_default_workspace().name)
    self.assertEqual("topp", self.cat.get_workspace("topp").name)

  def testStores(self):
    topp = self.cat.get_workspace("topp")
    sf = self.cat.get_workspace("sf")
    self.assertEqual(9, len(self.cat.get_stores()))
    self.assertEqual(2, len(self.cat.get_stores(topp)))
    self.assertEqual(2, len(self.cat.get_stores(sf)))
    self.assertEqual("states_shapefile", self.cat.get_store("states_shapefile", topp).name)
    self.assertEqual("states_shapefile", self.cat.get_store("states_shapefile").name)
    self.assertEqual("sfdem", self.cat.get_store("sfdem", sf).name)
    self.assertEqual("sfdem", self.cat.get_store("sfdem").name)
  
  def testResources(self):
    topp = self.cat.get_workspace("topp")
    sf = self.cat.get_workspace("sf")
    states = self.cat.get_store("states_shapefile", topp)
    sfdem = self.cat.get_store("sfdem", sf)
    self.assertEqual(19, len(self.cat.get_resources()))
    self.assertEqual(1, len(self.cat.get_resources(states)))
    self.assertEqual(5, len(self.cat.get_resources(workspace=topp)))
    self.assertEqual(1, len(self.cat.get_resources(sfdem)))
    self.assertEqual(6, len(self.cat.get_resources(workspace=sf)))

    self.assertEqual("states", self.cat.get_resource("states", states).name)
    self.assertEqual("states", self.cat.get_resource("states", workspace=topp).name)
    self.assertEqual("states", self.cat.get_resource("states").name)

    self.assertEqual("sfdem", self.cat.get_resource("sfdem", sfdem).name)
    self.assertEqual("sfdem", self.cat.get_resource("sfdem", workspace=sf).name)
    self.assertEqual("sfdem", self.cat.get_resource("sfdem").name)

  def testStyles(self):
    self.assertEqual(22, len(self.cat.get_styles()))
    self.assertEqual("population", self.cat.get_style("population").name)


class ModifyingTests(unittest.TestCase):
  def setUp(self):
    self.cat = Catalog("http://localhost:8080/geoserver/rest")

  def testFeatureTypeSave(self):
    # test saving round trip
    rs = self.cat.get_resource("bugsites")
    old_abstract = rs.abstract
    new_abstract = "Not the original abstract"

    # Change abstract on server
    rs.abstract = new_abstract
    self.cat.save(rs)
    rs = self.cat.get_resource("bugsites")
    self.assertEqual(new_abstract, rs.abstract)

    # Restore abstract
    rs.abstract = old_abstract
    self.cat.save(rs)
    rs = self.cat.get_resource("bugsites")
    self.assertEqual(old_abstract, rs.abstract)

  def testCoverageSave(self):
    # test saving round trip
    rs = self.cat.get_resource("Arc_Sample")
    old_abstract = rs.abstract
    new_abstract = "Not the original abstract"

    # # Change abstract on server
    rs.abstract = new_abstract
    self.cat.save(rs)
    rs = self.cat.get_resource("Arc_Sample")
    self.assertEqual(new_abstract, rs.abstract)

    # Restore abstract
    rs.abstract = old_abstract
    self.cat.save(rs)
    rs = self.cat.get_resource("Arc_Sample")
    self.assertEqual(old_abstract, rs.abstract)

  def testFeatureTypeCreate(self):
    shapefile_plus_boxcars = shapefile_and_friends("test/data/states")
    expected = {
      'shp': 'test/data/states.shp',
      'shx': 'test/data/states.shx',
      'dbf': 'test/data/states.dbf',
      'prj': 'test/data/states.prj'
    }

    self.assertEqual(len(expected), len(shapefile_plus_boxcars))
    for k, v in expected.iteritems():
      self.assertEqual(v, shapefile_plus_boxcars[k])

if __name__ == "__main__":
  unittest.main()
