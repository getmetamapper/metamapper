# -*- coding: utf-8 -*-


tables_and_views = [
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 16442,
        "table_name": "customers",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16442/1",
                "column_name": "customernumber",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16442/2",
                "column_name": "customername",
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16442/3",
                "column_name": "contactlastname",
                "ordinal_position": 3,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16442/4",
                "column_name": "contactfirstname",
                "ordinal_position": 4,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16442/5",
                "column_name": "phone",
                "ordinal_position": 5,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16442/6",
                "column_name": "addressline1",
                "ordinal_position": 6,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16442/7",
                "column_name": "addressline2",
                "ordinal_position": 7,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": "NULL::character varying"
            },
            {
                "column_object_id": "16442/8",
                "column_name": "city",
                "ordinal_position": 8,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16442/9",
                "column_name": "state",
                "ordinal_position": 9,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": "NULL::character varying"
            },
            {
                "column_object_id": "16442/10",
                "column_name": "postalcode",
                "ordinal_position": 10,
                "data_type": "character varying",
                "max_length": 15,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": "NULL::character varying"
            },
            {
                "column_object_id": "16442/11",
                "column_name": "country",
                "ordinal_position": 11,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16442/12",
                "column_name": "salesrepemployeenumber",
                "ordinal_position": 12,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16442/13",
                "column_name": "creditlimit",
                "ordinal_position": 13,
                "data_type": "numeric",
                "max_length": 10,
                "numeric_scale": 2,
                "is_nullable": True,
                "is_primary": False,
                "default_value": "NULL::numeric"
            }
        ]
    },
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 16522,
        "table_name": "departments",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16522/1",
                "column_name": "id",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": "nextval('app.departments_id_seq'::regclass)"
            },
            {
                "column_object_id": "16522/2",
                "column_name": "dept_name",
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 40,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 16501,
        "table_name": "orderdetails",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16501/1",
                "column_name": "ordernumber",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16501/2",
                "column_name": "productcode",
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 15,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16501/3",
                "column_name": "quantityordered",
                "ordinal_position": 3,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16501/4",
                "column_name": "priceeach",
                "ordinal_position": 4,
                "data_type": "numeric",
                "max_length": 10,
                "numeric_scale": 2,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16501/5",
                "column_name": "orderlinenumber",
                "ordinal_position": 5,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 16465,
        "table_name": "orders",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16465/1",
                "column_name": "ordernumber",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16465/2",
                "column_name": "orderdate",
                "ordinal_position": 2,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16465/3",
                "column_name": "requireddate",
                "ordinal_position": 3,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16465/4",
                "column_name": "shippeddate",
                "ordinal_position": 4,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16465/5",
                "column_name": "status",
                "ordinal_position": 5,
                "data_type": "character varying",
                "max_length": 15,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16465/6",
                "column_name": "comments",
                "ordinal_position": 6,
                "data_type": "text",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16465/7",
                "column_name": "customernumber",
                "ordinal_position": 7,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 16478,
        "table_name": "payments",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16478/1",
                "column_name": "customernumber",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16478/2",
                "column_name": "checknumber",
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16478/3",
                "column_name": "paymentdate",
                "ordinal_position": 3,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16478/4",
                "column_name": "amount",
                "ordinal_position": 4,
                "data_type": "numeric",
                "max_length": 10,
                "numeric_scale": 2,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 16456,
        "table_name": "productlines",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16456/1",
                "column_name": "productline",
                "ordinal_position": 1,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16456/2",
                "column_name": "textdescription",
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 4000,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": "NULL::character varying"
            },
            {
                "column_object_id": "16456/3",
                "column_name": "htmldescription",
                "ordinal_position": 3,
                "data_type": "text",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16456/4",
                "column_name": "image",
                "ordinal_position": 4,
                "data_type": "bytea",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 16488,
        "table_name": "products",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16488/1",
                "column_name": "productcode",
                "ordinal_position": 1,
                "data_type": "character varying",
                "max_length": 15,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16488/2",
                "column_name": "productname",
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 70,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16488/3",
                "column_name": "productline",
                "ordinal_position": 3,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16488/4",
                "column_name": "productscale",
                "ordinal_position": 4,
                "data_type": "character varying",
                "max_length": 10,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16488/5",
                "column_name": "productvendor",
                "ordinal_position": 5,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16488/6",
                "column_name": "productdescription",
                "ordinal_position": 6,
                "data_type": "text",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16488/7",
                "column_name": "quantityinstock",
                "ordinal_position": 7,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16488/8",
                "column_name": "buyprice",
                "ordinal_position": 8,
                "data_type": "numeric",
                "max_length": 10,
                "numeric_scale": 2,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16488/9",
                "column_name": "msrp",
                "ordinal_position": 9,
                "data_type": "numeric",
                "max_length": 10,
                "numeric_scale": 2,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 16516,
        "table_name": "sales_representatives",
        "table_type": "view",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16516/1",
                "column_name": "customernumber",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16516/2",
                "column_name": "customername",
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 50,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16516/3",
                "column_name": "salesrepemployeenumber",
                "ordinal_position": 3,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16516/4",
                "column_name": "emp_no",
                "ordinal_position": 4,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16516/5",
                "column_name": "name",
                "ordinal_position": 5,
                "data_type": "text",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16386,
        "table_schema": "employees",
        "table_object_id": 16437,
        "table_name": "current_dept_emp",
        "table_type": "view",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16437/1",
                "column_name": "emp_no",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16437/2",
                "column_name": "dept_no",
                "ordinal_position": 2,
                "data_type": "character",
                "max_length": 4,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16437/3",
                "column_name": "from_date",
                "ordinal_position": 3,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16437/4",
                "column_name": "to_date",
                "ordinal_position": 4,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16386,
        "table_schema": "employees",
        "table_object_id": 16392,
        "table_name": "departments",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16392/1",
                "column_name": "dept_no",
                "ordinal_position": 1,
                "data_type": "character",
                "max_length": 4,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16392/2",
                "column_name": "dept_name",
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 40,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16392/3",
                "column_name": "started_on",
                "ordinal_position": 3,
                "data_type": "timestamp without time zone",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16386,
        "table_schema": "employees",
        "table_object_id": 16418,
        "table_name": "dept_emp",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16418/1",
                "column_name": "emp_no",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16418/2",
                "column_name": "dept_no",
                "ordinal_position": 2,
                "data_type": "character",
                "max_length": 4,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16418/3",
                "column_name": "from_date",
                "ordinal_position": 3,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16418/4",
                "column_name": "to_date",
                "ordinal_position": 4,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16386,
        "table_schema": "employees",
        "table_object_id": 16433,
        "table_name": "dept_emp_latest_date",
        "table_type": "view",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16433/1",
                "column_name": "emp_no",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16433/2",
                "column_name": "from_date",
                "ordinal_position": 2,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16433/3",
                "column_name": "to_date",
                "ordinal_position": 3,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            }
        ]
    },
    {
        "schema_object_id": 16386,
        "table_schema": "employees",
        "table_object_id": 16399,
        "table_name": "dept_manager",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16399/1",
                "column_name": "dept_no",
                "ordinal_position": 1,
                "data_type": "character",
                "max_length": 4,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16399/2",
                "column_name": "emp_no",
                "ordinal_position": 2,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16399/3",
                "column_name": "from_date",
                "ordinal_position": 3,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16399/4",
                "column_name": "to_date",
                "ordinal_position": 4,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16399/5",
                "column_name": "extras",
                "ordinal_position": 5,
                "data_type": "text",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16399/6",
                "column_name": "rating",
                "ordinal_position": 6,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": True,
                "is_primary": False,
                "default_value": "5"
            }
        ]
    },
    {
        "schema_object_id": 16386,
        "table_schema": "employees",
        "table_object_id": 16387,
        "table_name": "employees",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "16387/1",
                "column_name": "emp_no",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "16387/2",
                "column_name": "birth_date",
                "ordinal_position": 2,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16387/3",
                "column_name": "first_name",
                "ordinal_position": 3,
                "data_type": "character varying",
                "max_length": 14,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16387/4",
                "column_name": "last_name",
                "ordinal_position": 4,
                "data_type": "character varying",
                "max_length": 16,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16387/5",
                "column_name": "hire_date",
                "ordinal_position": 5,
                "data_type": "date",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "16387/6",
                "column_name": "created_at",
                "ordinal_position": 6,
                "data_type": "timestamp without time zone",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            }
        ]
    }
]

indexes = [
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "customers",
        "table_object_id": 16442,
        "index_name": "customers_pkey",
        "index_object_id": 16449,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX customers_pkey ON app.customers USING btree (customernumber)",
        "columns": [
            {
                "column_name": "customernumber",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "departments",
        "table_object_id": 16522,
        "index_name": "departments_dept_name_key",
        "index_object_id": 16528,
        "is_unique": True,
        "is_primary": False,
        "definition": "CREATE UNIQUE INDEX departments_dept_name_key ON app.departments USING btree (dept_name)",
        "columns": [
            {
                "column_name": "dept_name",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "departments",
        "table_object_id": 16522,
        "index_name": "app_departments_pkey",
        "index_object_id": 16526,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX app_departments_pkey ON app.departments USING btree (id)",
        "columns": [
            {
                "column_name": "id",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "orderdetails",
        "table_object_id": 16501,
        "index_name": "orderdetails_pkey",
        "index_object_id": 16504,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX orderdetails_pkey ON app.orderdetails USING btree (ordernumber, productcode)",
        "columns": [
            {
                "column_name": "ordernumber",
                "ordinal_position": 1
            },
            {
                "column_name": "productcode",
                "ordinal_position": 2
            }
        ]
    },
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "orders",
        "table_object_id": 16465,
        "index_name": "orders_pkey",
        "index_object_id": 16471,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX orders_pkey ON app.orders USING btree (ordernumber)",
        "columns": [
            {
                "column_name": "ordernumber",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "payments",
        "table_object_id": 16478,
        "index_name": "payments_pkey",
        "index_object_id": 16481,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX payments_pkey ON app.payments USING btree (customernumber, checknumber)",
        "columns": [
            {
                "column_name": "customernumber",
                "ordinal_position": 1
            },
            {
                "column_name": "checknumber",
                "ordinal_position": 2
            }
        ]
    },
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "productlines",
        "table_object_id": 16456,
        "index_name": "productlines_pkey",
        "index_object_id": 16463,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX productlines_pkey ON app.productlines USING btree (productline)",
        "columns": [
            {
                "column_name": "productline",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "products",
        "table_object_id": 16488,
        "index_name": "products_pkey",
        "index_object_id": 16494,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX products_pkey ON app.products USING btree (productcode)",
        "columns": [
            {
                "column_name": "productcode",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "employees",
        "schema_object_id": 16386,
        "table_name": "departments",
        "table_object_id": 16392,
        "index_name": "departments_dept_name_key",
        "index_object_id": 16397,
        "is_unique": True,
        "is_primary": False,
        "definition": "CREATE UNIQUE INDEX departments_dept_name_key ON employees.departments USING btree (dept_name)",
        "columns": [
            {
                "column_name": "dept_name",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "employees",
        "schema_object_id": 16386,
        "table_name": "departments",
        "table_object_id": 16392,
        "index_name": "employees_departments_pkey",
        "index_object_id": 16395,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX employees_departments_pkey ON employees.departments USING btree (dept_no)",
        "columns": [
            {
                "column_name": "dept_no",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "employees",
        "schema_object_id": 16386,
        "table_name": "dept_emp",
        "table_object_id": 16418,
        "index_name": "dept_emp_pkey",
        "index_object_id": 16421,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX dept_emp_pkey ON employees.dept_emp USING btree (emp_no, dept_no)",
        "columns": [
            {
                "column_name": "emp_no",
                "ordinal_position": 1
            },
            {
                "column_name": "dept_no",
                "ordinal_position": 2
            }
        ]
    },
    {
        "schema_name": "employees",
        "schema_object_id": 16386,
        "table_name": "dept_manager",
        "table_object_id": 16399,
        "index_name": "dept_manager_pkey",
        "index_object_id": 16406,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX dept_manager_pkey ON employees.dept_manager USING btree (emp_no, dept_no)",
        "columns": [
            {
                "column_name": "emp_no",
                "ordinal_position": 1
            },
            {
                "column_name": "dept_no",
                "ordinal_position": 2
            }
        ]
    },
    {
        "schema_name": "employees",
        "schema_object_id": 16386,
        "table_name": "employees",
        "table_object_id": 16387,
        "index_name": "employees_pkey",
        "index_object_id": 16390,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX employees_pkey ON employees.employees USING btree (emp_no)",
        "columns": [
            {
                "column_name": "emp_no",
                "ordinal_position": 1
            }
        ]
    }
]
