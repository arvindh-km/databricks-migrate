# Updates S3 bucket paths and UC prefixes in exported metastore files for cross-region migration
import os

# Update these values before running
schemas = ['dsp']
path = 'export_dir/test/run2/metastore/'

# Map source region buckets to target region buckets
s3_buckets = {
    's3://swiggy-data-science-platform/': 's3://swiggy-data-science-platform-mumbai/',
    's3://swiggy-qubole/': 's3://swiggy-qubole-mumbai/',
}
# Map UC prefixes to target prefixes (removes UC-specific prefixes for Managed Tables)
uc_prefix = {
    '__unitystorage': 'uc_tables'
}

for schema in schemas:
    file_names = [f for f in os.listdir(path+schema) if os.path.isfile(os.path.join(path+schema, f))]
    for i in file_names:
        with open(path+schema+'/'+i, 'r', encoding='utf-8') as file:
            content = file.read()
            for bucket in s3_buckets:
                if bucket in content:
                    content = content.replace(bucket, s3_buckets[bucket])
                    break
            for prefix in uc_prefix:
                if prefix in content:
                    content = content.replace(prefix, uc_prefix[prefix])
                    break
            with open(path+schema+'/'+i, 'w', encoding='utf-8') as _f:
                _f.write(content)