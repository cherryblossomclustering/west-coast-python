executable = /bin/bash/python3
universe = vanilla
getenv = true
output = D3.out
error = D3.error
log = D3.log
arguments = "centroid.py corpora.json --size 100 --topN 10 --corpus reuters --centWeight 5 --posWeight 1 --first 1 --red 100 --topW 1"
transfer_executable = false
request_memory = 1024*2
queue
