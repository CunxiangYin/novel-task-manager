from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

class DatabaseStats(BaseModel):
    """Overall database statistics"""
    total_tasks: int
    total_logs: int
    total_results: int
    total_queue_items: int
    total_files: int
    status_distribution: Dict[str, int]
    database_size_bytes: int
    tasks_today: int

class ColumnInfo(BaseModel):
    """Information about a database column"""
    name: str
    type: str
    nullable: bool
    primary_key: bool
    foreign_key: bool

class TableInfo(BaseModel):
    """Information about a database table"""
    name: str
    row_count: int
    columns: List[ColumnInfo]

class QueryResult(BaseModel):
    """Result of a database query"""
    table_name: str
    total_count: int
    count: int
    offset: int
    limit: int
    data: List[Dict[str, Any]]

class DeleteResult(BaseModel):
    """Result of a delete operation"""
    success: bool
    deleted_id: Optional[str] = None
    message: str

class CleanupResult(BaseModel):
    """Result of a cleanup operation"""
    table_name: str
    deleted_count: int
    message: str