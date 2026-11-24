import json
import sys
from pathlib import Path

from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from jsonschema.validators import validator_for

## Load all the schemas in the schema directory into a registry
# The main schema is playbook.json, which references other schemas in the same directory.
# All of the schemas are loaded into a registry so that they can be resolved when validating the playbook.

registry = Registry()
for path in Path("schema").rglob("*.json"):
    contents = json.loads(path.read_text())
    resource = Resource.from_contents(contents, default_specification=DRAFT202012)
    registry = registry.with_resource(contents.get("$id", path.resolve().as_uri()), resource)

## Build a validator for the playbook schema and validate the playbook against it
# playbook.json is the top-level schema: the rules for the whole playbook document. 
    
root = json.loads(Path("schema/playbook.json").read_text())
Validator = validator_for(root)
validator = Validator(root, registry=registry)

## Load target playbook user wants to check. 

playbook = json.loads(Path(sys.argv[1]).read_text())

# Collects all errors (rule violations) found in the playbook and sorts them by their location in the document.

errors = sorted(validator.iter_errors(playbook), key=lambda e: list(e.path))

# Reports the results of the validation: 
# if there are no errors, the playbook is valid. 
# if there are errors, the playbook is invalid and the errors are printed with their location in the document.

if not errors:
    print("VALID: playbook conforms to the schema")
else:
    print(f"INVALID: {len(errors)} problem(s) found\n")
    for e in errors:
        location = "/".join(str(p) for p in e.path) or "(top level)"
        print(f"- at {location}: {e.message}")