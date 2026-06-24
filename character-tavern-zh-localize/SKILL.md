---
name: character-tavern-zh-localize
description: 将英文 SillyTavern 角色卡 JSON 中文化为可导入的中文角色卡，并保持原有 V2 结构、镜像字段、开场白、备用开场、作者说明、标签和角色扮演功能一致。用户要求翻译、汉化、本地化、润色、修复或批量处理英文 SillyTavern/chara_card_v2 角色卡，让角色默认用中文回复时使用。
---

# SillyTavern 角色卡中文化

把英文 `chara_card_v2` JSON 改写成自然中文角色卡，同时保留 SillyTavern 可导入结构和玩法功能。

## 工作流程

1. 完整读取源 JSON，确认 `spec`、`spec_version`、顶层字段和 `data` 镜像字段。
2. 运行结构脚本生成草稿或校验目标：

```bash
python3 scripts/localize_card.py INPUT.json OUTPUT.json
python3 scripts/localize_card.py --validate-only OUTPUT.json
```

3. 逐字段中文化并润色所有可玩内容：

   - 翻译 `description`、`scenario`、`first_mes`、`mes_example`、`creator_notes`、`post_history_instructions`、`alternate_greetings`、`character_book.entries[].content` 等文本载荷。
   - 保留 `{{char}}`、`{{user}}`、`<START>`、HTML 标签、CSS 样式、世界书结构、扩展字段和导入所需键名。
   - 将角色默认语言写清楚：叙述、心理、动作和对白均使用自然中文；只有专有名词、用户输入或剧情需要时才保留外语。
   - 译名要稳定；如果原名有辨识度，可以用中文名加括号原名，或保留英文名但中文化标题。
   - 不要逐词硬翻。末世、科幻、恋爱、恐怖、日常等类型词要按中文网文/跑团/角色扮演习惯改写。
   - 保持原角色事实、边界、身份、关系动态、开场局势和用户自由度一致；不要替 `{{user}}` 说话、思考、决定或行动。
   - 如果源卡的 `mes_example` 为空，可以保持为空；不要为了“完整”补写会改变原卡行为的示例。
   - 标签可中文化或保留常用英文标签，但要移除/替换表示语言的 `English` 标签，加入 `中文`。

4. 同步镜像字段。V2 卡中顶层和 `data` 同名字段必须完全一致。
5. 校验最终 JSON：

```bash
python3 scripts/localize_card.py --validate-only OUTPUT.json
python3 -m json.tool OUTPUT.json >/dev/null
```

6. 汇报输出路径、是否保留源文件、校验结果，以及任何有意保留英文的项目。

## 字段要求

必须保留：

- `spec: "chara_card_v2"`
- `spec_version: "2.0"`
- 顶层 `data`
- 顶层与 `data` 内的可镜像字段：`name`、`description`、`personality`、`scenario`、`first_mes`、`mes_example`、`creator_notes`、`system_prompt`、`post_history_instructions`、`alternate_greetings`、`tags`、`creator`、`character_version`、`extensions`、`character_book`

除非用户明确要求原地覆盖，否则输出到新文件。

## 参考资料

需要判断字段是否该翻译、保留、补写或同步时，读取 [references/sillytavern-v2-localization.md](references/sillytavern-v2-localization.md)。
