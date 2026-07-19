---
name: p2-data-model
description: >
  Phase P2 of the combinatorial-problem methodology — Data model & instances.
  Use after P1, to define the input data model, a JSON instance schema, and a
  synthetic instance generator. Applies the data-model, instance-schema and
  instance-generator templates. Follows docs/methodology/README.md.
---

# P2 — Data model & instances

Specify the input data independently of any technique, and build a way to
generate test instances.

## Inputs
- The P1 problem description (especially its Input information section).

## Templates
- `docs/methodology/templates/data-model.template.tex`
- `docs/methodology/templates/instance-schema.template.json`
- `docs/methodology/templates/instance_generator.template.py`

## Steps
1. **Data model doc**: fill the data-model template into
   `docs/<problem>/data_model.tex` (sets, entity attributes, relations, demand
   or other inputs, configuration, instance tuple, scenario parameters). Wire
   into `main.tex` and compile. Note: if it uses tables, ensure the harness
   preamble has `\usepackage{longtable}`.
2. **Schema**: fill the instance-schema template into
   `<problem>_model/schemas/instance.schema.json`. Keep field names in 1:1
   correspondence with the data-model symbols; `additionalProperties: false`.
3. **Generator**: fill the generator template into
   `<problem>_model/instance_generator.py` — seeded (`random.Random(seed)`),
   pure stdlib, `generate_instance(...)` + argparse CLI (`python -m ...`).
4. Generate a small instance and validate it against the schema (use
   `jsonschema` if available; else inspect manually).

## Done when
- data-model compiles; the generator runs and its output validates against the
  schema; field names match the data model.

## Governance
- Invoke `methodology-curator` to record P2 and extract/update the three
  templates.

## Next
- P3 solution model & checker (`p3-solution-checker`).
