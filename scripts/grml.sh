#!/bin/bash

option() {
    if [[ ${1,,} == @(true|on) ]]; then
        echo "$2"
    else
        echo "$3"
    fi
}

skipBinaries() {
    if [[ "$(option ${skipBinaries} 'true')" == "true" ]]; then
        echo "Skipping download of the binaries"
        exit 0
    fi
}