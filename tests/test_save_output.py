import importlib.util
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/maketoons/skills/maketoons"
spec = importlib.util.spec_from_file_location("save_output", SKILL / "scripts/save_output.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SaveOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve()
        self.source = SKILL / "assets/gangbyul-v1/gangbyul.png"
        self.now = datetime(2026, 9, 25, 5, 30, 52, tzinfo=timezone.utc)

    def save(self, **kwargs):
        return module.save_output(self.source, self.project, "월요일 출근", now=self.now, **kwargs)

    def test_sheet_is_one_file_without_panel_suffix_and_keeps_bytes(self):
        result = self.save()
        image = Path(result["image"])
        self.assertEqual(image.name, "20260925_143052_월요일_출근.png")
        self.assertEqual(image.read_bytes(), self.source.read_bytes())
        record = json.loads(Path(result["record"]).read_text())
        self.assertEqual(record["output_mode"], "sheet")
        self.assertEqual(record["panels"], 4)
        self.assertEqual(record["saved_at"], "2026-09-25T14:30:52+09:00")

    def test_collision_keeps_first_image_and_record(self):
        first = self.save(details={"note": "first"})
        second = self.save(details={"note": "second"})
        self.assertNotEqual(first["image"], second["image"])
        self.assertTrue(second["image"].endswith("_02.png"))
        self.assertEqual(json.loads(Path(first["record"]).read_text())["details"]["note"], "first")

    def test_panel_revision(self):
        result = self.save(panel=2, revision=1)
        self.assertTrue(result["image"].endswith("_02컷_수정01.png"))

    def test_bad_input_does_not_create_output(self):
        for kwargs in ({"panels": 0}, {"panel": 5}, {"revision": 0}, {"details": []}):
            with self.assertRaises(ValueError):
                self.save(**kwargs)
        self.assertFalse((self.project / "makeimgs").exists())

    def test_title_cannot_escape_output_folder(self):
        result = module.save_output(self.source, self.project, "../../a:b\\c?", now=self.now)
        self.assertEqual(Path(result["image"]).parent, self.project / "makeimgs/outputs")

    def test_actual_format_determines_extension(self):
        source = self.project / "wrong.jpg"
        source.write_bytes(self.source.read_bytes())
        result = module.save_output(source, self.project, "test")
        self.assertTrue(result["image"].endswith(".png"))

    def test_reject_nonimage_and_plugin_destination(self):
        bad = self.project / "bad.png"
        bad.write_text("not an image")
        with self.assertRaises(ValueError):
            module.save_output(bad, self.project, "test")
        with self.assertRaises(ValueError):
            module.save_output(self.source, SKILL, "test")


if __name__ == "__main__":
    unittest.main()
