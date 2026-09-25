#!/usr/bin/env python3
"""Copy a generated image without overwriting; record its production settings."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import shutil
import unicodedata

KST = timezone(timedelta(hours=9), name="Asia/Seoul")


def image_extension(source):
    with source.open("rb") as handle:
        header = handle.read(12)
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if header.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return ".webp"
    raise ValueError("PNG, JPEG 또는 WebP 이미지가 필요합니다.")


def safe_title(title):
    title = unicodedata.normalize("NFC", title)
    title = re.sub(r"[^\w가-힣-]+", "_", title, flags=re.UNICODE)
    return title.strip("_-")[:50] or "툰"


def save_output(source, project, title, panels=4, layout="2x2",
                text_mode="none", reference_version="gangbyul-v1",
                panel=None, revision=None, details=None, now=None):
    source, project = Path(source).resolve(), Path(project).resolve()
    if not project.is_dir():
        raise ValueError("존재하는 작업 폴더를 지정하세요.")
    plugin_root = Path(__file__).resolve().parents[3]
    if project == plugin_root or plugin_root in project.parents:
        raise ValueError("플러그인 설치 폴더 밖의 작업 폴더를 지정하세요.")
    if panels < 1 or (panel is not None and not 1 <= panel <= panels):
        raise ValueError("컷 수와 개별 컷 번호를 확인하세요.")
    if revision is not None and revision < 1:
        raise ValueError("수정 번호는 1 이상이어야 합니다.")
    if text_mode not in {"none", "dialogue", "other"}:
        raise ValueError("텍스트 방식이 올바르지 않습니다.")
    if details is not None and not isinstance(details, dict):
        raise ValueError("추가 제작 기록은 JSON 객체여야 합니다.")
    extension = image_extension(source)
    moment = now or datetime.now(KST)
    if moment.tzinfo is None:
        raise ValueError("저장 시각에 시간대가 필요합니다.")
    moment = moment.astimezone(KST)
    base = f"{moment:%Y%m%d_%H%M%S}_{safe_title(title)}"
    if panel is not None:
        base += f"_{panel:02d}컷"
    if revision is not None:
        base += f"_수정{revision:02d}"
    output_dir = project / ".thesameimgs" / "outputs"
    # Avoid a redirected output folder escaping the user's selected project.
    if project not in output_dir.resolve().parents:
        raise ValueError("출력 폴더가 작업 폴더 밖을 가리킵니다.")
    output_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "saved_at": moment.isoformat(), "timezone": "Asia/Seoul",
        "title": title, "reference_version": reference_version,
        "panels": panels, "layout": layout, "text_mode": text_mode,
        "output_mode": "separate" if panel is not None else "sheet",
        "panel": panel, "revision": revision, "details": details or {},
    }
    # Exclusive opens protect originals even when two writers choose the same second.
    index = 1
    while True:
        stem = base if index == 1 else f"{base}_{index:02d}"
        destination = output_dir / (stem + extension)
        sidecar = output_dir / (stem + ".json")
        if sidecar.exists():
            index += 1
            continue
        try:
            output = destination.open("xb")
        except FileExistsError:
            index += 1
            continue
        try:
            metadata = sidecar.open("x", encoding="utf-8")
        except FileExistsError:
            output.close()
            destination.unlink()
            index += 1
            continue
        except BaseException:
            output.close()
            destination.unlink()
            raise
        try:
            with output, metadata, source.open("rb") as original:
                shutil.copyfileobj(original, output)
                record["file"] = destination.name
                json.dump(record, metadata, ensure_ascii=False, indent=2)
                metadata.write("\n")
        except BaseException:
            destination.unlink(missing_ok=True)
            sidecar.unlink(missing_ok=True)
            raise
        return {"image": str(destination), "record": str(sidecar)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--panels", type=int, default=4)
    parser.add_argument("--layout", default="2x2")
    parser.add_argument("--text-mode", choices=["none", "dialogue", "other"], default="none")
    parser.add_argument("--reference-version", default="gangbyul-v1")
    parser.add_argument("--panel", type=int)
    parser.add_argument("--revision", type=int)
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()
    try:
        details = json.loads(args.record.read_text(encoding="utf-8")) if args.record else None
        result = save_output(args.source, args.project, args.title, args.panels,
                             args.layout, args.text_mode, args.reference_version,
                             args.panel, args.revision, details)
    except (OSError, ValueError) as error:
        parser.exit(1, f"저장 실패: {error}\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
