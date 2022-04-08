#!/bin/sh

error_check() {
    if [ $? -ne 0 ]; then
        echo "** Error: $1 **"
        exit 1
    fi
}

# check `unrar` exists
unrar -v >/dev/null || error_check "Please install unrar first."

# check go version >= 1.11
go_version=$(go version | awk '{print $3}')
go_version=${go_version#*1.}
minor_version=${go_version%*.8}
if [ $minor_version -lt 11 ]; then
    error_check "Please install go version >= 1.11"
fi
