#!/usr/bin/env python3
"""
把《碎星计划》源码级内置进 Mindustry v160.7 源码树。

用法:
    python3 scripts/integrate.py <upstream_dir> <mod_repo_dir> <work_dir>

产物（写入 work_dir）:
    core/src/project/**                 模组 Java 类（编译进游戏 jar）
    core/assets/shattered-star.zip      模组资源（贴图/声音/JSON/JS/bundle）
    core/src/mindustry/mod/Mods.java    打补丁：注册内置 LoadedMod
    SHATTERED_STAR.md                   集成与合规说明

设计要点：
    不重写任何内容定义。手工构造一个 LoadedMod，复用引擎原有的
    ContentParser / JS 脚本 / 贴图打包 / bundle 加载流程，
    因此 content/*.json 的 ss- 前缀、贴图 region 名、语言包键全部自动对齐。
    运行时不再需要外部 mods 目录，也不再加载外部 mod jar。
"""
import shutil
import sys
import zipfile
from pathlib import Path

OLD = """        for(var mod : mods){
            // Skip mods where the state has already been resolved
            if(mod.state != ModState.enabled) continue;
            if(!mod.isSupported()){
                mod.state = ModState.unsupported;
            }else if(!mod.shouldBeEnabled()){
                mod.state = ModState.disabled;
            }
        }

        sortMods();
        buildFiles();"""

NEW = """        for(var mod : mods){
            // Skip mods where the state has already been resolved
            if(mod.state != ModState.enabled) continue;
            if(!mod.isSupported()){
                mod.state = ModState.unsupported;
            }else if(!mod.shouldBeEnabled()){
                mod.state = ModState.disabled;
            }
        }

        // === Project Shattered Star: source-integrated built-in mod ===
        // 碎星计划已直接集成进游戏本体：Java 类编译进本 jar，资源随 jar 分发。
        // 这里手工构造 LoadedMod，复用引擎原有的 ContentParser / JS 脚本 /
        // 贴图打包 / bundle 加载流程，保证 ss- 前缀与内容定义完全一致，
        // 运行时不再需要外部 mods 目录或额外的 mod jar。
        try{
            if(mods.find(m -> m.name.equals("ss")) == null){
                Fi builtinSrc = Core.files.internal("shattered-star.zip");
                if(builtinSrc.exists()){
                    // 解压成真实的「文件夹 mod」：引擎 buildFiles() 只对目录 mod
                    // 计算正确的文件树路径，ZipFi 会让 maps/ 与 sounds/ 无法被
                    // Core.files.internal() 命中。目录放在可写的数据目录下。
                    Fi builtinDir = dataDirectory.child("shattered-star-builtin");
                    if(builtinDir.exists()) builtinDir.deleteDirectory();
                    builtinDir.mkdirs();
                    try(java.util.zip.ZipInputStream in = new java.util.zip.ZipInputStream(builtinSrc.read())){
                        java.util.zip.ZipEntry entry;
                        byte[] buffer = new byte[8192];
                        while((entry = in.getNextEntry()) != null){
                            if(entry.isDirectory()) continue;
                            Fi target = builtinDir.child(entry.getName());
                            target.parent().mkdirs();
                            try(OutputStream out = target.write(false)){
                                int count;
                                while((count = in.read(buffer)) > 0) out.write(buffer, 0, count);
                            }
                            in.closeEntry();
                        }
                    }
                    Fi builtinRoot = resolveRoot(builtinDir);
                    ModMeta builtinMeta = findMeta(builtinRoot);
                    if(builtinMeta != null){
                        LoadedMod builtin = new LoadedMod(builtinRoot, builtinRoot,
                            new project.ShatteredStarMod(), null, builtinMeta);
                        builtin.state = ModState.enabled;
                        mods.add(builtin);
                        lastOrderedMods = null;
                        Log.info("[Shattered Star] Built-in content registered.");
                    }else{
                        Log.warn("[Shattered Star] Built-in mod.hjson not found, skipping.");
                    }
                }else{
                    Log.warn("[Shattered Star] Built-in resource shattered-star.zip not found, skipping.");
                }
            }
        }catch(Throwable t){
            Log.err("[Shattered Star] Failed to register built-in content", t);
        }

        sortMods();
        buildFiles();"""

HOMEPAGE = """# Mindustry: Project Shattered Star · 源码仓库

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
"""

NOTES = """# Project Shattered Star · 源码级内置说明

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
"""


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    upstream, modrepo, work = map(lambda p: Path(p).resolve(), sys.argv[1:4])
    work.mkdir(parents=True, exist_ok=True)

    # 1. 复制完整上游源码（含二进制 assets），保留工作区已有的引导文件
    print("[1/5] 复制 Mindustry v160.7 完整源码 …")
    shutil.copytree(upstream, work, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('.git'))
    # 上游自带一批官方 CI 配置，在新仓库里会因缺少 secrets 而失败；
    # 只保留本仓库自己的引导 workflow。
    wf = work / '.github' / 'workflows'
    if wf.is_dir():
        for f in wf.glob('*.yml'):
            if f.name != 'integrate-source.yml':
                f.unlink()

    # 2. 模组 Java 类并入 core 源码树
    print("[2/5] 并入模组 Java 类 …")
    src = modrepo / 'src' / 'project'
    if not src.is_dir():
        sys.exit(f"[FATAL] 找不到模组源码目录: {src}")
    dst = work / 'core' / 'src' / 'project'
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    java_count = len(list(dst.rglob('*.java')))
    print(f"      {java_count} 个 Java 文件")

    # 3. 生成内置资源 zip（mod.hjson 在根，assets 内容平铺）
    print("[3/5] 生成 core/assets/shattered-star.zip …")
    assets = modrepo / 'assets'
    meta = modrepo / 'mod.hjson'
    if not assets.is_dir() or not meta.is_file():
        sys.exit("[FATAL] 找不到模组 assets/ 或 mod.hjson")
    assets_out = work / 'core' / 'assets'
    assets_out.mkdir(parents=True, exist_ok=True)
    zip_path = assets_out / 'shattered-star.zip'
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(meta, 'mod.hjson')
        for f in sorted(assets.rglob('*')):
            if f.is_file():
                z.write(f, f.relative_to(assets).as_posix())
    print(f"      {zip_path.stat().st_size} bytes")

    # 4. 给 Mods.java 打补丁，注册内置 LoadedMod
    print("[4/5] 给 Mods.java 打补丁 …")
    mods_java = work / 'core' / 'src' / 'mindustry' / 'mod' / 'Mods.java'
    text = mods_java.read_text(encoding='utf-8')
    if 'Project Shattered Star: source-integrated built-in mod' in text:
        print("      已打过补丁，跳过")
    elif OLD not in text:
        sys.exit("[FATAL] Mods.java 结构与 v160.7 不符，无法安全打补丁")
    else:
        mods_java.write_text(text.replace(OLD, NEW, 1), encoding='utf-8')
        print("      已注入内置注册代码")

    # 5. 写合规说明与仓库首页（上游 README 另存保留）
    print("[5/5] 写说明文档 …")
    (work / 'SHATTERED_STAR.md').write_text(NOTES, encoding='utf-8')
    upstream_readme = work / 'README.md'
    if upstream_readme.is_file():
        shutil.copyfile(upstream_readme, work / 'README-UPSTREAM.md')
    (work / 'README.md').write_text(HOMEPAGE, encoding='utf-8')

    print("[OK] 集成完成")


if __name__ == '__main__':
    main()
