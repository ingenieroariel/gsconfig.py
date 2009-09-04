from catalog import Catalog

cat = Catalog("http://localhost:8080/geoserver/rest")

print cat.getWorkspaces()
print cat.getDefaultWorkspace()
topp = cat.getWorkspace("topp")
sf = cat.getWorkspace("sf")
print topp, sf

print cat.getStores()
print cat.getStores(topp)
print cat.getStores(sf)
print cat.getStore("states_shapefile", topp)
print cat.getStore("sfdem", sf)
states_shapefile = cat.getStore("states_shapefile")
sfdem = cat.getStore("sfdem")
print states_shapefile, sfdem

print cat.getResources(states_shapefile)
print cat.getResources(workspace=topp)
print cat.getResources(sfdem)
print cat.getResources(workspace=sf)

print cat.getResource("states", states_shapefile)
print cat.getResource("states", workspace=topp)
print cat.getResource("states")
print cat.getResource("sfdem", sfdem)
print cat.getResource("sfdem", workspace=sf)
print cat.getResource("sfdem")

print cat.getStyles()
population = cat.getStyle("population")
print population

# print cat.getLayers()
# print cat.getLayers("population")
