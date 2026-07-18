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
