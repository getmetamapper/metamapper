"""
Drop an index (`app`.`orderdetails_pkey`) and re-create it with additional columns.
"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [])

inspected_indexes = mutate_inspected(inspected.indexes, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['table_object_id'] == 16392
        ),
    },
    {
        "type": "dropped",
        "filters": (
            lambda row: row['index_object_id'] == 16504
        ),
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16478
        ),
        "column_filters": (
            lambda col: col['column_name'] == "amount"
        ),
        "metadata": {
            "field": "columns.is_nullable",
            "new_value": True,
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16478
        ),
        "column_filters": (
            lambda col: col['column_name'] == "amount"
        ),
        "metadata": {
            "field": "columns.column_name",
            "new_value": "dollar_amount",
        },
    },
])

inspected_indexes += [
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "orderdetails",
        "table_object_id": 16501,
        "index_name": "orderdetails_pkey",
        "index_object_id": 26504,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX orderdetails_pkey ON app.orderdetails USING btree (ordernumber, orderlinenumber, productcode)",
        "columns": [
            {
                "column_name": "ordernumber",
                "ordinal_position": 1
            },
            {
                "column_name": "orderlinenumber",
                "ordinal_position": 2
            },
            {
                "column_name": "productcode",
                "ordinal_position": 3
            },
        ]
    },
]

test_cases = [
    {
        "description": "Expect revision logs to be created.",
        "assertions": [
            {
                "evaluation": lambda datastore, nulled: datastore.most_recent_run.revisions.filter(action=1, resource_type__model='index').count(),
                "pass_value": 0,
            },
        ]
    },
    {
        "model": "Index",
        "description": "The `app`.`orderdetails_pkey` index should be created.",
        "filters": {
            "table__schema__name": "app",
            "name": "orderdetails_pkey",
        },
        "assertions": [
            {
                "summarized": "It should have the same Index identity.",
                "evaluation": lambda datastore, index: index.pk,
                "pass_value": 4,
            },
            {
                "summarized": "It should have an updated `object_id` value.",
                "evaluation": lambda datastore, index: index.object_id,
                "pass_value": "26504",
            },
            {
                "summarized": "It should have the correct `is_primary` flag.",
                "evaluation": lambda datastore, index: index.is_primary,
                "pass_value": True,
            },
            {
                "summarized": "It should have the correct `is_unique` flag.",
                "evaluation": lambda datastore, index: index.is_unique,
                "pass_value": True,
            },
            {
                "summarized": "It should have updated Column instances.",
                "evaluation": lambda datastore, index: set(index.columns.values_list("name", flat=True)),
                "pass_value": {"ordernumber", "orderlinenumber", "productcode"},
            },
            {
                # Remember that we do an UPSERT here, so IDs are not reserved...
                "summarized": "It should have the same IndexColumn references (except for new one).",
                "evaluation": lambda datastore, index: set(index.index_columns.values_list("id", flat=True)),
                "pass_value": {11, 12, 19},
            },
        ]
    },
]
