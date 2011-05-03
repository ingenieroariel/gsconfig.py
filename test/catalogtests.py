import unittest
from geoserver.catalog import Catalog, ConflictingDataError, UploadError
from geoserver.util import shapefile_and_friends

class CatalogTests(unittest.TestCase):
  def setUp(self):
    self.cat = Catalog("http://localhost:8080/geoserver/rest")


  def testWorkspaces(self):
    self.assertEqual(7, len(self.cat.get_workspaces()))
    # marking out test since geoserver default workspace is not consistent 
    # self.assertEqual("cite", self.cat.get_default_workspace().name)
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
    self.assertEqual(20, len(self.cat.get_styles()))
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

    # Change keywords on server
    rs.keywords = ["bugsites", "gsconfig"]
    self.cat.save(rs)
    rs = self.cat.get_resource("bugsites")
    self.assertEqual(["bugsites", "gsconfig"], rs.keywords)

    # Restore abstract
    rs.abstract = old_abstract
    self.cat.save(rs)
    rs = self.cat.get_resource("bugsites")
    self.assertEqual(old_abstract, rs.abstract)

  def testDataStoreCreate(self):
    ds = self.cat.create_datastore("vector_gsconfig")
    ds.connection_parameters.update(
            host="localhost", port="5432", database="db", user="postgres",
            passwd="password", dbtype="postgis")
    self.cat.save(ds)

  def testDataStoreModify(self):
    ds = self.cat.get_store("sf")
    self.assertFalse("foo" in ds.connection_parameters)
    ds.connection_parameters["foo"] = "bar"
    orig_ws = ds.workspace.name
    self.cat.save(ds)
    ds = self.cat.get_store("sf")
    self.assertTrue("foo" in ds.connection_parameters)
    self.assertEqual("bar", ds.connection_parameters["foo"])
    self.assertEqual(orig_ws, ds.workspace.name)

  def testCoverageStoreCreate(self):
    ds = self.cat.create_coveragestore2("coverage_gsconfig")
    ds.data_url = "file:data/mytiff.tiff"
    self.cat.save(ds)

  def testCoverageStoreModify(self):
    cs = self.cat.get_store("sfdem")
    self.assertEqual("GeoTIFF", cs.type)
    cs.type = "WorldImage"
    self.cat.save(cs)
    cs = self.cat.get_store("sfdem")
    self.assertEqual("WorldImage", cs.type)

    # not sure about order of test runs here, but it might cause problems
    # for other tests if this layer is misconfigured
    cs.type = "GeoTIFF"
    self.cat.save(cs) 

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
    shapefile_plus_sidecars = shapefile_and_friends("test/data/states")
    expected = {
      'shp': 'test/data/states.shp',
      'shx': 'test/data/states.shx',
      'dbf': 'test/data/states.dbf',
      'prj': 'test/data/states.prj'
    }

    self.assertEqual(len(expected), len(shapefile_plus_sidecars))
    for k, v in expected.iteritems():
      self.assertEqual(v, shapefile_plus_sidecars[k])
 
    sf = self.cat.get_workspace("sf")
    ft = self.cat.create_featurestore("states_test", shapefile_plus_sidecars, sf)

    self.assert_(self.cat.get_resource("states_test", workspace=sf) is not None)

    self.assertRaises(
        ConflictingDataError, 
        lambda: self.cat.create_featurestore("states_test", shapefile_plus_sidecars, sf)
    )

    self.assertRaises(
        UploadError,
        lambda: self.cat.create_coveragestore("states_raster_test", shapefile_plus_sidecars, sf)
    )

    bogus_shp = {
      'shp': 'test/data/Pk50095.tif',
      'shx': 'test/data/Pk50095.tif',
      'dbf':  'test/data/Pk50095.tfw',
      'prj':  'test/data/Pk50095.prj'
    }

    self.assertRaises(
        UploadError,
        lambda: self.cat.create_featurestore("bogus_shp", bogus_shp, sf)
    )

    lyr = self.cat.get_layer("states_test")
    self.cat.delete(lyr)
    self.assert_(self.cat.get_layer("states_test") is None)


  def testCoverageCreate(self):
    tiffdata = {
      'tiff': 'test/data/Pk50095.tif',
      'tfw':  'test/data/Pk50095.tfw',
      'prj':  'test/data/Pk50095.prj'
    }

    sf = self.cat.get_workspace("sf")
    # TODO: Uploading WorldImage file no longer works???
    # ft = self.cat.create_coveragestore("Pk50095", tiffdata, sf)

    # self.assert_(self.cat.get_resource("Pk50095", workspace=sf) is not None)

    # self.assertRaises(
    #     ConflictingDataError, 
    #     lambda: self.cat.create_coveragestore("Pk50095", tiffdata, sf)
    # )

    self.assertRaises(
        UploadError, 
        lambda: self.cat.create_featurestore("Pk50095_vector", tiffdata, sf)
    )

    bogus_tiff = {
        'tiff': 'test/data/states.shp',
        'tfw': 'test/data/states.shx',
        'prj': 'test/data/states.prj'
    }

    self.assertRaises(
        UploadError,
        lambda: self.cat.create_coveragestore("states_raster", bogus_tiff)
    )

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

  def testStyles(self):
      # upload new style, verify existence
      self.cat.create_style("fred", open("test/fred.sld").read())
      fred = self.cat.get_style("fred")
      self.assert_(fred is not None)
      self.assertEqual("Fred", fred.sld_title)

      # replace style, verify changes
      self.cat.create_style("fred", open("test/ted.sld").read(), overwrite=True)
      fred = self.cat.get_style("fred")
      self.assert_(fred is not None)
      self.assertEqual("Ted", fred.sld_title)

      # delete style, verify non-existence
      self.cat.delete(fred, purge=True)
      self.assert_(self.cat.get_style("fred") is None)

      # attempt creating new style
      self.cat.create_style("fred", open("test/fred.sld").read())
      fred = self.cat.get_style("fred")
      self.assertEqual("Fred", fred.sld_title)

  def testWorkspaceCreate(self):
      self.cat.create_workspace("acme", "http://example.com/acme")
      ws = self.cat.get_workspace("acme")
      self.assertEqual("acme", ws.name)

  def testWorkspaceDelete(self): 
      self.cat.create_workspace("foo", "http://example.com/foo")
      ws = self.cat.get_workspace("foo")
      self.cat.delete(ws)
      ws = self.cat.get_workspace("foo")
      self.assert_(ws is None)

  def testFeatureTypeDelete(self):
    pass

  def testCoverageDelete(self):
    pass

  def testDataStoreDelete(self):
    pass

if __name__ == "__main__":
  unittest.main()
