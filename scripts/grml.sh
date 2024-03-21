#!/bin/bash

option() {
    local lower_option="${1,,}"  # Convert to lowercase
    if [[ "$lower_option" == "true" ]] || [[ "$lower_option" == "on" ]]; then
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