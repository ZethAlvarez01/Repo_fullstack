import unittest
from datetime import datetime, timezone

from scripts.import_reference_book import build_documents, load_source


class ReferenceBookImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records, manifest = load_source()
        cls.documents = build_documents(
            records,
            data_version=manifest["dataVersion"],
            imported_at=datetime(2026, 10, 25, tzinfo=timezone.utc),
        )

    def test_splits_workbook_kinds_into_requested_collections(self):
        self.assertEqual(len(self.documents["digimon"]), 1325)
        self.assertEqual(len(self.documents["appmon"]), 148)

    def test_every_record_has_a_stable_unique_id(self):
        for documents in self.documents.values():
            identifiers = [item["reference_id"] for item in documents]
            self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_images_use_the_existing_r2_object_path(self):
        agumon = next(item for item in self.documents["digimon"] if item["name"] == "Agumon")
        self.assertEqual(agumon["r2_bucket"], "zeth-portfolio-assets")
        self.assertEqual(agumon["img"], "img_reference_book/agumon.jpg")

    def test_appmon_keeps_appmon_fields_and_sheet(self):
        sample = self.documents["appmon"][0]
        self.assertEqual(sample["kind"], "Appmon")
        self.assertEqual(sample["source"]["sheet"], "Appmon")
        self.assertIn("appmon_id", sample)


if __name__ == "__main__":
    unittest.main()
