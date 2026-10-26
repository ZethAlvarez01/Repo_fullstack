import unittest

from app.vpet.reference_repository import _api_record


class ReferenceRepositoryTests(unittest.TestCase):
    def test_mongo_document_maps_to_frontend_contract(self):
        result = _api_record({
            "reference_id": "agumon:0",
            "normalized_name": "agumon",
            "variant_index": 0,
            "selector_label": "Agumon",
            "name": "Agumon",
            "kind": "Digimon",
            "level": "Rookie",
            "type": "Dinosaur",
            "attribute": "Vaccine",
            "attacks": ["Pepper Breath"],
            "description": "Profile",
            "has_x_antibody": False,
            "image_filename": "agumon.jpg",
        })
        self.assertEqual(result["normalizedName"], "agumon")
        self.assertEqual(result["image_url"], "/api/vpet/images/agumon.jpg")
        self.assertEqual(result["attacks"], ["Pepper Breath"])


if __name__ == "__main__":
    unittest.main()
