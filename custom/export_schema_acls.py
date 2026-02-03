'''
Export schema ACLs from source workspace to a JSON.
To filter for particular schema, mention the schema name without catalog in schemas_to_filter list. If list is empty, all schemas will be exported.
'''
import json

schemas = [i.databaseName for i in spark.sql('show schemas in prod').collect()]

schemas_to_filter = ['dsp']

schemas = [schema for schema in schemas if schema in schemas_to_filter]

schema_acl_map = {}

for schema in schemas:
    schema_grants = [f"GRANT {grant.ActionType} ON SCHEMA {schema} TO {grant.Principal}" for grant in spark.sql(f"SHOW GRANT ON SCHEMA {schema}").collect() if grant.ObjectType == 'SCHEMA']
    schema_acl_map[schema] = schema_grants

print(json.dumps(schema_acl_map, indent=4))