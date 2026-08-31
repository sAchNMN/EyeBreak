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
