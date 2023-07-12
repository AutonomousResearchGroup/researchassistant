#!/bin/bash

# Define the script to be run for each line
script_to_run() {
    url="$1"
    filename=$(echo "$url" | sed 's/https:\/\///;s/\//_/g').csv
    python3 researchassistant/extract/extract_test.py $url $filename
}

export -f script_to_run

# Call xargs to run the script for each line, 5 at a time
cat urls.txt | xargs -I {} -P 5 bash -c 'script_to_run "$@"' _ {}