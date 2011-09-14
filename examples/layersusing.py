#!/usr/bin/env python

from geoserver.catalog import Catalog

style_to_check = "point"

cat = Catalog("http://localhost:8080/geoserver/rest", "admin", "geoserver")

def has_the_style(l):
    return (l.default_style.name == style_to_check or
      any(s.name == style_to_check for s in l.styles))

print [l.name for l in cat.get_layers() if has_the_style(l)]
