import json
import sys
from pathlib import Path

from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
from jsonschema.validators import validator_for

registry = Registry()
for path in Path("schema").rglob("*.json"):
    contents = json.loads(path.read_text())
    resource = Resource.from_contents(contents, default_specification=DRAFT202012)
    registry = registry.with_resource(contents.get("$id", path.resolve().as_uri()), resource)
    
root = json.loads(Path("schema/playbook.json").read_text())
Validator = validator_for(root)
validator = Validator(root, registry=registry)

playbook = json.loads(Path(sys.argv[1]).read_text())
errors = sorted(validator.iter_errors(playbook), key=lambda e: list(e.path))

if not errors:
    print("VALID: playbook conforms to the schema")
else:
    print(f"INVALID: {len(errors)} problem(s) found\n")
    for e in errors:
        location = "/".join(str(p) for p in e.path) or "(top level)"
        print(f"- at {location}: {e.message}")