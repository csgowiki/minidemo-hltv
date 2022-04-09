#!bin/sh

# args num need == 1
if [ $# -ne 1 ]; then
    echo "need 1 args for demopath"
    exit 1
fi

cd minidemo-encoder/

go run cmd/main.go -file ../$1
