# Exports catalog ACLs as GRANT commands in JSON format
import json

# Update catalog name as needed
catalog = 'prod'

result = []

for grant in spark.sql(f"SHOW GRANT ON catalog {catalog}").collect():
    action = grant.ActionType
    principal = grant.Principal
    prod_cmd = f"GRANT {action} ON CATALOG {catalog} TO {principal}"
    result.append(prod_cmd)

print(json.dumps(result, indent=4))