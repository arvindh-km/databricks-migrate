# Exports schema creation commands with S3 locations
import json

schemas = [i.databaseName for i in spark.sql('show schemas in prod').collect()]

schema_commands = {}

# Update with schemas to export (empty list exports all schemas)
schemas_to_filter = ['data_science_prod']
schemas = [schema for schema in schemas if schema in schemas_to_filter]

for schema in schemas:
    schema_desc = spark.sql(f'describe schema {schema}').collect()
    catalog, name, location = None, None, None
    for i in schema_desc:
        if i.database_description_item == 'Catalog Name': catalog = i.database_description_value
        if i.database_description_item == 'Namespace Name': name = i.database_description_value
        if i.database_description_item == 'RootLocation': location = i.database_description_value
    schema_commands[schema] = f"CREATE SCHEMA IF NOT EXISTS {catalog}.{name} MANAGED LOCATION '{location}'"

print(json.dumps(schema_commands, indent=4))