# Imports catalog ACLs from exported GRANT commands
# Replace this list with output from export_catalog_acls.py
grant_cmds = ['GRANT USE CATALOG ON CATALOG prod TO PROD_CDC_OBSERVABILITY_READER',
 'GRANT USE CATALOG ON CATALOG prod TO PROD_DATA_SCIENCE_READER',
 'GRANT USE CATALOG ON CATALOG prod TO PROD_FINANCECIRCUSRECOVERY_READER',
 'GRANT USE CATALOG ON CATALOG prod TO PROD_OSIRIS_WRITER',
 'GRANT USE CATALOG ON CATALOG prod TO PROD_TEMP_READER',
 'GRANT USE CATALOG ON CATALOG prod TO PROD_DASHCATALOG_READER',
 'GRANT USE CATALOG ON CATALOG prod TO PROD_ALCHEMIST_WRITER']

for command in grant_cmds:
    try:
        spark.sql(command)
    except Exception as e:
        print(f"Error importing catalog ACL: {e}")
        continue

print("Catalog ACLs imported successfully")