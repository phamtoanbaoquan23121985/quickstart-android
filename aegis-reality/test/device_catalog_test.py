import json
import unittest

from device_catalog import select_supported_devices


class DeviceCatalogTests(unittest.TestCase):
    def test_selects_only_supported_pixel_10_targets_on_api_36(self):
        catalog = [
            {"name": "Pixel 10 Pro", "modelId": "pixel10pro", "supportedVersionIds": ["36"]},
            {"name": "Pixel 10 Pro XL", "modelId": "pixel10proxl", "supportedVersionIds": ["36"]},
            {"name": "Pixel 9 Pro", "modelId": "pixel9pro", "supportedVersionIds": ["36"]},
            {"name": "Pixel 10 Pro", "modelId": "pixel10pro", "supportedVersionIds": ["35"]},
        ]
        selected = select_supported_devices(catalog)
        self.assertEqual({item["modelId"] for item in selected}, {"pixel10pro", "pixel10proxl"})

    def test_fails_closed_when_one_required_target_is_missing(self):
        catalog = [
            {"name": "Pixel 10 Pro", "modelId": "pixel10pro", "supportedVersionIds": ["36"]}
        ]
        with self.assertRaises(ValueError):
            select_supported_devices(catalog)

    def test_rejects_ambiguous_or_incomplete_catalog_entries(self):
        catalog = [
            {"name": "Pixel 10 Pro", "modelId": "pixel10pro", "supportedVersionIds": ["36"]},
            {"name": "Pixel 10 Pro XL", "modelId": "pixel10proxl"},
        ]
        with self.assertRaises(ValueError):
            select_supported_devices(catalog)


if __name__ == "__main__":
    unittest.main()
