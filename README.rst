gsconfig.py
===========

gsconfig.py is a python library for manipulating a GeoServer instance via the GeoServer RESTConfig API. 

TODOS
=====

* Move code over to github
* Unify code to use XML
* Add support for adding and removing data from GeoServer
* Maintain test coverage


Sample Layer Creation Code
==========================

    from geoserver.catalog import Catalog
    cat = Catalog("http://localhost:8080/geoserver/")
    topp = self.cat.get_workspace("topp")
    shapefile_plus_boxcars = shapefile_and_friends("states")
    # shapefile_and_friends should look on the filesystem to find a shapefile
    # and related files based on the base path passed in
    #
    # shapefile_plus_boxcars == {
    #    'shp': 'states.shp',
    #    'shx': 'states.shx',
    #    'prj': 'states.prj',
    #    'dbf': 'states.dbf'
    # }
    
    # 'data' is required
    # 'workspace' is optional (GeoServer's default workspace is used by default)
    # 'name' is required
    ft = self.cat.create_featuretype(name, workspace=topp, data=shapefile_plus_boxcars)
