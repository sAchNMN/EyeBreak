# EyeBreak 交接文档

这份文档给后续接手的 AI 代码工具或开发者使用，只保留接手时立刻需要的信息。

本文档不重复其他来源：

* 用户可见行为、安装/运行/测试/构建命令、验收清单 → `README.md`
* 项目规则（范围、依赖、提交、测试、验收、推送） → `AGENTS.md`
* 逐次任务的变更、测试结果和排错过程 → `git log` 与 GitHub Releases

因此本文档不再向下追加历史记录；新任务只更新状态、限制和下一步，不复述已经进入提交历史的内容。

## 项目定位

EyeBreak 是面向 Windows 中文用户的护眼休息提醒工具，使用 Python、Tkinter 和 `pystray` 开发。

核心能力：按设定间隔弹出护眼提醒、可拖动且贴边自动隐藏的悬浮倒计时、系统托盘控制、暂停/恢复/立即休息、今日免打扰、本地统计、开机自启、用户离开检测、全屏运行时延后提醒、PyInstaller 打包成 Windows 可执行文件。

## 当前版本与发布

* `VERSION`：`V3.3`。`version_info.txt` 中的 `filevers`/`prodvers` 与 `FileVersion`/`ProductVersion` 必须与之一致。
* 最新 Release：`V3.3` — https://github.com/sAchNMN/EyeBreak/releases/tag/V3.3 （2026-10-01 发布，标记 Latest）
* 发布提交：`52bd74a5667c660ad72140c502c709abff068e5f`（`master`）
* 发布资产：`EyeBreak-v3.3-onedir.zip`，19,926,528 字节
  * 资产 SHA-256：`423B61DF5F4E5AA205D709DB527F96807AB1978D25896794139D8C3D527E4DCE`
  * 包内 `EyeBreak.exe` SHA-256：`F50E594AA0DE1D0065DA497475E4E9E4599B7F19AA3EBC2209757A274FFB4B66`
* `V3.3` 与上一版 `V3.2` 的唯一差异是打包配置：EXE 补上了 Windows PE 版本资源，`VERSION` 从 `V3` 对齐为 `V3.3`。功能行为不变。
* 已发布的可执行文件仍未做代码签名。
* 安装包：`installer.iss` + `scripts/build_installer.ps1` 可生成 `dist/installer/EyeBreak-Setup-3.3.exe`（15,161,148 字节，SHA-256 `BCF254BA7E1D99A5B872945B3DA7F8E5D7D9B1DEAA63DFD40B7EA9B5EA5C0A34`）。本地已构建，尚未作为 Release 资产发布，也未做代码签名。

`V3` 与 `V3.2` 的资产未被替换，仍按各自哈希发布。发布历史以 GitHub Releases 页面为准。

## 架构与目录

启动链路：`main.py` 以依赖注入方式组装 `EventBus → StateMachine → 平台适配器 → TimerEngine → EyeBreakBridge → Tk mainloop`。

* `app/core/`：核心域，零 UI/平台依赖（领域事件、`EventBus`、`StateMachine`、`TimerEngine`）。
* `app/platform/`：`Protocol` 接口定义，以及把现有模块级函数包装成接口实现的适配器。
* `app/ui/bridge.py`：事件驱动桥接层，负责 Tk 线程调度、设置窗口生命周期和托盘状态同步。
* `app/`：悬浮倒计时、提醒窗口、托盘、设置窗口，以及配置/状态/统计的原子 JSON 持久化，和 idle、fullscreen、autostart、single instance 等 Win32 能力。
* `tests/`：pytest 测试，与 `app/` 模块基本一一对应。
* `scripts/monitor_performance.py`：仅用标准库的 Windows CPU/RSS 监测脚本，不打进发布包。
* `build.spec` + `version_info.txt`：PyInstaller onedir 构建入口与 Windows PE 版本资源。
* `installer.iss` + `scripts/build_installer.ps1`：Inno Setup 安装包脚本，以及“PyInstaller → ISCC”一键出包脚本。
* `config.json`、`config.json.bak`、`app_state.json`、`stats.json`：本地运行数据，已被 Git 忽略。

旧的 `app/timer.py`（`ReminderTimer` God Class）已删除，不要重新引入。

## 运行 / 测试 / 构建

```powershell
python -m pip install -r requirements.txt
python main.py
python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest
python -m PyInstaller build.spec
.\scripts\build_installer.ps1
```

* 运行测试前 `.tmp` 目录必须存在：测试夹具只创建一层临时目录，否则报 `FileNotFoundError: [WinError 3]`。
* 构建产物是 onedir：`dist/EyeBreak/EyeBreak.exe` 加同级的 `_internal/`。不能只复制 EXE。
* 安装包构建需要 Inno Setup 6.3+（`winget install --id JRSoftware.InnoSetup -e`），只影响出安装包的机器，不是运行时依赖。产物在 `dist/installer/EyeBreak-Setup-<version>.exe`；`-SkipAppBuild` 可复用已有 `dist/EyeBreak/`。
* 安装包按用户安装到 `%LOCALAPPDATA%\Programs\EyeBreak`，不弹 UAC；原因和安装包行为见 `README.md` “生成安装包”。
* 最近一次有效全量回归：`.\.venv\Scripts\python.exe -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\final-pytest` → **268 passed in 2.90s**（2026-10-21，安装包改动后）。
* 本机 `.venv` 未装 pytest，本次通过 `PYTHONPATH` 指向 `.dsh-tmp/test_site` 提供 pytest；常规开发环境装好 pytest 后直接运行上面的命令即可。
* 已知环境问题：DSH 沙箱下 pytest 用 0700 权限创建 `tmp_path`/basetemp，当前用户随后无法读取，session finish 会抛 `PermissionError: [WinError 5]`。这是沙箱限制；本次已提权重跑验证。

## 依赖决策

* 运行时依赖只有 `pystray`（系统托盘）和 `Pillow`（图标与托盘图像）；其余全部使用 Python 标准库和 Tkinter。
* 当前没有新增运行时依赖。判断顺序：标准库 → 现有代码或 Tkinter → 成熟维护的包；不为扩展范围而加依赖。
* 构建期新增 **Inno Setup 6.7.3**（本机经 `winget install --id JRSoftware.InnoSetup -e` 装到用户目录）。理由：标准库和现有依赖都不提供 Windows 安装包能力，Inno Setup 是 Windows 上最常用、脚本最小的方案；NSIS 需要更多脚本代码，WiX/MSI 对个人项目过重，MSIX 需要签名证书。影响：只有出安装包的机器需要安装，运行、测试和 `main.py` 不受影响，`requirements.txt` 不变。
* Inno Setup 6.7 编译器会打印 `Non-commercial use only`（未安装商业许可）。本项目是 MIT 免费软件，按官方说明属于非商业使用；若将来商业化分发，需要购买许可或改用其他工具。
* `requirements.txt` 未固定版本（Pillow 未 pin），属于待办。

## 验收边界

* `README.md` 的验收清单是手动 GUI 验收的依据。真实 Windows 下的 DPI、多显示器、任务栏配置仍需人工确认。
* 自动化测试通过不等于手动验收通过；没有用户明确说“验收没有问题”，不提交推送。

## 已知限制与后续工作

* 未做代码签名：SmartScreen 仍会提示未知发布者，安装包同样如此。PE 版本资源只是降低误报概率，不能替代签名。
* 已按旧哈希记录的报毒不会因新版本自动消失，仍需向 Microsoft 及其他厂商提交误报申诉，并附上上文的 `V3.3` 新哈希。
* 安装包已在桌面副本上完成端到端验证：静默安装 3 秒成功，文件、开始菜单快捷方式、HKCU 卸载项、PE 版本资源都正确；模拟运行期 JSON 和开机自启值后卸载，安装目录、4 个 JSON、`Run`/`StartupApproved` 值、卸载项和快捷方式全部清理干净。
* **低完整性标签坑（已定位）**：本项目目录被之前的 AI 沙箱工具打上了 `Mandatory Label\Low Mandatory Level`（目录树递归，`icacls` 可见；Temp 的 ACL 里还留着 `CodexSandboxUsers` 组）。Windows 会按 exe 文件的完整性标签启动进程，所以 `dist\installer\EyeBreak-Setup-3.3.exe` 双击后是 Low 完整性，写不了 `%TEMP%`/HKCU，报 Error 5。实测把同一个 exe 复制到桌面（无标签）后：workspace 里的 `cmd.exe` 副本以 Low 运行，桌面副本以 Medium 运行，安装随即成功。**发布资产不受影响**（上传/下载不带 NTFS 标签），但本机调试时必须从桌面或下载目录运行。
* 同一标签也影响 `dist\EyeBreak\EyeBreak.exe`：从 `dist` 直接启动时是低完整性，程序内“开机自启”写 HKCU 会失败；需要本机验证自启时，也把程序复制到普通目录运行。
* 是否清除项目目录的 Low 标签尚未决定：它可能是 Codex 等 AI 沙箱工具加的，清除后那些工具的沙箱进程可能无法再写该目录，且可能被重新打上；因此本次没有改动目录 ACL/标签。
* 安装向导是英文：Inno Setup 不自带简体中文语言文件；中文向导需要引入 `ChineseSimplified.isl` 并在 `installer.iss` 加 `[Languages]`。
* 安装包只支持按用户安装，不能装到 `Program Files`：程序把 `config.json` 等写在 exe 旁边，普通用户对 `Program Files` 没有写权限。若要支持全机安装，需要先把数据目录迁到 `%APPDATA%`。
* 卸载会删除 `config.json`、`config.json.bak`、`app_state.json`、`stats.json` 并清理开机自启注册表值，即“卸载即清空设置”；这是刻意行为，不是遗漏。
* 待办：在没有项目和没有运行中实例的干净环境验证发布包与安装包、固定 `requirements.txt`、申请代码签名。
* 工作区状态：`.dsh-tmp/` 已被 `.gitignore` 忽略；`dist/`、`build/` 是本次构建产物（同样被忽略，含 `dist/installer/EyeBreak-Setup-3.3.exe`）；`.tmp/` 已清理并保留为空目录供测试命令使用。

## 本次变更：Windows 安装包（2026-10-21）

变更文件：

* `installer.iss`（新增）：Inno Setup 6.3+ 脚本。按用户安装到 `{localappdata}\Programs\EyeBreak`，`PrivilegesRequired=lowest`；`[Files]` 排除运行期 JSON；`AppMutex=EyeBreak.SingleInstance` 在程序运行时阻止覆盖；`[UninstallDelete]` 与 `[UninstallRun]` 清理运行期数据和 HKCU 自启项；安装包写入 PE 版本资源。
* `scripts/build_installer.ps1`（新增）：读 `VERSION`（去掉 `V` 前缀）并校验与 `version_info.txt` 的 `filevers` 一致；调用 `.venv` 的 PyInstaller；在 PATH、`Program Files (x86)`、`Program Files`、`LOCALAPPDATA` 中定位 `ISCC.exe`；通过 `/DAppVersion=` 传入版本；最后输出大小和 SHA-256。支持 `-SkipAppBuild`。
* `README.md`：安装章节补充“普通用户装安装包”；构建章节新增“生成安装包（Inno Setup）”；下一步改为“安装包已在本地生成、尚未发布”。
* `HANDOFF.md`：同步版本、目录、构建、依赖和已知限制。

当前行为：

* `.\scripts\build_installer.ps1` 一条命令产出 `dist\installer\EyeBreak-Setup-3.3.exe`（15,161,148 字节，SHA-256 `BCF254BA7E1D99A5B872945B3DA7F8E5D7D9B1DEAA63DFD40B7EA9B5EA5C0A34`）。
* 安装包按用户安装、不弹 UAC，创建开始菜单快捷方式，可选桌面快捷方式和安装后启动；卸载清理配置、统计和自启项。
* 程序本身没有代码改动，用户可见行为与 `V3.3` 一致。

依赖决策：

* 新增构建期工具 Inno Setup 6.7.3（详见“依赖决策”）；运行时依赖不变，`requirements.txt` 不变。

安装/运行/测试影响：

* 用户多了一种安装方式；源码运行、测试和 `python -m PyInstaller build.spec` 命令不变。
* 只有出安装包的机器需要安装 Inno Setup。

测试命令与结果：

* `.\.venv\Scripts\python.exe -m PyInstaller build.spec --noconfirm` → **Build complete**，`dist\EyeBreak\EyeBreak.exe` 3,112,081 字节。
* `.\scripts\build_installer.ps1 -SkipAppBuild`（内部执行 `ISCC.exe /DAppVersion=3.3 installer.iss`）→ **Successful compile (8.7 s)**，产物 15,161,148 字节；安装包 PE 元数据：`FileVersion`/`ProductVersion` = 3.3，`CompanyName` = sAchNMN，`FileDescription` = EyeBreak Setup。
* 安装/卸载端到端（桌面副本，`/VERYSILENT`）：安装 3 秒成功；`%LOCALAPPDATA%\Programs\EyeBreak` 下 `EyeBreak.exe`/`_internal`/`unins000.exe` 齐全，开始菜单 `EyeBreak.lnk` 指向正确，HKCU 卸载项 `DisplayName=EyeBreak`、`DisplayVersion=3.3`；预置 4 个运行期 JSON 和 `Run`/`StartupApproved` 值后卸载，目录、JSON、注册表值、快捷方式和卸载项全部清除。
* `.\.venv\Scripts\python.exe -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\final-pytest --tb=short`（`PYTHONPATH` 指向 `.dsh-tmp\test_site`）→ **268 passed in 2.90s**。
* `.\.venv\Scripts\python.exe -m compileall -q app main.py tests` → 通过。
* `git diff --check` → 通过。

已知失败与限制：

* **从 `dist\installer\` 直接双击会报 Error 5**：项目目录带 Low 完整性标签，exe 会以低完整性运行，写不了 `%TEMP%`；把安装包复制到桌面（无标签）后实测安装/卸载全部正常，原因与规避方式见“已知限制与后续工作”。
* 安装包未做代码签名，SmartScreen 仍会提示未知发布者；安装向导为英文。

## 本次变更：清理死代码与工作区（2026-10-21）

变更文件：

* `app/core/events.py`、`app/core/event_bus.py`：删除没有生产订阅者的 `TimerStarted`、`StateChanged`、`ConfigChanged`、`ExitRequested`。
* `app/core/state_machine.py`：不再依赖 `EventBus`，只保留状态校验；`main.py` 改为 `StateMachine()`。
* `app/core/timer_engine.py`、`app/ui/bridge.py`：删除对应的发布/订阅和两个空事件处理器。
* `app/platform/protocols.py`、`app/platform/adapters.py`：删除只被测试使用的 `ConfigRepository`、`StateRepository` 及其适配器。
* `app/floating_countdown.py`：删除未使用的 `set_paused`、`set_idle`、`set_fullscreen`。
* `app/state.py`：删除未使用的 `AppState.is_running`。
* `app/tray.py`、`app/reminder_window.py`：5 个同构动作工厂合并为 `_action()`；暂停时长文案共用 `format_pause_label()`。
* `app/config.py`、`app/settings_window.py`：设置页文本解析集中到 `parse_config_values()`，删除重复的解析辅助函数；错误文案保持不变。
* `app/infra/`、`scripts/__init__.py`：删除空包；`build.spec` 移除 `app.infra` hidden import。
* `.gitignore`：忽略 `.dsh-tmp/`。
* `tests/`：同步删除死代码测试、合并托盘测试、把配置解析测试移到 `test_config.py`。
* 清理 `.tmp/`（发布验证残留）和 `build/`（PyInstaller 中间产物），保留空 `.tmp/` 供测试命令使用。

当前行为：

* 用户可见行为不变：托盘菜单、悬浮窗、设置页、提醒弹窗、统计和快捷操作保持一致。
* 设置页非法输入的错误文案保持不变；配置解析仍由 `validate_config()` 做最终范围校验。
* 不再发布 `TimerStarted` / `StateChanged` / `ConfigChanged` / `ExitRequested`；这些事件没有生产消费者。
* `AppState` 仍保留 `paused_until` 和 `next_reminder_at` 作为运行中字段（不落盘），本次未迁移。

依赖决策：

* 无新增、移除或升级依赖。

安装/运行/测试影响：

* 安装、运行和构建命令未变；`app.infra` 本来就不是运行时模块。
* 测试命令不变；测试数量因删除死代码测试而减少。

测试命令与结果：

* `$env:PYTHONPATH = (Resolve-Path .dsh-tmp\test_site).Path`，然后 `.\.venv\Scripts\python.exe -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\final-pytest --tb=short` → **268 passed in 3.02s**。
  * 本机 `.venv` 未安装 pytest；`.dsh-tmp/test_site` 仅用于本次提供 pytest。常规环境装好 pytest 后直接运行 `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest`。
* `.\.venv\Scripts\python.exe -m compileall -q app main.py tests scripts` → 通过。
* `git diff --check` → 通过。
* 未重跑真实托盘/GUI 手动验收；沙箱无法验证托盘显示。

已知限制与后续工作：

* 本次未处理 `app/icons.py` 的运行时绘制（351 行）：`assets/eyebreak.ico` 已打包，后续可改为加载资源，需等图标改版验收后单独做。
* `EventBus` / `StateMachine` / bridge 的完整事件架构仍在；本次只删死事件，未改为直接回调。
* 沙箱仍无法完成真实托盘/GUI 验收；本次已在非沙箱环境完成全量自动化回归，但托盘显示和真实点击仍需人工确认。

## 本次变更：精简交接文档（2026-10-01）

变更文件：

* `HANDOFF.md`：由 1093 行、66 KB 的追加式流水压缩为本文档。

删除的内容（仍可从 `git log`、`README.md` 和 GitHub Releases 查到）：

* 逐条追加的历史任务记录：架构重构 Phase 1–4 与删除 God Class、单实例、悬浮窗尺寸与贴边系列修复、性能优化与 30 分钟基准、v1.2 功能实现、PyInstaller 构建修复等。
* 重复出现的依赖策略、项目重要规则和验收清单片段（现分别以 `AGENTS.md` 和 `README.md` 为唯一来源）。
* 过期内容：`V3` 发布记录、已删除文件（`app/timer.py`、`tests/test_timer.py`、`RELEASES.md`、`docs/`、`out/`、本地规划文档）的说明、被截断为 `??????` 的旧验收记录。
* 各阶段过期的测试计数（73 / 141 / 174 / 185 / 198 / 212 / 219 / 227 / 253 …）和一次性的沙箱排错日志。

当前行为：

* 只改文档。不改程序行为、依赖、安装/运行/构建命令和测试命令。

依赖决策：

* 无新增、移除或升级依赖。

测试影响与结果：

* 本次为文档变更，未重新运行全量测试。
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-handoff-cleanup`：沙箱在 session finish 删除 basetemp 时抛 `PermissionError: [WinError 5]`，未产生有效结果（见上文已知环境问题）。
* `py -m compileall -q app scripts main.py`：通过。
* `git diff --check`：通过。

## 本次变更：现代化应用图标（2026-10-21）

变更文件：

* `app/icons.py`：重写图标生成逻辑，新增深青渐变圆角底、顶部玻璃高光、薄荷色杏仁眼、青绿虹膜、深色瞳孔、琥珀色高光与四角星；按尺寸自动简化细节；`create_icon_image()` 使用 `lru_cache` 缓存母版并返回副本。
* `assets/eyebreak.ico`：替换为新图标，包含 16/20/24/32/40/48/64/128/256 九个尺寸，55,515 字节。
* `assets/eyebreak-icon.png`：新增 1024×1024 RGBA 预览/母版，仅用于 README 展示，不进入运行时打包。
* `tests/test_icons.py`：新增透明圆角、中心不透明、琥珀色强调色和 ICO 多尺寸断言。
* `README.md`：展示新图标，更新图标说明、测试状态和图标验收项。

当前行为：

* 托盘图标、提醒窗口标题栏图标和 Windows 任务栏图标统一使用新设计。
* `ensure_icon_file()` 在 ICO 缺失时按同一设计重新生成多尺寸 ICO。
* 小尺寸自动省略星点、玻璃高光和阴影：16/20/24/32 像素保留眼睛、虹膜和瞳孔轮廓，128/256 像素显示完整细节。
* 安装、运行、测试和构建命令未改变；README 的安装/构建示例已改为显式使用项目 `.venv` 的 Python，避免 `pip` 不在 PATH 或 PEP 668 拒绝安装。

依赖决策：

* 无新增、移除或升级依赖；继续只使用 Pillow 和 Python 标准库。
* 新增的 PNG 是静态预览资源，不引入运行时依赖。

安装/运行/构建影响：

* 程序入口不变；README 的安装/构建命令已改为 `.\.venv\Scripts\python ...`。
* `build.spec` 仍从 `assets/eyebreak.ico` 读取 EXE 图标；已使用 `.venv` 中的 PyInstaller 6.22.3 重新构建 `dist/EyeBreak`，新 EXE 已嵌入新图标。
* V3.3 发布资产仍是旧图标；发布前需要重新打包并更新发布文件。

测试命令与结果：

* `python -m pytest -q tests/test_icons.py -k "not ensure_icon_file" -p no:cacheprovider -p no_cleanup` → **6 passed, 2 deselected**。
* `.\.venv\Scripts\python.exe -m pytest -q tests/test_tray.py tests/test_bridge.py tests/test_icons.py -k "not ensure_icon_file" -p no:cacheprovider -p no_cleanup` → **46 passed, 2 deselected**（项目 `.venv` 中的真实 pystray 0.19.5）。
* `ensure_icon_file()` 使用工作区临时路径生成 ICO → 55,515 字节，`sizes` 为 16/20/24/32/40/48/64/128/256，四角 alpha 为 0，中心 alpha 为 255。
* Tk `apply_window_icon()` 冒烟检查 → `tk icon ok True`。
* 全量测试在沙箱中运行结果为 **254 passed, 1 failed, 27 errors**：1 个失败是 `HKCU` 注册表写入被拒，27 个 error 是 `tmp_path`/basetemp 目录被沙箱拒绝，均为已知环境限制，不是图标代码回归；未获得完整绿色全量结果。
* `python -m compileall -q app main.py tests/test_icons.py` → 通过。
* `git diff --check` → 通过（仅提示 `app/icons.py` 的 LF/CRLF 转换）。

已知限制与后续工作：

* 尚未在真实 Windows 托盘、任务栏和不同 DPI 下人工确认新图标观感；README 的“图标检查”仍需手动验收。
* 图标采用程序化 Pillow 绘制，没有外部设计源文件；后续调整需修改 `app/icons.py` 并重新生成 ICO/PNG。
* 下次构建发布前应重新运行 `python -m PyInstaller build.spec`，并确认 EXE、托盘和任务栏都显示新图标。

## 本次变更：修复托盘图标不显示（2026-10-21）

根因：

* 复现时托盘线程在 `pystray/_win32.py` 的 `ChangeWindowMessageFilterEx` 处抛出 `PermissionError: [WinError 5]`，线程直接结束，`EyeBreak` 进程继续运行但没有任何托盘图标。
* 同一环境下直接调用 `Shell_NotifyIcon(NIM_ADD)` 返回 `0`，`GetLastError()` 为 `5`（拒绝访问）。Windows 会拒绝完整性级别与 Explorer 不一致的进程添加托盘图标；本次复现进程是 DSH 沙箱的 `Low Mandatory Level`，用户之前的管理员 PowerShell 也会继承 `High`。
* 因此这不是新 ICO 或 Pillow 图像的问题，而是启动进程的权限/完整性级别问题。

变更文件：

* `app/tray.py`：安装 Windows 兼容补丁，捕获 `ChangeWindowMessageFilterEx` 的 `OSError`；记录 `NIM_ADD` 的返回值和错误码；`TrayIcon.last_notify_result()` 供 UI 检查。
* `app/ui/bridge.py`：托盘启动后检查结果；失败时显示自定义 Tk 警告窗口。
* `README.md`：安装/构建命令改为项目 `.venv`；补充托盘图标不显示的排查步骤和验收项。
* `dist/EyeBreak`：用 PyInstaller 6.22.3 重新构建，包含托盘补丁和新图标。

当前行为：

* 普通用户（Medium 完整性）启动时，托盘图标正常添加；Windows 11 可能把它放进 `^` 溢出区，需要在“其他系统托盘图标”中打开。
* 管理员进程或受限终端进程不再静默丢失托盘线程；程序会弹出“Windows 没有接受 EyeBreak 的托盘图标”提示，并建议从文件资源管理器以普通用户重启。
* 自定义 Tk 警告窗口替代 `tkinter.messagebox`：悬浮窗是 `overrideredirect` + topmost，`messagebox` 在这种状态下会立即返回而不显示。
* 无新增、移除或升级依赖。

安装/运行/构建影响：

* README 安装/构建示例改为 `python -m venv .venv`、`.\.venv\Scripts\python -m pip install -r requirements.txt pyinstaller`、`.\.venv\Scripts\python -m PyInstaller build.spec`。
* 程序入口仍是 `python main.py`；使用 `.venv` 时运行 `.\.venv\Scripts\python main.py`。

测试命令与结果：

* `.\.venv\Scripts\python.exe -m compileall -q app main.py tests` → 通过。
* `.\.venv\Scripts\python.exe -m pytest -q tests/test_tray.py tests/test_bridge.py tests/test_icons.py -k "not ensure_icon_file" -p no:cacheprovider -p no_cleanup` → **46 passed, 2 deselected**。
* `.\.venv\Scripts\python.exe -m PyInstaller build.spec --noconfirm` → **Build complete**，`dist/EyeBreak/EyeBreak.exe` 更新。
* 低完整性环境启动重建后的 EXE → 窗口标题变为 `EyeBreak 托盘图标`，警告窗口出现，说明失败检测和提示生效。
* 托盘线程不再输出 `Exception in thread Thread-2`。
* 未在 Medium 完整性下实际确认托盘图标可见；当前 DSH 沙箱进程固定为 Low，需要用户从资源管理器双击 EXE 做最终验收。

已知限制与后续工作：

* 以管理员身份运行时，Windows 的 UIPI 仍会拒绝托盘图标；程序只能提示，不能强制把高完整性进程变成普通权限进程。
* Windows 11 默认隐藏新托盘图标，程序无法强制“固定到任务栏”；需要在系统设置中打开。
* 若用户在 Medium 权限下仍看不到图标，优先检查 `^` 溢出区和“其他系统托盘图标”列表。

## 补充：工作区 Low 完整性标签（2026-10-21）

用户从资源管理器双击 `dist\EyeBreak\EyeBreak.exe` 后仍出现托盘警告。进一步检查确认：

* 运行中的 EyeBreak 进程（PID 8948）完整性为 **Low**，父进程为 Explorer（PID 10064，完整性 **Medium**）。
* `icacls dist\EyeBreak\EyeBreak.exe` 显示 `Mandatory Label\Low Mandatory Level:(I)(NW)`；整个 DSH `workspace-write` 工作区都被打了 Low 标签，EXE 继承该标签后以 Low 进程启动。
* Windows 的 `Shell_NotifyIcon` 对 Low 进程返回 `0` / `GetLastError=5`，因此即使从资源管理器双击，图标仍会被拒绝。问题不在管理员权限，也不在图标或 pystray 代码。

处理方式：

* 把整个 `dist\EyeBreak` 文件夹**复制**到桌面或普通目录（Desktop 没有 Low 标签），从副本启动；副本进程应为 Medium，托盘图标即可添加。
* 如果副本仍为 Low，在普通 PowerShell（非 DSH 终端）中执行：
  `icacls "$env:USERPROFILE\Desktop\EyeBreak" /setintegritylevel "(OI)(CI)Medium"`
  然后重新启动。不要在 DSH 终端中执行，因为该终端本身是 Low，写升级标签会被拒绝。
* 已更新警告文案和 README 排查步骤；重新构建 EXE 后，警告会直接提示 `icacls`/复制到普通目录。

验证命令与结果：

* `icacls dist\EyeBreak\EyeBreak.exe` → `Mandatory Label\Low Mandatory Level:(I)(NW)`。
* 进程令牌查询 → Explorer `Medium`，EyeBreak `Low`，父进程 PID 10064。
* 复制到 `%TEMP%\dsh-*` 后仍为 Low（DSH 临时目录同样被标记），因此不能作为验证位置。
* 复制到 Desktop 被当前 DSH 文件沙箱拒绝（`Access to the path ... is denied`）；需要用户在资源管理器中手动复制，或由更高权限进程执行。
* 尚未由当前会话验证 Desktop 副本的托盘显示；预期副本为 Medium 后正常。

已知限制：

* 这是 DSH 沙箱工作区的环境限制，不是 EyeBreak 的产品缺陷；正常 Git 检出不会带 Low 标签。
* 不要为了消除警告而修改工作区根目录的安全标签；优先复制到普通目录运行。
