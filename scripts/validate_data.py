import os
import json
import yaml
import jsonschema
from jsonschema import validate

# Configuration
SCHEMA_PATH = 'schemas/aircraft_schema.json'
DATA_DIRS = [
    '01_Military_Aviation',
    '02_Unmanned_Systems',
    '03_Civilian_&_Commercial',
    '04_Space_&_Hypersonic',
    '05_Core_Technologies'
]

def load_schema(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_yaml_file(file_path, schema):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Convert datetime objects to strings for JSON schema validation
        def json_serial(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return obj

        # Recursively convert dates in the dictionary
        def convert_dates(obj):
            if isinstance(obj, dict):
                return {k: convert_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_dates(i) for i in obj]
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return obj
            
        data = convert_dates(data)
        
        validate(instance=data, schema=schema)
        print(f"✅ Valid: {file_path}")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ Invalid: {file_path}")
        print(f"   Error: {e.message}")
        return False
    except Exception as e:
        print(f"⚠️ Error processing {file_path}: {e}")
        return False

def main():
    print("🚀 Starting NextGen-Flight-Registry Data Validation...\n")
    
    if not os.path.exists(SCHEMA_PATH):
        print(f"❌ Schema file not found: {SCHEMA_PATH}")
        return

    schema = load_schema(SCHEMA_PATH)
    
    total_files = 0
    passed_files = 0
    
    for directory in DATA_DIRS:
        if not os.path.exists(directory):
            continue
            
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    if validate_yaml_file(file_path, schema):
                        passed_files += 1

    print(f"\n📊 Summary: {passed_files}/{total_files} files passed validation.")
    
    if total_files > 0 and passed_files == total_files:
        print("🎉 All systems go!")
        exit(0)
    elif total_files == 0:
        print("ℹ️ No data files found.")
        exit(0)
    else:
        print("💥 Some files failed validation.")
        exit(1)

if __name__ == "__main__":
    main()
