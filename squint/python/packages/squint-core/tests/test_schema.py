"""Checks the Pydantic models against the latest Drizzle schema snapshot, so the Python and
TypeScript views of a table can't drift apart unnoticed."""

import json
import types
from datetime import datetime
from pathlib import Path
from typing import Union, get_args, get_origin
from uuid import UUID

import pytest
from pydantic import BaseModel

from squint_core.documents import Document, DocumentPage

MIGRATIONS = Path(__file__).parents[4] / "javascript" / "db" / "drizzle"

TABLE_MODELS: dict[str, type[BaseModel]] = {
    "document": Document,
    "document_page": DocumentPage,
}

PYTHON_TYPES = {
    "uuid": UUID,
    "text": str,
    "integer": int,
    "integer[]": list[int],
    "real": float,
    "bigint": int,
    "boolean": bool,
    "timestamp": datetime,
    "timestamp with time zone": datetime,
}


def latest_snapshot() -> dict:
    journal = json.loads((MIGRATIONS / "meta" / "_journal.json").read_text())
    idx = journal["entries"][-1]["idx"]
    return json.loads((MIGRATIONS / "meta" / f"{idx:04d}_snapshot.json").read_text())


def split_optional(annotation: object) -> tuple[object, bool]:
    """The annotation without `| None`, and whether it allowed None."""
    if get_origin(annotation) in (Union, types.UnionType):
        args = get_args(annotation)
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1:
            return non_none[0], len(non_none) < len(args)
    return annotation, False


@pytest.mark.parametrize("table", TABLE_MODELS)
def test_model_matches_table(table: str):
    model = TABLE_MODELS[table]
    columns = latest_snapshot()["tables"][f"public.{table}"]["columns"]

    assert set(model.model_fields) == set(columns)
    for name, column in columns.items():
        python_type, nullable = split_optional(model.model_fields[name].annotation)
        assert nullable == (not column["notNull"]), f"{table}.{name} nullability"
        assert python_type == PYTHON_TYPES[column["type"]], f"{table}.{name} type"
