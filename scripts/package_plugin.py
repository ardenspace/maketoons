#!/usr/bin/env python3
"""Build a portable ZIP with the complete plugin and a standalone skill ZIP."""
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
plugin = ROOT / "plugins/maketoons"
skill = plugin / "skills/maketoons"
manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
references = json.loads((skill / "assets/reference-set.json").read_text())
for entry in references["images"]:
    path = (skill / entry["file"]).resolve()
    if skill.resolve() not in path.parents or not path.is_file():
        raise SystemExit(f"Missing or invalid reference: {entry['file']}")
out = ROOT / "dist"
out.mkdir(exist_ok=True)
for source, name in ((plugin, "maketoons-plugin"), (skill, "maketoons-skill")):
    destination = out / f"{name}-{manifest['version']}.zip"
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store":
                archive.write(path, Path("maketoons") / path.relative_to(source))
    print(destination)
