# Add lifespan support for startup/shutdown with strong typing
import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import json
import os
from dotenv import load_dotenv
load_dotenv()

import logging
logger = logging.getLogger(__name__)

import asyncpg
from mcp.server.fastmcp import FastMCP

class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
    
    async def init(self):
        self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=10
            )

@dataclass
class AppContext:
    db: Database




#todo: What is asynccontextmanager?
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # Initialize on startup
    db = Database(os.getenv("DATABASE_URL"))
    await db.init()
    try:
        yield AppContext(db=db)
    except Exception as e:
        print("Failed to get Database instance")
        raise


# Pass lifespan to server
mcp = FastMCP("PSQL Server", lifespan=app_lifespan)


@mcp.tool(
        name="Execute SQL", 
        description="Tool for executing SQL queries at the database"
        )
async def execute_sql(sql: str) -> dict[str, any]:
    """Execute a SQL query and return results"""
    ctx = mcp.get_context()
    db = ctx.request_context.lifespan_context.db
    async with db.pool.acquire() as conn:
        try:
            if sql.strip().upper().startswith('SELECT'):
                rows = await conn.fetch(sql)
                return {
                    'type': 'SELECT',
                    'rows': [dict(row) for row in rows],
                    'row_count': len(rows)
                }
            else:
                return {
                    'type': 'MODIFY',
                    'status': None,
                    'message': 'Only SELECT queries are supported'
                }
        except Exception as e:
            return {
                'type': 'error',
                'error': str(e),
                'message': f'Query failed: {str(e)}'
            }

@mcp.resource(
        uri="postgresql://tables",
        name="All Database Tables",
        description="List all tables across the database",
        mime_type="application/json"
        )
async def get_tables() -> dict[str, any]:
    """Provide the database tables"""
    ctx = mcp.get_context()
    db = ctx.request_context.lifespan_context.db
    async with db.pool.acquire() as conn:
        query = """
            SELECT 
            schemaname,
            tablename,
            tableowner
            FROM pg_tables 
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schemaname, tablename;
        """
        result = await conn.fetch(query)
        tables = [row['tablename'] for row in result]
        
        return {
            "tables": tables,
            "count": len(tables)
        }

@mcp.resource(
        uri="postgresql://tables/{table_name}/schema",
        name="Table Schema",
        description="Provides detailed schema of a given database table {table_name}",
        mime_type="application/json"
        )
async def get_table_schema(table_name: str) -> dict[str, any]:
    """Get detailed schema for a specific table"""
    ctx = mcp.get_context()
    db = ctx.request_context.lifespan_context.db
    async with db.pool.acquire() as conn:
        query = f"""
            SELECT 
                c.column_name,
                c.data_type,
                tc.constraint_type,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.columns c
            LEFT JOIN information_schema.key_column_usage kcu 
                ON c.table_name = kcu.table_name 
                AND c.column_name = kcu.column_name
            LEFT JOIN information_schema.table_constraints tc 
                ON kcu.constraint_name = tc.constraint_name
                AND kcu.constraint_schema = tc.constraint_schema
            LEFT JOIN information_schema.referential_constraints rc 
                ON tc.constraint_name = rc.constraint_name
                AND tc.constraint_schema = rc.constraint_schema
            LEFT JOIN information_schema.constraint_column_usage ccu 
                ON rc.unique_constraint_name = ccu.constraint_name
                AND rc.unique_constraint_schema = ccu.constraint_schema
            WHERE c.table_schema = 'public' and c.table_name = '{table_name}';
        """
        
        result = await conn.fetch(query)
        if not result:
            return {"error": "Table not found"}
    
        return {
            "schema": [dict(row) for row in result]
        }

@mcp.resource(
        uri="postgresql://tables/schemas",
        name="Table Schemas",
        description="Provides database table as key and it's schema as the value of the key",
        mime_type="application/json"
        )
async def get_all_schemas() -> dict[str, any]:
    """Get detailed schema for a all database tables"""
    schemas = {}
    tables = await get_tables()

    for table in tables["tables"]:
        schemas[table] = await get_table_schema(table)
    
    return schemas
    

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
