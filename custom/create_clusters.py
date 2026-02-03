# Creates migration clusters in Databricks workspace for metastore and table ACLs migration
import os
import subprocess
import json

# Update these values before running
profile = 'dsp'
email = "arvindh.km@swiggy.in"

# Cluster configuration for metastore migration 
cluster_config_for_metastore = {
    "cluster_name": "metastore-migrate-mti",
    "spark_version": "13.3.x-scala2.12",
    "aws_attributes": {
        "first_on_demand": 0,
        "availability": "ON_DEMAND",
        "zone_id": "auto",
        "spot_bid_price_percent": 100,
        "ebs_volume_count": 0
    },
    "node_type_id": "m6gd.large",
    "driver_node_type_id": "r6gd.xlarge",
    "autotermination_minutes": 30,
    "enable_elastic_disk": True,
    "single_user_name": email,
    "enable_local_disk_encryption": False,
    "data_security_mode": "DATA_SECURITY_MODE_DEDICATED",
    "runtime_engine": "STANDARD",
    "kind": "CLASSIC_PREVIEW",
    "is_single_node": False,
    "autoscale": {
        "min_workers": 1,
        "max_workers": 5
    },
    "apply_policy_default_values": False
}

result = subprocess.run(['databricks', '--profile', profile, 'clusters', 'create', '--json', json.dumps(cluster_config_for_metastore), '--no-wait'])

print(result.returncode)

# Cluster configuration for table ACLs migration 
cluster_config_for_table_acls = {
    "cluster_name": "table-acls-migrate-mti",
    "spark_version": "13.3.x-scala2.12",
    "aws_attributes": {
        "first_on_demand": 0,
        "availability": "ON_DEMAND",
        "zone_id": "auto",
        "spot_bid_price_percent": 100,
        "ebs_volume_count": 0
    },
    "node_type_id": "m6gd.large",
    "driver_node_type_id": "r6gd.xlarge",
    "autotermination_minutes": 30,
    "enable_elastic_disk": True,
    "enable_local_disk_encryption": False,
    "data_security_mode": "DATA_SECURITY_MODE_STANDARD",
    "runtime_engine": "STANDARD",
    "kind": "CLASSIC_PREVIEW",
    "is_single_node": False,
    "autoscale": {
        "min_workers": 1,
        "max_workers": 5
    },
    "apply_policy_default_values": False
}

result = subprocess.run(['databricks', '--profile', profile, 'clusters', 'create', '--json', json.dumps(cluster_config_for_table_acls), '--no-wait'])

print(result.returncode)