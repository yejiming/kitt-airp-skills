# SillyTavern V2 中文化参考

## 镜像字段

很多 V2 卡同时在顶层和 `data` 中保存同一批字段。SillyTavern 读取时可能优先使用 `data`，所以只修改顶层会导致导入后仍显示旧内容。

常见镜像字段：

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

最终文件中，两处同名字段应完全相等。

## 翻译边界

保留：

- JSON 键名和 V2 结构字段
- `{{char}}`、`{{user}}`、`<START>`
- HTML 标签、CSS 属性、颜色值、布局结构
- lorebook/worldbook 的条目结构、id、keys、position、extensions
- 角色名、地名、阵营名等专有名词，除非中文化能保持辨识度

中文化：

- 角色简介、设定、人物口吻、场景、开场白、备用开场
- creator notes 中展示给用户看的介绍文字
- 明确表示语言的标签，例如将 `English` 替换为 `中文`
- 口语和吐槽要符合中文语境，不要保留英语句式

## 质量检查

完成后检查：

- 角色会默认用中文叙述和回复
- 开场白没有替 `{{user}}` 行动或决定身份
- `{{user}}` 身份仍按源卡保持开放或受场景约束
- 恐怖、恋爱、危险、边界等基调没有被翻丢
- `alternate_greetings` 数量与源卡一致，除非用户要求增删
- 空字段可以保持空，特别是源卡本来为空的 `mes_example`
