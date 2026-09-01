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

版本：`V3`

## 当前发布：EyeBreak V3

发布信息：

* GitHub Release：`V3`
* 发布提交：`5b46698cbcb6e5f35e77f431724d13b9345cfc38`
* 发布资产：`EyeBreak.zip`
* 资产 SHA-256：`ED74962BEAE30511CDADCC3CB2BD001E4A8C17A20158815FE36AA0FD11B1B884`

当前行为：

* V3 包含当前 `master` 分支上的 EyeBreak 功能，包括提醒、托盘、悬浮倒计时、暂停、今日免打扰、本地统计、配置校验和开机自启。
* 发布包只包含 `EyeBreak.exe`，不包含本地配置、运行状态、统计数据或工作区草稿。

依赖与安装/运行影响：

* 未新增运行时依赖。
* 安装、运行和 PyInstaller 构建命令不变。

发布前验证：

* `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\\pytest-release-current`：当前环境缺少 `pytest` 模块，未启动。
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\\pytest-release-current`：**280 passed in 1.38s**。
* `py -m compileall -q app main.py`：通过。
* `py -m PyInstaller build.spec`：通过；存在第三方 `pystray` 的既有 `SyntaxWarning`，不影响构建。
* `git diff --check`：通过。

已知限制与后续工作：

* 工作区仍保留未跟踪的 `docs/` 和 `out/`，未进入提交或发布包。
* `VERSION`、README 和本交接文档已同步为 `V3`。

## Current fix: reminder shown immediately after autostart

Changed files:

* `app/core/timer_engine.py`: adds `start()` to schedule a fresh reminder interval for each application session.
* `app/ui/bridge.py`: starts the engine after the UI is wired and before the first timer tick.
* `tests/test_timer_engine.py`: adds a regression test for new-session countdown initialization.
* `README.md`: documents the startup countdown behavior.

Current behavior:

* On autostart or manual launch, EyeBreak starts counting down from the configured interval instead of treating the default `next_reminder_at=0` as overdue.

Dependency decision:

* No new dependencies; uses the existing Python monotonic clock.
* Installed `pytest 9.1.1` only in the local test environment to run the existing test suite. `requirements.txt` is unchanged.

Test impact:

* `python -m pytest -q tests -p no:cacheprovider --basetemp C:\tmp\eyebreak-pytest-20260718` - **199 passed in 0.53s**.
* `git diff --check` - passed.

Build impact:

* `python -m PyInstaller build.spec` - passed; rebuilt `dist/EyeBreak.exe` with this fix.

Manual acceptance:

* User confirmed "??????" after verifying the rebuilt application starts from the configured countdown interval without immediately displaying a reminder.

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

## 当前这次新增 v1.1 体验优化规划

变更文件：

* `v1.1体验优化.md`：新增独立规划文件，记录 v1.1 体验优化建议、优先级、验收点和涉及文件。
* `HANDOFF.md`：同步记录本次文档变更。

当前行为：

* 只新增规划文档。
* 不改程序行为。
* 不改依赖。
* 不改安装、运行和构建命令。

测试影响：

* 本次是文档规划，没有运行自动化测试。

## 当前这次架构重构 Phase 1：核心基础设施

变更文件：

* `app/core/__init__.py`：新增 core 包初始化。
* `app/core/events.py`：新增 15 个领域事件 frozen dataclass（TimerStarted/Stopped/Tick、ReminderTriggered/Dismissed、StateChanged、IdleDetected/Ended、FullscreenDetected/Ended、Paused/Resumed、ConfigChanged、FloatingCountdownToggled、ExitRequested）。
* `app/core/event_bus.py`：新增 EventBus 类型安全发布/订阅总线，支持按事件类型订阅、取消订阅、错误隔离（单个订阅者异常不影响其他订阅者）、线程安全（RLock）。
* `app/core/state_machine.py`：新增 6 状态显式状态机（RUNNING/IDLE/FULLSCREEN/PAUSED/SHOWING_REMINDER/EXITED），含 17 条合法转换表、非法转换抛 IllegalTransition、每次成功转换发布 StateChanged 事件。
* `app/platform/__init__.py`：新增 platform 包初始化。
* `app/platform/protocols.py`：新增 5 个 runtime_checkable Protocol 接口（IdleDetector、FullscreenDetector、AutostartManager、ConfigRepository、StateRepository），核心层依赖 Protocol 而非具体实现。
* `app/infra/__init__.py`：新增 infra 包初始化（预留，Phase 2 填充）。
* `app/ui/__init__.py`：新增 ui 包初始化（预留，Phase 4 填充）。
* `tests/test_event_bus.py`：新增 11 个 EventBus 测试。
* `tests/test_state_machine.py`：新增 46 个 StateMachine 测试（含参数化合法/非法转换、事件发布、真实工作场景模拟）。
* `tests/test_protocols.py`：新增 8 个 Protocol 接口测试（含 Fake 实现和现有模块适配器验证）。

当前行为：

* 新增核心基础设施代码，不修改任何现有源文件。
* 现有 `main.py` → `ReminderTimer` 流程完全不受影响。
* 新增代码与现有代码并存，为后续 Phase 2-4 迁移提供基础。

依赖决策：

* 零新依赖。仅使用 Python 标准库：`typing.Protocol`、`dataclasses`、`enum`、`threading`、`collections`、`logging`。
* 不影响 `requirements.txt`。

测试命令与结果：

```powershell
python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest
```

* 结果：`141 passed in 0.86s`（73 原有 + 68 新增，零回归）。

已知限制：

* EventBus 和 StateMachine 已就绪但尚未接入 ReminderTimer。
* Protocol 接口已定义但现有 idle.py/fullscreen.py/autostart.py 尚未适配（仍为模块级函数，需要 Phase 3 包装为 Protocol 实现）。

## 当前这次架构重构 Phase 2：TimerEngine 核心域提取

变更文件：

* `app/core/timer_engine.py`（新增）：TimerEngine 纯业务逻辑核心，依赖 EventBus/StateMachine/Protocol 接口，零 UI/平台实现依赖。包含 tick、pause/resume、break_now、skip_reminder、save_config、toggle_floating_countdown、toggle_autostart、request_exit 等完整操作集。发布 12 个领域事件类型（Tick、ReminderTriggered、ReminderDismissed、Paused、Resumed、IdleDetected、IdleEnded、FullscreenDetected、FullscreenEnded、ConfigChanged、FloatingCountdownToggled、TimerStopped）。
* `tests/test_timer_engine.py`（新增）：33 个 TimerEngine 单元测试，覆盖格式辅助函数、tick 正常流/暂停/idle/全屏/提醒触发/退出、pause/resume、break_now、skip_reminder、save_config、toggle_floating_countdown、toggle_autostart、request_exit。

当前行为：

* 新增核心域代码，不修改任何现有源文件。
* 现有 main.py → ReminderTimer 流程完全不受影响。
* EventBus + StateMachine + TimerEngine + Protocol 接口已就绪，为 Phase 3 平台适配和 Phase 4 UI 重构提供完整的核心域层。

依赖决策：

* 零新依赖。仅使用 Python 标准库。

测试命令与结果：

```powershell
python -m pytest -q tests -p no:cacheprovider
```

* 结果：**174 passed in 1.05s**（73 原有 + 101 新增，零回归）。
* 额外 11 个 ERROR 是 sandbox `--basetemp` 回收站不可用的已知环境问题（HANDOFF.md 已有记载），非代码问题。

## 当前这次架构重构 Phase 3：平台适配器

变更文件：

* `app/platform/adapters.py`（新增）：5 个 Protocol 适配器类（IdleDetectorAdapter、FullscreenDetectorAdapter、AutostartManagerAdapter、ConfigRepositoryAdapter、StateRepositoryAdapter），每个适配器包装现有模块级函数为 Protocol 兼容类。零侵入——不修改现有模块。
* `tests/test_adapters.py`（新增）：11 个测试，验证每个适配器满足 Protocol isinstance 检查，以及委托调用正常返回。

当前行为：

* 新增适配器代码，不修改任何现有源文件。
* 现有 main.py → ReminderTimer 流程完全不受影响。
* 所有 5 个 Protocol 接口都有对应的生产适配器，TimerEngine 可以实际注入。

依赖决策：

* 零新依赖。仅使用 Python 标准库。

测试命令与结果：

```powershell
python -m pytest -q tests -p no:cacheprovider
```

* 结果：**185 passed in 0.66s**（+11 适配器测试，零回归）。

## 当前这次架构重构 Phase 4：UI 事件桥接层

变更文件：

* `app/ui/bridge.py`（修改）：实现 EyeBreakBridge 事件驱动桥接层，完成 `ReminderTimer` God Class → EventBus 风格的迁移。包括：
  - 事件订阅（Tick、ReminderTriggered/Dismissed、Paused/Resumed、Idle/Fullscreen、TimerStopped、FloatingCountdownToggled、ConfigChanged）
  - `_main_tick()` 每秒驱动 engine.tick() 的循环
  - `_ui_thread()` 跨线程安全调度
  - `_save_settings()` 内存 + 磁盘双持久化
  - `_on_timer_stopped()` 保存悬浮窗位置并清理资源
  - 托盘自启动切换后立即刷新菜单
* `main.py`（重写）：DI 容器风格，注入 EventBus → StateMachine → 平台适配器 → TimerEngine → EyeBreakBridge → Tk mainloop
* `tests/test_bridge.py`（新增）：27 个 EyeBreakBridge 单元测试，覆盖所有事件处理器、设置窗口生命周期、主循环、状态标签参数化测试、清理流程、EventBus 集成测试

当前行为：

* 新启动流程：`main.py` 使用 TimerEngine + EyeBreakBridge 替代 ReminderTimer
* 旧 `app/timer.py` 仍然保留，`tests/test_timer.py` 的 73 个测试继续通过

依赖决策：

* 零新依赖。

测试命令与结果：

```powershell
python -m pytest -q tests -p no:cacheprovider
```

* 结果：**212 passed in 0.51s**（+27 bridge 测试，零回归）。

## 当前这次架构重构 Phase 4 收尾：删除 God Class

变更文件：

* `tests/test_timer.py`（删除）：14 个旧 ReminderTimer 测试已全部被新架构覆盖（test_timer_engine.py + test_bridge.py）。
* `app/timer.py`（删除）：ReminderTimer God Class（310 行）已完全退役，被 TimerEngine + EyeBreakBridge 替代。
* 残留 `.pyc` 缓存文件一并清理。

当前行为：

* 启动入口 `main.py` 使用 DI 容器风格：`load_config/state → EventBus → StateMachine → 平台适配器 → TimerEngine → EyeBreakBridge → tkinter mainloop`。
* 所有模块不再引用旧 `app.timer`。

测试命令与结果：

```powershell
python -m pytest -q tests -p no:cacheprovider
```

* 结果：**198 passed in 0.56s**（14 个旧测试移除，零回归零失败）。

## 当前这次修复 PyInstaller 构建

变更文件：

* `HANDOFF.md`：同步记录本次修复。
* `README.md`：更新构建说明，增加沙箱环境限制提示。

当前行为：

* 构建命令不变：`python -m PyInstaller build.spec`
* 构建产物 `dist/EyeBreak.exe` 约 19MB，正常运行。

修复说明：

**根本原因**不是 `build.spec` 或代码问题。PyInstaller 在 Analysis 阶段创建临时 `base_library.zip`，完成后用 `os.remove()` 清理。WorkBuddy 沙箱的安全删除机制（`safe-delete`）拦截了该调用，试图将文件送入回收站，而 Windows 沙箱回收站不可用，导致 `SAFE_DELETE_FAIL_CLOSED` 错误。

**解决方式**：
1. 确认所有项目依赖（pystray、Pillow）已正确安装至 managed Python 环境。
2. 用非沙箱模式运行 PyInstaller：构建本身不需要沙箱隔离，脱离沙箱后 `os.remove()` 正常工作。
3. `build.spec` 无需修改，`hiddenimports` 清单已完整覆盖所有模块。

构建警告文件 `warn-build.txt` 中的缺失模块均为 Unix/macOS 专用：
- `pwd`、`grp`、`fcntl`、`termios`、`posix` → 仅 Linux/macOS
- `Xlib`、`gi.repository` → Linux 桌面
- `PyObjCTools`、`objc`、`Foundation`、`AppKit` → macOS
- `numpy` → PIL 可选依赖
- `olefile`、`defusedxml` → PIL 可选插件

这些对 Windows 构建无任何影响。

测试影响：

* 本次是构建修复，没有修改 Python 代码，不需要重新运行测试。
* 最近一次有效回归：`198 passed in 0.56s`（Phase 4 收尾后）。

## 下一步

* 用户验收后提交 + 推送。

### 依赖策略回顾

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

## Current fix: single running session

Changed files:

* `app/single_instance.py`: adds the Windows named mutex and named activation event coordinator.
* `main.py`: allows only the primary instance to construct the timer, tray, and UI; it polls activation requests on the Tk UI thread and releases handles when exiting.
* `app/ui/bridge.py`: adds the existing-session activation entry point.
* `tests/test_single_instance.py` and `tests/test_bridge.py`: cover single ownership, startup-event retry, activation polling, and Settings-window focus behavior.
* `README.md`: documents the repeated-launch behavior.

Current behavior:

* A later EyeBreak launch signals the current Windows-session instance and exits. The primary instance opens or focuses its Settings window without resetting the countdown or creating another tray icon.

Dependency decision:

* No product dependencies added; the implementation uses Python standard library `ctypes` and Windows kernel objects.

Test commands and results:

* `python -m pytest -q tests\test_single_instance.py tests\test_bridge.py -p no:cacheprovider --basetemp C:\tmp\eyebreak-single-instance-tests-2` - **32 passed in 0.17s**.
* `python -m pytest -q tests -p no:cacheprovider --basetemp C:\tmp\eyebreak-full-tests-20260718` - sandbox blocked temporary-directory and registry access (1 failed, 191 passed, 12 errors); rerun outside the sandbox passed.
* `python -m pytest -q tests -p no:cacheprovider --basetemp C:\tmp\eyebreak-final-tests-20260718` (outside sandbox) - **204 passed in 0.51s**.
* `git diff --check` - passed.

Build and manual acceptance:

* `python -m PyInstaller build.spec` - passed; rebuilt `dist/EyeBreak.exe` with the single-instance implementation.
* Manual acceptance passed: the user confirmed "??????" after verifying repeated launches keep one active session and focus the existing Settings window without resetting the countdown.

## Current fix: floating countdown startup visibility and autostart synchronization

Changed files:

* `app/state.py`: persists and restores the floating-countdown enabled flag.
* `app/floating_countdown.py` and `app/ui/bridge.py`: apply the saved flag during startup and show an enabled docked countdown before normal auto-hide behavior.
* `app/autostart.py`: synchronizes the current-user `Run` command with Windows `StartupApproved` state.
* `tests/test_state.py`, `tests/test_floating_countdown.py`, `tests/test_bridge.py`, and `tests/test_autostart.py`: add regression coverage.
* `README.md`: documents the corrected visible startup and synchronized autostart behavior.

Current behavior:

* The tray state now comes from the persisted floating-countdown flag; an enabled countdown is visible on launch even when it is docked to a screen edge.
* Enabling autostart registers the current executable under `HKCU\...\Run` and explicitly records the enabled state under `HKCU\...\StartupApproved\Run`. The tray reflects a StartupApproved-disabled entry as disabled.
* The Startup folder remains unused so a single autostart mechanism cannot create duplicate launches.

Dependency decision:

* No dependencies added; implementation uses Python standard-library `winreg` and the existing Tk UI.

Tests and build:

* `python -m pytest -q tests\test_state.py tests\test_autostart.py tests\test_floating_countdown.py tests\test_bridge.py -p no:cacheprovider --basetemp C:\tmp\eyebreak-startup-targeted` - sandbox could not create the requested temporary directory (4 setup errors); rerun with the required Windows permissions passed: `55 passed in 0.24s`.
* `python -m pytest -q tests -p no:cacheprovider --basetemp C:\tmp\eyebreak-startup-full-20260718` - passed: `207 passed in 0.50s`.
* `python -m PyInstaller build.spec` - passed; rebuilt `dist/EyeBreak.exe`.
* Registry verification after the build: `EyeBreak` points to `"G:\桌面\CODE\EyeBreak\dist\EyeBreak.exe"` in `Run`, and `StartupApproved` is `020000000000000000000000` (enabled).

Manual acceptance:

* User confirmed "??????": an enabled docked countdown is immediately visible after launch and EyeBreak is enabled under Windows Startup apps.

## Current fix: floating countdown edge interaction

Changed files:

* `app/floating_countdown.py`: widens the docked tab from 10 to 16 pixels, delays edge hiding by 200 milliseconds, cancels pending hides when the pointer returns, and suppresses hiding during drag operations.
* `tests/test_floating_countdown.py`: adds regression coverage for the reachable tab width, delayed hide scheduling, hide cancellation, drag protection, and resetting drag state when disabled.
* `README.md`: documents the updated floating-countdown interaction and acceptance points.

Current behavior:

* A docked floating countdown leaves a 16-pixel tab visible at the screen edge.
* Leaving the panel schedules hiding after 200 milliseconds instead of hiding immediately.
* Re-entering the panel cancels the pending hide.
* Dragging cannot trigger auto-hide; after release, the panel resumes normal docked or undocked behavior.
* Disabling the floating window clears any active drag state so re-enabling it cannot leave auto-hide permanently disabled.

Dependency decision:

* No product dependencies added. The implementation uses the existing Tkinter `after` and `after_cancel` APIs.
* `pytest` was installed only in the local Python 3.14 test environment because the default `python` executable has no pip or pytest; `requirements.txt` is unchanged.

Test commands and results:

* `py -m pytest -q tests\test_floating_countdown.py -p no:cacheprovider --basetemp=.tmp\pytest-floating-final` — **16 passed in 0.04s**.
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-final` — **212 passed in 0.40s**.
* `git diff --check` — passed.

Known limitations:

* The 200-millisecond delay and 16-pixel tab width are fixed constants; they are intentionally not user settings until manual usage shows a real need.
* Manual GUI acceptance has not been confirmed yet, so this milestone must not be pushed.

## Current fix: floating countdown vertical layout

Changed files:

* `app/floating_countdown.py`: increases the floating window height from 64 to 96 pixels so the 16-pixel edge tab and the status/countdown content have separate space.
* `tests/test_floating_countdown.py`: adds a real Tk layout regression test that checks the bottom-docked countdown receives its requested height and stays inside the content area.
* `README.md`: documents the non-overlapping vertical layout and acceptance point.

Current behavior:

* The floating countdown content area has 80 pixels of height when the tab is placed at the top or bottom.
* The status label and countdown label retain their requested sizes instead of being compressed into an overlapping layout.
* The green edge tab does not cover the status text or countdown digits.

Dependency decision:

* No dependencies added; the regression test uses the existing Tkinter runtime.

Test commands and results:

* `py -m pytest -q tests\test_floating_countdown.py::test_bottom_layout_gives_countdown_text_enough_height -p no:cacheprovider --basetemp=.tmp\pytest-layout-green` — **1 passed in 0.13s**.
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-layout-final` — **213 passed in 0.43s**.
* A real Tk diagnostic reported `content=80`, `status=23`, and `countdown=42/42` pixels for the bottom-docked layout.
* `py -m compileall -q app main.py` — passed.
* `git diff --check` — passed.

Known limitations:

* Manual visual acceptance on all four screen edges is still required; this change has not been pushed.

## Current fix: shrink floating countdown without overlap

Changed files:

* `app/floating_countdown.py`: reduces the window from 188×96 to 188×84 pixels, separates the 16-pixel side tab width from the 10-pixel top/bottom tab height, reduces the countdown font from 20 to 18, and tightens vertical padding.
* `tests/test_floating_countdown.py`: covers the separate vertical tab size and verifies real Tk top/bottom layouts keep the countdown at its requested height inside the content area.
* `README.md`: documents the smaller floating-window dimensions and updated latest test count.

Current behavior:

* The floating countdown is smaller while keeping 6 pixels of vertical layout headroom under the current Tk font metrics.
* Top and bottom docking use a thinner 10-pixel green tab; left and right docking keep a 16-pixel reachable tab.
* The status text and countdown digits remain fully visible and do not overlap the green tab.

Dependency decision:

* No dependencies added; layout verification uses the existing Tkinter runtime.

Test commands and results:

* `py -m pytest -q tests\test_floating_countdown.py -p no:cacheprovider --basetemp=.tmp\pytest-small-final` — **18 passed in 0.15s**.
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-small-final` — **214 passed in 0.47s**.
* `py -m compileall -q app main.py` — passed.
* `git diff --check` — passed.

Known limitations:

* The 188×84 dimensions are validated against the current Windows/Tk font metrics; a different system font or scaling configuration still requires manual visual confirmation.
* This milestone remains uncommitted and unpushed until user acceptance.

## Current tool: Windows CPU/RSS performance monitor

Changed files:

* `scripts/__init__.py`: marks the monitoring script directory as an importable test package.
* `scripts/monitor_performance.py`: adds a standard-library-only Windows process monitor using `GetProcessTimes` and `GetProcessMemoryInfo`; supports an existing `--pid` or launching a command, writes flushed CSV samples, and prints CPU/RSS summary statistics.
* `tests/test_monitor_performance.py`: covers CPU normalization, summary calculations, CSV preservation, and command-line separator handling.
* `README.md`: documents source, EXE, and existing-PID monitoring commands.

Current behavior:

* The monitor defaults to 600 seconds and a 5-second interval; both are configurable.
* CSV fields are `elapsed_seconds`, `cpu_percent`, and `rss_mb`.
* The CPU percentage is normalized across logical CPUs, so 100% means the process is using all logical CPUs. RSS on Windows is measured through the process working set.
* Samples are flushed as they arrive. Ctrl+C preserves already-written rows. A process started by the monitor is intentionally not closed automatically.

Dependency and build impact:

* No dependencies added; the monitor uses Python standard-library `ctypes`, `csv`, `argparse`, and `subprocess`.
* EyeBreak install/run/build commands are unchanged. The monitor is a separate diagnostic script and is not bundled into `dist\\EyeBreak.exe`.

Test commands and results:

* `py -m pytest -q tests\\test_monitor_performance.py -p no:cacheprovider --basetemp=.tmp\\pytest-monitor-green2` — **4 passed in 0.04s**.
* `py scripts\\monitor_performance.py --duration 0.4 --interval 0.1 --output .tmp\\monitor-source-smoke.csv -- py -c "import time; time.sleep(1)"` — passed; wrote 5 samples and summary.
* `$exePath = (Resolve-Path -LiteralPath 'dist\\EyeBreak.exe').Path; $testProcess = Start-Process -FilePath $exePath -PassThru; try { py scripts\\monitor_performance.py --pid $testProcess.Id --duration 0.4 --interval 0.1 --output .tmp\\monitor-exe-smoke.csv } finally { if (-not $testProcess.HasExited) { Stop-Process -Id $testProcess.Id -Force } }` — passed; read 5 samples from the freshly built `dist\\EyeBreak.exe`.
* `$sourcePath = (Get-Command python.exe).Source; $testProcess = Start-Process -FilePath $sourcePath -ArgumentList @('main.py') -WorkingDirectory (Get-Location).Path -PassThru; try { py scripts\\monitor_performance.py --pid $testProcess.Id --duration 0.4 --interval 0.1 --output .tmp\\monitor-source-direct-smoke.csv } finally { if (-not $testProcess.HasExited) { Stop-Process -Id $testProcess.Id -Force } }` — passed; read 5 samples from the direct `python.exe main.py` process.
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\\pytest-monitor-final` — **227 passed in 0.72s**.
* `py -m compileall -q app scripts main.py` — passed.
* `git diff --check` — passed.

Known limitations:

* The monitor is Windows-only and measures working-set memory rather than every Windows memory metric such as private commit.
* The short source/EXE runs are smoke tests, not the requested 10–30 minute performance measurements. Run the README commands for long-term comparison under identical conditions.
* Manual GUI acceptance of EyeBreak remains pending; this milestone is uncommitted and unpushed.

## Measurement correction: source command must target the real Python process

The first user-run source measurement used `py main.py`. On Windows, `py.exe` can remain as a launcher process while the real `python.exe` runs the script, so the monitor's launched PID is not guaranteed to be the EyeBreak process. The resulting `.tmp\\source.csv` must not be used as a strict source-versus-EXE comparison. README now uses `python main.py`; for the single-file EXE, direct command mode can monitor the PyInstaller launcher instead of the real application child, so README documents the child-PID procedure. The two existing runs also used different config files (`config.json` has a 10-minute reminder interval; `dist\\config.json` has 25 minutes), so a strict comparison requires synchronizing those files and rerunning both versions.

## 30-minute CPU/RSS benchmark with one-second sampling

Scope and setup:

* The user approved a temporary configuration sync so both builds used the same settings. The original `dist\config.json` was backed up to `.tmp\dist-config-backup-perf.json`, then the root `config.json` was copied to `dist\config.json`.
* The source run used the actual managed Python interpreter resolved by `py -c "import sys; print(sys.executable)"`, started with `main.py`, and monitored PID 8316.
* The first EXE run monitored the PyInstaller launcher PID and is invalid for application-memory comparison; `.tmp\exe-30m-1s.csv` is intentionally excluded. The valid rerun found launcher PID 1016 and monitored the real application child PID 19672 in `.tmp\exe-real-30m-1s.csv`.
* Both valid monitors ran with `--duration 1800 --interval 1` and returned exit code 0. The elapsed time reached 1800 seconds. Windows scheduling produced 1777 source rows and 1778 real-EXE rows, with approximately one-second sampling intervals rather than a hard real-time guarantee.

Measured results from the stable period after the first 60 seconds:

| Target | CPU average | CPU P95 | CPU max | RSS range | RSS first → last | RSS delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Source Python | 0.0113% | 0.0959% | 0.9588% | 53.05–55.22 MB | 54.54 → 53.48 MB | -1.06 MB |
| Real EXE child | 0.0084% | 0.0959% | 0.2928% | 54.73–57.20 MB | 56.02 → 55.05 MB | -0.97 MB |

Interpretation:

* Neither target showed a monotonic RSS increase during 30 minutes. The initial source RSS sample was taken before full Python/Tk initialization, so the stable-period values are the meaningful comparison.
* Both targets stayed at effectively idle CPU usage under this idle test. This does not measure CPU usage while a reminder, break window, fullscreen detection, or user interaction is active.
* The valid EXE result measures the real application child, not the approximately 8 MB PyInstaller launcher process. README now documents the child-PID procedure.

Exact run and recovery commands:

* `Copy-Item -LiteralPath 'dist\config.json' -Destination '.tmp\dist-config-backup-perf.json' -Force` followed by `Copy-Item -LiteralPath 'config.json' -Destination 'dist\config.json' -Force` — temporary sync completed.
* Source monitor: `py scripts\monitor_performance.py --pid 8316 --duration 1800 --interval 1 --output .tmp\source-30m-1s.csv` — exit code 0; elapsed 1800.0002 seconds.
* Valid EXE monitor: `py scripts\monitor_performance.py --pid 19672 --duration 1800 --interval 1 --output .tmp\exe-real-30m-1s.csv` — exit code 0; elapsed 1800.0001 seconds.
* `Copy-Item -LiteralPath '.tmp\dist-config-backup-perf.json' -Destination 'dist\config.json' -Force` — restore completed; `dist\config.json` SHA-256 matches the backup (`0ABF56C6DB8C065B9B7ED456142003962B9059C01A31506A076ADFD34DE093D8`), and no `EyeBreak` process remained.
* Both valid application error logs and monitor error logs were 0 bytes.

Dependency and test impact:

* No dependencies added or changed. This benchmark used the existing standard-library-only monitor.
* The benchmark generated diagnostic files under `.tmp\`; the original `out\` contents were preserved.
* Final verification completed after this handoff update; manual acceptance for this performance-optimization milestone is recorded below.

## Current fix: directional floating countdown widths

Changed files:

* `app/floating_countdown.py`: uses a 220×84 window for top/bottom docking and a 144×84 window for left/right docking; keeps the existing 10-pixel top/bottom tab and 16-pixel side tab.
* `tests/test_floating_countdown.py`: covers direction-based widths, all four real Tk layouts, and resizing only after drag release docks to a new edge.
* `README.md`: documents the directional floating-window dimensions and acceptance point.

Current behavior:

* Top and bottom docking use the wider 220×84 layout so the status text and countdown remain comfortably readable.
* Left and right docking use the narrower 144×84 layout to reduce the visual footprint along the screen sides.
* While dragging, the current width remains stable; when the window is released onto another edge, it snaps to that edge's width and tab orientation.
* Hidden positions and pointer hit testing use the active directional width, so the visible tab remains reachable and the full window does not overlap its own content.

Dependency and build impact:

* No product dependencies added; the implementation uses the existing Tkinter geometry and placement APIs.
* `build.spec` and packaging inputs are unchanged; no executable rebuild was needed for this layout-only change.

Test commands and results:

* `py -m pytest -q tests\test_floating_countdown.py -p no:cacheprovider --basetemp=.tmp\pytest-directional-floating` — **22 passed**.
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-directional-final` — **218 passed in 0.65s**.
* `py -m compileall -q app main.py` — passed.
* `git diff --check` — passed.

Known limitations:

* The four-edge visual result still needs manual confirmation on the user's actual display scaling and taskbar configuration.
* This milestone remains uncommitted and unpushed until the user confirms acceptance.

## Current fix: side height and edge-anchored resizing

Changed files:

* `app/floating_countdown.py`: gives left/right docking a 144×72 window while keeping top/bottom at 220×84; uses the release mouse position when deciding the new edge and anchors the resized window to that edge.
* `tests/test_floating_countdown.py`: adds regression coverage for the 72-pixel side height and for a stale window-coordinate scenario during top-to-right docking.
* `README.md`: documents the side height and edge-anchored resize behavior.

Root cause and current behavior:

* The side layout needed 68 pixels for the current Tk font metrics, but retained 84 pixels, leaving 16 pixels of unused vertical space. The new 72-pixel height keeps 4 pixels of headroom.
* Drag release previously ignored the release event and trusted the window manager's current top-left coordinate. When that coordinate lagged behind the mouse, resizing could be calculated from an old position and appear to move away from the target edge.
* Release handling now derives the position from the mouse release point, clamps it using the active pre-resize dimensions, then recalculates the final position with the new dimensions. The target left/right screen boundary therefore remains fixed during the width shrink.

Dependency and build impact:

* No product dependencies added; the implementation uses existing Tkinter geometry and event APIs.
* `build.spec` and packaging inputs are unchanged; no executable rebuild was needed for this layout-only change.

Test commands and results:

* `py -m pytest -q tests\test_floating_countdown.py -p no:cacheprovider --basetemp=.tmp\pytest-directional-regression-green2` — **23 passed in 0.29s**.
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-height-anchor-full` — **219 passed in 0.57s**.
* Real Tk diagnostic: left/right `144×72`, content request height `68`; top/bottom `220×84`.
* Real Tk top-to-right transition: final right boundary remained equal to the screen width after resizing.

Known limitations:

* Manual visual acceptance is still required on the user's actual DPI, multi-monitor, and taskbar configuration.
* This milestone remains uncommitted and unpushed until the user confirms acceptance.

## Repository cleanup follow-up

* 从 Git 跟踪中移除 `overview.md`；文件仍保留在本地并已加入 `.gitignore`，不会再次推送。
* 本次不改变程序代码、依赖、安装、运行或测试命令。

## Current implementation: v1.2 eye-break flow

Changed files:

* `app/persistence.py`: 新增同目录临时文件、刷新、`os.replace()` 原子 JSON 保存，以及可选 `.bak` 恢复读取。
* `app/config.py`, `app/settings_window.py`: 集中校验有限数值和配置范围；设置窗口显示具体错误与本地统计。
* `app/state.py`, `app/paths.py`: 状态复用原子保存，新增按本地 ISO 日期持久化的今日免打扰标记和 `stats.json` 路径。
* `app/core/events.py`, `app/core/event_bus.py`, `app/core/timer_engine.py`: 区分计划/手动提醒来源、自然完成/主动跳过，并实现今日免打扰及跨午夜恢复。
* `app/reminder_window.py`, `app/tray.py`, `app/ui/bridge.py`: 增加可见暂停调节、5/15/30 分钟快捷暂停、今日免打扰入口和统计桥接。
* `app/stats.py`: 新增仅基于应用领域事件的本地统计追踪，不读取全局键鼠、摄像头或前台窗口活动。
* `tests/test_persistence.py`, `tests/test_stats.py`, `tests/test_reminder_window.py` 及既有相关测试：覆盖新行为和回归。
* `README.md`, `.gitignore`: 同步用户可见行为、运行数据和验证结果。

Current behavior:

* 配置范围为提醒间隔 `0 < 分钟 <= 1440`、休息时长 `1–3600` 秒、默认暂停 `1–120` 分钟、离开检测 `0–1440` 分钟；NaN、正负 Infinity、非整数休息时长和非法类型会被拒绝。
* 设置窗口文本解析同样经过集中校验，超范围和非有限值不会进入内存配置或覆盖磁盘配置；重启后已保存的今日免打扰会恢复对应悬浮状态。
* 配置保存前生成同目录临时 JSON，成功刷新后原子替换；替换失败会抛出错误并保留旧主文件；主配置损坏时尝试 `.bak`。
* 自然倒计时发布 `ReminderCompleted`，主动跳过/关闭发布 `ReminderDismissed`；`立即休息` 携带 `source="manual"`，不进入计划提醒完成率。
* 今日免打扰按本地日期保存，跨重启有效；跨午夜清除标记并从新的提醒间隔开始。它只抑制自动提醒，“立即休息”仍可用，“恢复”可提前解除。
* 统计包含计划提醒、自然完成、主动跳过、暂停四项；暂停包括普通暂停和今日免打扰。损坏统计文件恢复为零，清空统计只重置 `stats.json`。

Dependency and install/run impact:

* 未新增运行时依赖；继续使用 Python 标准库、Tkinter、已有 `pystray` 和 Pillow。
* 新增本地运行文件 `stats.json`，并加入 `.gitignore`；安装、运行和 PyInstaller 命令不变。

Test commands and results:

* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-v12-baseline` — **228 passed in 1.20s**。
* `py -m pytest -q tests/test_persistence.py tests/test_config.py tests/test_state.py -p no:cacheprovider --basetemp=.tmp\pytest-v12-persistence-green` — **39 passed in 0.14s**。
* `py -m pytest -q tests/test_timer_engine.py tests/test_reminder_window.py tests/test_bridge.py -p no:cacheprovider --basetemp=.tmp\pytest-v12-outcome-green` — **67 passed in 0.15s**。
* `py -m pytest -q tests/test_state.py tests/test_timer_engine.py tests/test_reminder_window.py tests/test_tray.py tests/test_bridge.py -p no:cacheprovider --basetemp=.tmp\pytest-v12-today-green` — **91 passed in 0.26s**。
* `py -m pytest -q tests/test_stats.py tests/test_bridge.py tests/test_settings_window.py -p no:cacheprovider --basetemp=.tmp\pytest-v12-stats-green` — **46 passed in 0.25s**。
* `py -m pytest -q tests/test_settings_window.py tests/test_bridge.py tests/test_config.py -p no:cacheprovider --basetemp=.tmp\pytest-v12-final-hardening-green` — **73 passed in 0.23s**。
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-v12-final` — **280 passed in 1.34s**。
* `py -m compileall -q app main.py` — passed。
* `git diff --check` — passed；仅输出既有文件的 LF/CRLF 提示，没有空白错误。

Known limitations and next work:

* 尚未完成用户实际 Windows DPI、多显示器、托盘和提醒窗口的手动 GUI 验收；不能把本地自动化测试当作手动验收。
* 用户已确认“验收没问题”，v1.2 已推送到 GitHub；当前本地分支为 `master`。
* 工作树中的原有 `v1.1体验优化.md`、`docs/` 和 `out/` 改动仍需继续保留并单独核对。

## Repository cleanup: keep public tree focused

* 从 Git 跟踪中移除 `架构重构方案.md`、`v1.1体验优化.md` 和 `v1.2功能规划.md`；这些文件仍保留在本地，并已加入 `.gitignore`，不会再次被推送。
* `docs/` 和 `out/` 原本未被跟踪，本次未加入提交。
* 源码、测试、资源、依赖、构建入口、`README.md`、`HANDOFF.md` 和 `AGENTS.md` 保留。
* 本次只改变远程仓库内容，不改变程序行为、依赖、安装、运行或测试命令。

## Current planning: v1.2 功能开发规划

Changed files:

* `v1.2功能规划.md`: 新增配置可靠性、提醒窗口快捷暂停、本地统计和暂停到今天结束的开发规划、数据语义、阶段顺序和验收标准。
* `v1.1体验优化.md`: 增加边界说明，避免 v1.1 体验优化文档与 v1.2 新功能规划冲突。

Current behavior:

* 只修改规划文档，不修改程序行为、依赖、安装、运行和构建命令。
* v1.2 只聚焦护眼提醒，计划交付阶段 1 至 3；番茄钟不纳入产品范围。
* 本地统计的三个指标定义为提醒次数、用户明确跳过次数和成功暂停次数；自动结束的休息不算跳过。
* “今天不再提醒”按本地自然日持久化，跨重启有效，跨午夜自动解除。

Dependency and test impact:

* 规划默认不新增运行时依赖，配置校验使用 Python 标准库 `math.isfinite`，数据继续使用本地 JSON。
* 本次只改 Markdown 规划文档，未运行自动化测试。

Known limitations:

* 这是开发规划，不代表上述功能已经实现或完成手动验收。
* 当前工作区仍存在此前未提交的代码、测试和工具文件；开发 v1.2 前应先单独整理并验收现有修改。

## Current planning update: remove Pomodoro scope

Changed files:

* `v1.2功能规划.md`: 删除番茄钟阶段、模式设计、涉及文件和验收标准，明确 EyeBreak 只聚焦护眼提醒。
* `v1.1体验优化.md`: 删除对番茄钟规划的引用。

Current behavior:

* 只修改规划文档，不修改程序行为、依赖、安装、运行和构建命令。
* v1.2 仅保留配置可靠性、提醒窗口快捷暂停、本地统计和“今天不再提醒”三个阶段。

Dependency and test impact:

* 依赖不变。
* 本次只改 Markdown 规划文档，未运行自动化测试。

Known limitations:

* 番茄钟仍会出现在早期历史记录和“未实现范围”说明中，表示它明确不属于当前产品范围，不代表待开发功能。

## Current planning finalization: v1.2 eye-break scope

Changed files:

* `v1.2功能规划.md`: 根据最终产品定位重写为完整的护眼提醒 v1.2 规划，删除番茄钟开发阶段、前台检测、全局键鼠监控和摄像头监控；明确倒计时完成、跳过、暂停和未结束的结果语义。
* `docs/superpowers/plans/2026-09-01-eyebreak-v1-2.md`: 新增按明日开发顺序拆分的实施计划，覆盖测试、实现、验收、提交和推送边界。

Current behavior:

* 本次只修改规划文档，不修改程序行为、依赖、安装、运行和构建命令。
* v1.2 开发阶段为：配置合法性与安全保存、提醒窗口快捷暂停、今天不再提醒、本地统计和倒计时结果、完整回归与验收。
* EyeBreak 不监督用户；鼠标移动、键盘输入、后台窗口、系统通知和 UAC 不参与休息结果判断。
* 统计中的“完成”仅表示提醒倒计时自然结束，不代表程序验证了用户真实的视觉休息。

Dependency and test impact:

* 规划不新增运行时依赖，使用 Python 标准库 JSON、原子文件替换和 `math.isfinite`。
* 本次只改 Markdown 规划文档，未运行自动化测试。

Known limitations:

* 实施计划尚未执行，所有 v1.2 功能仍未实现，也没有完成手动 GUI 验收。
* `docs/superpowers/plans/2026-09-01-eyebreak-v1-2.md` 中的提交命令仅供明日开发阶段使用，不能跳过测试、文档同步和用户验收。

## Acceptance: performance optimization milestone

* On 2026-09-01, the user confirmed: “功能都能够正常运行，验收通过”。
* Manual acceptance for the performance optimization, monitoring, temporary configuration sync/restore, and verified runtime behavior is **passed**.
* No commit or push was performed; the accepted changes remain in the working tree for the user to review and commit when ready.

## Current optimization: reduce idle background CPU and allocation churn

Changed files:

* `app/idle.py`: caches the Win32 ctypes structure and API function references with a one-entry standard-library cache instead of rebuilding them on every timer tick.
* `app/fullscreen.py`: caches the Win32 ctypes structures and API function references with the same one-entry cache; existing `False` fallbacks remain unchanged.
* `app/ui/bridge.py`: skips Tk label updates while the floating countdown is hidden, using the existing `should_update_display()` contract.
* `tests/test_idle.py`, `tests/test_fullscreen.py`, `tests/test_bridge.py`: add cache reuse and hidden-window refresh regression coverage.

Current behavior:

* Reminder timing, idle/fullscreen detection semantics, error fallbacks, and the one-second timer cadence are unchanged.
* Hidden floating countdown windows no longer receive a per-second Tk `Label.configure()` call; showing the window still requests an immediate tick.

Performance evidence:

* Same 1,000-tick cProfile benchmark: `0.107s / 174,455 calls` before the change; `0.026s / 29,602 calls` after the change.
* Same 1,000-call detector benchmark with tracemalloc: idle `73.57ms` → `21.74ms`, fullscreen `149.65ms` → `12.16ms`.
* These are synthetic process-local measurements, not a Task Manager RSS measurement.

Dependency and build impact:

* No dependencies added; `functools.lru_cache` is Python standard library.
* Install, run, packaging, and build commands are unchanged. The executable was rebuilt successfully as a packaging verification.

Test commands and results:

* `py -m pytest -q tests\\test_bridge.py::test_on_tick_updates_floating_label tests\\test_bridge.py::test_on_tick_skips_hidden_floating_window_update -p no:cacheprovider --basetemp=.tmp\\pytest-perf-green-bridge` — **2 passed**.
* `py -m pytest -q tests\\test_idle.py::test_get_idle_seconds_windows_calls_api tests\\test_idle.py::test_get_idle_seconds_reuses_win32_api_cache -p no:cacheprovider --basetemp=.tmp\\pytest-perf-green-idle` — **2 passed**.
* `py -m pytest -q tests\\test_fullscreen.py::test_is_foreground_window_fullscreen_returns_false_outside_windows tests\\test_fullscreen.py::test_fullscreen_detector_reuses_win32_api_cache -p no:cacheprovider --basetemp=.tmp\\pytest-perf-green-fullscreen` — **2 passed**.
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\\pytest-perf-final` — **223 passed in 0.65s**.
* `py -m compileall -q app main.py` — passed.
* `py -m PyInstaller build.spec` — passed; rebuilt `dist\\EyeBreak.exe`.
* `git diff --check` — passed.

Known limitations:

* The performance benchmark is repeatable but synthetic; real-world memory should still be checked with the built app in Task Manager over several minutes.
* PyInstaller emitted an existing third-party `pystray` `SyntaxWarning` in `pystray\\_util\\gtk.py`; the build still completed successfully and this change does not touch that dependency.
* Manual GUI acceptance on the user's actual DPI, multi-monitor, and taskbar configuration remains required.
* This milestone remains uncommitted and unpushed until user acceptance.

## Current fix: horizontal floating countdown width

Changed files:

* `app/floating_countdown.py`: reduces the top/bottom dock width from 220 to 96 pixels while keeping the 84-pixel height; left/right remains 144×72.
* `tests/test_floating_countdown.py`: locks the horizontal width to 96 pixels and keeps the real Tk four-edge layout coverage.
* `README.md`: documents the final directional dimensions.

Current behavior:

* The longest current status text requests 78 pixels; the 96-pixel top/bottom window leaves 18 pixels of total horizontal headroom instead of the previous 142 pixels of empty width.
* Top and bottom docking now use 96×84, with the 10-pixel green tab and countdown content still separated.
* Left and right docking remain 144×72, with the 16-pixel reachable side tab.
* Directional width/height switching and edge-anchored resize behavior remain unchanged.

Dependency and build impact:

* No product dependencies added; this is a single Tkinter geometry constant adjustment.
* `build.spec` and packaging inputs are unchanged; no executable rebuild was needed for this layout-only change.

Test commands and results:

* `py -m pytest -q tests\test_floating_countdown.py -p no:cacheprovider --basetemp=.tmp\pytest-horizontal-width-green` — **23 passed in 0.32s**.
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-horizontal-width-full-final` — **219 passed in 0.67s**.
* Real Tk diagnostic: top/bottom `96×84`, content request width `78`, content height `74`.
* `py -m compileall -q app main.py` — passed.
* `git diff --check` — passed.

Known limitations:

* Manual visual acceptance is still required on the user's actual DPI, multi-monitor, and taskbar configuration.
* This milestone remains uncommitted and unpushed until the user confirms acceptance.

## Current fix: auto-hide docked window after opening

Changed files:

* `app/floating_countdown.py`: after enabling/reopening the floating window, schedules the existing one-shot 200 ms pointer-outside check so docked windows collapse without requiring a prior mouse-enter/leave cycle.
* `tests/test_floating_countdown.py`: adds regression coverage proving that enabling a docked window schedules the existing hide callback.
* `README.md`: documents automatic collapse after startup and tray reopening.

Root cause and current behavior:

* Startup and tray re-enable paths made a docked window visible, but did not schedule a hide check. Hiding therefore depended on a later `<Leave>` event, which never occurred if the pointer had not first entered the window.
* `set_enabled(True)` now reuses `schedule_hide()`. Tkinter performs one delayed pointer check; if the pointer is outside, the existing `hide()` path moves the window to its reachable edge tab. If the pointer is inside, the check exits and the existing `<Leave>` event handles later hiding. Undocked windows and active drags remain unaffected.

Dependency and build impact:

* No new dependencies; the fix uses the existing Tkinter `after()` scheduling and pointer hit-test logic.
* `build.spec` and packaging inputs are unchanged; no executable rebuild was needed for this code-only behavior fix.

Test commands and results:

* `python -m pytest -q tests/test_floating_countdown.py -k enabling_docked_window_schedules_initial_hide_check -p no:cacheprovider --basetemp=.tmp\pytest-floating-red` — could not start because the active `python` environment has no `pytest` module.
* `py -m pytest -q tests/test_floating_countdown.py -k enabling_docked_window_schedules_initial_hide_check -p no:cacheprovider --basetemp=.tmp\pytest-floating-red` — **failed as expected before the fix**: 1 failed, 23 deselected.
* `py -m pytest -q tests/test_floating_countdown.py -k "enabling_docked_window_schedules_initial_hide_check or schedule_hide or show_cancels_pending_hide" -p no:cacheprovider --basetemp=.tmp\pytest-floating-green` — **4 passed**.
* `py -m pytest -q tests/test_floating_countdown.py -p no:cacheprovider --basetemp=.tmp\pytest-floating-all` — **24 passed in 0.33s**.
* `py -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest-all` — **220 passed in 0.69s**.

Known limitations:

* Manual visual acceptance is still required on the user's actual DPI, multi-monitor, and taskbar configuration.
* This milestone remains uncommitted and unpushed until the user confirms acceptance.
