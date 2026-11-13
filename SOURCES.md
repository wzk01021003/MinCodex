SOURCES.md — 组件源码与复现构建
================================

本文件说明本仓库中每一部分内容的来源，以及如何从源码复现构建，
以满足 GPL-3.0 对「提供对应源码」的要求。

## 组件清单

| 组件 | 版本 / 标识 | 来源 | 许可 |
| --- | --- | --- | --- |
| Mindustry 本体 | v160.7 (Build 160.7) | https://github.com/Anuken/Mindustry/tree/v160.7 | GPL-3.0 |
| Arc 引擎 | 与 v160.7 `archash` 对齐 | https://github.com/Anuken/Arc | GPL-3.0 |
| 碎星计划 Mod | 0.2.0 | https://github.com/wzk01021003/Mindustry-Project-Shattered-Star | 作者 A4PAPER |
| 集成补丁 | 本仓库新增 | `core/src/mindustry/mod/Mods.java` | GPL-3.0 |

本仓库的完整对应源码即本仓库自身；`git clone` 本仓库即可获得全部内容，
包括所有 Java 源码、Gradle 构建脚本、贴图、音频、内容 JSON、JS 脚本与语言包。

## 源码级集成做了什么

| 改动 | 位置 |
| --- | --- |
| 模组 Java 类并入引擎源码树 | `core/src/project/**`（44 个类，编译进游戏 jar） |
| 模组资源打包随 jar 分发 | `core/assets/shattered-star.zip` |
| 引擎注册内置内容包 | `core/src/mindustry/mod/Mods.java` 中 `Mods.load()` 末尾 |
| 集成与合规说明 | `SHATTERED_STAR.md`、`NOTICE`、`SOURCES.md` |

详细原理见 `SHATTERED_STAR.md`。简言之：手工构造一个 `LoadedMod`，复用引擎
原有的 `ContentParser`、JS 脚本执行、贴图打包与 bundle 加载流程，
因此内容命名前缀、贴图 region 名与语言包键全部自动对齐，无需重写内容定义。
运行时不需要 `%APPDATA%/Mindustry/mods/`，也不加载外部 mod jar。

## 复现构建

要求：**JDK 17**（Mindustry v160.7 官方要求）。

```bash
git clone https://github.com/wzk01021003/<本仓库名>.git
cd <本仓库名>
JAVA_HOME=/path/to/jdk17 ./gradlew desktop:dist
# 产物：desktop/build/libs/Mindustry.jar
java -jar desktop/build/libs/Mindustry.jar
```

Gradle 依赖（含 Arc）由官方构建脚本拉取。若 jitpack 访问不稳定，
可把 `gradle/wrapper/gradle-wrapper.properties` 换成可用的 Gradle 镜像。

## 复现集成（可选）

CI 中的集成流程由 `scripts/integrate.py` 完成，可本地重跑：

```bash
git clone --depth 1 --branch v160.7 https://github.com/Anuken/Mindustry.git /tmp/upstream
git clone --depth 1 https://github.com/wzk01021003/Mindustry-Project-Shattered-Star.git /tmp/modrepo
python3 scripts/integrate.py /tmp/upstream /tmp/modrepo <目标源码目录>
```

## GPL-3.0 合规动作

- 保留上游 `LICENSE`（GPL-3.0 全文）与全部版权声明。
- 附 `NOTICE` 列明各组件来源、作者与许可。
- 附本 `SOURCES.md` 提供对应源码获取方式与复现步骤。
- 不添加任何限制再分发的条款；二进制分发包随附上述三份文件。
- 内置 JRE（分发包）为 GPL-2.0 with Classpath Exception，其许可文本
  保留在 `jre/legal/`。
