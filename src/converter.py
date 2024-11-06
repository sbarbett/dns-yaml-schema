import json
import yaml
import os
import dns.zone
import dns.rdataclass
import dns.rdatatype
from dns.exception import DNSException
from modules.ConvertBINDToJSON import ConvertBINDToJSON

# Load JSON Schema for DNS Records
def load_schema(schema_file_path):
    with open(schema_file_path, "r") as schema_file:
        return json.load(schema_file)

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

# Convert JSON to BIND Zone File
def json_to_bind(json_file_path, bind_file_path, schema_file_path):
    schema = load_schema(schema_file_path)

    with open(json_file_path, "r") as json_file:
        json_data = json.load(json_file)

    domain = json_data.get("domain", "")
    zone = dns.zone.Zone(dns.name.from_text(domain))

    for record in json_data.get("records", []):
        if not record or "type" not in record:
            continue

        name = record["name"]
        rdtype = record["type"]
        ttl = record.get("ttl", 3600)

        # Using the schema to construct the rdata format
        record_schema = next((r for r in schema["records"]["items"]["oneOf"] if r["properties"]["type"]["enum"][0] == rdtype), None)
        if not record_schema:
            print(f"Unsupported record type found in JSON: {rdtype}")
            continue

        rdata_text_parts = []
        for prop, details in record_schema["properties"].items():
            if prop not in ["type", "name", "ttl"] and prop in record:
                rdata_text_parts.append(str(record[prop]))

        rdata_text = " ".join(rdata_text_parts)

        try:
            rdata = dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.from_text(rdtype), rdata_text)
            zone_node = zone.get_node(name, create=True)
            rdataset = zone_node.find_rdataset(dns.rdataclass.IN, dns.rdatatype.from_text(rdtype), create=True)
            rdataset.add(rdata, ttl)
        except Exception as e:
            print(f"Failed to add record {record}: {e}")

    with open(bind_file_path, "w") as bind_file:
        zone.to_file(bind_file, sorted=True)
    print(f"Converted {json_file_path} to {bind_file_path}")

# Convert BIND Zone File to JSON
def bind_to_json(bind_file_path, json_file_path):
    try:
        # Read the zone file into a string
        with open(bind_file_path, "r") as bind_file:
            zone_text = bind_file.read()

        # Attempt to parse the zone text using dnspython
        zone = dns.zone.from_text(zone_text, origin=None, relativize=False)

        # Extract the default TTL if available
        default_ttl = getattr(zone, 'default_ttl', None)

        json_data = {
            "domain": str(zone.origin),
            "soa": {},
            "ns": [],
            "records": []
        }

        # Include the TTL directive if it was found
        if default_ttl is not None:
            json_data["ttl"] = default_ttl

        # Extract $ORIGIN directive if present
        if zone.origin:
            json_data["origin"] = str(zone.origin)

        converter = ConvertBINDToJSON()

        for name, node in zone.nodes.items():
            for rdataset in node.rdatasets:
                records = converter.convert_record(name, rdataset)
                for record in records:
                    if record["type"] == "SOA":
                        json_data["soa"] = record
                    elif record["type"] == "NS":
                        json_data["ns"].append(record)
                    else:
                        json_data["records"].append(record)

        with open(json_file_path, "w") as json_file:
            json.dump(json_data, json_file, indent=2)
        print(f"Converted {bind_file_path} to {json_file_path}")

    except DNSException as e:
        print(f"Failed to parse BIND zone file: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert between JSON, YAML, and BIND zone files.")
    parser.add_argument("input_file", help="Path to the input JSON, YAML, or BIND (.conf) file.")
    parser.add_argument("output_file", help="Path to the output JSON, YAML, or BIND (.conf) file.")
    parser.add_argument("--schema_file", help="Path to the zone schema file (for JSON/BIND conversion).", default="src/zone_schema.json")

    args = parser.parse_args()

    # Determine conversion direction based on file extension
    if args.input_file.endswith(".json") and args.output_file.endswith(".yaml"):
        json_to_yaml(args.input_file, args.output_file)
    elif args.input_file.endswith(".yaml") and args.output_file.endswith(".json"):
        yaml_to_json(args.input_file, args.output_file)
    elif args.input_file.endswith(".json") and args.output_file.endswith(".conf"):
        json_to_bind(args.input_file, args.output_file, args.schema_file)
    elif args.input_file.endswith(".conf") and args.output_file.endswith(".json"):
        bind_to_json(args.input_file, args.output_file)
    else:
        print("Unsupported conversion type. Please provide a valid combination of file types.")
