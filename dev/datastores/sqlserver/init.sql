SET NOCOUNT ON
GO

CREATE LOGIN metamapper WITH PASSWORD = '340Uuxwp7Mcxo7Khy'
GO

USE master
GO
IF EXISTS (select * from sysdatabases where name='Testing')
  drop database Testing
GO

DECLARE @device_directory NVARCHAR(520)
SELECT @device_directory = SUBSTRING(filename, 1, CHARINDEX(N'master.mdf', LOWER(filename)) - 1)
  FROM master.dbo.sysaltfiles
 WHERE dbid = 1 AND fileid = 1

EXECUTE (N'CREATE DATABASE Testing
  ON PRIMARY (NAME = N''Testing'', FILENAME = N''' + @device_directory + N'northwnd.mdf'')
  LOG ON (NAME = N''Testing_log'',  FILENAME = N''' + @device_directory + N'northwnd.ldf'')')
GO

IF CAST(SERVERPROPERTY('ProductMajorVersion') AS INT)<12
BEGIN
  exec sp_dboption 'Testing','trunc. log on chkpt.','true'
  exec sp_dboption 'Testing','select into/bulkcopy','true'
END
ELSE ALTER DATABASE [Testing] SET RECOVERY SIMPLE WITH NO_WAIT
GO

IF EXISTS (select * from sysdatabases where name='IsPrivate')
  drop database PrivateDatabase
GO

EXECUTE (N'CREATE DATABASE IsPrivate
  ON PRIMARY (NAME = N''IsPrivate'', FILENAME = N''' + @device_directory + N'IsPrivate.mdf'')
  LOG ON (NAME = N''IsPrivate_log'',  FILENAME = N''' + @device_directory + N'IsPrivate.ldf'')')
GO

if CAST(SERVERPROPERTY('ProductMajorVersion') AS INT)<12
BEGIN
  exec sp_dboption 'IsPrivate','trunc. log on chkpt.','true'
  exec sp_dboption 'IsPrivate','select into/bulkcopy','true'
END
ELSE ALTER DATABASE [IsPrivate] SET RECOVERY SIMPLE WITH NO_WAIT
GO

SET quoted_identifier on
GO

SET DATEFORMAT mdy
GO

/*
 * This is a test database that should not be found by the Revisioner.
 */
USE "IsPrivate"
GO

CREATE SCHEMA [secrets]
GO

CREATE TABLE [secrets].[secrets] (
  "secret_id" "int" IDENTITY (1, 1) NOT NULL ,
  "name" nvarchar (20) NOT NULL ,
  CONSTRAINT "PK_Secrets" PRIMARY KEY CLUSTERED
  (
    "secret_id"
  )
)
GO

CREATE INDEX "secret_name" ON "secrets"."secrets"("name")
GO

/*
 * This is the typical inspection test database.
 */

USE "testing"
GO

/*
 * User Information
 */
CREATE USER metamapper_ro FOR LOGIN metamapper
GO

EXEC sp_addrolemember 'db_datareader', 'metamapper_ro'
GO

/*
 * Employees
 */

CREATE SCHEMA [employees]
GO

CREATE TABLE [employees].[employees] (
  "emp_no"      INT IDENTITY (1, 1) NOT NULL ,
  "birth_date"  DATE                NOT NULL,
  "first_name"  NVARCHAR(14)        NOT NULL,
  "last_name"   NVARCHAR(16)        NOT NULL,
  "hire_date"   DATE                NOT NULL,
  created_at    DATETIME            NOT NULL,
  CONSTRAINT "PK_employees_employees" PRIMARY KEY CLUSTERED
  (
    "emp_no"
  ),
  CONSTRAINT "CK_Birthdate" CHECK (birth_date < getdate())
)
GO


CREATE TABLE [employees].[departments] (
    dept_no     NVARCHAR(4)     NOT NULL,
    dept_name   VARCHAR(40)     NOT NULL UNIQUE,
    started_on  DATETIME        NOT NULL,
    CONSTRAINT "PK_employees_departments" PRIMARY KEY CLUSTERED
    (
      "dept_no"
    )
)
GO

CREATE TABLE [employees].[dept_manager] (
  dept_no      NVARCHAR(4)     NOT NULL,
  emp_no       INT             NOT NULL,
  from_date    DATE            NOT NULL,
  to_date      DATE            NOT NULL,
  extras       TEXT,
  rating       INT             DEFAULT 5,
  CONSTRAINT "FK_employees_dept_manager_employee" FOREIGN KEY
  (
    "emp_no"
  ) REFERENCES "employees"."employees" (
    "emp_no"
  ),
  CONSTRAINT "FK_employees_dept_manager_department" FOREIGN KEY
  (
    "dept_no"
  ) REFERENCES "employees"."departments" (
    "dept_no"
  ),
  CONSTRAINT "PK_employees_dept_manager" PRIMARY KEY CLUSTERED
  (
    "emp_no", "dept_no"
  )
)
GO

CREATE TABLE [employees].[dept_emp] (
  emp_no      INT             NOT NULL,
  dept_no     NVARCHAR(4)     NOT NULL,
  from_date   DATE            NOT NULL,
  to_date     DATE            NOT NULL,
  CONSTRAINT "FK_employees_dept_emp_employee" FOREIGN KEY
  (
    "emp_no"
  ) REFERENCES "employees"."employees" (
    "emp_no"
  ),
  CONSTRAINT "FK_employees_dept_emp_department" FOREIGN KEY
  (
    "dept_no"
  ) REFERENCES "employees"."departments" (
    "dept_no"
  ),
  CONSTRAINT "PK_employees_dept_emp" PRIMARY KEY CLUSTERED
  (
    "emp_no", "dept_no"
  )
)
GO


CREATE VIEW [employees].[dept_emp_latest_date] AS
  SELECT emp_no, MAX(from_date) AS from_date, MAX(to_date) AS to_date
  FROM employees.dept_emp
  GROUP BY emp_no
GO

CREATE VIEW [employees].[current_dept_emp] AS
  SELECT l.emp_no, dept_no, l.from_date, l.to_date
  FROM employees.dept_emp d
    INNER JOIN employees.dept_emp_latest_date l
      ON d.emp_no=l.emp_no AND d.from_date=l.from_date AND l.to_date = d.to_date
GO

/*
 * orderSystem
 */

CREATE SCHEMA [orderSystem]
GO


CREATE TABLE [orderSystem].[customers] (
  customerNumber int NOT NULL,
  customerName varchar(50) NOT NULL,
  contactLastName varchar(50) NOT NULL,
  contactFirstName varchar(50) NOT NULL,
  phone varchar(50) NOT NULL,
  addressLine1 varchar(50) NOT NULL,
  addressLine2 varchar(50) DEFAULT NULL,
  city varchar(50) NOT NULL,
  state varchar(50) DEFAULT NULL,
  postalCode varchar(15) DEFAULT NULL,
  country varchar(50) NOT NULL,
  salesRepEmployeeNumber int DEFAULT NULL,
  creditLimit decimal(10,2) DEFAULT NULL,
  CONSTRAINT "PK_ordersystem_customerNumber" PRIMARY KEY CLUSTERED
  (
    "customerNumber"
  ),
  CONSTRAINT "FK_ordersytem_customers_employee" FOREIGN KEY
  (
    "salesRepEmployeeNumber"
  ) REFERENCES "employees"."employees" (
    "emp_no"
  )
)
GO

CREATE TABLE [orderSystem].[departments] (
  id int NOT NULL,
  dept_name  VARCHAR(40) NOT NULL UNIQUE
  CONSTRAINT "PK_ordersystem_departments" PRIMARY KEY CLUSTERED
  (
    "id"
  )
)
GO

CREATE TABLE [orderSystem].[productLines] (
  productLine varchar(50) NOT NULL,
  textDescription varchar(4000) DEFAULT NULL,
  htmlDescription varchar(4000),
  image text,
  CONSTRAINT "PK_ordersystem_productLines" PRIMARY KEY CLUSTERED
  (
    "productLine"
  )
)
GO

CREATE TABLE [orderSystem].[products] (
  productCode varchar(15) NOT NULL,
  productName varchar(70) NOT NULL,
  productLine varchar(50) NOT NULL,
  productScale varchar(10) NOT NULL,
  productVendor varchar(50) NOT NULL,
  productDescription text NOT NULL,
  quantityInStock INT NOT NULL,
  buyPrice decimal(10,2) NOT NULL,
  MSRP decimal(10,2) NOT NULL,
  CONSTRAINT "PK_ordersystem_products" PRIMARY KEY CLUSTERED
  (
    "productCode"
  ),
  CONSTRAINT "FK_ordersytem_products_productLine" FOREIGN KEY
  (
    "productLine"
  ) REFERENCES "orderSystem"."productLine" (
    "productLine"
  )
)
GO

CREATE TABLE [orderSystem].[orders] (
  orderNumber INT NOT NULL,
  orderDate DATE NOT NULL,
  requiredDate DATE NOT NULL,
  shippedDate DATE DEFAULT NULL,
  status varchar(15) NOT NULL,
  comments text,
  customerNumber INT NOT NULL,
  CONSTRAINT "PK_ordersystem_orders" PRIMARY KEY CLUSTERED
  (
    "orderNumber"
  ),
  CONSTRAINT "FK_ordersytem_orders_customers" FOREIGN KEY
  (
    "customerNumber"
  ) REFERENCES "orderSystem"."orderSystem" (
    "customerNumber"
  )
)
GO

CREATE TABLE [orderSystem].[orderDetails] (
  orderNumber INT NOT NULL,
  productCode varchar(15) NOT NULL,
  quantityOrdered INT NOT NULL,
  priceEach decimal(10,2) NOT NULL,
  orderLineNumber INT NOT NULL,
  CONSTRAINT "PK_ordersystem_orderDetails" PRIMARY KEY CLUSTERED
  (
    "orderNumber", "productCode"
  ),
  CONSTRAINT "FK_ordersytem_orderDetails_orders" FOREIGN KEY
  (
    "orderNumber"
  ) REFERENCES "orderSystem"."orders" (
    "orderNumber"
  ),
  CONSTRAINT "FK_ordersytem_orderDetails_products" FOREIGN KEY
  (
    "productCode"
  ) REFERENCES "orderSystem"."products" (
    "productCode"
  )
)
GO

CREATE TABLE [orderSystem].[payments] (
  customerNumber INT NOT NULL,
  checkNumber varchar(50) NOT NULL,
  paymentDate DATE NOT NULL,
  amount decimal(10,2) NOT NULL,
  CONSTRAINT "PK_ordersystem_payments" PRIMARY KEY  CLUSTERED
  (
    "customerNumber", "checkNumber"
  ),
  CONSTRAINT "FK_ordersytem_payments_customer" FOREIGN KEY
  (
    "customerNumber"
  ) REFERENCES "orderSystem"."customers" (
    "customerNumber"
  )
)
GO

CREATE VIEW [orderSystem].[salesRepresentatives] AS (
  SELECT d.customerNumber,
         d.customerName,
         d.salesRepEmployeeNumber,
         l.emp_no,
         CONCAT(l.first_name, '', l.last_name) as name
  FROM orderSystem.customers d
    INNER JOIN employees.employees l
      ON d.salesRepEmployeeNumber=l.emp_no
)
GO

/*
 * auth_service
 */

CREATE SCHEMA [auth_service]
GO

CREATE TABLE auth_service.privileges (
  id INT NOT NULL,
  privilege_name NVARCHAR(50) NULL,
  CONSTRAINT "pk_auth_service_privileges" PRIMARY KEY  CLUSTERED
  (
    "id"
  )
)
GO

CREATE TABLE auth_service.employee_privileges (
  employee_id INT NOT NULL,
  privilege_id INT NOT NULL,
  CONSTRAINT "pk_auth_service_employee_privileges" PRIMARY KEY  CLUSTERED
  (
    "employee_id", "privilege_id"
  )
  CONSTRAINT "FK_employee_privileges_employee" FOREIGN KEY
  (
    "employee_id"
  ) REFERENCES "employees"."employees" (
    "emp_no"
  )
  CONSTRAINT "FK_employee_privileges_privilege" FOREIGN KEY
  (
    "privilege_id"
  ) REFERENCES "auth_service"."privileges" (
    "id"
  )
  FOREIGN KEY (employee_id)  REFERENCES employees.employees (emp_no) ON DELETE NO ACTION ON UPDATE NO ACTION,
  FOREIGN KEY (privilege_id) REFERENCES auth_service.privileges (id) ON DELETE NO ACTION ON UPDATE NO ACTION
)
GO

CREATE INDEX auth_employee_privilege_idx ON auth_service.employee_privileges (employee_id, privilege_id);
GO
