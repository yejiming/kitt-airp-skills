#!/usr/bin/env python3
"""将 MuseAI 伙伴项目角色卡转换为 SillyTavern V2 草稿。"""

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


class ChineseArgumentParser(argparse.ArgumentParser):
    def format_usage(self) -> str:
        return super().format_usage().replace("usage:", "用法:", 1)

    def format_help(self) -> str:
        return super().format_help().replace("usage:", "用法:", 1)


def text(fields: dict[str, Any], key: str, fallback: str = "未说明") -> str:
    value = fields.get(key)
    if isinstance(value, list):
        return "、".join(str(item) for item in value) or fallback
    if value is None or value == "":
        return fallback
    return str(value)


def section(title: str, rows: list[tuple[str, str]]) -> str:
    lines = [f"## {title}"]
    lines.extend(f"{label}：{value}" for label, value in rows if value != "未说明")
    return "\n".join(lines)


def lore_entry(
    entry_id: int,
    name: str,
    keys: list[str],
    content: str,
    *,
    constant: bool = False,
    order: int = 10,
) -> dict[str, Any]:
    return {
        "id": entry_id,
        "keys": keys,
        "secondary_keys": [],
        "comment": name,
        "content": content,
        "constant": constant,
        "selective": False,
        "insertion_order": order,
        "enabled": True,
        "position": "after_char",
        "extensions": {},
    }


def select_card(source: dict[str, Any], card_name: str | None) -> dict[str, Any]:
    if source.get("spec") == "chara_card_v2":
        raise ValueError("输入文件已经是 SillyTavern 角色卡 V2")
    cards = source.get("characterCards")
    if not isinstance(cards, list) or not cards:
        raise ValueError("未找到 MuseAI characterCards 数组")
    if card_name:
        matches = [card for card in cards if card.get("name") == card_name]
        if len(matches) != 1:
            raise ValueError(f"无法唯一匹配角色：{card_name}")
        return matches[0]
    if len(cards) != 1:
        names = "、".join(str(card.get("name", "未命名")) for card in cards)
        raise ValueError(f"文件包含多个角色，请使用 --card-name 指定：{names}")
    return cards[0]


def build_card(source: dict[str, Any], card_name: str | None) -> dict[str, Any]:
    card = select_card(source, card_name)
    fields = card.get("fields")
    if not isinstance(fields, dict):
        raise ValueError("角色缺少 fields 对象")

    name = str(card.get("name") or fields.get("name") or "未命名角色")
    profile = section(
        "{{char}}基本资料",
        [
            ("姓名", name),
            ("年龄", text(fields, "age")),
            ("性别", text(fields, "gender")),
            ("种族", text(fields, "race")),
            ("出生地", text(fields, "birthplace")),
            ("身份与职业", text(fields, "occupation")),
            ("社会背景", text(fields, "socialClass")),
        ],
    )
    appearance = section(
        "外貌与气质",
        [
            ("身高与体型", text(fields, "heightBuild")),
            ("标志性特征", text(fields, "iconicFeatures")),
            ("穿衣风格", text(fields, "clothingStyle")),
            ("整体气质", text(fields, "overallVibe")),
        ],
    )
    character = section(
        "性格与内心",
        [
            ("外在性格", text(fields, "externalPersonality")),
            ("内在性格", text(fields, "internalPersonality")),
            ("核心愿望", text(fields, "coreDesire")),
            ("恐惧与弱点", text(fields, "fearWeakness")),
            ("道德观念", text(fields, "moralValues")),
            ("习惯", text(fields, "quirk")),
            ("典型反应", text(fields, "typicalReactions")),
        ],
    )
    history = section(
        "能力、经历与关系",
        [
            ("能力与物品", text(fields, "skills")),
            ("背景故事", text(fields, "backgroundStory")),
            ("人际关系", text(fields, "relationships")),
        ],
    )
    user_relation = section(
        "与{{user}}的关系",
        [
            ("关系定位", text(fields, "userRelationType")),
            ("互动模式", text(fields, "userInteractionModel")),
            ("关系底线", text(fields, "userRelationBottomLine")),
        ],
    )
    description = "\n\n".join(
        block for block in [profile, appearance, character, history, user_relation] if block
    )

    personality = "；".join(
        value
        for value in [
            text(fields, "externalPersonality", ""),
            text(fields, "internalPersonality", ""),
            text(fields, "moralValues", ""),
        ]
        if value
    )
    scenario = (
        f"{{{{char}}}}是{name}。{{{{user}}}}与{{{{char}}}}的关系是："
        f"{text(fields, 'userRelationType')}。故事应依据角色背景和关键事件展开，"
        "全部叙述与对白使用中文，并为{{user}}保留行动和选择空间。"
    )
    first_mes = (
        f"*{{{{char}}}}注意到{{{{user}}}}走近，短暂地停下了手中的动作。"
        f"此刻的{{{{char}}}}仍带着{text(fields, 'overallVibe', '熟悉而复杂的气质')}。*\n\n"
        f"“你来了，{{{{user}}}}。”\n\n"
        "*{{char}}像是有一件重要的事想说，却先观察着{{user}}的反应。*\n\n"
        "“我正需要一个可以信任的人。你愿意听听发生了什么吗？”"
    )
    speaking = text(fields, "speakingStyle", "说话自然，并符合角色身份与处境")
    reactions = text(fields, "typicalReactions", "根据危险、误解和关系变化作出合理反应")
    mes_example = (
        "<START>\n"
        "{{user}}：“你真的没事吗？”\n"
        f"{{{{char}}}}：*{{{{char}}}}沉默片刻，显然不习惯立刻袒露自己。*\n\n"
        f"“我会处理好的。只是……{text(fields, 'fearWeakness', '有些事情比看上去更复杂')}。”\n\n"
        "<START>\n"
        "{{user}}：“我们可以一起想办法。”\n"
        f"{{{{char}}}}：*{{{{char}}}}的神情稍稍缓和。*\n\n"
        f"“好。但你要明白，{text(fields, 'userRelationBottomLine', '我不会拿你的安全冒险')}。”\n\n"
        "<START>\n"
        "{{user}}：“那你打算怎么做？”\n"
        f"{{{{char}}}}：*{{{{char}}}}按照一贯的方式迅速权衡局势。{reactions}*\n\n"
        "“先弄清楚真相，再决定下一步。你怎么看？”"
    )
    instructions = (
        "始终使用中文进行叙述和对白。\n\n"
        "扮演{{char}}并描写必要的环境与配角，但绝不替{{user}}说话、思考、"
        "选择或行动。每次回复都应为{{user}}留下明确的行动空间。\n\n"
        f"保持角色说话方式：{speaking}。\n\n"
        "保持身份、能力、关系和时间线一致。角色可以犯错、受伤、误判或不知道答案，"
        "不得表现得全知全能。关系必须通过互动自然发展，不得强迫{{user}}接受亲密或浪漫关系。"
    )

    tags_value = fields.get("identityTags", [])
    tags = [str(item) for item in tags_value] if isinstance(tags_value, list) else [str(tags_value)]
    if "中文" not in tags:
        tags.insert(0, "中文")

    entries = [
        lore_entry(
            1,
            "能力与重要物品",
            ["能力", "技能", "物品", "战斗"],
            text(fields, "skills"),
            order=10,
        ),
        lore_entry(
            2,
            "背景故事",
            ["过去", "身世", "出生", "经历"],
            text(fields, "backgroundStory"),
            order=20,
        ),
        lore_entry(
            3,
            "人际关系",
            ["家人", "朋友", "同伴", "敌人", "关系"],
            text(fields, "relationships"),
            order=30,
        ),
        lore_entry(
            4,
            "关键事件",
            ["事件", "冒险", "危机", "过去"],
            text(fields, "keyEvents"),
            order=40,
        ),
        lore_entry(
            5,
            "{{user}}与{{char}}",
            ["{{user}}", "信任", "保护", "伙伴"],
            (
                f"关系定位：{text(fields, 'userRelationType')}。"
                f"互动模式：{text(fields, 'userInteractionModel')}。"
                f"底线：{text(fields, 'userRelationBottomLine')}。"
            ),
            constant=True,
            order=50,
        ),
    ]
    entries = [entry for entry in entries if entry["content"] != "未说明"]
    book = {
        "name": f"{name}世界书",
        "description": "保存角色稳定事实、关系和关键事件。",
        "scan_depth": 4,
        "token_budget": 2048,
        "recursive_scanning": False,
        "extensions": {},
        "entries": entries,
    }
    extensions = {
        "depth_prompt": {
            "prompt": "保持角色身份、人物关系和时间线一致；不要替{{user}}行动。",
            "depth": 4,
        },
        "visual_description": text(fields, "iconicFeatures", ""),
    }
    payload = {
        "name": name,
        "description": description,
        "personality": personality,
        "scenario": scenario,
        "first_mes": first_mes,
        "mes_example": mes_example,
        "creator_notes": "由 MuseAI 角色卡转换而成的 SillyTavern 角色卡 V2 中文草稿。",
        "system_prompt": "",
        "post_history_instructions": instructions,
        "alternate_greetings": [],
        "tags": tags,
        "creator": "MuseAI",
        "character_version": "2.0",
        "extensions": extensions,
        "character_book": book,
    }
    return {
        "spec": "chara_card_v2",
        "spec_version": "2.0",
        **payload,
        "data": json.loads(json.dumps(payload, ensure_ascii=False)),
    }


def validate(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if card.get("spec") != "chara_card_v2":
        errors.append('spec 必须为 "chara_card_v2"')
    if card.get("spec_version") != "2.0":
        errors.append('spec_version 必须为 "2.0"')
    data = card.get("data")
    if not isinstance(data, dict):
        return errors + ["缺少 data 对象"]
    for key in MIRRORED_FIELDS:
        if key not in card:
            errors.append(f"顶层缺少字段：{key}")
        if key not in data:
            errors.append(f"data 缺少字段：{key}")
        if key in card and key in data and card[key] != data[key]:
            errors.append(f"顶层与 data 字段不一致：{key}")
    if not isinstance(card.get("character_book", {}).get("entries"), list):
        errors.append("character_book.entries 必须为数组")
    return errors


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("JSON 顶层必须是对象")
    return value


def main() -> int:
    parser = ChineseArgumentParser(description=__doc__, add_help=False)
    parser._positionals.title = "位置参数"
    parser._optionals.title = "选项"
    parser.add_argument("-h", "--help", action="help", help="显示帮助信息并退出")
    parser.add_argument("input", type=Path, metavar="输入文件", help="MuseAI 输入文件，或待验证的 V2 文件")
    parser.add_argument("output", type=Path, nargs="?", metavar="输出文件", help="SillyTavern 输出文件")
    parser.add_argument("--card-name", metavar="角色名", help="多角色文件中的精确角色名")
    parser.add_argument("--validate-only", action="store_true", help="只验证 V2 文件")
    args = parser.parse_args()

    try:
        source = load_json(args.input)
        if args.validate_only:
            errors = validate(source)
            if errors:
                print("\n".join(f"错误：{error}" for error in errors), file=sys.stderr)
                return 1
            print(f"验证通过：{args.input}")
            return 0
        if args.output is None:
            parser.error("转换模式必须提供输出文件")
        result = build_card(source, args.card_name)
        errors = validate(result)
        if errors:
            raise ValueError("生成结果无效：" + "；".join(errors))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print(f"转换完成：{args.output}")
        print(f"角色：{result['name']}；世界书条目：{len(result['character_book']['entries'])}")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
