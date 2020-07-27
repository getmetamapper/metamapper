/*
 * User Information
 */

CREATE USER metamapper_ro WITH PASSWORD '340Uuxwp7Mcxo7Khy';

/*
 * Employees
 */

DROP SCHEMA IF EXISTS employees CASCADE;

CREATE SCHEMA employees;

GRANT USAGE ON SCHEMA employees TO metamapper_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA employees TO metamapper_ro;

ALTER DEFAULT PRIVILEGES IN SCHEMA employees GRANT SELECT ON TABLES TO metamapper_ro;

CREATE TABLE employees.employees (
    emp_no      INT             NOT NULL,
    birth_date  DATE            NOT NULL,
    first_name  VARCHAR(14)     NOT NULL,
    last_name   VARCHAR(16)     NOT NULL,
    hire_date   DATE            NOT NULL,
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (emp_no)
);

CREATE TABLE employees.departments (
    dept_no     CHAR(4)         NOT NULL,
    dept_name   VARCHAR(40)     NOT NULL,
    started_on  TIMESTAMP       NOT NULL,
    PRIMARY KEY (dept_no),
    UNIQUE      (dept_name)
);

CREATE TABLE employees.dept_manager (
   dept_no      CHAR(4)         NOT NULL,
   emp_no       INT             NOT NULL,
   from_date    DATE            NOT NULL,
   to_date      DATE            NOT NULL,
   extras       TEXT,
   rating       INT             DEFAULT 5,
   FOREIGN KEY (emp_no)  REFERENCES employees.employees (emp_no)    ON DELETE CASCADE,
   FOREIGN KEY (dept_no) REFERENCES employees.departments (dept_no) ON DELETE CASCADE,
   PRIMARY KEY (emp_no,dept_no)
);

CREATE TABLE employees.dept_emp (
    emp_no      INT             NOT NULL,
    dept_no     CHAR(4)         NOT NULL,
    from_date   DATE            NOT NULL,
    to_date     DATE            NOT NULL,
    FOREIGN KEY (emp_no)  REFERENCES employees.employees   (emp_no)  ON DELETE CASCADE,
    FOREIGN KEY (dept_no) REFERENCES employees.departments (dept_no) ON DELETE CASCADE,
    PRIMARY KEY (emp_no,dept_no)
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

DROP SCHEMA IF EXISTS orderSystem CASCADE;

CREATE SCHEMA orderSystem;

GRANT USAGE ON SCHEMA orderSystem TO metamapper_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA orderSystem TO metamapper_ro;

ALTER DEFAULT PRIVILEGES IN SCHEMA orderSystem GRANT SELECT ON TABLES TO metamapper_ro;

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
  creditLimit decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (customerNumber),
  FOREIGN KEY (salesRepEmployeeNumber) REFERENCES employees.employees (emp_no)
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
  MSRP decimal(10,2) NOT NULL,
  PRIMARY KEY (productCode),
  FOREIGN KEY (productLine) REFERENCES orderSystem.productLines (productLine)
);

CREATE TABLE orderSystem.orders (
  orderNumber INT NOT NULL,
  orderDate DATE NOT NULL,
  requiredDate DATE NOT NULL,
  shippedDate DATE DEFAULT NULL,
  status varchar(15) NOT NULL,
  comments text,
  customerNumber INT NOT NULL,
  PRIMARY KEY (orderNumber),
  FOREIGN KEY (customerNumber) REFERENCES orderSystem.customers (customerNumber)
);

CREATE TABLE orderSystem.orderDetails (
  orderNumber INT NOT NULL,
  productCode varchar(15) NOT NULL,
  quantityOrdered INT NOT NULL,
  priceEach decimal(10,2) NOT NULL,
  orderLineNumber INT NOT NULL,
  PRIMARY KEY (orderNumber,productCode),
  FOREIGN KEY (orderNumber) REFERENCES orderSystem.orders (orderNumber),
  FOREIGN KEY (productCode) REFERENCES orderSystem.products (productCode)
);

CREATE TABLE orderSystem.payments (
  customerNumber INT NOT NULL,
  checkNumber varchar(50) NOT NULL,
  paymentDate DATE NOT NULL,
  amount decimal(10,2) NOT NULL,
  PRIMARY KEY (customerNumber,checkNumber),
  FOREIGN KEY (customerNumber) REFERENCES orderSystem.customers (customerNumber)
);

CREATE VIEW orderSystem.salesRepresentatives AS
  SELECT d.customerNumber,
         d.customerName,
         d.salesRepEmployeeNumber,
         l.emp_no,
         CONCAT(l.first_name, '', l.last_name) as name
  FROM orderSystem.customers d
    INNER JOIN employees.employees l
      ON d.salesRepEmployeeNumber=l.emp_no;

/*
 * auth_service
 */

DROP SCHEMA IF EXISTS auth_service CASCADE;

CREATE SCHEMA auth_service;

GRANT USAGE ON SCHEMA auth_service TO metamapper_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_service TO metamapper_ro;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth_service GRANT SELECT ON TABLES TO metamapper_ro;

CREATE TABLE auth_service.privileges (
  id INT NOT NULL,
  privilege_name VARCHAR(50) NULL,
  PRIMARY KEY (id)
);

CREATE TABLE auth_service.employee_privileges (
  employee_id INT NOT NULL,
  privilege_id INT NOT NULL,
  PRIMARY KEY (employee_id, privilege_id),
  FOREIGN KEY (employee_id)  REFERENCES employees.employees (emp_no) ON DELETE NO ACTION ON UPDATE NO ACTION,
  FOREIGN KEY (privilege_id) REFERENCES auth_service.privileges (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE INDEX auth_employee_privilege_idx ON auth_service.employee_privileges (employee_id, privilege_id);
