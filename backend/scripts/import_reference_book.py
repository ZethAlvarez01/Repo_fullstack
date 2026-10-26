"""Import the normalized Reference Book into MongoDB Atlas.

The import is idempotent: records are upserted by ``reference_id`` and existing
documents not present in the workbook are never deleted.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient, UpdateOne
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.server_api import ServerApi


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = BACKEND_ROOT / "app" / "vpet" / "data"
DEFAULT_DATABASE = "reference_book"
COLLECTIONS = {"Digimon": "digimon", "Appmon": "appmon"}
R2_BUCKET = "zeth-portfolio-assets"
R2_PREFIX = "img_reference_book"


def load_source(data_dir: Path = DEFAULT_DATA_DIR) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reference = json.loads((data_dir / "reference_book.json").read_text(encoding="utf-8"))
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    return reference["records"], manifest


def build_documents(
    records: list[dict[str, Any]],
    *,
    data_version: str,
    imported_at: datetime | None = None,
) -> dict[str, list[dict[str, Any]]]:
    timestamp = imported_at or datetime.now(timezone.utc)
    documents = {collection: [] for collection in COLLECTIONS.values()}
    for record in records:
        collection = COLLECTIONS.get(record["kind"])
        if collection is None:
            raise ValueError(f"Unsupported Reference Book kind: {record['kind']!r}")
        image = record.get("image")
        document = {
            "reference_id": record["id"],
            "name": record["name"],
            "normalized_name": record["normalizedName"],
            "variant_index": record["variantIndex"],
            "selector_label": record["selectorLabel"],
            "kind": record["kind"],
            "level": record.get("level"),
            "type": record.get("type"),
            "attribute": record.get("attribute"),
            "attacks": record.get("attacks", []),
            "description": record.get("description", ""),
            "has_x_antibody": bool(record.get("antibody")),
            "appmon_id": record.get("appmon_id"),
            "image_filename": image,
            "img": f"{R2_PREFIX}/{image}" if image else None,
            "r2_bucket": R2_BUCKET if image else None,
            "source_url": record.get("source_url"),
            "source": {
                "workbook": "reference_book_2_with_images_and_appmon.xlsx",
                "sheet": "Appmon" if record["kind"] == "Appmon" else "Sheet1",
                "data_version": data_version,
            },
            "updated_at": timestamp,
        }
        documents[collection].append(document)
    return documents


def import_collection(collection, documents: list[dict[str, Any]]) -> dict[str, int]:
    collection.create_index(
        [("reference_id", ASCENDING)],
        unique=True,
        name="reference_id_unique",
    )
    collection.create_index(
        [("normalized_name", ASCENDING), ("variant_index", ASCENDING)],
        name="reference_name_variant",
    )
    operations = [
        UpdateOne(
            {"reference_id": document["reference_id"]},
            {
                "$set": document,
                "$setOnInsert": {"created_at": document["updated_at"]},
            },
            upsert=True,
        )
        for document in documents
    ]
    result = collection.bulk_write(operations, ordered=False)
    return {
        "source": len(documents),
        "matched": result.matched_count,
        "modified": result.modified_count,
        "inserted": result.upserted_count,
        "stored": collection.count_documents({}),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv(BACKEND_ROOT / ".env")
    records, manifest = load_source(args.data_dir)
    documents = build_documents(records, data_version=manifest["dataVersion"])
    counts = {name: len(items) for name, items in documents.items()}
    if counts != {"digimon": 1325, "appmon": 148}:
        raise RuntimeError(f"Unexpected workbook split: {counts}")

    if args.dry_run:
        print(json.dumps({"database": args.database, "collections": counts, "write": False}, indent=2))
        return

    uri = os.getenv("MONGODB_URI")
    if not uri:
        parser.error("MONGODB_URI is missing from backend/.env")
    client = MongoClient(
        uri,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10_000,
    )
    try:
        client.admin.command("ping")
    except ServerSelectionTimeoutError as error:
        raise SystemExit(
            "No se pudo conectar a Atlas. Actualiza MONGODB_URI en backend/.env "
            "con la cadena del cluster donde creaste reference_book y revisa Network Access. "
            "No se escribio ningun documento."
        ) from error
    database = client[args.database]
    results = {
        name: import_collection(database[name], items)
        for name, items in documents.items()
    }
    print(json.dumps({"database": args.database, "collections": results}, indent=2))


if __name__ == "__main__":
    main()
