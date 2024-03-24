#!/bin/bash

option() {
    local lower_option=$(echo "$1" | tr '[:upper:]' '[:lower:]')  # Convert to lowercase using tr
    if [[ "$lower_option" == "true" ]] || [[ "$lower_option" == "on" ]]; then
        echo "$2"
    else
        echo "$3"
    fi
}
