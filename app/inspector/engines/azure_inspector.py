# -*- coding: utf-8 -*-
from app.inspector.engines.sqlserver_inspector import SQLServerInspector


class AzureInspector(SQLServerInspector):
    """Inspector for querying Azure DW and Azure SQL Database.
    """
    @classmethod
    def has_checks(self):
        return True

    @classmethod
    def has_indexes(self):
        return False

    @classmethod
    def has_partitions(self):
        return False

    @classmethod
    def has_usage(self):
        return False
