# V-Pet data builder

`build_data.py` creates the canonical runtime package used by the V-Pet backend. It reads the frozen Digimon Alpha JSON files and Reference Book workbook, applies the existing repairs and aliases, and writes normalized JSON. The workbook and image directory remain read-only.

Example from the monorepo root:

```powershell
python .\tools\vpet\build_data.py `
  --legacy-root "C:\path\to\Digimon_Alpha" `
  --reference-book "C:\path\to\reference_book.xlsx" `
  --image-dir "C:\path\to\img" `
  --output-dir ".\backend\app\vpet\data"
```

The backend owns the generated package. Vue reads it through `/api/vpet/*`, so the rules and catalogs have one source of truth. Images are indexed and hashed but are not copied into Git; the manifest will be used when the assets move to R2.
