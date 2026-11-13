# Mindustry: Project Shattered Star · 源码仓库

基于 **Anuken/Mindustry v160.7**（GPL-3.0）的完整游戏源码，并把
《碎星计划》模组**直接改源码集成进游戏本体**——不是外挂 Mod jar。

> 上游原始 README 保留在 [`README-UPSTREAM.md`](README-UPSTREAM.md)。
> 本仓库为非官方粉丝衍生项目，与 Mindustry 官方无关。

## 快速开始

需要 **JDK 17**：

```bash
JAVA_HOME=/path/to/jdk17 ./gradlew desktop:dist
java -jar desktop/build/libs/Mindustry.jar
```

产物是单一 `Mindustry.jar`，**自带碎星计划全部内容**，运行时不需要
`%APPDATA%/Mindustry/mods/` 目录，也不需要安装任何 Mod 或 Java（分发包内置 JRE）。

## 集成了什么

| 改动 | 位置 |
| --- | --- |
| 模组 Java 类（44 个，编译进游戏 jar） | `core/src/project/**` |
| 模组资源（贴图/音频/内容 JSON/JS/语言包） | `core/assets/shattered-star.zip` |
| 引擎注册内置内容包 | `core/src/mindustry/mod/Mods.java` |

详细原理见 [`SHATTERED_STAR.md`](SHATTERED_STAR.md)。

## 许可

GPL-3.0。分发二进制时必须随附 `LICENSE`、`NOTICE`、`SOURCES.md` 与对应源码。
详见 [`NOTICE`](NOTICE) 与 [`SOURCES.md`](SOURCES.md)。
