-- Licensed to the Apache Software Foundation (ASF) under one or more
-- contributor license agreements.  See the NOTICE file distributed with
-- this work for additional information regarding copyright ownership.
-- The ASF licenses this file to You under the Apache License, Version 2.0
-- (the "License")
-- you may not use this file except in compliance with
-- the License.  You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

------------------------------------------------------------------
-- DataNucleus SchemaTool (ran at 08/04/2014 15:10:15)
------------------------------------------------------------------
-- Complete schema required for the following classes:-
--     org.apache.hadoop.hive.metastore.model.MColumnDescriptor
--     org.apache.hadoop.hive.metastore.model.MDBPrivilege
--     org.apache.hadoop.hive.metastore.model.MDatabase
--     org.apache.hadoop.hive.metastore.model.MDelegationToken
--     org.apache.hadoop.hive.metastore.model.MFieldSchema
--     org.apache.hadoop.hive.metastore.model.MFunction
--     org.apache.hadoop.hive.metastore.model.MGlobalPrivilege
--     org.apache.hadoop.hive.metastore.model.MIndex
--     org.apache.hadoop.hive.metastore.model.MMasterKey
--     org.apache.hadoop.hive.metastore.model.MOrder
--     org.apache.hadoop.hive.metastore.model.MPartition
--     org.apache.hadoop.hive.metastore.model.MPartitionColumnPrivilege
--     org.apache.hadoop.hive.metastore.model.MPartitionColumnStatistics
--     org.apache.hadoop.hive.metastore.model.MPartitionEvent
--     org.apache.hadoop.hive.metastore.model.MPartitionPrivilege
--     org.apache.hadoop.hive.metastore.model.MResourceUri
--     org.apache.hadoop.hive.metastore.model.MRole
--     org.apache.hadoop.hive.metastore.model.MRoleMap
--     org.apache.hadoop.hive.metastore.model.MSerDeInfo
--     org.apache.hadoop.hive.metastore.model.MStorageDescriptor
--     org.apache.hadoop.hive.metastore.model.MStringList
--     org.apache.hadoop.hive.metastore.model.MTable
--     org.apache.hadoop.hive.metastore.model.MTableColumnPrivilege
--     org.apache.hadoop.hive.metastore.model.MTableColumnStatistics
--     org.apache.hadoop.hive.metastore.model.MTablePrivilege
--     org.apache.hadoop.hive.metastore.model.MType
--     org.apache.hadoop.hive.metastore.model.MVersionTable
--
-- Table MASTER_KEYS for classes [org.apache.hadoop.hive.metastore.model.MMasterKey]
SET quoted_identifier on
GO

USE "master"
GO

CREATE TABLE MASTER_KEYS
(
    KEY_ID int NOT NULL,
    MASTER_KEY nvarchar(767) NULL
)
GO

ALTER TABLE MASTER_KEYS ADD CONSTRAINT MASTER_KEYS_PK PRIMARY KEY (KEY_ID)
GO

-- Table IDXS for classes [org.apache.hadoop.hive.metastore.model.MIndex]
CREATE TABLE IDXS
(
    INDEX_ID bigint NOT NULL,
    CREATE_TIME int NOT NULL,
    DEFERRED_REBUILD bit NOT NULL,
    INDEX_HANDLER_CLASS nvarchar(4000) NULL,
    INDEX_NAME nvarchar(128) NULL,
    INDEX_TBL_ID bigint NULL,
    LAST_ACCESS_TIME int NOT NULL,
    ORIG_TBL_ID bigint NULL,
    SD_ID bigint NULL
)
GO

ALTER TABLE IDXS ADD CONSTRAINT IDXS_PK PRIMARY KEY (INDEX_ID)
GO

-- Table PART_COL_STATS for classes [org.apache.hadoop.hive.metastore.model.MPartitionColumnStatistics]
CREATE TABLE PART_COL_STATS
(
    CS_ID bigint NOT NULL,
    AVG_COL_LEN float NULL,
    "COLUMN_NAME" nvarchar(767) NOT NULL,
    COLUMN_TYPE nvarchar(128) NOT NULL,
    DB_NAME nvarchar(128) NOT NULL,
    BIG_DECIMAL_HIGH_VALUE nvarchar(255) NULL,
    BIG_DECIMAL_LOW_VALUE nvarchar(255) NULL,
    DOUBLE_HIGH_VALUE float NULL,
    DOUBLE_LOW_VALUE float NULL,
    LAST_ANALYZED bigint NOT NULL,
    LONG_HIGH_VALUE bigint NULL,
    LONG_LOW_VALUE bigint NULL,
    MAX_COL_LEN bigint NULL,
    NUM_DISTINCTS bigint NULL,
    NUM_FALSES bigint NULL,
    NUM_NULLS bigint NOT NULL,
    NUM_TRUES bigint NULL,
    PART_ID bigint NULL,
    PARTITION_NAME nvarchar(767) NOT NULL,
    "TABLE_NAME" nvarchar(256) NOT NULL
)
GO

ALTER TABLE PART_COL_STATS ADD CONSTRAINT PART_COL_STATS_PK PRIMARY KEY (CS_ID)
GO

CREATE INDEX PCS_STATS_IDX ON PART_COL_STATS (DB_NAME,TABLE_NAME,COLUMN_NAME,PARTITION_NAME)
GO

-- Table PART_PRIVS for classes [org.apache.hadoop.hive.metastore.model.MPartitionPrivilege]
CREATE TABLE PART_PRIVS
(
    PART_GRANT_ID bigint NOT NULL,
    CREATE_TIME int NOT NULL,
    GRANT_OPTION smallint NOT NULL CHECK (GRANT_OPTION IN (0,1)),
    GRANTOR nvarchar(128) NULL,
    GRANTOR_TYPE nvarchar(128) NULL,
    PART_ID bigint NULL,
    PRINCIPAL_NAME nvarchar(128) NULL,
    PRINCIPAL_TYPE nvarchar(128) NULL,
    PART_PRIV nvarchar(128) NULL
)
GO

ALTER TABLE PART_PRIVS ADD CONSTRAINT PART_PRIVS_PK PRIMARY KEY (PART_GRANT_ID)
GO

-- Table SKEWED_STRING_LIST for classes [org.apache.hadoop.hive.metastore.model.MStringList]
CREATE TABLE SKEWED_STRING_LIST
(
    STRING_LIST_ID bigint NOT NULL
)
GO

ALTER TABLE SKEWED_STRING_LIST ADD CONSTRAINT SKEWED_STRING_LIST_PK PRIMARY KEY (STRING_LIST_ID)
GO

-- Table ROLES for classes [org.apache.hadoop.hive.metastore.model.MRole]
CREATE TABLE ROLES
(
    ROLE_ID bigint NOT NULL,
    CREATE_TIME int NOT NULL,
    OWNER_NAME nvarchar(128) NULL,
    ROLE_NAME nvarchar(128) NULL
)
GO

ALTER TABLE ROLES ADD CONSTRAINT ROLES_PK PRIMARY KEY (ROLE_ID)
GO

-- Table PARTITIONS for classes [org.apache.hadoop.hive.metastore.model.MPartition]
CREATE TABLE PARTITIONS
(
    PART_ID bigint NOT NULL,
    CREATE_TIME int NOT NULL,
    LAST_ACCESS_TIME int NOT NULL,
    PART_NAME nvarchar(767) NULL,
    SD_ID bigint NULL,
    TBL_ID bigint NULL
)
GO

ALTER TABLE PARTITIONS ADD CONSTRAINT PARTITIONS_PK PRIMARY KEY (PART_ID)
GO

-- Table CDS for classes [org.apache.hadoop.hive.metastore.model.MColumnDescriptor]
CREATE TABLE CDS
(
    CD_ID bigint NOT NULL
)
GO

ALTER TABLE CDS ADD CONSTRAINT CDS_PK PRIMARY KEY (CD_ID)
GO

-- Table VERSION for classes [org.apache.hadoop.hive.metastore.model.MVersionTable]
CREATE TABLE VERSION
(
    VER_ID bigint NOT NULL,
    SCHEMA_VERSION nvarchar(127) NOT NULL,
    VERSION_COMMENT nvarchar(255) NOT NULL
)
GO

ALTER TABLE VERSION ADD CONSTRAINT VERSION_PK PRIMARY KEY (VER_ID)
GO

-- Table GLOBAL_PRIVS for classes [org.apache.hadoop.hive.metastore.model.MGlobalPrivilege]
CREATE TABLE GLOBAL_PRIVS
(
    USER_GRANT_ID bigint NOT NULL,
    CREATE_TIME int NOT NULL,
    GRANT_OPTION smallint NOT NULL CHECK (GRANT_OPTION IN (0,1)),
    GRANTOR nvarchar(128) NULL,
    GRANTOR_TYPE nvarchar(128) NULL,
    PRINCIPAL_NAME nvarchar(128) NULL,
    PRINCIPAL_TYPE nvarchar(128) NULL,
    USER_PRIV nvarchar(128) NULL
)
GO

ALTER TABLE GLOBAL_PRIVS ADD CONSTRAINT GLOBAL_PRIVS_PK PRIMARY KEY (USER_GRANT_ID)
GO

-- Table PART_COL_PRIVS for classes [org.apache.hadoop.hive.metastore.model.MPartitionColumnPrivilege]
CREATE TABLE PART_COL_PRIVS
(
    PART_COLUMN_GRANT_ID bigint NOT NULL,
    "COLUMN_NAME" nvarchar(767) NULL,
    CREATE_TIME int NOT NULL,
    GRANT_OPTION smallint NOT NULL CHECK (GRANT_OPTION IN (0,1)),
    GRANTOR nvarchar(128) NULL,
    GRANTOR_TYPE nvarchar(128) NULL,
    PART_ID bigint NULL,
    PRINCIPAL_NAME nvarchar(128) NULL,
    PRINCIPAL_TYPE nvarchar(128) NULL,
    PART_COL_PRIV nvarchar(128) NULL
)
GO

ALTER TABLE PART_COL_PRIVS ADD CONSTRAINT PART_COL_PRIVS_PK PRIMARY KEY (PART_COLUMN_GRANT_ID)
GO

-- Table DB_PRIVS for classes [org.apache.hadoop.hive.metastore.model.MDBPrivilege]
CREATE TABLE DB_PRIVS
(
    DB_GRANT_ID bigint NOT NULL,
    CREATE_TIME int NOT NULL,
    DB_ID bigint NULL,
    GRANT_OPTION smallint NOT NULL CHECK (GRANT_OPTION IN (0,1)),
    GRANTOR nvarchar(128) NULL,
    GRANTOR_TYPE nvarchar(128) NULL,
    PRINCIPAL_NAME nvarchar(128) NULL,
    PRINCIPAL_TYPE nvarchar(128) NULL,
    DB_PRIV nvarchar(128) NULL
)
GO

ALTER TABLE DB_PRIVS ADD CONSTRAINT DB_PRIVS_PK PRIMARY KEY (DB_GRANT_ID)
GO

-- Table TAB_COL_STATS for classes [org.apache.hadoop.hive.metastore.model.MTableColumnStatistics]
CREATE TABLE TAB_COL_STATS
(
    CS_ID bigint NOT NULL,
    AVG_COL_LEN float NULL,
    "COLUMN_NAME" nvarchar(767) NOT NULL,
    COLUMN_TYPE nvarchar(128) NOT NULL,
    DB_NAME nvarchar(128) NOT NULL,
    BIG_DECIMAL_HIGH_VALUE nvarchar(255) NULL,
    BIG_DECIMAL_LOW_VALUE nvarchar(255) NULL,
    DOUBLE_HIGH_VALUE float NULL,
    DOUBLE_LOW_VALUE float NULL,
    LAST_ANALYZED bigint NOT NULL,
    LONG_HIGH_VALUE bigint NULL,
    LONG_LOW_VALUE bigint NULL,
    MAX_COL_LEN bigint NULL,
    NUM_DISTINCTS bigint NULL,
    NUM_FALSES bigint NULL,
    NUM_NULLS bigint NOT NULL,
    NUM_TRUES bigint NULL,
    TBL_ID bigint NULL,
    "TABLE_NAME" nvarchar(256) NOT NULL
)
GO

ALTER TABLE TAB_COL_STATS ADD CONSTRAINT TAB_COL_STATS_PK PRIMARY KEY (CS_ID)
GO

-- Table TYPES for classes [org.apache.hadoop.hive.metastore.model.MType]
CREATE TABLE TYPES
(
    TYPES_ID bigint NOT NULL,
    TYPE_NAME nvarchar(128) NULL,
    TYPE1 nvarchar(767) NULL,
    TYPE2 nvarchar(767) NULL
)
GO

ALTER TABLE TYPES ADD CONSTRAINT TYPES_PK PRIMARY KEY (TYPES_ID)
GO

-- Table TBL_PRIVS for classes [org.apache.hadoop.hive.metastore.model.MTablePrivilege]
CREATE TABLE TBL_PRIVS
(
    TBL_GRANT_ID bigint NOT NULL,
    CREATE_TIME int NOT NULL,
    GRANT_OPTION smallint NOT NULL CHECK (GRANT_OPTION IN (0,1)),
    GRANTOR nvarchar(128) NULL,
    GRANTOR_TYPE nvarchar(128) NULL,
    PRINCIPAL_NAME nvarchar(128) NULL,
    PRINCIPAL_TYPE nvarchar(128) NULL,
    TBL_PRIV nvarchar(128) NULL,
    TBL_ID bigint NULL
)
GO

ALTER TABLE TBL_PRIVS ADD CONSTRAINT TBL_PRIVS_PK PRIMARY KEY (TBL_GRANT_ID)
GO

-- Table DBS for classes [org.apache.hadoop.hive.metastore.model.MDatabase]
CREATE TABLE DBS
(
    DB_ID bigint NOT NULL,
    "DESC" nvarchar(4000) NULL,
    DB_LOCATION_URI nvarchar(4000) NOT NULL,
    "NAME" nvarchar(128) NULL,
    OWNER_NAME nvarchar(128) NULL,
    OWNER_TYPE nvarchar(10) NULL
)
GO

ALTER TABLE DBS ADD CONSTRAINT DBS_PK PRIMARY KEY (DB_ID)
GO

-- Table TBL_COL_PRIVS for classes [org.apache.hadoop.hive.metastore.model.MTableColumnPrivilege]
CREATE TABLE TBL_COL_PRIVS
(
    TBL_COLUMN_GRANT_ID bigint NOT NULL,
    "COLUMN_NAME" nvarchar(767) NULL,
    CREATE_TIME int NOT NULL,
    GRANT_OPTION smallint NOT NULL CHECK (GRANT_OPTION IN (0,1)),
    GRANTOR nvarchar(128) NULL,
    GRANTOR_TYPE nvarchar(128) NULL,
    PRINCIPAL_NAME nvarchar(128) NULL,
    PRINCIPAL_TYPE nvarchar(128) NULL,
    TBL_COL_PRIV nvarchar(128) NULL,
    TBL_ID bigint NULL
)
GO

ALTER TABLE TBL_COL_PRIVS ADD CONSTRAINT TBL_COL_PRIVS_PK PRIMARY KEY (TBL_COLUMN_GRANT_ID)
GO

-- Table DELEGATION_TOKENS for classes [org.apache.hadoop.hive.metastore.model.MDelegationToken]
CREATE TABLE DELEGATION_TOKENS
(
    TOKEN_IDENT nvarchar(767) NOT NULL,
    TOKEN nvarchar(767) NULL
)
GO

ALTER TABLE DELEGATION_TOKENS ADD CONSTRAINT DELEGATION_TOKENS_PK PRIMARY KEY (TOKEN_IDENT)
GO

-- Table SERDES for classes [org.apache.hadoop.hive.metastore.model.MSerDeInfo]
CREATE TABLE SERDES
(
    SERDE_ID bigint NOT NULL,
    "NAME" nvarchar(128) NULL,
    SLIB nvarchar(4000) NULL
)
GO

ALTER TABLE SERDES ADD CONSTRAINT SERDES_PK PRIMARY KEY (SERDE_ID)
GO

-- Table FUNCS for classes [org.apache.hadoop.hive.metastore.model.MFunction]
CREATE TABLE FUNCS
(
    FUNC_ID bigint NOT NULL,
    CLASS_NAME nvarchar(4000) NULL,
    CREATE_TIME int NOT NULL,
    DB_ID bigint NULL,
    FUNC_NAME nvarchar(128) NULL,
    FUNC_TYPE int NOT NULL,
    OWNER_NAME nvarchar(128) NULL,
    OWNER_TYPE nvarchar(10) NULL
)
GO

ALTER TABLE FUNCS ADD CONSTRAINT FUNCS_PK PRIMARY KEY (FUNC_ID)
GO

-- Table ROLE_MAP for classes [org.apache.hadoop.hive.metastore.model.MRoleMap]
CREATE TABLE ROLE_MAP
(
    ROLE_GRANT_ID bigint NOT NULL,
    ADD_TIME int NOT NULL,
    GRANT_OPTION smallint NOT NULL CHECK (GRANT_OPTION IN (0,1)),
    GRANTOR nvarchar(128) NULL,
    GRANTOR_TYPE nvarchar(128) NULL,
    PRINCIPAL_NAME nvarchar(128) NULL,
    PRINCIPAL_TYPE nvarchar(128) NULL,
    ROLE_ID bigint NULL
)
GO

ALTER TABLE ROLE_MAP ADD CONSTRAINT ROLE_MAP_PK PRIMARY KEY (ROLE_GRANT_ID)
GO

-- Table TBLS for classes [org.apache.hadoop.hive.metastore.model.MTable]
CREATE TABLE TBLS
(
    TBL_ID bigint NOT NULL,
    CREATE_TIME int NOT NULL,
    DB_ID bigint NULL,
    LAST_ACCESS_TIME int NOT NULL,
    OWNER nvarchar(767) NULL,
    RETENTION int NOT NULL,
    SD_ID bigint NULL,
    TBL_NAME nvarchar(256) NULL,
    TBL_TYPE nvarchar(128) NULL,
    VIEW_EXPANDED_TEXT text NULL,
    VIEW_ORIGINAL_TEXT text NULL
)
GO

ALTER TABLE TBLS ADD CONSTRAINT TBLS_PK PRIMARY KEY (TBL_ID)
GO

-- Table SDS for classes [org.apache.hadoop.hive.metastore.model.MStorageDescriptor]
CREATE TABLE SDS
(
    SD_ID bigint NOT NULL,
    CD_ID bigint NULL,
    INPUT_FORMAT nvarchar(4000) NULL,
    IS_COMPRESSED bit NOT NULL,
    IS_STOREDASSUBDIRECTORIES bit NOT NULL,
    LOCATION nvarchar(4000) NULL,
    NUM_BUCKETS int NOT NULL,
    OUTPUT_FORMAT nvarchar(4000) NULL,
    SERDE_ID bigint NULL
)
GO

ALTER TABLE SDS ADD CONSTRAINT SDS_PK PRIMARY KEY (SD_ID)
GO

-- Table PARTITION_EVENTS for classes [org.apache.hadoop.hive.metastore.model.MPartitionEvent]
CREATE TABLE PARTITION_EVENTS
(
    PART_NAME_ID bigint NOT NULL,
    DB_NAME nvarchar(128) NULL,
    EVENT_TIME bigint NOT NULL,
    EVENT_TYPE int NOT NULL,
    PARTITION_NAME nvarchar(767) NULL,
    TBL_NAME nvarchar(256) NULL
)
GO

ALTER TABLE PARTITION_EVENTS ADD CONSTRAINT PARTITION_EVENTS_PK PRIMARY KEY (PART_NAME_ID)
GO

-- Table SORT_COLS for join relationship
CREATE TABLE SORT_COLS
(
    SD_ID bigint NOT NULL,
    "COLUMN_NAME" nvarchar(767) NULL,
    "ORDER" int NOT NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE SORT_COLS ADD CONSTRAINT SORT_COLS_PK PRIMARY KEY (SD_ID,INTEGER_IDX)
GO

-- Table SKEWED_COL_NAMES for join relationship
CREATE TABLE SKEWED_COL_NAMES
(
    SD_ID bigint NOT NULL,
    SKEWED_COL_NAME nvarchar(255) NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE SKEWED_COL_NAMES ADD CONSTRAINT SKEWED_COL_NAMES_PK PRIMARY KEY (SD_ID,INTEGER_IDX)
GO

-- Table SKEWED_COL_VALUE_LOC_MAP for join relationship
CREATE TABLE SKEWED_COL_VALUE_LOC_MAP
(
    SD_ID bigint NOT NULL,
    STRING_LIST_ID_KID bigint NOT NULL,
    LOCATION nvarchar(4000) NULL
)
GO

ALTER TABLE SKEWED_COL_VALUE_LOC_MAP ADD CONSTRAINT SKEWED_COL_VALUE_LOC_MAP_PK PRIMARY KEY (SD_ID,STRING_LIST_ID_KID)
GO

-- Table SKEWED_STRING_LIST_VALUES for join relationship
CREATE TABLE SKEWED_STRING_LIST_VALUES
(
    STRING_LIST_ID bigint NOT NULL,
    STRING_LIST_VALUE nvarchar(255) NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE SKEWED_STRING_LIST_VALUES ADD CONSTRAINT SKEWED_STRING_LIST_VALUES_PK PRIMARY KEY (STRING_LIST_ID,INTEGER_IDX)
GO

-- Table PARTITION_KEY_VALS for join relationship
CREATE TABLE PARTITION_KEY_VALS
(
    PART_ID bigint NOT NULL,
    PART_KEY_VAL nvarchar(255) NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE PARTITION_KEY_VALS ADD CONSTRAINT PARTITION_KEY_VALS_PK PRIMARY KEY (PART_ID,INTEGER_IDX)
GO

-- Table PARTITION_KEYS for join relationship
CREATE TABLE PARTITION_KEYS
(
    TBL_ID bigint NOT NULL,
    PKEY_COMMENT nvarchar(4000) NULL,
    PKEY_NAME nvarchar(128) NOT NULL,
    PKEY_TYPE nvarchar(767) NOT NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE PARTITION_KEYS ADD CONSTRAINT PARTITION_KEY_PK PRIMARY KEY (TBL_ID,PKEY_NAME)
GO

-- Table SKEWED_VALUES for join relationship
CREATE TABLE SKEWED_VALUES
(
    SD_ID_OID bigint NOT NULL,
    STRING_LIST_ID_EID bigint NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE SKEWED_VALUES ADD CONSTRAINT SKEWED_VALUES_PK PRIMARY KEY (SD_ID_OID,INTEGER_IDX)
GO

-- Table SD_PARAMS for join relationship
CREATE TABLE SD_PARAMS
(
    SD_ID bigint NOT NULL,
    PARAM_KEY nvarchar(256) NOT NULL,
    PARAM_VALUE varchar(max) NULL
)
GO

ALTER TABLE SD_PARAMS ADD CONSTRAINT SD_PARAMS_PK PRIMARY KEY (SD_ID,PARAM_KEY)
GO

-- Table FUNC_RU for join relationship
CREATE TABLE FUNC_RU
(
    FUNC_ID bigint NOT NULL,
    RESOURCE_TYPE int NOT NULL,
    RESOURCE_URI nvarchar(4000) NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE FUNC_RU ADD CONSTRAINT FUNC_RU_PK PRIMARY KEY (FUNC_ID,INTEGER_IDX)
GO

-- Table TYPE_FIELDS for join relationship
CREATE TABLE TYPE_FIELDS
(
    TYPE_NAME bigint NOT NULL,
    COMMENT nvarchar(256) NULL,
    FIELD_NAME nvarchar(128) NOT NULL,
    FIELD_TYPE nvarchar(767) NOT NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE TYPE_FIELDS ADD CONSTRAINT TYPE_FIELDS_PK PRIMARY KEY (TYPE_NAME,FIELD_NAME)
GO

-- Table BUCKETING_COLS for join relationship
CREATE TABLE BUCKETING_COLS
(
    SD_ID bigint NOT NULL,
    BUCKET_COL_NAME nvarchar(255) NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE BUCKETING_COLS ADD CONSTRAINT BUCKETING_COLS_PK PRIMARY KEY (SD_ID,INTEGER_IDX)
GO

-- Table DATABASE_PARAMS for join relationship
CREATE TABLE DATABASE_PARAMS
(
    DB_ID bigint NOT NULL,
    PARAM_KEY nvarchar(180) NOT NULL,
    PARAM_VALUE nvarchar(4000) NULL
)
GO

ALTER TABLE DATABASE_PARAMS ADD CONSTRAINT DATABASE_PARAMS_PK PRIMARY KEY (DB_ID,PARAM_KEY)
GO

-- Table INDEX_PARAMS for join relationship
CREATE TABLE INDEX_PARAMS
(
    INDEX_ID bigint NOT NULL,
    PARAM_KEY nvarchar(256) NOT NULL,
    PARAM_VALUE nvarchar(4000) NULL
)
GO

ALTER TABLE INDEX_PARAMS ADD CONSTRAINT INDEX_PARAMS_PK PRIMARY KEY (INDEX_ID,PARAM_KEY)
GO

-- Table COLUMNS_V2 for join relationship
CREATE TABLE COLUMNS_V2
(
    CD_ID bigint NOT NULL,
    COMMENT nvarchar(256) NULL,
    "COLUMN_NAME" nvarchar(767) NOT NULL,
    TYPE_NAME varchar(max) NOT NULL,
    INTEGER_IDX int NOT NULL
)
GO

ALTER TABLE COLUMNS_V2 ADD CONSTRAINT COLUMNS_PK PRIMARY KEY (CD_ID,"COLUMN_NAME")
GO

-- Table SERDE_PARAMS for join relationship
CREATE TABLE SERDE_PARAMS
(
    SERDE_ID bigint NOT NULL,
    PARAM_KEY nvarchar(256) NOT NULL,
    PARAM_VALUE varchar(max) NULL
)
GO

ALTER TABLE SERDE_PARAMS ADD CONSTRAINT SERDE_PARAMS_PK PRIMARY KEY (SERDE_ID,PARAM_KEY)
GO

-- Table PARTITION_PARAMS for join relationship
CREATE TABLE PARTITION_PARAMS
(
    PART_ID bigint NOT NULL,
    PARAM_KEY nvarchar(256) NOT NULL,
    PARAM_VALUE nvarchar(4000) NULL
)
GO

ALTER TABLE PARTITION_PARAMS ADD CONSTRAINT PARTITION_PARAMS_PK PRIMARY KEY (PART_ID,PARAM_KEY)
GO

-- Table TABLE_PARAMS for join relationship
CREATE TABLE TABLE_PARAMS
(
    TBL_ID bigint NOT NULL,
    PARAM_KEY nvarchar(256) NOT NULL,
    PARAM_VALUE varchar(max) NULL
)
GO

ALTER TABLE TABLE_PARAMS ADD CONSTRAINT TABLE_PARAMS_PK PRIMARY KEY (TBL_ID,PARAM_KEY)
GO

CREATE TABLE NOTIFICATION_LOG
(
    NL_ID bigint NOT NULL,
    EVENT_ID bigint NOT NULL,
    EVENT_TIME int NOT NULL,
    EVENT_TYPE nvarchar(32) NOT NULL,
    DB_NAME nvarchar(128) NULL,
    TBL_NAME nvarchar(256) NULL,
    MESSAGE_FORMAT nvarchar(16),
    MESSAGE text NULL
)
GO

ALTER TABLE NOTIFICATION_LOG ADD CONSTRAINT NOTIFICATION_LOG_PK PRIMARY KEY (NL_ID)
GO

CREATE TABLE NOTIFICATION_SEQUENCE
(
    NNI_ID bigint NOT NULL,
    NEXT_EVENT_ID bigint NOT NULL
)
GO

ALTER TABLE NOTIFICATION_SEQUENCE ADD CONSTRAINT NOTIFICATION_SEQUENCE_PK PRIMARY KEY (NNI_ID)
GO

-- Constraints for table MASTER_KEYS for class(es) [org.apache.hadoop.hive.metastore.model.MMasterKey]

-- Constraints for table IDXS for class(es) [org.apache.hadoop.hive.metastore.model.MIndex]
ALTER TABLE IDXS ADD CONSTRAINT IDXS_FK1 FOREIGN KEY (INDEX_TBL_ID) REFERENCES TBLS (TBL_ID)
GO

ALTER TABLE IDXS ADD CONSTRAINT IDXS_FK2 FOREIGN KEY (SD_ID) REFERENCES SDS (SD_ID)
GO

ALTER TABLE IDXS ADD CONSTRAINT IDXS_FK3 FOREIGN KEY (ORIG_TBL_ID) REFERENCES TBLS (TBL_ID)
GO

CREATE UNIQUE INDEX UNIQUEINDEX ON IDXS (INDEX_NAME,ORIG_TBL_ID)
GO

CREATE INDEX IDXS_N51 ON IDXS (SD_ID)
GO

CREATE INDEX IDXS_N50 ON IDXS (ORIG_TBL_ID)
GO

CREATE INDEX IDXS_N49 ON IDXS (INDEX_TBL_ID)
GO


-- Constraints for table PART_COL_STATS for class(es) [org.apache.hadoop.hive.metastore.model.MPartitionColumnStatistics]
ALTER TABLE PART_COL_STATS ADD CONSTRAINT PART_COL_STATS_FK1 FOREIGN KEY (PART_ID) REFERENCES PARTITIONS (PART_ID)
GO

CREATE INDEX PART_COL_STATS_N49 ON PART_COL_STATS (PART_ID)
GO


-- Constraints for table PART_PRIVS for class(es) [org.apache.hadoop.hive.metastore.model.MPartitionPrivilege]
ALTER TABLE PART_PRIVS ADD CONSTRAINT PART_PRIVS_FK1 FOREIGN KEY (PART_ID) REFERENCES PARTITIONS (PART_ID)
GO

CREATE INDEX PARTPRIVILEGEINDEX ON PART_PRIVS (PART_ID,PRINCIPAL_NAME,PRINCIPAL_TYPE,PART_PRIV,GRANTOR,GRANTOR_TYPE)
GO

CREATE INDEX PART_PRIVS_N49 ON PART_PRIVS (PART_ID)
GO


-- Constraints for table SKEWED_STRING_LIST for class(es) [org.apache.hadoop.hive.metastore.model.MStringList]

-- Constraints for table ROLES for class(es) [org.apache.hadoop.hive.metastore.model.MRole]
CREATE UNIQUE INDEX ROLEENTITYINDEX ON ROLES (ROLE_NAME)
GO


-- Constraints for table PARTITIONS for class(es) [org.apache.hadoop.hive.metastore.model.MPartition]
ALTER TABLE PARTITIONS ADD CONSTRAINT PARTITIONS_FK1 FOREIGN KEY (TBL_ID) REFERENCES TBLS (TBL_ID)
GO

ALTER TABLE PARTITIONS ADD CONSTRAINT PARTITIONS_FK2 FOREIGN KEY (SD_ID) REFERENCES SDS (SD_ID)
GO

CREATE INDEX PARTITIONS_N49 ON PARTITIONS (SD_ID)
GO

CREATE INDEX PARTITIONS_N50 ON PARTITIONS (TBL_ID)
GO

CREATE UNIQUE INDEX UNIQUEPARTITION ON PARTITIONS (PART_NAME,TBL_ID)
GO


-- Constraints for table CDS for class(es) [org.apache.hadoop.hive.metastore.model.MColumnDescriptor]

-- Constraints for table VERSION for class(es) [org.apache.hadoop.hive.metastore.model.MVersionTable]

-- Constraints for table GLOBAL_PRIVS for class(es) [org.apache.hadoop.hive.metastore.model.MGlobalPrivilege]
CREATE UNIQUE INDEX GLOBALPRIVILEGEINDEX ON GLOBAL_PRIVS (PRINCIPAL_NAME,PRINCIPAL_TYPE,USER_PRIV,GRANTOR,GRANTOR_TYPE)
GO


-- Constraints for table PART_COL_PRIVS for class(es) [org.apache.hadoop.hive.metastore.model.MPartitionColumnPrivilege]
ALTER TABLE PART_COL_PRIVS ADD CONSTRAINT PART_COL_PRIVS_FK1 FOREIGN KEY (PART_ID) REFERENCES PARTITIONS (PART_ID)
GO

CREATE INDEX PART_COL_PRIVS_N49 ON PART_COL_PRIVS (PART_ID)
GO

CREATE INDEX PARTITIONCOLUMNPRIVILEGEINDEX ON PART_COL_PRIVS (PART_ID,"COLUMN_NAME",PRINCIPAL_NAME,PRINCIPAL_TYPE,PART_COL_PRIV,GRANTOR,GRANTOR_TYPE)
GO


-- Constraints for table DB_PRIVS for class(es) [org.apache.hadoop.hive.metastore.model.MDBPrivilege]
ALTER TABLE DB_PRIVS ADD CONSTRAINT DB_PRIVS_FK1 FOREIGN KEY (DB_ID) REFERENCES DBS (DB_ID)
GO

CREATE UNIQUE INDEX DBPRIVILEGEINDEX ON DB_PRIVS (DB_ID,PRINCIPAL_NAME,PRINCIPAL_TYPE,DB_PRIV,GRANTOR,GRANTOR_TYPE)
GO

CREATE INDEX DB_PRIVS_N49 ON DB_PRIVS (DB_ID)
GO


-- Constraints for table TAB_COL_STATS for class(es) [org.apache.hadoop.hive.metastore.model.MTableColumnStatistics]
ALTER TABLE TAB_COL_STATS ADD CONSTRAINT TAB_COL_STATS_FK1 FOREIGN KEY (TBL_ID) REFERENCES TBLS (TBL_ID)
GO

CREATE INDEX TAB_COL_STATS_N49 ON TAB_COL_STATS (TBL_ID)
GO


-- Constraints for table TYPES for class(es) [org.apache.hadoop.hive.metastore.model.MType]
CREATE UNIQUE INDEX UNIQUETYPE ON TYPES (TYPE_NAME)
GO


-- Constraints for table TBL_PRIVS for class(es) [org.apache.hadoop.hive.metastore.model.MTablePrivilege]
ALTER TABLE TBL_PRIVS ADD CONSTRAINT TBL_PRIVS_FK1 FOREIGN KEY (TBL_ID) REFERENCES TBLS (TBL_ID)
GO

CREATE INDEX TBL_PRIVS_N49 ON TBL_PRIVS (TBL_ID)
GO

CREATE INDEX TABLEPRIVILEGEINDEX ON TBL_PRIVS (TBL_ID,PRINCIPAL_NAME,PRINCIPAL_TYPE,TBL_PRIV,GRANTOR,GRANTOR_TYPE)
GO


-- Constraints for table DBS for class(es) [org.apache.hadoop.hive.metastore.model.MDatabase]
CREATE UNIQUE INDEX UNIQUEDATABASE ON DBS ("NAME")
GO


-- Constraints for table TBL_COL_PRIVS for class(es) [org.apache.hadoop.hive.metastore.model.MTableColumnPrivilege]
ALTER TABLE TBL_COL_PRIVS ADD CONSTRAINT TBL_COL_PRIVS_FK1 FOREIGN KEY (TBL_ID) REFERENCES TBLS (TBL_ID)
GO

CREATE INDEX TABLECOLUMNPRIVILEGEINDEX ON TBL_COL_PRIVS (TBL_ID,"COLUMN_NAME",PRINCIPAL_NAME,PRINCIPAL_TYPE,TBL_COL_PRIV,GRANTOR,GRANTOR_TYPE)
GO

CREATE INDEX TBL_COL_PRIVS_N49 ON TBL_COL_PRIVS (TBL_ID)
GO


-- Constraints for table DELEGATION_TOKENS for class(es) [org.apache.hadoop.hive.metastore.model.MDelegationToken]

-- Constraints for table SERDES for class(es) [org.apache.hadoop.hive.metastore.model.MSerDeInfo]

-- Constraints for table FUNCS for class(es) [org.apache.hadoop.hive.metastore.model.MFunction]
ALTER TABLE FUNCS ADD CONSTRAINT FUNCS_FK1 FOREIGN KEY (DB_ID) REFERENCES DBS (DB_ID)
GO

CREATE UNIQUE INDEX UNIQUEFUNCTION ON FUNCS (FUNC_NAME,DB_ID)
GO

CREATE INDEX FUNCS_N49 ON FUNCS (DB_ID)
GO


-- Constraints for table ROLE_MAP for class(es) [org.apache.hadoop.hive.metastore.model.MRoleMap]
ALTER TABLE ROLE_MAP ADD CONSTRAINT ROLE_MAP_FK1 FOREIGN KEY (ROLE_ID) REFERENCES ROLES (ROLE_ID)
GO

CREATE INDEX ROLE_MAP_N49 ON ROLE_MAP (ROLE_ID)
GO

CREATE UNIQUE INDEX USERROLEMAPINDEX ON ROLE_MAP (PRINCIPAL_NAME,ROLE_ID,GRANTOR,GRANTOR_TYPE)
GO


-- Constraints for table TBLS for class(es) [org.apache.hadoop.hive.metastore.model.MTable]
ALTER TABLE TBLS ADD CONSTRAINT TBLS_FK2 FOREIGN KEY (SD_ID) REFERENCES SDS (SD_ID)
GO

ALTER TABLE TBLS ADD CONSTRAINT TBLS_FK1 FOREIGN KEY (DB_ID) REFERENCES DBS (DB_ID)
GO

CREATE INDEX TBLS_N50 ON TBLS (SD_ID)
GO

CREATE UNIQUE INDEX UNIQUETABLE ON TBLS (TBL_NAME,DB_ID)
GO

CREATE INDEX TBLS_N49 ON TBLS (DB_ID)
GO


-- Constraints for table SDS for class(es) [org.apache.hadoop.hive.metastore.model.MStorageDescriptor]
ALTER TABLE SDS ADD CONSTRAINT SDS_FK1 FOREIGN KEY (SERDE_ID) REFERENCES SERDES (SERDE_ID)
GO

ALTER TABLE SDS ADD CONSTRAINT SDS_FK2 FOREIGN KEY (CD_ID) REFERENCES CDS (CD_ID)
GO

CREATE INDEX SDS_N50 ON SDS (CD_ID)
GO

CREATE INDEX SDS_N49 ON SDS (SERDE_ID)
GO


-- Constraints for table PARTITION_EVENTS for class(es) [org.apache.hadoop.hive.metastore.model.MPartitionEvent]
CREATE INDEX PARTITIONEVENTINDEX ON PARTITION_EVENTS (PARTITION_NAME)
GO


-- Constraints for table SORT_COLS
ALTER TABLE SORT_COLS ADD CONSTRAINT SORT_COLS_FK1 FOREIGN KEY (SD_ID) REFERENCES SDS (SD_ID)
GO

CREATE INDEX SORT_COLS_N49 ON SORT_COLS (SD_ID)
GO


-- Constraints for table SKEWED_COL_NAMES
ALTER TABLE SKEWED_COL_NAMES ADD CONSTRAINT SKEWED_COL_NAMES_FK1 FOREIGN KEY (SD_ID) REFERENCES SDS (SD_ID)
GO

CREATE INDEX SKEWED_COL_NAMES_N49 ON SKEWED_COL_NAMES (SD_ID)
GO


-- Constraints for table SKEWED_COL_VALUE_LOC_MAP
ALTER TABLE SKEWED_COL_VALUE_LOC_MAP ADD CONSTRAINT SKEWED_COL_VALUE_LOC_MAP_FK1 FOREIGN KEY (SD_ID) REFERENCES SDS (SD_ID)
GO

ALTER TABLE SKEWED_COL_VALUE_LOC_MAP ADD CONSTRAINT SKEWED_COL_VALUE_LOC_MAP_FK2 FOREIGN KEY (STRING_LIST_ID_KID) REFERENCES SKEWED_STRING_LIST (STRING_LIST_ID)
GO

CREATE INDEX SKEWED_COL_VALUE_LOC_MAP_N50 ON SKEWED_COL_VALUE_LOC_MAP (STRING_LIST_ID_KID)
GO

CREATE INDEX SKEWED_COL_VALUE_LOC_MAP_N49 ON SKEWED_COL_VALUE_LOC_MAP (SD_ID)
GO


-- Constraints for table SKEWED_STRING_LIST_VALUES
ALTER TABLE SKEWED_STRING_LIST_VALUES ADD CONSTRAINT SKEWED_STRING_LIST_VALUES_FK1 FOREIGN KEY (STRING_LIST_ID) REFERENCES SKEWED_STRING_LIST (STRING_LIST_ID)
GO

CREATE INDEX SKEWED_STRING_LIST_VALUES_N49 ON SKEWED_STRING_LIST_VALUES (STRING_LIST_ID)
GO


-- Constraints for table PARTITION_KEY_VALS
ALTER TABLE PARTITION_KEY_VALS ADD CONSTRAINT PARTITION_KEY_VALS_FK1 FOREIGN KEY (PART_ID) REFERENCES PARTITIONS (PART_ID)
GO

CREATE INDEX PARTITION_KEY_VALS_N49 ON PARTITION_KEY_VALS (PART_ID)
GO


-- Constraints for table PARTITION_KEYS
ALTER TABLE PARTITION_KEYS ADD CONSTRAINT PARTITION_KEYS_FK1 FOREIGN KEY (TBL_ID) REFERENCES TBLS (TBL_ID)
GO

CREATE INDEX PARTITION_KEYS_N49 ON PARTITION_KEYS (TBL_ID)
GO


-- Constraints for table SKEWED_VALUES
ALTER TABLE SKEWED_VALUES ADD CONSTRAINT SKEWED_VALUES_FK1 FOREIGN KEY (SD_ID_OID) REFERENCES SDS (SD_ID)
GO

ALTER TABLE SKEWED_VALUES ADD CONSTRAINT SKEWED_VALUES_FK2 FOREIGN KEY (STRING_LIST_ID_EID) REFERENCES SKEWED_STRING_LIST (STRING_LIST_ID)
GO

CREATE INDEX SKEWED_VALUES_N50 ON SKEWED_VALUES (SD_ID_OID)
GO

CREATE INDEX SKEWED_VALUES_N49 ON SKEWED_VALUES (STRING_LIST_ID_EID)
GO


-- Constraints for table SD_PARAMS
ALTER TABLE SD_PARAMS ADD CONSTRAINT SD_PARAMS_FK1 FOREIGN KEY (SD_ID) REFERENCES SDS (SD_ID)
GO

CREATE INDEX SD_PARAMS_N49 ON SD_PARAMS (SD_ID)
GO


-- Constraints for table FUNC_RU
ALTER TABLE FUNC_RU ADD CONSTRAINT FUNC_RU_FK1 FOREIGN KEY (FUNC_ID) REFERENCES FUNCS (FUNC_ID)
GO

CREATE INDEX FUNC_RU_N49 ON FUNC_RU (FUNC_ID)
GO


-- Constraints for table TYPE_FIELDS
ALTER TABLE TYPE_FIELDS ADD CONSTRAINT TYPE_FIELDS_FK1 FOREIGN KEY (TYPE_NAME) REFERENCES TYPES (TYPES_ID)
GO

CREATE INDEX TYPE_FIELDS_N49 ON TYPE_FIELDS (TYPE_NAME)
GO


-- Constraints for table BUCKETING_COLS
ALTER TABLE BUCKETING_COLS ADD CONSTRAINT BUCKETING_COLS_FK1 FOREIGN KEY (SD_ID) REFERENCES SDS (SD_ID)
GO

CREATE INDEX BUCKETING_COLS_N49 ON BUCKETING_COLS (SD_ID)
GO


-- Constraints for table DATABASE_PARAMS
ALTER TABLE DATABASE_PARAMS ADD CONSTRAINT DATABASE_PARAMS_FK1 FOREIGN KEY (DB_ID) REFERENCES DBS (DB_ID)
GO

CREATE INDEX DATABASE_PARAMS_N49 ON DATABASE_PARAMS (DB_ID)
GO


-- Constraints for table INDEX_PARAMS
ALTER TABLE INDEX_PARAMS ADD CONSTRAINT INDEX_PARAMS_FK1 FOREIGN KEY (INDEX_ID) REFERENCES IDXS (INDEX_ID)
GO

CREATE INDEX INDEX_PARAMS_N49 ON INDEX_PARAMS (INDEX_ID)
GO


-- Constraints for table COLUMNS_V2
ALTER TABLE COLUMNS_V2 ADD CONSTRAINT COLUMNS_V2_FK1 FOREIGN KEY (CD_ID) REFERENCES CDS (CD_ID)
GO

CREATE INDEX COLUMNS_V2_N49 ON COLUMNS_V2 (CD_ID)
GO


-- Constraints for table SERDE_PARAMS
ALTER TABLE SERDE_PARAMS ADD CONSTRAINT SERDE_PARAMS_FK1 FOREIGN KEY (SERDE_ID) REFERENCES SERDES (SERDE_ID)
GO

CREATE INDEX SERDE_PARAMS_N49 ON SERDE_PARAMS (SERDE_ID)
GO


-- Constraints for table PARTITION_PARAMS
ALTER TABLE PARTITION_PARAMS ADD CONSTRAINT PARTITION_PARAMS_FK1 FOREIGN KEY (PART_ID) REFERENCES PARTITIONS (PART_ID)
GO

CREATE INDEX PARTITION_PARAMS_N49 ON PARTITION_PARAMS (PART_ID)
GO


-- Constraints for table TABLE_PARAMS
ALTER TABLE TABLE_PARAMS ADD CONSTRAINT TABLE_PARAMS_FK1 FOREIGN KEY (TBL_ID) REFERENCES TBLS (TBL_ID)
GO

CREATE INDEX TABLE_PARAMS_N49 ON TABLE_PARAMS (TBL_ID)
GO


-- -----------------------------------------------------------------------------------------------------------------------------------------------
-- Transaction and Lock Tables
-- These are not part of package jdo, so if you are going to regenerate this file you need to manually add the following section back to the file.
-- -----------------------------------------------------------------------------------------------------------------------------------------------
CREATE TABLE COMPACTION_QUEUE(
    CQ_ID bigint NOT NULL,
    CQ_DATABASE nvarchar(128) NOT NULL,
    CQ_TABLE nvarchar(128) NOT NULL,
    CQ_PARTITION nvarchar(767) NULL,
    CQ_STATE char(1) NOT NULL,
    CQ_TYPE char(1) NOT NULL,
    CQ_TBLPROPERTIES nvarchar(2048) NULL,
    CQ_WORKER_ID nvarchar(128) NULL,
    CQ_START bigint NULL,
    CQ_RUN_AS nvarchar(128) NULL,
    CQ_HIGHEST_TXN_ID bigint NULL,
    CQ_META_INFO varbinary(2048) NULL,
    CQ_HADOOP_JOB_ID nvarchar(128) NULL,
PRIMARY KEY CLUSTERED
(
    CQ_ID ASC
)
)
GO

CREATE TABLE COMPLETED_COMPACTIONS (
    CC_ID bigint NOT NULL,
    CC_DATABASE nvarchar(128) NOT NULL,
    CC_TABLE nvarchar(128) NOT NULL,
    CC_PARTITION nvarchar(767) NULL,
    CC_STATE char(1) NOT NULL,
    CC_TYPE char(1) NOT NULL,
    CC_TBLPROPERTIES nvarchar(2048) NULL,
    CC_WORKER_ID nvarchar(128) NULL,
    CC_START bigint NULL,
    CC_END bigint NULL,
    CC_RUN_AS nvarchar(128) NULL,
    CC_HIGHEST_TXN_ID bigint NULL,
    CC_META_INFO varbinary(2048) NULL,
    CC_HADOOP_JOB_ID nvarchar(128) NULL,
PRIMARY KEY CLUSTERED
(
    CC_ID ASC
)
)
GO

CREATE TABLE COMPLETED_TXN_COMPONENTS(
    CTC_TXNID bigint NULL,
    CTC_DATABASE nvarchar(128) NOT NULL,
    CTC_TABLE nvarchar(128) NULL,
    CTC_PARTITION nvarchar(767) NULL
)
GO

CREATE TABLE HIVE_LOCKS(
    HL_LOCK_EXT_ID bigint NOT NULL,
    HL_LOCK_INT_ID bigint NOT NULL,
    HL_TXNID bigint NULL,
    HL_DB nvarchar(128) NOT NULL,
    HL_TABLE nvarchar(128) NULL,
    HL_PARTITION nvarchar(767) NULL,
    HL_LOCK_STATE char(1) NOT NULL,
    HL_LOCK_TYPE char(1) NOT NULL,
    HL_LAST_HEARTBEAT bigint NOT NULL,
    HL_ACQUIRED_AT bigint NULL,
    HL_USER nvarchar(128) NOT NULL,
    HL_HOST nvarchar(128) NOT NULL,
    HL_HEARTBEAT_COUNT int NULL,
    HL_AGENT_INFO nvarchar(128) NULL,
    HL_BLOCKEDBY_EXT_ID bigint NULL,
    HL_BLOCKEDBY_INT_ID bigint NULL,
PRIMARY KEY CLUSTERED
(
    HL_LOCK_EXT_ID ASC,
    HL_LOCK_INT_ID ASC
)
)
GO

CREATE TABLE NEXT_COMPACTION_QUEUE_ID(
    NCQ_NEXT bigint NOT NULL
)
GO

INSERT INTO NEXT_COMPACTION_QUEUE_ID VALUES(1)
GO

CREATE TABLE NEXT_LOCK_ID(
    NL_NEXT bigint NOT NULL
)
GO

INSERT INTO NEXT_LOCK_ID VALUES(1)
GO

CREATE TABLE NEXT_TXN_ID(
    NTXN_NEXT bigint NOT NULL
)
GO

INSERT INTO NEXT_TXN_ID VALUES(1)
GO

CREATE TABLE TXNS(
    TXN_ID bigint NOT NULL,
    TXN_STATE char(1) NOT NULL,
    TXN_STARTED bigint NOT NULL,
    TXN_LAST_HEARTBEAT bigint NOT NULL,
    TXN_USER nvarchar(128) NOT NULL,
    TXN_HOST nvarchar(128) NOT NULL,
    TXN_AGENT_INFO nvarchar(128) NULL,
    TXN_META_INFO nvarchar(128) NULL,
    TXN_HEARTBEAT_COUNT int NULL,
PRIMARY KEY CLUSTERED
(
    TXN_ID ASC
)
)
GO

CREATE TABLE TXN_COMPONENTS(
    TC_TXNID bigint NULL,
    TC_DATABASE nvarchar(128) NOT NULL,
    TC_TABLE nvarchar(128) NULL,
    TC_PARTITION nvarchar(767) NULL,
    TC_OPERATION_TYPE char(1) NOT NULL
)
GO

ALTER TABLE TXN_COMPONENTS  WITH CHECK ADD FOREIGN KEY(TC_TXNID) REFERENCES TXNS (TXN_ID)
GO

CREATE INDEX TC_TXNID_INDEX ON TXN_COMPONENTS (TC_TXNID)
GO

CREATE TABLE AUX_TABLE (
  MT_KEY1 nvarchar(128) NOT NULL,
  MT_KEY2 bigint NOT NULL,
  MT_COMMENT nvarchar(255) NULL,
  PRIMARY KEY CLUSTERED
(
    MT_KEY1 ASC,
    MT_KEY2 ASC
)
)
GO

CREATE TABLE KEY_CONSTRAINTS
(
  CHILD_CD_ID BIGINT,
  CHILD_INTEGER_IDX INT,
  CHILD_TBL_ID BIGINT,
  PARENT_CD_ID BIGINT NOT NULL,
  PARENT_INTEGER_IDX INT NOT NULL,
  PARENT_TBL_ID BIGINT NOT NULL,
  POSITION INT NOT NULL,
  CONSTRAINT_NAME VARCHAR(400) NOT NULL,
  CONSTRAINT_TYPE SMALLINT NOT NULL,
  UPDATE_RULE SMALLINT,
  DELETE_RULE SMALLINT,
  ENABLE_VALIDATE_RELY SMALLINT NOT NULL
)
GO

ALTER TABLE KEY_CONSTRAINTS ADD CONSTRAINT CONSTRAINTS_PK PRIMARY KEY (CONSTRAINT_NAME, POSITION)
GO

CREATE INDEX CONSTRAINTS_PARENT_TBL_ID__INDEX ON KEY_CONSTRAINTS(PARENT_TBL_ID)
GO

CREATE TABLE WRITE_SET (
  WS_DATABASE nvarchar(128) NOT NULL,
  WS_TABLE nvarchar(128) NOT NULL,
  WS_PARTITION nvarchar(767),
  WS_TXNID bigint NOT NULL,
  WS_COMMIT_ID bigint NOT NULL,
  WS_OPERATION_TYPE char(1) NOT NULL
)
GO


-- -----------------------------------------------------------------
-- Record schema version. Should be the last step in the init script
-- -----------------------------------------------------------------
INSERT INTO VERSION (VER_ID, SCHEMA_VERSION, VERSION_COMMENT) VALUES (1, '2.3.0', 'Hive release version 2.3.0')
GO

INSERT INTO DBS VALUES (1,'Default Hive database','file:/shared_data/hive/warehouse','default','public','ROLE'),(2,'','file:/shared_data/hive/warehouse/tpcds.db','tpcds',NULL,'USER'),(8,NULL,'file:/shared_data/hive/warehouse/employees.db','employees','root','USER'),(9,NULL,'file:/shared_data/hive/warehouse/app.db','app','root','USER'),(10,NULL,'file:/shared_data/hive/warehouse/complex.db','complex','root','USER')
GO

INSERT INTO CDS VALUES (1),(6),(11),(12),(13),(14),(15),(16)
GO

INSERT INTO SERDES VALUES (1,NULL,'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'),(6,NULL,'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'),(11,NULL,'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'),(12,NULL,NULL),(13,NULL,'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'),(14,NULL,'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'),(15,NULL,'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'),(16,NULL,'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe')
GO

INSERT INTO SDS VALUES (1,1,'org.apache.hadoop.mapred.TextInputFormat',0,0,'file:/shared_data/table_data/tpcds/customer',-1,'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',1),(6,6,'org.apache.hadoop.mapred.TextInputFormat',0,0,'file:/shared_data/hive/warehouse/table_tab1',-1,'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',6),(11,11,'org.apache.hadoop.mapred.TextInputFormat',0,0,'file:/shared_data/hive/warehouse/employees.db/employee',-1,'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',11),(12,12,'org.apache.hadoop.mapred.SequenceFileInputFormat',0,0,NULL,-1,'org.apache.hadoop.hive.ql.io.HiveSequenceFileOutputFormat',12),(13,13,'org.apache.hadoop.mapred.TextInputFormat',0,0,'file:/shared_data/hive/warehouse/app.db/log_messages',-1,'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',13),(14,14,'org.apache.hadoop.mapred.TextInputFormat',0,0,'file:/shared_data/table_data/tpcds/customer',-1,'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',14),(15,15,'org.apache.hadoop.mapred.TextInputFormat',0,0,'file:/shared_data/hive/warehouse/app.db/orders',-1,'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',15),(16,16,'org.apache.hadoop.mapred.TextInputFormat',0,0,'file:/shared_data/hive/warehouse/complex.db/complextest',-1,'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',16)
GO

INSERT INTO TBLS VALUES (1,1598384969,2,0,'root',0,1,'customer','EXTERNAL_TABLE',NULL,NULL),(6,1598385675,1,0,'root',0,6,'table_tab1','MANAGED_TABLE',NULL,NULL),(11,1598736516,8,0,'root',0,11,'employee','MANAGED_TABLE',NULL,NULL),(12,1598736550,8,0,'root',0,12,'employees_high_salary','VIRTUAL_VIEW','SELECT "employee"."eid", "employee"."name", "employee"."salary", "employee"."destination" FROM "employees"."employee"\nWHERE "employee"."salary">30000','SELECT * FROM employees.employee\nWHERE salary>30000'),(13,1598736607,9,0,'root',0,13,'log_messages','EXTERNAL_TABLE',NULL,NULL),(14,1598736646,9,0,'root',0,14,'customer','MANAGED_TABLE',NULL,NULL),(15,1598736744,9,0,'root',0,15,'orders','MANAGED_TABLE',NULL,NULL),(16,1598736796,10,0,'root',0,16,'complextest','MANAGED_TABLE',NULL,NULL);
GO

INSERT INTO TABLE_PARAMS VALUES (1,'COLUMN_STATS_ACCURATE','false'),(1,'EXTERNAL','TRUE'),(1,'numFiles','0'),(1,'numRows','-1'),(1,'rawDataSize','-1'),(1,'spark.sql.create.version','2.4.5'),(1,'spark.sql.sources.schema.numParts','1'),(1,'spark.sql.sources.schema.part.0','{\"type\":\"struct\",\"fields\":[{\"name\":\"c_customer_sk\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_customer_id\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_current_cdemo_sk\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_current_hdemo_sk\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_current_addr_sk\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_first_shipto_date_sk\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_first_sales_date_sk\",\"type\":\"long\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_salutation\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_first_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_last_name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_preferred_cust_flag\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_birth_day\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_birth_month\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_birth_year\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_birth_country\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_login\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_email_address\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"c_last_review_date\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]}'),(1,'totalSize','0'),(1,'transient_lastDdlTime','1598384969'),(6,'spark.sql.create.version','2.4.5'),(6,'spark.sql.sources.schema.numPartCols','1'),(6,'spark.sql.sources.schema.numParts','1'),(6,'spark.sql.sources.schema.part.0','{\"type\":\"struct\",\"fields\":[{\"name\":\"id\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"name\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"dept\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}},{\"name\":\"yoj\",\"type\":\"integer\",\"nullable\":true,\"metadata\":{}},{\"name\":\"year\",\"type\":\"string\",\"nullable\":true,\"metadata\":{}}]}'),(6,'spark.sql.sources.schema.partCol.0','year'),(6,'transient_lastDdlTime','1598385675'),(11,'comment','Details about the employees'),(11,'transient_lastDdlTime','1598736516'),(12,'transient_lastDdlTime','1598736550'),(13,'EXTERNAL','TRUE'),(13,'transient_lastDdlTime','1598736607'),(14,'COLUMN_STATS_ACCURATE','false'),(14,'numFiles','0'),(14,'numRows','-1'),(14,'rawDataSize','-1'),(14,'totalSize','0'),(14,'transient_lastDdlTime','1598736646'),(15,'transient_lastDdlTime','1598736744'),(16,'transient_lastDdlTime','1598736796')
GO

INSERT INTO PARTITION_KEYS VALUES (6,NULL,'year','string',0),(13,NULL,'day','int',2),(13,NULL,'month','int',1),(13,NULL,'year','int',0),(15,NULL,'order_date','date',0)
GO

INSERT INTO COLUMNS_V2 VALUES (1,NULL,'c_birth_country','string',14),(1,NULL,'c_birth_day','int',11),(1,NULL,'c_birth_month','int',12),(1,NULL,'c_birth_year','int',13),(1,NULL,'c_current_addr_sk','bigint',4),(1,NULL,'c_current_cdemo_sk','bigint',2),(1,NULL,'c_current_hdemo_sk','bigint',3),(1,NULL,'c_customer_id','string',1),(1,NULL,'c_customer_sk','bigint',0),(1,NULL,'c_email_address','string',16),(1,NULL,'c_first_name','string',8),(1,NULL,'c_first_sales_date_sk','bigint',6),(1,NULL,'c_first_shipto_date_sk','bigint',5),(1,NULL,'c_last_name','string',9),(1,NULL,'c_last_review_date','string',17),(1,NULL,'c_login','string',15),(1,NULL,'c_preferred_cust_flag','string',10),(1,NULL,'c_salutation','string',7),(6,NULL,'dept','string',2),(6,NULL,'id','int',0),(6,NULL,'name','string',1),(6,NULL,'yoj','int',3),(11,NULL,'destination','string',3),(11,NULL,'eid','int',0),(11,NULL,'name','string',1),(11,NULL,'salary','string',2),(12,NULL,'destination','string',3),(12,NULL,'eid','int',0),(12,NULL,'name','string',1),(12,NULL,'salary','string',2),(13,NULL,'hms','int',0),(13,NULL,'message','string',4),(13,NULL,'process_id','int',3),(13,NULL,'server','string',2),(13,NULL,'severity','string',1),(14,NULL,'c_birth_country','string',14),(14,NULL,'c_birth_day','int',11),(14,NULL,'c_birth_month','int',12),(14,NULL,'c_birth_year','int',13),(14,NULL,'c_current_addr_sk','bigint',4),(14,NULL,'c_current_cdemo_sk','bigint',2),(14,NULL,'c_current_hdemo_sk','bigint',3),(14,NULL,'c_customer_id','string',1),(14,NULL,'c_customer_sk','bigint',0),(14,NULL,'c_email_address','string',16),(14,NULL,'c_first_name','string',8),(14,NULL,'c_first_sales_date_sk','bigint',6),(14,NULL,'c_first_shipto_date_sk','bigint',5),(14,NULL,'c_last_name','string',9),(14,NULL,'c_last_review_date','string',17),(14,NULL,'c_login','string',15),(14,NULL,'c_preferred_cust_flag','string',10),(14,NULL,'c_salutation','string',7),(15,NULL,'c_customer_id','string',1),(15,NULL,'c_order_id','bigint',0),(15,NULL,'c_price','decimal(5,3)',3),(15,NULL,'c_product_id','bigint',2),(16,NULL,'details','array<struct<Name:string,age:string,Sex:string>>',2),(16,NULL,'infomap','struct<Name:string,age:string,Sex:string>',1),(16,NULL,'names','array<string>',0)
GO
