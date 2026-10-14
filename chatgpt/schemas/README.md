# Portable schema snapshots

Retrieved on September 30, 2026 from:

- https://agent-plugins.org/schemas/1.0.0/plugin.schema.json
- https://agent-plugins.org/schemas/1.0.0/mcp.schema.json

These schemas validate Agent Plugins 1.0 core files. Client-specific extensions
have additional requirements; the builder checks the known OpenAI listing and
review constraints from Plugin Creator's installed documentation. The public
submission portal remains authoritative for its current validation.

To repeat core schema validation with a Python environment containing
`jsonschema`:

```sh
python3 - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator
for stem in ('plugin', 'mcp'):
    schema = json.loads(Path(f'schemas/{stem}.schema.json').read_text())
    data = json.loads(Path(f'sleuth-mcp/{stem}.json').read_text())
    Draft202012Validator(schema).validate(data)
    print(stem, 'schema passed')
PY
```
