import json
import yaml
import os

# Convert JSON to YAML
def json_to_yaml(json_file_path, yaml_file_path):
    with open(json_file_path, "r") as json_file:
        json_data = json.load(json_file)

    with open(yaml_file_path, "w") as yaml_file:
        yaml.dump(json_data, yaml_file, default_flow_style=False)
    print(f"Converted {json_file_path} to {yaml_file_path}")

# Convert YAML to JSON
def yaml_to_json(yaml_file_path, json_file_path):
    with open(yaml_file_path, "r") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

    with open(json_file_path, "w") as json_file:
        json.dump(yaml_data, json_file, indent=2)
    print(f"Converted {yaml_file_path} to {json_file_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert between JSON and YAML.")
    parser.add_argument("input_file", help="Path to the input JSON or YAML file.")
    parser.add_argument("output_file", help="Path to the output YAML or JSON file.")

    args = parser.parse_args()

    # Determine conversion direction based on file extension
    if args.input_file.endswith(".json") and args.output_file.endswith(".yaml"):
        json_to_yaml(args.input_file, args.output_file)
    elif args.input_file.endswith(".yaml") and args.output_file.endswith(".json"):
        yaml_to_json(args.input_file, args.output_file)
    else:
        print("Unsupported conversion type. Please provide a valid combination of JSON and YAML files.")
