# -*- coding: utf-8 -*-
from app.inspector.engines.sqlserver_inspector import SQLServerInspector


class AzureInspector(SQLServerInspector):
    """Inspector for querying Azure DW and Azure SQL Database.
    """
