executable = /bin/bash
universe = vanilla
getenv = true
output = D2.out
error = D2.error
log = D2.log
arguments = "python3 centroid.py corpora.json 10 20 brown"
transfer_executable = false
request_memory = 1024*2
queue
