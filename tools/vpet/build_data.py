"""Build the canonical V-Pet data package from the frozen Digimon Alpha app."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


JSON_SOURCES = (
    "battle_probability.json",
    "catalogo.json",
    "complete_local.json",
    "dmc_battle_profiles.json",
    "pen20_battle_profiles.json",
    "reference_overrides.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_legacy_modules(legacy_root: Path, reference_book: Path, image_dir: Path):
    os.environ["DIGIMON_REFERENCE_BOOK"] = str(reference_book)
    os.environ["DIGIMON_IMAGE_DIR"] = str(image_dir)
    sys.path.insert(0, str(legacy_root))
    try:
        reference = importlib.import_module("reference_book")
        beta_link = importlib.import_module("beta_link")
    finally:
        sys.path.pop(0)
    return reference, beta_link


def normalize_reference(reference_module) -> dict[str, Any]:
    records = reference_module.load_reference_book()["records"]
    name_counts = Counter(reference_module.normalize_name(item["name"]) for item in records)
    positions: defaultdict[str, int] = defaultdict(int)
    normalized = []
    for item in records:
        key = reference_module.normalize_name(item["name"])
        variant_index = positions[key]
        positions[key] += 1
        details = [str(value) for value in (item.get("level"), item.get("type")) if value]
        selector_label = item["name"]
        if name_counts[key] > 1:
            selector_label += " — " + " · ".join(details or [f"Variante {variant_index + 1}"])
        normalized.append(
            {
                "id": f"{key}:{variant_index}",
                "normalizedName": key,
                "variantIndex": variant_index,
                "selectorLabel": selector_label,
                **item,
            }
        )
    normalized.sort(key=lambda item: (item["name"].casefold(), item["variantIndex"]))
    return {"schemaVersion": 1, "records": normalized}


def build_image_manifest(reference_data: dict[str, Any], image_dir: Path) -> dict[str, Any]:
    names = sorted({item["image"] for item in reference_data["records"] if item.get("image")})
    entries = []
    for name in names:
        candidate = image_dir / name
        if candidate.is_file():
            entries.append(
                {
                    "filename": name,
                    "available": True,
                    "bytes": candidate.stat().st_size,
                    "sha256": sha256_file(candidate),
                }
            )
        else:
            entries.append({"filename": name, "available": False, "bytes": 0, "sha256": None})
    return {"schemaVersion": 1, "images": entries}


def build_protocol_profiles(beta_link_module) -> dict[str, Any]:
    profiles = {}
    for key, profile in sorted(beta_link_module.PERFILES.items()):
        alpha = beta_link_module.BATALLAS_ALPHA.get(key)
        profiles[key] = {
            "name": profile["nombre"],
            "wireCode": profile["codigo"],
            "packetCount": profile["paquetes"],
            "digitsPerPacket": profile.get("digitos_por_paquete", 4),
            "alpha": (
                {
                    "command": alpha["comando"],
                    "protocolRepresentative": alpha["rival_protocolo"],
                }
                if alpha
                else None
            ),
        }
    return {
        "schemaVersion": 1,
        "profiles": profiles,
        "verifiedResults": beta_link_module.RESULTADOS_VERIFICADOS,
        "dmcProxyModels": sorted(beta_link_module.DMC_PROXY_MODELS),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-root", type=Path, required=True)
    parser.add_argument("--reference-book", type=Path, required=True)
    parser.add_argument("--image-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    legacy_root = args.legacy_root.resolve()
    reference_book = args.reference_book.resolve()
    image_dir = args.image_dir.resolve()
    output_dir = args.output_dir.resolve()
    for path, label in (
        (legacy_root, "legacy root"),
        (reference_book, "reference workbook"),
        (image_dir, "image directory"),
    ):
        if not path.exists():
            parser.error(f"Missing {label}: {path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    reference_module, beta_link_module = load_legacy_modules(
        legacy_root, reference_book, image_dir
    )

    source_hashes = {"referenceWorkbook": sha256_file(reference_book)}
    for filename in JSON_SOURCES:
        source = legacy_root / "data" / filename
        source_hashes[filename] = sha256_file(source)
        output_name = "catalog.json" if filename == "catalogo.json" else filename
        write_json(output_dir / output_name, json.loads(source.read_text(encoding="utf-8")))

    reference_data = normalize_reference(reference_module)
    image_manifest = build_image_manifest(reference_data, image_dir)
    protocol_profiles = build_protocol_profiles(beta_link_module)
    aliases = {
        "schemaVersion": 1,
        "aliases": dict(sorted(reference_module.ALIASES.items())),
    }
    write_json(output_dir / "reference_book.json", reference_data)
    write_json(output_dir / "reference_aliases.json", aliases)
    write_json(output_dir / "image_manifest.json", image_manifest)
    write_json(output_dir / "protocol_profiles.json", protocol_profiles)

    output_files = sorted(path for path in output_dir.glob("*.json") if path.name != "manifest.json")
    output_hashes = {path.name: sha256_file(path) for path in output_files}
    catalog = json.loads((output_dir / "catalog.json").read_text(encoding="utf-8"))
    manifest = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "dataVersion": hashlib.sha256(
            json.dumps(source_hashes, sort_keys=True).encode("utf-8")
        ).hexdigest()[:16],
        "counts": {
            "referenceRecords": len(reference_data["records"]),
            "referenceImages": len(image_manifest["images"]),
            "availableImages": sum(item["available"] for item in image_manifest["images"]),
            "catalogFamilies": len(catalog["familias"]),
            "protocolProfiles": len(protocol_profiles["profiles"]),
        },
        "sourceHashes": source_hashes,
        "outputHashes": output_hashes,
    }
    write_json(output_dir / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
