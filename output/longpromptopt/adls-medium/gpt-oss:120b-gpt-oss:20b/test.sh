#!/bin/bash

# For each directory, print the directory name and display the accuracy.png image
for dir in */; do
		echo "Directory: $dir"
		kitty +icat "$dir/accuracy.png"
		echo ""
done
