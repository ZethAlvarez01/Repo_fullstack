"""Read-only access to the canonical V-Pet data package."""

from __future__ import annotations

import json
import os
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from pymongo.errors import PyMongoError

from app.vpet import reference_repository


DATA_DIR = Path(__file__).with_name("data")
PUBLIC_CONFIGS = {
    "battle-probability": "battle_probability.json",
    "protocol-profiles": "protocol_profiles.json",
    "dmc-battle-profiles": "dmc_battle_profiles.json",
    "pen20-battle-profiles": "pen20_battle_profiles.json",
}
DEFAULT_R2_IMAGE_PREFIX = "img_reference_book"


def normalize_name(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(character for character in text if not unicodedata.combining(character))
    text = text.casefold()
    text = re.sub(r"\(\s*x[- ]?antibody\s*\)", " x", text)
    text = re.sub(r"\bx[- ]?antibody\b", "x", text)
    return re.sub(r"[^a-z0-9]+", "", text)


@lru_cache(maxsize=None)
def load_data(filename: str) -> Any:
    path = DATA_DIR / filename
    if path.parent != DATA_DIR or not path.is_file():
        raise FileNotFoundError(filename)
    return json.loads(path.read_text(encoding="utf-8"))


def bootstrap() -> dict[str, Any]:
    manifest = load_data("manifest.json")
    return {
        "schemaVersion": 1,
        "dataVersion": manifest["dataVersion"],
        "counts": manifest["counts"],
        "probability": load_data("battle_probability.json"),
        "protocols": load_data("protocol_profiles.json"),
        "resources": {
            "reference": "/api/vpet/reference",
            "catalog": "/api/vpet/catalog",
            "images": "/api/vpet/images/{filename}",
            "configs": "/api/vpet/config/{name}",
        },
    }


def search_reference(query: str = "", offset: int = 0, limit: int = 50) -> dict[str, Any]:
    needle = normalize_name(query)
    try:
        return reference_repository.search(needle, offset, limit)
    except PyMongoError:
        pass
    records = load_data("reference_book.json")["records"]
    if needle:
        records = [
            item
            for item in records
            if needle in item["normalizedName"]
            or needle in normalize_name(item.get("selectorLabel", ""))
        ]
    total = len(records)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": records[offset : offset + limit],
        "source": "json-fallback",
    }


def reference_variants(name: str) -> list[dict[str, Any]]:
    key = normalize_name(name)
    aliases = load_data("reference_aliases.json")["aliases"]
    key = aliases.get(key, key)
    try:
        return reference_repository.variants(key)
    except PyMongoError:
        pass
    return [
        item
        for item in load_data("reference_book.json")["records"]
        if item["normalizedName"] == key
    ]


def catalog_family(family: str | None = None, include_reference: bool = False) -> dict[str, Any]:
    catalog = load_data("catalog.json")
    if family is None:
        return catalog
    entry = catalog["familias"].get(family)
    if entry is None:
        raise KeyError(family)
    result = {"schema": catalog.get("schema"), "family": family, **entry}
    if include_reference:
        records = load_data("reference_book.json")["records"]
        by_name = {record["normalizedName"]: record for record in records}
        aliases = load_data("reference_aliases.json")["aliases"]
        profiles = {}
        for catalog_entry in entry.get("entradas", []):
            name = catalog_entry.get("nombre", "")
            key = normalize_name(name)
            profile = by_name.get(aliases.get(key, key))
            if profile is not None:
                profiles[name] = profile
        result["referenceProfiles"] = profiles
    return result


def public_config(name: str) -> dict[str, Any]:
    filename = PUBLIC_CONFIGS.get(name)
    if filename is None:
        raise KeyError(name)
    return load_data(filename)


def image_object_key(filename: str) -> str | None:
    """Return the R2 key only for an image included in the generated manifest."""
    if Path(filename).name != filename or Path(filename).suffix.casefold() not in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }:
        return None
    allowed = {
        item["filename"]
        for item in load_data("image_manifest.json")["images"]
        if item["available"]
    }
    if filename not in allowed:
        return None
    prefix = os.getenv("VPET_R2_IMAGE_PREFIX", DEFAULT_R2_IMAGE_PREFIX).strip("/")
    return f"{prefix}/{filename}" if prefix else filename


def image_path(filename: str) -> Path | None:
    """Resolve an indexed local image without allowing directory traversal."""
    if image_object_key(filename) is None:
        return None
    configured = os.getenv("VPET_IMAGE_DIR")
    if not configured:
        return None
    root = Path(configured).resolve()
    candidate = (root / filename).resolve()
    if root not in candidate.parents:
        return None
    return candidate if candidate.is_file() else None
