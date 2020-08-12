"""
Not many database systems we support have this feature, but we should test for it anyways.

Example SQL:

    ALTER TABLE foo MODIFY bar bartype AFTER baz;

"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected

from app.definitions.models import Column


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16488
        ),
        "column_filters": (
            lambda col: col['column_name'] == "productline"
        ),
        "metadata": {
            "field": "columns.ordinal_position",
            "new_value": 4,
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16488
        ),
        "column_filters": (
            lambda col: col['column_name'] == "productscale"
        ),
        "metadata": {
            "field": "columns.ordinal_position",
            "new_value": 3,
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16488
        ),
        "column_filters": (
            lambda col: col['column_name'] == "productscale"
        ),
        "metadata": {
            "field": "columns.column_name",
            "new_value": "scale",
        },
    },
    # Rename for MySQL would also change the `object_id` value.
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16488
        ),
        "column_filters": (
            lambda col: col['column_name'] == "scale"
        ),
        "metadata": {
            "field": "columns.column_object_id",
            "new_value": "16488/scale",
        },
    },
])

inspected_indexes = mutate_inspected(inspected.indexes, [])

test_cases = [
    {
        "model": "Table",
        "description": "The `app`.`products` table should have the same basic structure.",
        "filters": {
            "object_id": "16488",
        },
        "assertions": [
            {
                "summarized": "It should have the same Table identity.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": 7,
            },
            {
                "summarized": "It should not modify metadata about the Table.",
                "evaluation": lambda datastore, table: set(table.columns.order_by('ordinal_position').values_list("name", flat=True)),
                "pass_value": {
                    "productcode",
                    "productname",
                    "scale",
                    "productline",
                    "productvendor",
                    "productdescription",
                    "quantityinstock",
                    "buyprice",
                    "msrp",
                },
            }
        ]
    },
    {
        "model": "Column",
        "description": "The `app`.`products`.`productline` column should retain integrity.",
        "filters": {
            "table__name": "products",
            "name": "productline",
        },
        "assertions": [
            {
                "summarized": "It should have the same Column identity.",
                "evaluation": lambda datastore, column: column.pk,
                "pass_value": 38,
            },
            {
                "summarized": "It should have the same Column description.",
                "evaluation": lambda datastore, column: column.short_desc,
                "pass_value": "Hello, world.",
            },
            {
                "summarized": "It should have the same Table identity.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": 7,
            },
            # MySQL object IDs are calculated as: MD5(CONCAT(it.table_id, '/', c.column_name))
            # which means the object ID will not change in this case.
            {
                "summarized": "It should have the same the `object_id` field.",
                "evaluation": lambda datastore, column: column.object_id,
                "pass_value": "16488/3",
            },
            {
                "summarized": "It should update the `ordinal_position` field.",
                "evaluation": lambda datastore, column: column.ordinal_position,
                "pass_value": 4,
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app`.`products`.`productscale` column be renamed.",
        "filters": {
            "name": "scale",
        },
        "assertions": [
            {
                "summarized": "It should have a different Column identity.",
                "evaluation": lambda datastore, column: column.pk == "xAMHA4bgVdL7",
                "pass_value": False,
            },
            {
                # This is expected, but non-ideal behavior. When we rename a column
                # in MySQL, we lose all comments related to it.
                "summarized": "It should have no description.",
                "evaluation": lambda datastore, column: column.short_desc,
                "pass_value": None,
            },
            {
                "summarized": "It should have the same Table identity.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": 7,
            },
            {
                "summarized": "It should update the `ordinal_position` field.",
                "evaluation": lambda datastore, column: column.ordinal_position,
                "pass_value": 3,
            },
        ]
    },
    {
        "description": "The `app`.`products`.`productscale` column should be soft-deleted.",
        "assertions": [
            {
                "summarized": "It should have soft deleted the `productscale` column.",
                "evaluation": lambda datastore, null: (
                    Column.all_objects.filter(name="productscale").first().is_deleted
                ),
                "pass_value": True,
            },
        ]
    },
]
