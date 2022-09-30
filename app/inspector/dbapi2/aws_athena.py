# -*- coding: utf-8 -*-
import collections
import time


from app.inspector.aws import get_aws_client


class DatabaseError(Exception):
    pass


class OperationalError(DatabaseError):
    pass


class ProgrammingError(DatabaseError):
    pass


class DataError(DatabaseError):
    pass


class AthenaQueryExecution:
    STATE_QUEUED = "QUEUED"
    STATE_RUNNING = "RUNNING"
    STATE_SUCCEEDED = "SUCCEEDED"
    STATE_FAILED = "FAILED"
    STATE_CANCELLED = "CANCELLED"

    def __init__(self, data):
        self.data = data

    @property
    def query_id(self):
        return self.data.get("QueryExecutionId")

    @property
    def query(self):
        return self.data.get("Query")

    @property
    def status(self):
        return self.data.get("Status", {})

    @property
    def state(self):
        return self.status.get("State")

    @property
    def state_change_reason(self):
        return self.status.get("StateChangeReason")


class ResultSet(object):
    def __init__(self, connection, query_execution, arraysize=1000):
        self._connection = connection
        self._query_execution = query_execution
        self._metadata = None
        self._rows = collections.deque()
        self._next_token = None
        self._arraysize = arraysize

        if self.state == AthenaQueryExecution.STATE_SUCCEEDED:
            self._rownumber = 0
            self._pre_fetch()

    @property
    def is_closed(self):
        return self._connection is None

    @property
    def query_id(self):
        if not self._query_execution:
            return None
        return self._query_execution.query_id

    @property
    def query(self):
        if not self._query_execution:
            return None
        return self._query_execution.query

    @property
    def state(self):
        if not self._query_execution:
            return None
        return self._query_execution.state

    @property
    def description(self):
        if self._metadata is None:
            return None
        return [
            (
                m["Name"],
                m["Type"],
                None,
                None,
                m["Precision"],
                m["Scale"],
                m["Nullable"],
            )
            for m in self._metadata
        ]

    def close(self) -> None:
        self._connection = None
        self._query_execution = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def fetchone(self):
        if not self._rows and self._next_token:
            self._fetch()
        if not self._rows:
            return None
        else:
            if self._rownumber is None:
                self._rownumber = 0
            self._rownumber += 1
            return self._rows.popleft()

    def fetchmany(self, size=None):
        if not size or size <= 0:
            size = self._arraysize
        rows = []
        for _ in range(size):
            row = self.fetchone()
            if row:
                rows.append(row)
            else:
                break
        return rows

    def fetchall(self):
        rows = []
        while True:
            row = self.fetchone()
            if row:
                rows.append(row)
            else:
                break
        return rows

    def _pre_fetch(self):
        response = self.__fetch()
        self._process_metadata(response)
        self._process_rows(response)

    def __fetch(self, next_token=None):
        if not self.query_id:
            raise ProgrammingError("QueryExecutionId is none or empty.")
        if self.state != AthenaQueryExecution.STATE_SUCCEEDED:
            raise ProgrammingError("QueryExecutionState is not SUCCEEDED.")
        if self.is_closed:
            raise ProgrammingError("AthenaResultSet is closed.")
        request = {
            "QueryExecutionId": self.query_id,
            "MaxResults": self._arraysize,
        }
        if next_token:
            request.update({"NextToken": next_token})
        try:
            response = self._connection.client.get_query_results(
                **request
            )
        except Exception as e:
            raise OperationalError(*e.args) from e
        else:
            return response

    def _fetch(self):
        if not self._next_token:
            raise ProgrammingError("NextToken is none or empty.")
        response = self.__fetch(self._next_token)
        self._process_rows(response)

    def _get_rows(self, offset, metadata, rows):
        return [
            dict(
                [
                    (
                        meta.get("Name"),
                        row.get("VarCharValue", None),
                    )
                    for meta, row in zip(metadata, rows[i].get("Data", []))
                ]
            )
            for i in range(offset, len(rows))
        ]

    def _process_metadata(self, response):
        result_set = response.get("ResultSet", None)
        if not result_set:
            raise DataError("KeyError `ResultSet`")
        metadata = result_set.get("ResultSetMetadata", None)
        if not metadata:
            raise DataError("KeyError `ResultSetMetadata`")
        column_info = metadata.get("ColumnInfo", None)
        if column_info is None:
            raise DataError("KeyError `ColumnInfo`")
        self._metadata = tuple(column_info)

    def _process_rows(self, response):
        result_set = response.get("ResultSet", None)
        if not result_set:
            raise DataError("KeyError `ResultSet`")
        rows = result_set.get("Rows", None)
        if rows is None:
            raise DataError("KeyError `Rows`")
        processed_rows = []
        if len(rows) > 0:
            offset = (
                1
                if not self._next_token and self._is_first_row_column_labels(rows)
                else 0
            )
            metadata = self._metadata
            processed_rows = self._get_rows(offset, metadata, rows)
        self._rows.extend(processed_rows)
        self._next_token = response.get("NextToken", None)

    def _is_first_row_column_labels(self, rows) -> bool:
        first_row_data = rows[0].get("Data", [])
        metadata = self._metadata
        for meta, data in zip(metadata, first_row_data):
            if meta.get("Name", None) != data.get("VarCharValue", None):
                return False
        return True


class Cursor(object):
    def __init__(
        self,
        connection,
        poll_interval=3,
        arraysize=1000,
        kill_on_interrupt=True,
    ):
        self._connection = connection
        self._poll_interval = poll_interval
        self._kill_on_interrupt = kill_on_interrupt
        self._arraysize = arraysize
        self._query_id = None
        self._query_result_set = None

    @property
    def work_group(self):
        return self._connection.work_group

    @property
    def catalog_name(self):
        return self._connection.catalog_name

    @property
    def client(self):
        return self._connection.client

    @property
    def timeout(self):
        return self._connection.timeout

    @property
    def result_set(self):
        return self._query_result_set

    @property
    def has_result_set(self):
        return self.result_set is not None

    @property
    def description(self):
        if self.has_result_set:
            return self.result_set.description

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _reset_state(self):
        self._query_id = None
        self._query_result_set = None

    def execute(self, operation, parameters=None):
        self._reset_state()
        self._query_id = self._execute(
            operation,
            parameters=parameters,
        )
        query_execution = self._poll(self._query_id)
        if query_execution.state == AthenaQueryExecution.STATE_SUCCEEDED:
            self._query_result_set = ResultSet(
                self._connection,
                query_execution,
                arraysize=self._arraysize)
        else:
            raise OperationalError(query_execution.state_change_reason)
        return self

    def executemany(self, operation, seq_of_parameters):
        raise NotImplementedError()

    def fetchall(self):
        if not self.has_result_set:
            raise ProgrammingError("No result set.")
        return self.result_set.fetchall()

    def fetchmany(self, size=None):
        if not self.has_result_set:
            raise ProgrammingError("No result set.")
        return self.result_set.fetchmany()

    def fetchone(self):
        if not self.has_result_set:
            raise ProgrammingError("No result set.")
        return self.result_set.fetchone()

    def close(self):
        if self._query_result_set and not self._query_result_set.is_closed:
            self._query_result_set.close()

    def _execute(self, operation, parameters):
        try:
            query_id = self._start_query_execution(
                query=self._format_query(operation, parameters),
            ).get("QueryExecutionId", None)
        except Exception as e:
            raise DatabaseError(*e.args) from e
        else:
            return query_id

    def __poll(self, query_id):
        start = time.time()
        while True:
            query_timed_out = (time.time() - start) > self.timeout
            query_execution = self._get_query_execution(query_id)
            if query_execution.state in [
                AthenaQueryExecution.STATE_SUCCEEDED,
                AthenaQueryExecution.STATE_FAILED,
                AthenaQueryExecution.STATE_CANCELLED,
            ]:
                return query_execution
            elif query_timed_out:
                self._cancel_query_execution(query_id)
                return
            else:
                time.sleep(self._poll_interval)

    def _poll(self, query_id):
        try:
            query_execution = self.__poll(query_id)
        except KeyboardInterrupt as e:
            if self._kill_on_interrupt:
                self._cancel_query_execution(query_id)
                query_execution = self.__poll(query_id)
            else:
                raise e
        return query_execution

    def _format_query(self, operation, parameters):
        return operation

    def _start_query_execution(self, query):
        request = {
            "QueryString": query,
            "QueryExecutionContext": {
                "Catalog": self.catalog_name,
            },
            "WorkGroup": self.work_group,
        }

        try:
            response = self.client.start_query_execution(
                **request
            )
        except Exception as e:
            raise OperationalError(*e.args) from e
        else:
            return response

    def _get_query_execution(self, query_id):
        request = {"QueryExecutionId": query_id}
        try:
            response = self.client.get_query_execution(
                **request
            )
        except Exception as e:
            raise OperationalError(*e.args) from e
        else:
            return AthenaQueryExecution(response["QueryExecution"])

    def _cancel_query_execution(self, query_id):
        request = {"QueryExecutionId": query_id}
        try:
            self.client.stop_query_execution(**request)
        except Exception as e:
            raise OperationalError(*e.args) from e


class Connection(object):
    def __init__(
        self,
        role_arn,
        region_name,
        work_group=None,
        catalog_name="awsdatacatalog",
        timeout=3600,
    ):
        self.role_arn = role_arn
        self.work_group = work_group
        self.region_name = region_name
        self.catalog_name = catalog_name
        self.timeout = timeout
        self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def client(self):
        if self._client is None:
            self._client = get_aws_client(
                'athena',
                role_arn=self.role_arn,
                role_session_name=f'metamapper_{self.region_name}_{self.catalog_name}',
                region=self.region_name)
        return self._client

    def cursor(self, **kwargs):
        return Cursor(connection=self, **kwargs)

    def close(self):
        pass

    def commit(self):
        pass


def connect(role_arn, region_name, work_group, catalog_name="awsdatacatalog", timeout=3600):
    return Connection(
        role_arn=role_arn,
        region_name=region_name,
        work_group=work_group,
        catalog_name=catalog_name,
        timeout=timeout)
