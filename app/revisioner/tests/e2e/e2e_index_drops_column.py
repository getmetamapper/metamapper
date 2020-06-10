"""
Drop one column from an index (`app`.`orderdetails_pkey`).
"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['table_object_id'] == 16501
        ),
        "column_filters": (
            lambda col: col['column_name'] == "ordernumber"
        ),
    },
])

inspected_indexes = mutate_inspected(inspected.indexes, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['index_object_id'] == 16504
        ),
        "column_filters": (
            lambda col: col['column_name'] == "ordernumber"
        ),
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['index_object_id'] == 16504
        ),
        "column_filters": (
            lambda col: col['column_name'] == "productcode"
        ),
        "metadata": {
            "field": "columns.ordinal_position",
            "new_value": 1,
        }
    },
])

test_cases = [
    {
        "model": "Column",
        "description": "The `app`.`orderdetails`.`ordernumber` column was dropped.",
        "filters": {
            "table__name": "orderdetails",
            "name": "ordernumber",
        },
        "assertions": [
            {
                "summarized": "It should not be found via the `name` values.",
                "evaluation": lambda datastore, column: column is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Index",
        "description": "The `app`.`orderdetails_pkey` index is persisted.",
        "filters": {
            "object_id": "16504",
        },
        "assertions": [
            {
                "summarized": "It should have the same Index identity.",
                "evaluation": lambda datastore, index: index.pk,
                "pass_value": "HYs6hRJDUkqL",
            },
            {
                "summarized": "It should have the same Table identity.",
                "evaluation": lambda datastore, index: index.table_id,
                "pass_value": "Hh2eS38kpRX0",
            },
            {
                "summarized": "It should not be found via the `name` values.",
                "evaluation": lambda datastore, index: set(index.columns.values_list("name", flat=True)),
                "pass_value": {"productcode"},
            },
        ]
    },
    {
        "model": "IndexColumn",
        "description": "The `app`.`orderdetails_pkey`.`ordernumber` index column is removed.",
        "filters": {
            "pk": 12,
        },
        "assertions": [
            {
                "summarized": "It should have removed the IndexColumn.",
                "evaluation": lambda datastore, index_column: index_column.column.name,
                "pass_value": "productcode",
            },
        ]
    },
]
