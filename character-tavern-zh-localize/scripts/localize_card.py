#!/usr/bin/env python3
"""Prepare and validate localized SillyTavern V2 character cards."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MIRRORED_FIELDS = [
    "name",
    "description",
    "personality",
    "scenario",
    "first_mes",
    "mes_example",
    "creator_notes",
    "system_prompt",
    "post_history_instructions",
    "alternate_greetings",
    "tags",
    "creator",
    "character_version",
    "extensions",
    "character_book",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("角色卡根节点必须是 JSON 对象")
    return data


def mirror_payload(card: dict[str, Any]) -> dict[str, Any]:
    if card.get("spec") != "chara_card_v2":
        raise ValueError("仅支持 spec=chara_card_v2 的 SillyTavern V2 角色卡")
    card["spec_version"] = str(card.get("spec_version") or "2.0")
    data = card.get("data")
    if not isinstance(data, dict):
        data = {}
        card["data"] = data

    for field in MIRRORED_FIELDS:
        if field in card:
            data[field] = card[field]
        elif field in data:
            card[field] = data[field]

    tags = card.get("tags")
    if isinstance(tags, list):
        cleaned = []
        for tag in tags:
            if str(tag).lower() == "english":
                continue
            cleaned.append(tag)
        if "中文" not in cleaned:
            cleaned.append("中文")
        card["tags"] = cleaned
        data["tags"] = cleaned

    return card


def validate(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if card.get("spec") != "chara_card_v2":
        errors.append("spec 必须是 chara_card_v2")
    if str(card.get("spec_version")) != "2.0":
        errors.append("spec_version 必须是 2.0")
    if not isinstance(card.get("data"), dict):
        errors.append("缺少 data 对象")

    data = card.get("data") if isinstance(card.get("data"), dict) else {}
    for field in MIRRORED_FIELDS:
        if field not in card:
            errors.append(f"顶层缺少字段：{field}")
        if field not in data:
            errors.append(f"data 缺少字段：{field}")
        if field in card and field in data and card[field] != data[field]:
            errors.append(f"镜像字段不一致：{field}")

    for field in ["name", "description", "scenario", "first_mes"]:
        value = card.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"关键文本字段为空：{field}")

    tags = card.get("tags")
    if isinstance(tags, list):
        if any(str(tag).lower() == "english" for tag in tags):
            errors.append("tags 中仍包含 English")
        if "中文" not in tags:
            errors.append("tags 中缺少 中文")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if args.validate_only:
        if not args.input or args.output:
            parser.error("--validate-only 只接受一个角色卡路径")
        card = load_json(args.input)
        errors = validate(card)
        if errors:
            for error in errors:
                print(f"[ERROR] {error}", file=sys.stderr)
            return 1
        print(f"[OK] {args.input} is a valid localized SillyTavern V2 card.")
        return 0

    if not args.input or not args.output:
        parser.error("需要 INPUT 和 OUTPUT")

    card = mirror_payload(load_json(args.input))
    errors = validate(card)
    # A source English card may fail the language tag check before manual localization.
    blocking = [error for error in errors if error not in ("tags 中缺少 中文",)]
    if blocking:
        for error in blocking:
            print(f"[ERROR] {error}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(card, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"[OK] Wrote mirrored draft: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
