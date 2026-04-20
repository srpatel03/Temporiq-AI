# prepare_secrets.py
import sys
import json

def escape_json_for_toml(file_path):
    """
    Reads a GCP JSON key file and prints its content as a single-line,
    escaped string, making it safe to use as a Streamlit secret.
    """
    try:
        with open(file_path, 'r') as f:
            # Load the JSON to properly handle its structure and contents.
            data = json.load(f)
        
        # Dump the data back into a string without any extra whitespace.
        # json.dumps correctly escapes characters within the JSON values,
        # such as the '\n' in the private_key.
        compact_json_string = json.dumps(data, separators=(',', ':'))
        
        # Create the full TOML line for the user to copy. We use json.dumps again to properly
        # escape the JSON string (turning " into \" and \ into \\) so it becomes a valid 
        # TOML basic string. This completely avoids issues with single quotes in the data.
        toml_value = json.dumps(compact_json_string)
        toml_line = f"GCP_CREDENTIALS_JSON = {toml_value}"

        print("\n✅ Conversion successful!")
        print("\n---")
        print("COPY THE ENTIRE LINE BELOW and paste it into your Streamlit Secrets editor.")
        print("This single line replaces any existing `GCP_CREDENTIALS_JSON` entry.")
        print("---\n")
        print(toml_line)

    except FileNotFoundError:
        print(f"\n❌ Error: File not found at '{file_path}'")
        print("Please make sure you provide the correct path to your JSON key file.")
    except json.JSONDecodeError as e:
        print(f"\n❌ Error: The file at '{file_path}' is not a valid JSON file.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python prepare_secrets.py /path/to/your/gcp-key.json")
        print("Example: python prepare_secrets.py ./my-gcp-key.json")
    else:
        json_file_path = sys.argv[1]
        escape_json_for_toml(json_file_path)