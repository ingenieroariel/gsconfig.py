#!/usr/bin/env python

import httplib2, subprocess, tempfile

http = httplib2.Http()
http.add_credentials("admin", "geoserver")
url = "http://localhost:8080/geoserver/rest/workspaces/topp/datastores/states_shapefile/featuretypes/states.xml"

headers, body = http.request(url)

__, temp = tempfile.mkstemp()
with open(temp, 'w') as f:
    f.write(body)

subprocess.call(['vim', temp])

headers = { "content-type": "application/xml" }
http.request(url,
    method="PUT", headers=headers, body=open(temp).read())
