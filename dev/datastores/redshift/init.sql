/*
 * User Information
 */

CREATE USER metamapper_ro WITH PASSWORD '340Uuxwp7Mcxo7Khy';

/*
 * Employees
 */

CREATE SCHEMA employees;

GRANT USAGE ON SCHEMA employees TO metamapper_ro;

CREATE TABLE employees.employees (
    emp_no      INT             NOT NULL,
    birth_date  DATE            NOT NULL,
    first_name  VARCHAR(14)     NOT NULL,
    last_name   VARCHAR(16)     NOT NULL,
    hire_date   DATE            NOT NULL,
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN employees.employees.emp_no IS 'The employee identification number';

CREATE TABLE employees.departments (
    dept_no     CHAR(4)         NOT NULL,
    dept_name   VARCHAR(40)     NOT NULL,
    started_on  TIMESTAMP       NOT NULL
);

CREATE TABLE employees.dept_manager (
   dept_no      CHAR(4)         NOT NULL,
   emp_no       INT             NOT NULL,
   from_date    DATE            NOT NULL,
   to_date      DATE            NOT NULL,
   extras       TEXT,
   rating       INT             DEFAULT 5
);

CREATE TABLE employees.dept_emp (
    emp_no      INT             NOT NULL,
    dept_no     CHAR(4)         NOT NULL,
    from_date   DATE            NOT NULL,
    to_date     DATE            NOT NULL
);

CREATE VIEW employees.dept_emp_latest_date AS
  SELECT emp_no, MAX(from_date) AS from_date, MAX(to_date) AS to_date
  FROM employees.dept_emp
  GROUP BY emp_no;


CREATE VIEW employees.current_dept_emp AS
  SELECT l.emp_no, dept_no, l.from_date, l.to_date
  FROM employees.dept_emp d
    INNER JOIN employees.dept_emp_latest_date l
      ON d.emp_no=l.emp_no AND d.from_date=l.from_date AND l.to_date = d.to_date;

/*
 * orderSystem
 */

CREATE SCHEMA orderSystem;

GRANT USAGE ON SCHEMA orderSystem TO metamapper_ro;

CREATE TABLE orderSystem.customers (
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
  creditLimit decimal(10,2) DEFAULT NULL
);

CREATE TABLE orderSystem.departments (
  id int NOT NULL,
  dept_name  VARCHAR(40) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE      (dept_name)
);

CREATE TABLE orderSystem.productLines (
  productLine varchar(50) NOT NULL,
  textDescription varchar(4000) DEFAULT NULL,
  htmlDescription varchar(4000),
  image bytea,
  PRIMARY KEY (productLine)
);

CREATE TABLE orderSystem.products (
  productCode varchar(15) NOT NULL,
  productName varchar(70) NOT NULL,
  productLine varchar(50) NOT NULL,
  productScale varchar(10) NOT NULL,
  productVendor varchar(50) NOT NULL,
  productDescription text NOT NULL,
  quantityInStock INT NOT NULL,
  buyPrice decimal(10,2) NOT NULL,
  MSRP decimal(10,2) NOT NULL
);

CREATE TABLE orderSystem.orders (
  orderNumber INT NOT NULL,
  orderDate DATE NOT NULL,
  requiredDate DATE NOT NULL,
  shippedDate DATE DEFAULT NULL,
  status varchar(15) NOT NULL,
  comments text,
  customerNumber INT NOT NULL
);

CREATE TABLE orderSystem.orderDetails (
  orderNumber INT NOT NULL,
  productCode varchar(15) NOT NULL,
  quantityOrdered INT NOT NULL,
  priceEach decimal(10,2) NOT NULL,
  orderLineNumber INT NOT NULL
);

CREATE TABLE orderSystem.payments (
  customerNumber INT NOT NULL,
  checkNumber varchar(50) NOT NULL,
  paymentDate DATE NOT NULL,
  amount decimal(10,2) NOT NULL
);

CREATE VIEW orderSystem.salesRepresentatives AS
  SELECT d.customerNumber,
         d.customerName,
         d.salesRepEmployeeNumber,
         l.emp_no
  FROM orderSystem.customers d
    INNER JOIN employees.employees l
      ON d.salesRepEmployeeNumber=l.emp_no;

/*
 * auth_service
 */

CREATE SCHEMA auth_service;

GRANT USAGE ON SCHEMA auth_service TO metamapper_ro;

CREATE TABLE auth_service.privileges (
  id INT NOT NULL,
  privilege_name VARCHAR(50) NULL
);

CREATE TABLE auth_service.employee_privileges (
  employee_id INT NOT NULL,
  privilege_id INT NOT NULL
);
