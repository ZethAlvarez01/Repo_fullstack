"""MongoDB-backed Reference Book access with normalized API output."""

from __future__ import annotations

import os
import re
from typing import Any

from pymongo.errors import PyMongoError


DATABASE_NAME = "reference_book"
COLLECTIONS = ("digimon", "appmon")


def _database():
    from app.database import client

    return client[DATABASE_NAME]


def use_atlas() -> bool:
    return os.getenv("VPET_REFERENCE_SOURCE", "atlas").strip().casefold() != "json"


def _api_record(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": document["reference_id"],
        "normalizedName": document["normalized_name"],
        "variantIndex": document.get("variant_index", 0),
        "selectorLabel": document.get("selector_label", document["name"]),
        "name": document["name"],
        "kind": document["kind"],
        "level": document.get("level"),
        "type": document.get("type"),
        "attribute": document.get("attribute"),
        "attacks": document.get("attacks", []),
        "description": document.get("description", ""),
        "antibody": bool(document.get("has_x_antibody")),
        "appmon_id": document.get("appmon_id"),
        "image": document.get("image_filename"),
        "image_url": (
            f"/api/vpet/images/{document['image_filename']}"
            if document.get("image_filename")
            else None
        ),
        "source_url": document.get("source_url"),
    }


def search(query_key: str, offset: int, limit: int) -> dict[str, Any]:
    if not use_atlas():
        raise PyMongoError("Atlas Reference Book disabled")
    database = _database()
    match = {"normalized_name": {"$regex": re.escape(query_key)}} if query_key else {}
    totals = [database[name].count_documents(match) for name in COLLECTIONS]
    remaining_offset = offset
    items: list[dict[str, Any]] = []
    for name in COLLECTIONS:
        collection_total = database[name].count_documents(match)
        if remaining_offset >= collection_total:
            remaining_offset -= collection_total
            continue
        cursor = (
            database[name]
            .find(match)
            .sort([("name", 1), ("variant_index", 1)])
            .skip(remaining_offset)
            .limit(limit - len(items))
        )
        items.extend(_api_record(document) for document in cursor)
        remaining_offset = 0
        if len(items) >= limit:
            break
    return {
        "total": sum(totals),
        "offset": offset,
        "limit": limit,
        "items": items,
        "source": "atlas",
    }


def variants(normalized_name: str) -> list[dict[str, Any]]:
    if not use_atlas():
        raise PyMongoError("Atlas Reference Book disabled")
    database = _database()
    items = []
    for name in COLLECTIONS:
        cursor = database[name].find({"normalized_name": normalized_name}).sort("variant_index", 1)
        items.extend(_api_record(document) for document in cursor)
    return items
