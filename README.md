# DNS YAML Schema Project

## Overview
This project proposes a JSON and YAML specification for how DNS zone files should be represented. It includes a JSON Schema for validating zone files and a utility to convert between JSON and YAML formats.

## Setting Up the Environment
Follow the steps below to set up the project in a virtual environment and validate the example DNS zone file.

### 1. Create a Virtual Environment
Create a virtual environment to keep dependencies isolated:

```sh
python3 -m venv venv
```

Activate the virtual environment:

- On Linux/macOS:
  ```sh
  source venv/bin/activate
  ```
- On Windows:
  ```cmd
  venv\Scripts\activate
  ```

### 2. Install Requirements
Install the required Python libraries from `requirements.txt`:

```sh
pip install -r requirements.txt
```

### 3. Run the Schema Validator
Use the schema validator to validate the example zone file:

```sh
python3 src/schema_validator.py examples/example_zone.json src/zone_schema.json
```

If the validation is successful, you'll see:

```
Validation successful.
```

If there are errors, they will be listed.

## Additional Commands
To convert between JSON and YAML formats, use the `converter.py` script:

```sh
python3 src/converter.py input_file output_file
```

