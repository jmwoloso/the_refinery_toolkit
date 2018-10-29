"""
schemas.py: Schemas for the BiqQuery tables where the enriched data is
            stored.
"""

__author__ = "jason wolosonovich <jason@avaland.io>"
__license__ = "BSD 3 clause"

from google.cloud import bigquery as bq

# mobile friendly test
MOBILE_FRIENDLY_SCHEMA = [
    bq.SchemaField(name="refinery_id",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="refined_at",
                   field_type="timestamp",
                   mode="required"),
    bq.SchemaField(name="refined_date",
                   field_type="date",
                   mode="required"),
    bq.SchemaField(name="domain",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="url",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="test_results",
                   field_type="string",
                   mode="required")
]

# clearbit tag history
TAGS_HISTORY_SCHEMA = [
    bq.SchemaField(name="refinery_id",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="refined_at",
                   field_type="timestamp",
                   mode="required"),
    bq.SchemaField(name="refined_date",
                   field_type="date",
                   mode="required"),
    bq.SchemaField(name="domain",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="url",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="tag",
                   field_type="string",
                   mode="required")
]

# clearbit tech history
TECH_HISTORY_SCHEMA = [
    bq.SchemaField(name="refinery_id",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="refined_at",
                   field_type="timestamp",
                   mode="required"),
    bq.SchemaField(name="refined_date",
                   field_type="date",
                   mode="required"),
    bq.SchemaField(name="domain",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="url",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="tech",
                   field_type="string",
                   mode="required")
]

# crawler asset history
ASSET_HISTORY_SCHEMA = [
    bq.SchemaField(name="refinery_id",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="refined_at",
                   field_type="timestamp",
                   mode="required"),
    bq.SchemaField(name="refined_date",
                   field_type="date",
                   mode="required"),
    bq.SchemaField(name="domain",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="url",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="asset",
                   field_type="string",
                   mode="required"),
    bq.SchemaField(name="type",
                   field_type="string",
                   mode="required")
]
