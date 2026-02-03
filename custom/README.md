# Databricks UC Metastore Migration Guide

This guide provides step-by-step instructions for exporting and importing Unity Catalog (UC) metastore data between Databricks workspaces, including table metadata and access control lists (ACLs).

## Overview

This migration process allows you to:
- Export metastore metadata from a source workspace
- Update S3 paths and prefixes for cross-region migration
- Export table ACLs
- Import metastore and ACLs into a target workspace

## Prerequisites

1. **Clone the repository**
   ```bash
   git clone https://github.com/arvindh-km/databricks-migrate.git
   cd databricks-migrate
   ```

2. **Install Databricks CLI**
   - Using Homebrew: `brew install databricks-cli`
   - Or using curl

3. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Initial Setup

### Step 1: Configure Source Workspace

1. **Create a Personal Access Token (PAT)**
   - Navigate to your source Databricks workspace
   - Go to User Settings → Access Tokens
   - Generate a new token and save it securely

2. **Configure Databricks CLI profile**
   ```bash
   databricks configure --token --profile sg_dsp
   ```
   - Replace `sg_dsp` with a profile name of your choice
   - When prompted, enter your workspace host URL and PAT token

3. **Create migration clusters**
   - Open `custom/create_clusters.py`
   - Update the `profile` value to match your profile name
   - Update the `email` field
   - Run the script:
     ```bash
     python3 custom/create_clusters.py
     ```
   - **Important**: Wait for cluster creation to complete in the source workspace before proceeding
   - If cluster creation fails due to workspace-specific init scripts or restrictions, update the script accordingly

## Export Process

### Step 2: Export Metastore

Run the following command to export the metastore:

```bash
python3 migration_pipeline.py \
  --profile <your-profile> \
  --set-export-dir <local-dir-path> \
  --cluster-name "metastore-migrate-mti" \
  --export-pipeline \
  --use-checkpoint \
  --num-parallel 10 \
  --retry-total 3 \
  --retry-backoff 2 \
  --keep-tasks metastore \
  --session run1 \
  --skip-failed \
  --metastore-unicode \
  --repair-metastore-tables \
  --database <schema-name>
```

**Parameters to update:**
- `<your-profile>`: Your Databricks CLI profile name
- `<local-dir-path>`: Local directory path (e.g., `/export_dir/`)
- `<schema-name>`: Schema/database name to export (leave empty for all schemas)
- `--cluster-name`: Should match the cluster created in Step 1

**Output:** Metastore data will be exported to `/export_dir/run1/metastore/`

### Step 3: Update S3 Paths and Prefixes

Before importing, you need to update S3 paths to point to the target region's buckets:

1. Open `custom/metastore_s3.py`
2. Update the following fields:
   - `schemas`: Add all schemas you want to migrate
   - `path`: Update to the metastore export path (e.g., `/export_dir/run1/metastore/`)
   - `s3_buckets` dictionary: Update with equivalent region-specific bucket names
   - `uc_prefix` dictionary: Update with required region-specific prefixes
3. Save the file and run:
   ```bash
   python3 custom/metastore_s3.py
   ```

**What this does:**
- Updates S3 paths from source region (e.g., Singapore) to target region (e.g., Mumbai) buckets
- Removes UC-specific prefixes that prevent table creation for Managed Tables
- Apply additional filters as needed based on your bucket requirements

### Step 4: Export Table ACLs

Export table access control lists:

```bash
python3 migration_pipeline.py \
  --profile <your-profile> \
  --set-export-dir <local-dir-path> \
  --cluster-name "table-acls-migrate-mti" \
  --export-pipeline \
  --use-checkpoint \
  --num-parallel 10 \
  --retry-total 3 \
  --retry-backoff 2 \
  --keep-tasks metastore_table_acls \
  --session run1 \
  --skip-failed \
  --metastore-unicode \
  --repair-metastore-tables \
  --database <schema-name>
```

**Note:** Users and groups do not need to be exported separately. The ACL export works without them.

**Output:** Table ACLs will be exported to `/export_dir/run1/table_acls/` as zip files (no need to decompress)

## Import Process

### Step 5: Configure Target Workspace

1. **Create PAT token in target workspace** (e.g., Mumbai workspace)
2. **Configure Databricks CLI profile for target workspace:**
   ```bash
   databricks configure --token --profile <target-profile>
   ```
3. **Create clusters in target workspace:**
   - Follow Step 1 instructions, but use the target workspace profile and PAT

### Step 6: Export and Import Catalog ACLs

1. **Export catalog ACLs from source workspace:**
   - Clone the notebook `custom/export_catalog_acls.py` in your source workspace
   - Update the `catalog` variable to match your catalog name (e.g., `'prod'`)
   - Run the notebook to generate catalog ACL export
   - Copy the JSON output containing the GRANT commands

2. **Import catalog ACLs to target workspace:**
   - Clone the notebook `custom/import_catalog_acls.py` in your target workspace
   - Replace the `grant_cmds` list with the output from the previous step
   - Run all cells in the notebook to apply catalog ACLs

### Step 7: Export and Import Schemas

1. **Export schemas from source workspace:**
   - Clone the notebook `custom/export_schema_s3.py` in your source workspace
   - Update the `schemas_to_filter` list with the schemas you want to migrate
   - Run the notebook to generate schema export
   - Copy the JSON output containing schema creation commands

2. **Import schemas to target workspace:**
   - Clone the notebook `custom/import_schema_s3.py` in your target workspace
   - Update the schema map using the output from the previous step
   - Run all cells in the notebook to create schemas

### Step 8: Export and Import Schema ACLs

1. **Export schema ACLs from source workspace:**
   - Clone the notebook `custom/export_schema_acls.py` in your source workspace
   - Update the `schemas_to_filter` list with the schemas you want to export ACLs for (leave empty to export all schemas)
   - Run the notebook to generate schema ACL export
   - Copy the JSON output containing the schema ACL map

2. **Import schema ACLs to target workspace:**
   - Clone the notebook `custom/import_schema_acls.py` in your target workspace
   - Replace the `grant_cmds` dictionary with the JSON output from the previous step
   - Run all cells in the notebook to apply schema ACLs

### Step 9: Import Metastore

Import the metastore into the target workspace:

```bash
python3 migration_pipeline.py \
  --profile <target-profile> \
  --set-export-dir <local-dir-path> \
  --cluster-name "metastore-migrate-mti" \
  --import-pipeline \
  --use-checkpoint \
  --num-parallel 8 \
  --retry-total 3 \
  --retry-backoff 2 \
  --keep-tasks metastore \
  --session run1 \
  --skip-failed \
  --metastore-unicode \
  --repair-metastore-tables \
  --database <schema-name>
```

**Important:**
- Use the target workspace profile (e.g., Mumbai workspace profile)
- Maintain the same export directory used during export
- Specify the schema you want to import
- This creates tables on top of the updated S3 paths

### Step 10: Import Table ACLs

Update table access control lists in the target workspace:

```bash
python3 migration_pipeline.py \
  --profile <target-profile> \
  --set-export-dir <local-dir-path> \
  --cluster-name "metastore-migrate-mti" \
  --import-pipeline \
  --use-checkpoint \
  --num-parallel 8 \
  --retry-total 3 \
  --retry-backoff 2 \
  --keep-tasks metastore_table_acls \
  --session run1 \
  --skip-failed \
  --metastore-unicode \
  --repair-metastore-tables \
  --database <schema-name>
```

**Parameters to update:**
- `<target-profile>`: Target workspace profile (e.g., Mumbai workspace profile)
- `<schema-name>`: Schema for which you want to update access controls

## Troubleshooting

- **Cluster creation failures**: Update `custom/create_clusters.py` with workspace-specific init scripts and restrictions
- **S3 path issues**: Verify bucket names and prefixes in `custom/metastore_s3.py` match your target region configuration
- **Import failures**: Ensure schemas are created in the target workspace before importing metastore

