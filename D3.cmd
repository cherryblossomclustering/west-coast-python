executable = centroid.py
universe = vanilla
getenv = true
output = D2.out
error = D2.error
log = D2.log
arguments = corpora.json --size 100 --topN 10 --corpus reuters --centWeight 5 --posWeight 1 --first 1 --red 100 --topW 1
transfer_executable = false
request_memory = 1024*2
queue
