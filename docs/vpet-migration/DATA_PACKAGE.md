# V-Pet canonical data package

Step 2 of the migration moves all editable battle data and Reference Book metadata into `backend/app/vpet/data`.

## Ownership

- `tools/vpet/build_data.py` is the only supported generator.
- `backend/app/vpet/data` is the generated canonical runtime package.
- FastAPI exposes the package through `/api/vpet/*`.
- Vue uses `frontend/src/features/vpet/data/client.ts`; it does not duplicate JSON tables.

## Included data

- Weighted battle probability configuration and noise settings.
- Identity catalog for 16 V-Pet families.
- Seventeen wire/protocol profiles and Alpha commands.
- Verified win/loss packets for compatible three-pin families.
- DMC and Pendulum 20th mask profiles.
- Reference Book metadata for 1,473 Digimon/Appmon entries.
- Name aliases, repaired Reference Book entries and local Ver. Complete observations.
- Manifest for 1,473 referenced images, including byte sizes and SHA-256 hashes.

## Images in Cloudflare R2

The source image directory is approximately 168 MB and is not duplicated in Git. Production images are read from the existing `zeth-portfolio-assets` bucket with this object prefix:

```text
img_reference_book/{filename}
```

The existing R2 client and credentials remain the only connection configuration. `VPET_R2_IMAGE_PREFIX` can override the prefix without changing code. During local development, this optional fallback remains available:

```text
VPET_IMAGE_DIR=C:\path\to\Digimon_Game\img
```

FastAPI serves only filenames present in the generated manifest through `/api/vpet/images/{filename}`. Path traversal and unindexed files are rejected. If R2 reports a missing object, the endpoint tries the local fallback when configured.

## API contract

```text
GET /api/vpet/bootstrap
GET /api/vpet/reference?query=&offset=&limit=
GET /api/vpet/reference/{name}
GET /api/vpet/catalog
GET /api/vpet/catalog/{family}
GET /api/vpet/config/{name}
GET /api/vpet/images/{filename}
```

`/bootstrap` is intentionally small. It provides the current data version, probability rules, protocol profiles, resource URLs and record counts. Large catalogs are requested separately.

## MongoDB Reference Book import

The idempotent importer writes the normalized workbook into database `reference_book`:

```text
Sheet1 (Digimon) -> digimon: 1,325 documents
Appmon           -> appmon:    148 documents
```

Every document has a unique `reference_id` and an `img` object key such as `img_reference_book/agumon.jpg`. Running the importer again updates matching documents without duplicating them or deleting unrelated records.

```powershell
cd backend
.\.venv\Scripts\python.exe -m scripts.import_reference_book --dry-run
.\.venv\Scripts\python.exe -m scripts.import_reference_book
```
