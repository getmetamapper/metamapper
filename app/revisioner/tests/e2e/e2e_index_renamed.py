"""
Update the name of an index (`app`.`departments_pkey`).

Example SQL:

  ALTER TABLE `app`.`departments_pkey` RENAME TO `departments_primary_key`;

"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [])

inspected_indexes = mutate_inspected(inspected.indexes, [
    {
        "type": "modified",
        "filters": (
            lambda row: row['index_object_id'] == 16528
        ),
        "metadata": {
            "field": "index_name",
            "new_value": "departments_primary_key",
        }
    }
])

test_cases = [
    {
        "model": "Index",
        "description": "The `employees`.`departments` table should not longer exist.",
        "filters": {
            "object_id": "16528",
        },
        "assertions": [
            {
                "summarized": "It should have the same Index identity.",
                "evaluation": lambda datastore, index: index.pk,
                "pass_value": 2,
            },
            {
                "summarized": "It should have an updated name.",
                "evaluation": lambda datastore, index: index.name,
                "pass_value": "departments_primary_key",
            },
            {
                "summarized": "It should the same columns.",
                "evaluation": lambda datastore, index: set(index.columns.values_list("name", flat=True)),
                "pass_value": {"dept_name"},
            },
        ]
    },
]
