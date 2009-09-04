import unittest
from catalog import Catalog

class CatalogTests(unittest.TestCase):
  def setUp(self):
    self.cat = Catalog("http://localhost:8080/geoserver/rest")

  def testWorkspaces(self):
    self.assertEqual(7, len(self.cat.getWorkspaces()))
    self.assertEqual("tiger", self.cat.getDefaultWorkspace().name)
    self.assertEqual("topp", self.cat.getWorkspace("topp").name)

  def testStores(self):
    topp = self.cat.getWorkspace("topp")
    sf = self.cat.getWorkspace("sf")
    self.assertEqual(9, len(self.cat.getStores()))
    self.assertEqual(2, len(self.cat.getStores(topp)))
    self.assertEqual(2, len(self.cat.getStores(sf)))
    self.assertEqual("states_shapefile", self.cat.getStore("states_shapefile", topp).name)
    self.assertEqual("states_shapefile", self.cat.getStore("states_shapefile").name)
    self.assertEqual("sfdem", self.cat.getStore("sfdem", sf).name)
    self.assertEqual("sfdem", self.cat.getStore("sfdem").name)
  
  def testResources(self):
    topp = self.cat.getWorkspace("topp")
    sf = self.cat.getWorkspace("sf")
    states = self.cat.getStore("states_shapefile", topp)
    sfdem = self.cat.getStore("sfdem", sf)
    self.assertEqual(19, len(self.cat.getResources()))
    self.assertEqual(1, len(self.cat.getResources(states)))
    self.assertEqual(5, len(self.cat.getResources(workspace=topp)))
    self.assertEqual(1, len(self.cat.getResources(sfdem)))
    self.assertEqual(6, len(self.cat.getResources(workspace=sf)))

    self.assertEqual("states", self.cat.getResource("states", states).name)
    self.assertEqual("states", self.cat.getResource("states", workspace=topp).name)
    self.assertEqual("states", self.cat.getResource("states").name)

    self.assertEqual("sfdem", self.cat.getResource("sfdem", sfdem).name)
    self.assertEqual("sfdem", self.cat.getResource("sfdem", workspace=sf).name)
    self.assertEqual("sfdem", self.cat.getResource("sfdem").name)

  def testStyles(self):
    self.assertEqual(23, len(self.cat.getStyles()))
    self.assertEqual("population", self.cat.getStyle("population").name)

if __name__ == "__main__":
  unittest.main()
