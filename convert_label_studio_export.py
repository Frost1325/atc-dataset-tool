from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Label Studio audio export JSON into a flat dataset."
    )
    parser.add_argument("input", help="Path to the Label Studio exported JSON file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Output JSON path. Defaults to <input_stem>.dataset.json",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indent for output JSON. Defaults to 2.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pick_latest_annotation(task: dict[str, Any]) -> dict[str, Any] | None:
    annotations = task.get("annotations") or []
    if not annotations:
        return None
    return max(annotations, key=lambda item: item.get("updated_at") or item.get("created_at") or "")


def extract_original_filename(task: dict[str, Any]) -> str:
    file_upload = task.get("file_upload") or ""
    if not file_upload:
        return ""

    parts = file_upload.split("-", 2)
    if len(parts) == 3:
        return parts[2]
    return file_upload


def build_record_base(task: dict[str, Any], annotation: dict[str, Any], region_id: str) -> dict[str, Any]:
    project_id = task.get("project")
    task_id = task.get("id")
    annotation_id = annotation.get("id")
    original_filename = extract_original_filename(task)

    return {
        "id": f"project{project_id}_task{task_id}_annotation{annotation_id}_{region_id}",
        "project_id": project_id,
        "task_id": task_id,
        "annotation_id": annotation_id,
        "region_id": region_id,
        "audio": original_filename,
        "start": None,
        "end": None,
        "text": "",
        "speaker": "",
        "language": "",
        "label": "",
    }


def flatten_task(task: dict[str, Any]) -> list[dict[str, Any]]:
    annotation = pick_latest_annotation(task)
    if not annotation:
        return []

    grouped: dict[str, dict[str, Any]] = {}
    for item in annotation.get("result") or []:
        region_id = item.get("id")
        if not region_id:
            continue

        record = grouped.setdefault(region_id, build_record_base(task, annotation, region_id))
        value = item.get("value") or {}

        if record["start"] is None and "start" in value:
            record["start"] = value.get("start")
        if record["end"] is None and "end" in value:
            record["end"] = value.get("end")

        item_type = item.get("type")
        from_name = item.get("from_name")

        if item_type == "labels":
            labels = value.get("labels") or []
            if labels:
                record["label"] = labels[0]
        elif item_type == "textarea":
            texts = value.get("text") or []
            if texts:
                record["text"] = "\n".join(texts).strip()
        elif item_type == "choices":
            choices = value.get("choices") or []
            if not choices:
                continue
            if from_name == "speaker":
                record["speaker"] = choices[0]
            elif from_name == "language":
                record["language"] = choices[0]

    records = list(grouped.values())
    records.sort(key=lambda item: (item["task_id"], item["start"] if item["start"] is not None else float("inf")))
    return records


def convert_export(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dataset: list[dict[str, Any]] = []
    for task in tasks:
        dataset.extend(flatten_task(task))
    return dataset


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_name(f"{input_path.stem}.dataset.json")
    )

    if not input_path.exists():
        print(f"[ERROR] Input file does not exist: {input_path}")
        return 1

    tasks = load_json(input_path)
    if not isinstance(tasks, list):
        print("[ERROR] Expected a JSON array exported from Label Studio.")
        return 1

    dataset = convert_export(tasks)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=args.indent)

    print(f"[OK] Wrote {len(dataset)} records to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
