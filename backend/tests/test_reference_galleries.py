import unittest
from unittest.mock import patch

from app.vpet import service


class ReferenceGalleryTests(unittest.TestCase):
    def setUp(self):
        service.load_data.cache_clear()
        self.source_patch = patch.dict("os.environ", {"VPET_REFERENCE_SOURCE": "json"})
        self.source_patch.start()

    def tearDown(self):
        self.source_patch.stop()

    def test_ceresmon_search_and_detail_include_both_illustrations(self):
        detail = service.reference_variants("Ceresmon")[0]
        search = service.search_reference("Ceresmon")["items"][0]
        expected = ["ceresmon.jpg", "ceresmon_2.jpg"]
        self.assertEqual([image["filename"] for image in detail["images"]], expected)
        self.assertEqual(search["images"], detail["images"])
        self.assertEqual(detail["image"], "ceresmon.jpg")
        self.assertEqual(detail["images"][1]["image_url"], "/api/vpet/images/ceresmon_2.jpg")

    def test_all_sixteen_galleries_match_existing_records_and_r2_keys(self):
        records = service.load_data("reference_book.json")["records"]
        galleries = service.load_data("reference_galleries.json")["galleries"]
        by_image = {record["image"]: record for record in records if record.get("image")}
        self.assertEqual(len(galleries), 16)
        for primary, extras in galleries.items():
            with self.subTest(primary=primary):
                profile = service.with_reference_images(by_image[primary])
                self.assertEqual([image["filename"] for image in profile["images"]], [primary, *extras])
                for filename in extras:
                    self.assertEqual(service.image_object_key(filename), f"img_reference_book/{filename}")

    def test_atlas_search_and_detail_are_enriched_without_modifying_source_records(self):
        record = next(r for r in service.load_data("reference_book.json")["records"] if r["name"] == "Bacchusmon")
        atlas_result = {"items": [record], "total": 1, "offset": 0, "limit": 50, "source": "atlas"}
        with (
            patch.object(service.reference_repository, "search", return_value=atlas_result),
            patch.object(service.reference_repository, "variants", return_value=[record]),
        ):
            search = service.search_reference("Bacchusmon")
            detail = service.reference_variants("Bacchusmon")[0]
        self.assertEqual(len(detail["images"]), 2)
        self.assertEqual(search["source"], "atlas")
        self.assertEqual(search["items"][0]["images"], detail["images"])
        self.assertEqual(detail["id"], record["id"])
        self.assertEqual(detail["attacks"], record["attacks"])
        self.assertNotIn("images", record)

    def test_catalog_physical_profiles_also_have_galleries(self):
        profiles = service.catalog_family("pen20", include_reference=True)["referenceProfiles"].values()
        self.assertTrue(any(len(profile["images"]) > 1 for profile in profiles))

    def test_single_image_profiles_and_appmon_keep_their_primary(self):
        digimon = service.reference_variants("Agumon")[0]
        self.assertEqual([image["filename"] for image in digimon["images"]], [digimon["image"]])
        self.assertEqual(service.with_reference_images({"kind": "Appmon", "image": "ceresmon.jpg"})["images"], [
            {"filename": "ceresmon.jpg", "image_url": "/api/vpet/images/ceresmon.jpg", "label": "Ilustración 1"},
        ])
        self.assertEqual(service.with_reference_images({"kind": "Digimon", "image": None})["images"], [])

    def test_bootstrap_image_counts_include_the_additional_illustrations(self):
        self.assertEqual(service.bootstrap()["counts"]["referenceImages"], 1489)
        self.assertEqual(service.bootstrap()["counts"]["referenceRecords"], 1473)

    def test_image_allowlist_still_rejects_unknown_files_and_traversal(self):
        for filename in ("../ceresmon_2.jpg", "missing_2.jpg", "ceresmon_2.svg"):
            self.assertIsNone(service.image_object_key(filename))


if __name__ == "__main__":
    unittest.main()
