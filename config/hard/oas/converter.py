import json
import yaml

class VAPIOpenAPISpecConverter:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.spec_data = None
        self.converted_data = {
            "openapi": "3.0.0",
            "info": {},
            "paths": {},
            "components": {
                "schemas": {}
            }
        }

    def load_spec(self):
        with open(self.input_file, "r") as file:
            self.spec_data = json.load(file)

    def convert_info(self):
        self.converted_data["info"] = {
            "title": self.spec_data["info"].get("title", "vAPI Specification"),
            "description": self.spec_data["info"].get("description", ""),
            "version": self.spec_data["info"].get("version", "1.0")
        }

    def convert_paths_and_schemas(self):
        paths = self.spec_data.get("paths", {})
        for path, methods in paths.items():
            self.converted_data["paths"][path] = {}
            for method, details in methods.items():
                # Extract the requestBody schema and move it to components.schemas
                schema_ref = None
                if "requestBody" in details:
                    schema = details["requestBody"].get("content", {}).get("application/json", {}).get("schema", {})
                    if schema:
                        schema_name = f"{details['summary'].replace(' ', '')}Request"
                        self.converted_data["components"]["schemas"][schema_name] = schema
                        schema_ref = f"#/components/schemas/{schema_name}"

                # Add the method details
                self.converted_data["paths"][path][method] = {
                    "tags": details.get("tags", []),
                    "summary": details.get("summary", ""),
                    "parameters": details.get("parameters", []),
                    "responses": details.get("responses", {}),
                }
                if schema_ref:
                    self.converted_data["paths"][path][method]["requestBody"] = {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": schema_ref
                                }
                            }
                        }
                    }

    def save_converted_spec(self):
        with open(self.output_file, "w") as file:
            json.dump(self.converted_data, file, indent=4)

    def convert(self):
        self.load_spec()
        self.convert_info()
        self.convert_paths_and_schemas()
        self.save_converted_spec()

# Example usage
if __name__ == "__main__":
    converter = VAPIOpenAPISpecConverter(
        input_file="crapi_oas.json",
        output_file="crapi_oas_x.json"
    )
    converter.convert()
    print("Conversion complete. Output saved to vapi_oas.yaml")
