import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.vpet import service
from app.vpet.router import get_catalog_family, get_config, router


class VPetDataTests(unittest.TestCase):
    def setUp(self):
        service.load_data.cache_clear()
        self.source_patch = patch.dict("os.environ", {"VPET_REFERENCE_SOURCE": "json"})
        self.source_patch.start()

    def tearDown(self):
        self.source_patch.stop()

    def test_bootstrap_uses_canonical_package(self):
        result = service.bootstrap()
        self.assertEqual(result["counts"]["referenceRecords"], 1473)
        self.assertEqual(result["counts"]["catalogFamilies"], 16)
        self.assertEqual(result["probability"]["minimumProbability"], 0.05)
        self.assertEqual(result["protocols"]["profiles"]["mini"]["alpha"]["command"], "A1")

    def test_reference_preserves_burgamon_variants(self):
        result = service.reference_variants("Burgamon")
        self.assertEqual(len(result), 2)
        self.assertEqual({item["level"] for item in result}, {"Rookie", "Champion"})

    def test_reference_alias_resolves_beelzebumon(self):
        result = service.reference_variants("Beelzebumon: Blast Mode")
        self.assertTrue(result)
        self.assertEqual(result[0]["name"], "Beelzemon: Blast Mode")

    def test_reference_search_is_paginated(self):
        result = service.search_reference("Agumon", offset=0, limit=3)
        self.assertGreaterEqual(result["total"], 3)
        self.assertEqual(len(result["items"]), 3)

    def test_catalog_exposes_all_families(self):
        catalog = service.catalog_family()
        self.assertIn("penx", catalog["familias"])
        self.assertIn("penc", catalog["familias"])

    def test_unknown_public_config_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            get_config("../manifest")
        self.assertEqual(context.exception.status_code, 404)

    def test_unknown_family_is_404(self):
        with self.assertRaises(HTTPException) as context:
            get_catalog_family("missing")
        self.assertEqual(context.exception.status_code, 404)

    def test_router_contract_is_registered(self):
        paths = {route.path for route in router.routes}
        self.assertIn("/api/vpet/bootstrap", paths)
        self.assertIn("/api/vpet/reference", paths)
        self.assertIn("/api/vpet/catalog/{family}", paths)
        self.assertIn("/api/vpet/images/{filename}", paths)

    def test_image_path_rejects_directory_traversal(self):
        with patch.dict("os.environ", {"VPET_IMAGE_DIR": str(service.DATA_DIR)}):
            self.assertIsNone(service.image_path("../manifest.json"))

    def test_reference_image_uses_existing_r2_prefix(self):
        with patch.dict("os.environ", {}, clear=False):
            self.assertEqual(
                service.image_object_key("agumon.jpg"),
                "img_reference_book/agumon.jpg",
            )

    def test_unindexed_image_is_not_requested_from_r2(self):
        self.assertIsNone(service.image_object_key("not-a-real-digimon.jpg"))


if __name__ == "__main__":
    unittest.main()
