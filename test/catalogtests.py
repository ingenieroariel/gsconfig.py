import unittest
from geoserver.catalog import Catalog

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
    states = self.cat.get_resource("states")

    fields = [
        states.title,
        states.abstract,
        states.native_bbox,
        states.latlon_bbox,
        states.projection,
        states.projection_policy
    ]

    self.assertFalse(None in fields, str(fields))
    self.assertFalse(len(states.keywords) == 0)
    self.assertFalse(len(states.attributes) == 0)
    self.assertTrue(states.enabled)

    self.assertEqual("sfdem", self.cat.get_resource("sfdem", sfdem).name)
    self.assertEqual("sfdem", self.cat.get_resource("sfdem", workspace=sf).name)
    self.assertEqual("sfdem", self.cat.get_resource("sfdem").name)


  def testLayers(self):
    expected = set(["Arc_Sample", "Pk50095", "Img_Sample", "mosaic", "sfdem",
      "bugsites", "restricted", "streams", "archsites", "roads",
      "tasmania_roads", "tasmania_water_bodies", "tasmania_state_boundaries",
      "tasmania_cities", "states", "poly_landmarks", "tiger_roads", "poi",
      "giant_polygon"
    ])

    actual = set(l.name for l in self.cat.get_layers())
    missing = expected - actual
    extras = actual - expected
    message = "Actual layer list did not match expected! (Extras: %s) (Missing: %s)" % (extras, missing)
    self.assert_(len(expected ^ actual) == 0, message)

    self.assert_("states", self.cat.get_layer("states").name)


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


  def testLayerSave(self):
    # test saving round trip
    lyr = self.cat.get_layer("states")
    old_attribution = lyr.attribution
    new_attribution = "Not the original attribution"

    # change attribution on server
    lyr.attribution = new_attribution
    self.cat.save(lyr)
    lyr = self.cat.get_layer("states")
    self.assertEqual(new_attribution, lyr.attribution)

    # Restore attribution
    lyr.attribution = old_attribution
    self.cat.save(lyr)
    self.assertEqual(old_attribution, lyr.attribution)


if __name__ == "__main__":
  unittest.main()
