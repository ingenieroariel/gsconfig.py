#!/usr/bin/env python

from geoserver.catalog import Catalog

cat = Catalog("http://localhost:8080/geoserver/rest", "admin", "geoserver")

ds = cat.create_datastore(name)
ds.connection_parameters.update(
    host="localhost",
    port="5432",
    database="gis",
    user="postgres",
    password="",
    dbtype="postgis")

cat.save(ds)
ds = cat.get_store(name)
components = \
  dict((ext, "myfile." + ext) for ext in ["shp", "prj", "shx", "dbf"])
cat.add_data_to_store(ds, "mylayer", components)
