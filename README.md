# kitt-airp-skills

面向 [SillyTavern](https://docs.sillytavern.app/) 角色卡处理的 AI 编码助手技能集合，专注于中文角色卡的制作、转换与本地化。每个技能包含工作流说明（`SKILL.md`）、结构化脚本、字段参考资料以及 Agent 接口配置。

## 包含的技能

### character-museai-to-tavern

将 MuseAI 伙伴项目角色卡（`museai.partner-items` JSON）转换为可导入 SillyTavern 的中文角色卡 V2（`chara_card_v2`）。

- 整理零散的 MuseAI `fields` 为连贯的角色指令。
- 生成中文开场白、示例对话、备用开场与内嵌世界书。
- 保持 V2 顶层与 `data` 镜像字段一致。

```bash
python3 character-museai-to-tavern/scripts/convert_character.py 输入.json 输出.json
python3 character-museai-to-tavern/scripts/convert_character.py 输入.json 输出.json --card-name "角色名"
python3 character-museai-to-tavern/scripts/convert_character.py --validate-only 输出.json
```

### character-tavern-zh-localize

将英文 SillyTavern 角色卡 V2 中文化为自然中文角色卡，同时保留可导入结构、镜像字段、世界书和角色扮演功能。

- 翻译面向用户的文本载荷，保留 `{{char}}`、`{{user}}`、`<START>`、HTML/CSS 与键名。
- 同步顶层与 `data` 镜像字段，移除 `English` 标签并加入 `中文`。
- 不替 `{{user}}` 说话或行动，保持原角色边界与基调。

```bash
python3 character-tavern-zh-localize/scripts/localize_card.py 输入.json 输出.json
python3 character-tavern-zh-localize/scripts/localize_card.py --validate-only 输出.json
```

## 目录结构

```
.
├── character-museai-to-tavern/      # MuseAI → SillyTavern 转换技能
│   ├── SKILL.md                      # 技能工作流与输出要求
│   ├── scripts/convert_character.py  # 转换与校验脚本
│   ├── references/field-mapping.md   # MuseAI 字段到 ST 字段的映射参考
│   └── agents/openai.yaml            # Agent 接口配置
└── character-tavern-zh-localize/     # 英文 ST 卡中文化技能
    ├── SKILL.md
    ├── scripts/localize_card.py
    ├── references/sillytavern-v2-localization.md
    └── agents/openai.yaml
```

## 在 Claude Code 中使用

将技能目录软链接到 `.claude/skills/`，Claude Code 会自动发现 `SKILL.md` 并在涉及角色卡转换或中文化时调用：

```bash
mkdir -p .claude/skills
ln -s ../../character-museai-to-tavern .claude/skills/character-museai-to-tavern
ln -s ../../character-tavern-zh-localize .claude/skills/character-tavern-zh-localize
```

## 在 Codex 中使用

将技能目录软链接到 `.codex/skills/`，Codex 会加载技能并通过 `agents/openai.yaml` 暴露入口：

```bash
mkdir -p .codex/skills
ln -s ../../character-museai-to-tavern .codex/skills/character-museai-to-tavern
ln -s ../../character-tavern-zh-localize .codex/skills/character-tavern-zh-localize
```

