import json
import os
import jsonschema
from jsonschema import Draft202012Validator

# Load schema for zone validation
def load_schema(schema_file):
    schema_path = os.path.abspath(schema_file)
    with open(schema_path, "r") as file:
        return json.load(file)

# Load all record schemas and replace $refs with the actual schema
def resolve_references(schema, base_dir):
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref_path = schema["$ref"]
            ref_path = ref_path.replace("./", "")  # Remove './' from the reference path
            ref_full_path = os.path.join(base_dir, ref_path)
            with open(ref_full_path, "r") as ref_file:
                ref_schema = json.load(ref_file)
            return resolve_references(ref_schema, base_dir)  # Recursively resolve references
        else:
            return {k: resolve_references(v, base_dir) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [resolve_references(item, base_dir) for item in schema]
    else:
        return schema

# Validate JSON data against a given schema
def validate_schema(data, schema_file):
    base_dir = os.path.abspath(os.path.dirname(schema_file))
    schema = load_schema(schema_file)

    # Resolve all $ref references within the schema
    resolved_schema = resolve_references(schema, base_dir)

    # Create a validator and validate the data
    validator = Draft202012Validator(resolved_schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        for error in errors:
            print(f"Validation error: {error.message}")
    else:
        print("Validation successful.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate JSON or YAML file against a schema.")
    parser.add_argument("data_file", help="Path to the JSON or YAML file to validate.")
    parser.add_argument("schema_file", help="The schema file to use for validation.")

    args = parser.parse_args()

    # Load data
    with open(args.data_file, "r") as file:
        data = json.load(file)

    # Validate data
    validate_schema(data, args.schema_file)