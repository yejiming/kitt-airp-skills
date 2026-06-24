---
name: character-museai-to-tavern
description: 将 MuseAI 伙伴项目角色卡 JSON 转换为可导入 SillyTavern 的角色卡 V2 JSON，并保持、整理和补写中文角色内容。用户要求转换、迁移、重排、修复或批量处理 MuseAI 角色卡到 SillyTavern 时使用；也适用于中文开场白、示例对话、行为指令、备用开场、内嵌世界书或 V2 结构校验。
---

# MuseAI 角色卡转 SillyTavern

将 `museai.partner-items` JSON 中的一个 MuseAI 角色转换为打磨后的中文 SillyTavern 角色卡 V2。

## 工作流程

1. 完整读取源 JSON。选择用户指定的 `characterCards[]` 条目；如果文件中只有一个角色，自动使用它。
2. 运行内置转换脚本，先生成结构有效的草稿：

```bash
python3 scripts/convert_character.py INPUT.json OUTPUT.json
```

3. 阅读生成的草稿，并依据源文件事实继续打磨：

   - 所有面向角色扮演的内容都保持中文。SillyTavern 结构字段、`{{char}}`、`{{user}}` 和 `<START>` 可以保留原样。
   - 保留源文件中的身份、外貌、性格、价值观、能力、经历、关系、用户关系、边界和关键事件。
   - 将零散字段整理为连贯可用的角色指令，而不是直接堆叠原始键值对。
   - 编写有场景感的 `first_mes`，包含动作、对白、张力，并给 `{{user}}` 留出开放选择。
   - 编写至少三段有差异的 `mes_example` 交流，用来展示语气、反应、边界和关系动态。
   - 当源文件支持多个时期或场景时，添加两到三个 `alternate_greetings`。
   - 将稳定事实和受时间线影响的材料放入 `character_book.entries`。
   - 明确要求不得替 `{{user}}` 说话、思考、决定或行动。
   - 保持时间线一致，不要在对应时期之前泄露未来事实。
   - 不要发明与源文件冲突的身份特征、关系、能力或正史事件。

4. V2 中顶层和 `data` 内重复出现的载荷字段必须完全一致。编辑其中一处后，要同步镜像到另一处。
5. 校验最终文件：

```bash
python3 scripts/convert_character.py --validate-only OUTPUT.json
```

6. 汇报输出路径和校验结果。

## 输出要求

使用 `spec: "chara_card_v2"` 和 `spec_version: "2.0"`。必须包含：

- `name`
- `description`
- `personality`
- `scenario`
- `first_mes`
- `mes_example`
- `creator_notes`
- `system_prompt`
- `post_history_instructions`
- `alternate_greetings`
- `tags`
- `creator`
- `character_version`
- `extensions`
- `character_book`
- `data`，并镜像上方所有字段

除非用户要求改名或改路径，否则保留用户指定的目标位置和文件名。只有在用户明确要求，或请求清楚说明要原地转换时，才覆盖源文件。

## 参考资料

当源文件包含不熟悉的 MuseAI 字段、多个角色卡、关联世界书，或需要判断某条事实该放在哪里时，读取 [references/field-mapping.md](references/field-mapping.md)。

## 脚本行为

`scripts/convert_character.py` 支持：

```bash
python3 scripts/convert_character.py INPUT OUTPUT
python3 scripts/convert_character.py INPUT OUTPUT --card-name "角色名"
python3 scripts/convert_character.py --validate-only OUTPUT
```

脚本输出只是结构有效的草稿，不能替代针对具体角色的写作打磨和事实复核。
