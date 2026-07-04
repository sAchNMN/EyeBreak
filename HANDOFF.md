# EyeBreak 交接文档

这份文档给后续接手的 AI 代码工具或开发者使用。目标是让没有看过项目的人能快速判断项目状态、运行方式、约束和下一步工作。

## 项目定位

EyeBreak 是一个面向 Windows 中文用户的护眼休息提醒工具。

核心能力：

* 按固定间隔弹出护眼提醒。
* 显示可拖动、可贴边自动隐藏的悬浮倒计时。
* 支持系统托盘控制。
* 支持暂停、恢复、立即休息和退出。
* 支持开机自启。
* 支持用户离开检测。
* 支持全屏应用运行时延后提醒。
* 支持 PyInstaller 打包成 Windows 可执行文件。

## 当前版本

版本：`v1`

最近已推送提交：`49601e4 Clean repository tracked files`

当前仓库已清理：

* `config.json` 不再进入 Git。
* `github仓库地址.md` 已删除。
* `MVP软件开发.md` 已删除。
* 本地运行状态、构建产物、缓存和工具草稿已加入 `.gitignore`。

## 重要规则

* 每次改代码、行为、依赖、命令、测试结论或用户可见文档后，都要更新 `HANDOFF.md`。
* 用户可见行为、安装命令、运行命令、测试命令或验收状态变化时，同步更新 `README.md`。
* 没有实际运行测试，不能说测试通过。
* 没有用户明确说“验收没有问题”或“验收没问题”，不能推送到 GitHub。
* 提交前必须检查 `git status`。
* 不提交本地配置、缓存、构建产物、IDE 状态和工具草稿。
* `AGENTS.md` 是项目级规则文件。除非用户明确要求改项目规则，否则不要改。

## 依赖策略

项目优先使用标准库、现有代码、Tkinter 或成熟维护的包。

已有依赖：

* `pystray`：系统托盘。
* `Pillow`：图标和托盘图像支持。

当前未新增依赖。

判断顺序：

1. Python 标准库能解决就用标准库。
2. Tkinter 或现有项目代码能解决就复用。
3. 有成熟维护的包能直接降低风险时，优先使用包。
4. 不为了扩展范围而加依赖。

## 目录说明

```text
app/             主程序模块
assets/          应用图标
tests/           自动化测试
README.md        面向用户和 GitHub 的中文说明
VERSION          当前版本号
build.spec       PyInstaller 构建脚本
requirements.txt Python 运行依赖
```

`config.json` 和 `app_state.json` 是本地运行状态，不进入 Git。

## 运行方式

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

启动程序：

```powershell
python main.py
```

首次运行会自动生成 `config.json`。

## 测试方式

推荐命令：

```powershell
python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest
```

最近一次验证：

* 普通权限运行：`62 passed, 11 errors`。
* 失败原因：Windows 沙箱清理 `.tmp\pytest` 时触发 `PermissionError: [WinError 5]`。
* 提权重跑同一命令：`73 passed in 0.40s`。
* 没有断言失败。

## 构建方式

```powershell
pip install pyinstaller
python -m PyInstaller build.spec
```

产物：

```text
dist/EyeBreak.exe
```

`build.spec` 要保留。虽然通用 Python `.gitignore` 常忽略 `*.spec`，但本项目使用它作为已验收的 Windows 构建入口。

## 已验收功能

* 基础提醒流程。
* 悬浮倒计时。
* 悬浮倒计时贴边自动隐藏。
* 暂停倒计时显示。
* 鼠标滚轮调整暂停时长。
* 系统托盘菜单。
* 托盘暂停时长选择。
* 托盘勾选状态即时刷新。
* 程序图标。
* 设置窗口。
* 用户离开检测。
* 全屏检测。
* 开机自启。
* 自启动运行路径修复。
* PyInstaller 构建产物。
* v1 GitHub Release。
* 仓库清理。

## 未实现范围

这些内容不属于当前版本：

* 账号系统。
* 云同步。
* 每日报告。
* AI 分析。
* 摄像头检测。
* 完整番茄钟流程。
* Windows 安装包。

## 当前这次文档中文化

变更文件：

* `README.md`：完整改为中文项目说明。
* `.gitignore`：注释改为中文。
* 删除 `RELEASES.md`：发布记录改以 GitHub Releases 页面为准。
* `HANDOFF.md`：重写为中文交接文档。

当前行为：

* 只改文档和忽略规则注释。
* 不改程序行为。
* 不改依赖。
* 不改构建入口。

测试影响：

* 本次是文档中文化，没有重新运行测试。
* 最近一次有效回归仍是 `73 passed in 0.40s`。

下一步：

* 用户验收后再提交。
* 用户明确说“验收没问题”后再推送。
## 当前这次删除本地发布记录

变更文件：

* 删除 `RELEASES.md`：避免公开仓库出现不常见的重复发布记录文件。
* `README.md`：说明发布记录以 GitHub Releases 页面为准。
* `HANDOFF.md`：同步当前仓库结构和本次删除原因。

当前行为：

* 只改文档结构。
* 不改程序行为。
* 不改依赖。
* 不改构建入口。

测试影响：

* 本次是文档清理，没有重新运行测试。
