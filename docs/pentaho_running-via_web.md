# Running Jobs & Transformations From The Web UI

## Base URL syntax

[http://HOSTNAME/kettle/executeJob?job=/opt/pentaho-di/data-integration/job/JOBNAME.kjb](Job)

[http://HOSTNAME/kettle/executeTrans?trans=/opt/pentaho-bi/data-integration/transformation/TRANSFORMATIONNAME.ktr](transformation)

## QA5

### Run a transformation

http://HOSTNAME:8005/kettle/executeTrans/?sort_size=10000&trans=transformation/TRANSFORMATION.ktr

### Status

http://HOSTNAME:8005/kettle/status/
