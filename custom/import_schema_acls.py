'''
Import schema ACLs from JSON to Target UC.
Use the JSON logged from export_schema_acls.py to import schema ACLs.
'''
grant_cmds = {
    "dsp": ["GRANT SELECT ON SCHEMA dsp TO PROD_DSP_READER"]
}

for schema, commands in grant_cmds.items():
    for command in commands:
        try:
            spark.sql(command)
        except Exception as e:
            print(f"Error importing schema ACLs for {schema}: {e}")
            continue

print("Schema ACLs imported successfully")