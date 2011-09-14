#!/usr/bin/env python

from geoserver.catalog import Catalog

cat = Catalog("http://localhost:8080/geoserver/rest", "admin", "geoserver")


ws = cat.get_workspace("sf")
    resources = cat.get_resources(workspace=ws)
    if len(resources) != 0:
        assert all(r.projection == "EPSG:27613" for r in resources), ws.name
