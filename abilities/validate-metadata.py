#!/usr/bin/env python3
import json
from jsonschema import validate
import sys
import os.path

if len(sys.argv) != 2:
    print("Usage: validate-metadata.py <ability>")
    sys.exit(1)

ability = sys.argv[1]
metadata_file = os.path.join(ability, "metadata.json")

# Load the JSON Schema
with open("schema-metadata.json", "r") as file:
    schema = json.load(file)

# Load the metadata.json file to validate
with open(metadata_file, "r") as file:
    metadata = json.load(file)

# Validate the metadata against the schema
validate(instance=metadata, schema=schema)
