# Grasshopper Plug-in Development Skills

面向 Rhino / Grasshopper C# 插件开发的可复用技能库。经验来自 [Moyu](https://github.com/ChenmingHe0126/moyu) 的实际实现、测试和发布，以及 QSM 图标设计迭代。

图标制作只是其中一个模块。这个仓库覆盖组件契约、状态与序列化、交互和视口、分层测试、构建与发布。

## 技能入口

| 技能 | 适用任务 |
| --- | --- |
| [grasshopper-plugin-development](skills/grasshopper-plugin-development/SKILL.md) | 新组件、架构调整、数据类型、状态与持久化；不确定从哪里开始时使用 |
| [grasshopper-interaction-display](skills/grasshopper-interaction-display/SKILL.md) | GH 自绘界面、Rhino 视口、输入与焦点、定时会话、DPI 和多语言 |
| [grasshopper-testing](skills/grasshopper-testing/SKILL.md) | 纯核心测试、Rhino 宿主集成、保存重开、真实界面验证 |
| [grasshopper-build-release](skills/grasshopper-build-release/SKILL.md) | 目标运行时、资源与依赖、版本一致性、Yak / ZIP 发布准备 |
| [grasshopper-icons](skills/grasshopper-icons/SKILL.md) | 功能语义、成套设计、24px 透明 PNG、预览与资源接入 |

每个目录都是独立的 `SKILL.md` 技能包，包含按需读取的参考资料。需要哪个任务，就加载对应技能；不需要一次读取整库。

## 使用

克隆仓库后，把需要的完整技能目录放到所用 coding agent 支持的技能目录中，或直接让 agent 阅读对应 `SKILL.md`。保留技能内的 `references/`、`scripts/` 和 `agents/`，不要只复制入口文件。

例如：

- “用 grasshopper-plugin-development 给现有插件增加一个可以保存、重开的状态型组件。”
- “用 grasshopper-testing 区分核心算法通过与 Rhino 实际界面通过。”
- “用 grasshopper-icons 做一组能在 24×24 下区分功能的组件图标。”
- “用 grasshopper-build-release 检查这次 Yak 包有没有装入旧版本程序集。”

## 这份经验与普通教程的区别

- 从真实代码提炼可迁移的决策，不复制整套 Moyu，也不把它的历史限制当作 Grasshopper 限制。
- 保留踩坑及修正：丢失按键释放、跨文档残留、Goo 共享引用与持久化、旧程序集误测、版本号不一致、图标透明度与资源缓存。
- 清楚区分“已在代码看到”“历史报告记录通过”“本次重新执行通过”；不把截图或无界面绘图说成真实交互验收。
- 根据实际 Rhino 版本和宿主运行时选择框架，不把 Moyu 的历史 net7/net48 组合写成新项目默认配置。
- 图标工具处理独立 PNG 或 manifest 指定的图标表，保留白色内容和预乘 alpha，检查真实 24px 效果。

详见 [Moyu 案例与证据](docs/moyu-case-study.md)。

## 维护与验证

```text
python -m pip install -r requirements-dev.txt
python scripts/validate_repository.py
python -m unittest discover -s tests
python -m unittest discover -s skills/grasshopper-icons/scripts -p "test_*.py"
```

工具只验证它实际观察到的内容。发布包检查不会启动 Rhino 或证明程序集版本正确；图像导出不会证明 Grasshopper 已加载资源。

技能、文档和工具采用 [MIT](LICENSE) 许可。Moyu 来源及归属见 [NOTICE](NOTICE)；未包含其品牌图标、录制素材、聊天记录或插件二进制。
