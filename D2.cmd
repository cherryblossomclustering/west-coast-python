executable = /bin/bash
universe = vanilla
getenv = true
output = D2.out
error = D2.error
log = D2.log
arguments = "./ROUGE-1.5.5.pl -e /dropbox/16-17/573/code/ROUGE/data -a -n 4 -x -m -c 95 -r 1000 -f A -p 0.5 -t 0 -l 100 -s -d rouge_run.xml"
transfer_executable = false
request_memory = 1024*2
queue
