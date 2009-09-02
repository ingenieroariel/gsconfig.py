from catalog import Catalog

cat = Catalog("http://localhost:8080/geoserver/rest")

print cat.getWorkspaces()
topp = cat.getWorkspace("topp")
sf = cat.getWorkspace("sf")
print topp, sf

print cat.getStores()
print cat.getStore("states_shapefile", topp)
print cat.getStore("states_shapefile")
print cat.getStore("sfdem", sf)
print cat.getStore("sfdem")


