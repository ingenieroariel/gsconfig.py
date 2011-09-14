#!/usr/bin/env python

from geoserver.catalog import Catalog

cat = Catalog("http://localhost:8080/geoserver/rest", "admin", "geoserver")

pg_stores = [s for s in cat.get_stores() 
    if s.connection_parameters and \
    s.connection_parameters.get("dbtype") == "postgis"]

res = []
for s in pg_stores:
    res.extend(r.name for r in cat.get_resources(store=s))
print res
