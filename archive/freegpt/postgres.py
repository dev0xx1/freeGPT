import json
import os
import socket
import uuid
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime
from decimal import Decimal

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text, select
from sqlalchemy.exc import OperationalError, TimeoutError, DisconnectionError, DatabaseError, DBAPIError
from psycopg2 import OperationalError as Psycopg2OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

DB_RETRIES = 3
WAIT_SEC = 2

exceptions = (socket.gaierror, OperationalError, TimeoutError, DisconnectionError, DatabaseError, DBAPIError, Psycopg2OperationalError)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.float32):
            return float(obj)
        elif isinstance(obj, np.float64):
            return float(obj)
        elif isinstance(obj, np.int32):
            return int(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        return super(CustomEncoder, self).default(obj)


class PostgresDB:

    @retry(
        reraise=True,
        stop=stop_after_attempt(DB_RETRIES),
        wait=wait_fixed(WAIT_SEC),
        retry=retry_if_exception_type(exceptions)
    )
    def __init__(self, username, password, host, port, db_name, sslmode=None):
        # Sync client
        self.db_uri = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}' + (
            f'?sslmode={sslmode}' if sslmode else '')
        self.engine = create_engine(self.db_uri)
        self.sync_session_maker = sessionmaker(bind=self.engine)

        # Async client
        async_db_uri = f'postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}' + (
            f'?sslmode={sslmode}' if sslmode else '')
        self.async_engine = create_async_engine(async_db_uri)
        self.async_session_maker = sessionmaker(
            bind=self.async_engine,
            expire_on_commit=False,
            class_=AsyncSession,
            sync_session_class=self.sync_session_maker
        )

    @retry(
        reraise=True,
        stop=stop_after_attempt(DB_RETRIES),
        wait=wait_fixed(WAIT_SEC),
        retry=retry_if_exception_type(exceptions)
    )
    def connect(self):
        self.engine.connect()

    @retry(
        reraise=True,
        stop=stop_after_attempt(DB_RETRIES),
        wait=wait_fixed(WAIT_SEC),
        retry=retry_if_exception_type(exceptions)
    )
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.sync_session_maker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    @retry(
        reraise=True,
        stop=stop_after_attempt(DB_RETRIES),
        wait=wait_fixed(WAIT_SEC),
        retry=retry_if_exception_type(exceptions)
    )
    @asynccontextmanager
    async def async_session_scope(self):
        """Provide a transactional scope around a series of operations for asynchronous sessions."""
        session = self.async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @retry(
        reraise=True,
        stop=stop_after_attempt(DB_RETRIES),
        wait=wait_fixed(WAIT_SEC),
        retry=retry_if_exception_type(exceptions)
    )
    def read(self, query, params={}):
        with self.session_scope() as session:
            result = session.execute(text(query), params).fetchall()
            result = [r._asdict() for r in result]
            return result

    @retry(
        reraise=True,
        stop=stop_after_attempt(DB_RETRIES),
        wait=wait_fixed(WAIT_SEC),
        retry=retry_if_exception_type(exceptions)
    )
    async def async_read(self, query: str, params={}):
        async with self.async_session_scope() as session:
            result = await session.execute(text(query), params)
            result = result.fetchall()
            result = [r._asdict() for r in result]
            return result

    @retry(
        reraise=True,
        stop=stop_after_attempt(DB_RETRIES),
        wait=wait_fixed(WAIT_SEC),
        retry=retry_if_exception_type(exceptions)
    )
    def write(self, query, params={}):
        # Make params into list and execute as list
        if isinstance(params, dict):
            params = [params]

        if isinstance(query, str):
            query = [query]

        with self.session_scope() as session:
            for query_, param in zip(query, params):
                result = session.execute(text(query_), param)

        return result

    @retry(
        reraise=True,
        stop=stop_after_attempt(DB_RETRIES),
        wait=wait_fixed(WAIT_SEC),
        retry=retry_if_exception_type(exceptions)
    )
    async def run_function(self, function_call):
        async with self.async_session_scope() as session:
            result = await session.execute(
                select(function_call)
            )
            # result = await session.execute(text(query), params)
            result = result.fetchall()
            result = [r._asdict() for r in result]
            return result

    @retry(
        reraise=True,
        stop=stop_after_attempt(DB_RETRIES),
        wait=wait_fixed(WAIT_SEC),
        retry=retry_if_exception_type(exceptions)
    )
    async def async_write(self, query: str, params={}):
        async with self.async_session_scope() as session:
            result = await session.execute(text(query), params)
            return result

    def insert(self, table_name, rows, pk_key='id', on_conflict="do nothing", uuid_cols=[]):
        if len(rows) == 0:
            return None, None
        query, params = self._get_upsert_query(table_name, rows, pk_key, on_conflict, uuid_cols)
        cursor_result = self.write(query, params)
        return cursor_result

    async def async_insert(self, table_name, rows, pk_key='id', on_conflict="do nothing", uuid_cols=[]):
        if len(rows) == 0:
            return None, None
        query, params = self._get_upsert_query(table_name, rows, pk_key, on_conflict, uuid_cols=uuid_cols)
        result = await self.async_write(query, params)
        return result

    def _get_upsert_query(self,
                          table_name,
                          rows,
                          pk_key,
                          on_conflict="do nothing",
                          uuid_cols=[]):
        # Check that rows is not empty
        if not rows:
            raise ValueError("The 'rows' list cannot be empty")

        # Extract columns from the first row
        columns = list(rows[0].keys())

        # Create parameterized placeholders and parameters dictionary
        values_placeholders = []
        params = {}
        for i, row in enumerate(rows):
            placeholder = []
            for col in columns:
                param_key = f"{col}{i}"
                placeholder.append(f":{param_key}")
                value = row.get(col, None)
                if isinstance(value, dict):
                    params[param_key] = json.dumps(value, cls=CustomEncoder)
                elif col in uuid_cols and row.get(col, None) is not None:
                    params[param_key] = uuid.UUID(row[col][0])
                else:
                    params[param_key] = row.get(col, None)
            params.keys()
            values_placeholders.append(f"({', '.join(placeholder)})")

        values_placeholders_str = ', '.join(values_placeholders)

        # Construct base SQL query using parameterized placeholders
        query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES {values_placeholders_str}
        """

        # Handling ON CONFLICT scenarios
        if on_conflict == "do nothing":
            query += " ON CONFLICT DO NOTHING"
        elif on_conflict == "update":
            update_columns = ', '.join([
                f"{col} = EXCLUDED.{col}" for col in columns if col != pk_key
            ])
            query += f" ON CONFLICT ({pk_key}) DO UPDATE SET {update_columns}"
        elif on_conflict != "raise":
            raise ValueError("Invalid on_conflict option")

        return query, params

    def format_uuid_list(self, uuid_list):
        return ','.join([f"'{id}'::uuid" for id in uuid_list])
