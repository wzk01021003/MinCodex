# Project Shattered Star · 源码级内置说明

本仓库是 **Anuken/Mindustry v160.7**（GPL-3.0）的源码副本，并在此基础上把
《Mindustry: Project Shattered Star / 碎星计划》**直接改源码集成进游戏本体**。

## 与「外挂 Mod」的区别

原版做法是把 `ProjectShatteredStar.jar` 放进 `mods/` 目录，由引擎当插件加载。
本仓库改为：

| 项目 | 原版（外挂 Mod） | 本仓库（源码内置） |
| --- | --- | --- |
| 模组 Java 类 | 独立 jar，独立 ClassLoader | `core/src/project/**`，编译进游戏 jar |
| 模组资源 | 独立 jar / 目录 | `core/assets/shattered-star.zip`，随 jar 分发 |
| 内容注册 | `ModClassLoader` 加载 | `Mods.load()` 里手工注册内置 `LoadedMod` |
| 运行时 | 需要 `%APPDATA%/Mindustry/mods/` | 不需要，游戏本体自带 |
| 引擎改动 | 无 | 修改 `core/src/mindustry/mod/Mods.java` |

## 为什么仍保留 `LoadedMod`

`LoadedMod` 不是「外挂」，而是引擎内部表示一份内容包的数据结构。
手工构造它，可以复用引擎原有的 `ContentParser`（解析 `content/*.json`）、
JS 脚本执行、贴图打包与 bundle 加载流程，从而让 `ss-` 前缀、
贴图 region 名、语言包键全部自动对齐——不需要重写任何内容定义，
也不会出现贴图丢失或翻译失效。

`ClientLauncher` 里的 `mods.eachClass(Mod::init)` 会自动调用内置 mod 的
`init()`，`Mods.loadContent()` 会自动调用 `loadContent()`。

## 构建

需要 JDK 17：

```bash
JAVA_HOME=/opt/jdk17 ./gradlew desktop:dist
# 产物：desktop/build/libs/Mindustry.jar（单一 jar，自带碎星计划内容）
java -jar desktop/build/libs/Mindustry.jar
```

## 许可与合规

- Mindustry 本体：**GPL-3.0**，见 `LICENSE`。版权归 Anuken 及贡献者。
- 本仓库是 GPL-3.0 作品的衍生作品，同样以 **GPL-3.0** 分发；
  分发二进制时必须随附 `LICENSE`、`NOTICE`、`SOURCES.md` 与对应源码。
- 碎星计划 Mod 内容版权归 A4PAPER / `wzk01021003`。
- 详见 `NOTICE` 与 `SOURCES.md`。

本仓库为非官方粉丝衍生项目，与 Anuken/Mindustry 官方无关。
