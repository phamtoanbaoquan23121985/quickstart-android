import unittest

from device_catalog import select_supported_devices


class DeviceCatalogTests(unittest.TestCase):
    def test_selects_only_exact_physical_pixel_10_targets_on_api_36(self):
        catalog = [
            {"name": "Pixel 10 Pro", "modelId": "pixel10pro", "codename": "blazer",
             "form": "PHYSICAL", "supportedVersionIds": ["36"]},
            {"name": "Pixel 10 Pro XL", "modelId": "pixel10proxl", "codename": "mustang",
             "form": "PHYSICAL", "supportedVersionIds": ["36"]},
            {"name": "Pixel 9 Pro", "modelId": "pixel9pro", "codename": "caiman",
             "form": "PHYSICAL", "supportedVersionIds": ["36"]},
            {"name": "Pixel 10 Pro", "modelId": "pixel10pro-virtual", "codename": "blazer",
             "form": "VIRTUAL", "supportedVersionIds": ["36"]},
        ]
        selected = select_supported_devices(catalog)
        self.assertEqual({item["model_id"] for item in selected}, {"pixel10pro", "pixel10proxl"})
        self.assertTrue(all(item["physical_device_required"] for item in selected))

    def test_fails_closed_when_one_required_target_is_missing(self):
        catalog = [
            {"name": "Pixel 10 Pro", "modelId": "pixel10pro", "codename": "blazer",
             "form": "PHYSICAL", "supportedVersionIds": ["36"]}
        ]
        with self.assertRaises(ValueError):
            select_supported_devices(catalog)

    def test_rejects_wrong_codename_or_virtual_device(self):
        base = [
            {"name": "Pixel 10 Pro", "modelId": "pixel10pro", "codename": "blazer",
             "form": "PHYSICAL", "supportedVersionIds": ["36"]},
            {"name": "Pixel 10 Pro XL", "modelId": "pixel10proxl", "codename": "mustang",
             "form": "PHYSICAL", "supportedVersionIds": ["36"]},
        ]
        wrong_codename = [dict(item) for item in base]
        wrong_codename[1]["codename"] = "other"
        with self.assertRaises(ValueError):
            select_supported_devices(wrong_codename)

        virtual = [dict(item) for item in base]
        virtual[0]["form"] = "VIRTUAL"
        with self.assertRaises(ValueError):
            select_supported_devices(virtual)

    def test_rejects_incomplete_catalog_entries(self):
        catalog = [
            {"name": "Pixel 10 Pro", "modelId": "pixel10pro", "codename": "blazer",
             "form": "PHYSICAL", "supportedVersionIds": ["36"]},
            {"name": "Pixel 10 Pro XL", "modelId": "pixel10proxl",
             "form": "PHYSICAL", "supportedVersionIds": ["36"]},
        ]
        with self.assertRaises(ValueError):
            select_supported_devices(catalog)


if __name__ == "__main__":
    unittest.main()
