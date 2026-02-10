import json

def map_columns(df):
    with open("config/schema_config.json") as f:
        schema = json.load(f)

    mapping = {}
    for standard, variants in schema.items():
        for col in df.columns:
            if col in variants:
                mapping[col] = standard

    return df.rename(columns=mapping)
