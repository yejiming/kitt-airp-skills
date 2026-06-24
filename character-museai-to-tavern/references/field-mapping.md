# 字段映射

按含义将 MuseAI `characterCards[].fields` 映射到 SillyTavern 字段，不要机械依赖原始键名。

| MuseAI 内容 | SillyTavern 目标位置 |
|---|---|
| 姓名、年龄、性别、种族、出生地、职业、阶层 | `description` 中的基础资料 |
| 身高体型、标志性特征、服装、整体气质 | `description` 中的外貌描写 |
| 外在/内在性格、愿望、恐惧、价值观、习惯 | `description` 和简洁的 `personality` |
| 技能和物品 | `description`；内容较多时放入世界书条目 |
| 背景故事 | `description`；时间线类世界书条目 |
| 人际关系 | `description`；关系类世界书条目 |
| 说话风格和典型反应 | `description`、`mes_example`、`post_history_instructions` |
| 与用户的关系类型、互动模式、底线 | `description`、`scenario`、`post_history_instructions`、常驻用户关系世界书条目 |
| 关键事件 | 时间线类世界书条目，也可用于备用开场 |
| 身份标签 | `tags` |

## 世界书

如果 `worldBooks` 包含该角色卡的 `worldBookId`，将有用条目保留到 `character_book`。合并重复信息，丢弃仅供应用内部使用的 ID 或时间戳。优先整理为 4 到 10 条聚焦条目，可按以下类型分组：

- 核心冲突或反派；
- 亲密关系；
- 能力与重要物品；
- 地点与组织；
- 事件时间线；
- 与 `{{user}}` 的关系。

关键词数组应使用对话中可能触发的词。与 `{{user}}` 的关系条目设为 `constant: true`；大型背景和时间线条目不要设为常驻。

## 中文保留

只翻译参考卡或模板额外带入的外语正文。不要翻译 JSON 结构字段、占位符或 `<START>`。检查面向角色扮演的字段，确保没有意外残留的英文段落。

## 质量边界

保留源文件事实，同时提升可用性。可以添加中性的衔接文字、场景框架和行为约束。不要添加源文件不支持的恋爱关系、性内容、能力、诊断、死亡或正史结局。
