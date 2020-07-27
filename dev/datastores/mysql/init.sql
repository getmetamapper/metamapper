/*
 * User Information
 */

CREATE USER metamapper_ro IDENTIFIED BY '340Uuxwp7Mcxo7Khy';
GRANT SELECT, PROCESS ON *.* TO 'metamapper_ro';
FLUSH PRIVILEGES;

/*
 * Employees
 */

CREATE SCHEMA employees;

USE employees;

CREATE TABLE employees (
    emp_no      INT             NOT NULL,
    birth_date  DATE            NOT NULL,
    first_name  VARCHAR(14)     NOT NULL,
    last_name   VARCHAR(16)     NOT NULL,
    hire_date   DATE            NOT NULL,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (emp_no)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE departments (
    dept_no     CHAR(4)         NOT NULL,
    dept_name   VARCHAR(40)     NOT NULL,
    started_on  DATETIME        NOT NULL,
    PRIMARY KEY (dept_no),
    UNIQUE      (dept_name)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE dept_manager (
   emp_no       INT             NOT NULL,
   dept_no      CHAR(4)         NOT NULL,
   from_date    DATE            NOT NULL,
   to_date      DATE            NOT NULL,
   extras       TEXT,
   rating       INT             DEFAULT 5,
   FOREIGN KEY (emp_no)  REFERENCES employees (emp_no)    ON DELETE CASCADE,
   FOREIGN KEY (dept_no) REFERENCES departments (dept_no) ON DELETE CASCADE,
   PRIMARY KEY (emp_no,dept_no)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE dept_emp (
    emp_no      INT             NOT NULL,
    dept_no     CHAR(4)         NOT NULL,
    from_date   DATE            NOT NULL,
    to_date     DATE            NOT NULL,
    FOREIGN KEY (emp_no)  REFERENCES employees   (emp_no)  ON DELETE CASCADE,
    FOREIGN KEY (dept_no) REFERENCES departments (dept_no) ON DELETE CASCADE,
    PRIMARY KEY (emp_no,dept_no)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE salaries (
    emp_no      INT             NOT NULL,
    salary      INT             NOT NULL,
    from_date   DATE            NOT NULL,
    to_date     DATE            NOT NULL,
    FOREIGN KEY (emp_no) REFERENCES employees (emp_no) ON DELETE CASCADE,
    PRIMARY KEY (emp_no, from_date)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE VIEW dept_emp_latest_date AS
  SELECT emp_no, MAX(from_date) AS from_date, MAX(to_date) AS to_date
  FROM dept_emp
  GROUP BY emp_no;

CREATE VIEW current_dept_emp AS
  SELECT l.emp_no, dept_no, l.from_date, l.to_date
  FROM dept_emp d
    INNER JOIN dept_emp_latest_date l
      ON d.emp_no=l.emp_no AND d.from_date=l.from_date AND l.to_date = d.to_date;

/*
 * orderSystem
 */

CREATE SCHEMA orderSystem;

USE orderSystem;

CREATE TABLE customers (
  `customerNumber` int(11) NOT NULL,
  `customerName` varchar(50) NOT NULL,
  `contactLastName` varchar(50) NOT NULL,
  `contactFirstName` varchar(50) NOT NULL,
  `phone` varchar(50) NOT NULL,
  `addressLine1` varchar(50) NOT NULL,
  `addressLine2` varchar(50) DEFAULT NULL,
  `city` varchar(50) NOT NULL,
  `state` varchar(50) DEFAULT NULL,
  `postalCode` varchar(15) DEFAULT NULL,
  `country` varchar(50) NOT NULL,
  `salesRepEmployeeNumber` int(11) DEFAULT NULL,
  `creditLimit` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`customerNumber`),
  CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`salesRepEmployeeNumber`) REFERENCES `employees`.`employees` (`emp_no`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE departments (
  `id` int(11) NOT NULL,
  `dept_name`  VARCHAR(40) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE      (dept_name)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE productLines (
  `productLine` varchar(50) NOT NULL,
  `textDescription` varchar(4000) DEFAULT NULL,
  `htmlDescription` mediumtext,
  `image` mediumblob,
  PRIMARY KEY (`productLine`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE products (
  `productCode` varchar(15) NOT NULL,
  `productName` varchar(70) NOT NULL,
  `productLine` varchar(50) NOT NULL,
  `productScale` varchar(10) NOT NULL,
  `productVendor` varchar(50) NOT NULL,
  `productDescription` text NOT NULL,
  `quantityInStock` smallint(6) NOT NULL,
  `buyPrice` decimal(10,2) NOT NULL,
  `MSRP` decimal(10,2) NOT NULL,
  PRIMARY KEY (`productCode`),
  KEY `productLine` (`productLine`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`productLine`) REFERENCES `productLines` (`productLine`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE orders (
  `orderNumber` int(11) NOT NULL,
  `orderDate` date NOT NULL,
  `requiredDate` date NOT NULL,
  `shippedDate` date DEFAULT NULL,
  `status` varchar(15) NOT NULL,
  `comments` text,
  `customerNumber` int(11) NOT NULL,
  PRIMARY KEY (`orderNumber`),
  KEY `customerNumber` (`customerNumber`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customerNumber`) REFERENCES `customers` (`customerNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE orderDetails (
  `orderNumber` int(11) NOT NULL,
  `productCode` varchar(15) NOT NULL,
  `quantityOrdered` int(11) NOT NULL,
  `priceEach` decimal(10,2) NOT NULL,
  `orderLineNumber` smallint(6) NOT NULL,
  PRIMARY KEY (`orderNumber`,`productCode`),
  KEY `productCode` (`productCode`),
  CONSTRAINT `orderdetails_ibfk_1` FOREIGN KEY (`orderNumber`) REFERENCES `orders` (`orderNumber`),
  CONSTRAINT `orderdetails_ibfk_2` FOREIGN KEY (`productCode`) REFERENCES `products` (`productCode`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE payments (
  `customerNumber` int(11) NOT NULL,
  `checkNumber` varchar(50) NOT NULL,
  `paymentDate` date NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`customerNumber`,`checkNumber`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`customerNumber`) REFERENCES `customers` (`customerNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE VIEW salesRepresentatives AS
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

CREATE SCHEMA auth_service;

USE auth_service;

CREATE TABLE IF NOT EXISTS `auth_service`.`privileges` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `privilege_name` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `auth_service`.`employee_privileges` (
  `employee_id` INT(11) NOT NULL,
  `privilege_id` INT(11) NOT NULL,
  PRIMARY KEY (`employee_id`, `privilege_id`),
  INDEX `employee_id` (`employee_id` ASC),
  INDEX `privilege_id` (`privilege_id` ASC),
  INDEX `privilege_id_2` (`privilege_id` ASC),
  CONSTRAINT `fk_employee_privileges_employees1`
    FOREIGN KEY (`employee_id`)
    REFERENCES `employees`.`employees` (`emp_no`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_employee_privileges_privileges1`
    FOREIGN KEY (`privilege_id`)
    REFERENCES `auth_service`.`privileges` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

CREATE INDEX auth_employee_privilege_idx ON `employee_privileges` (`employee_id`, `privilege_id`);
