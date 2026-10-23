# EyeBreak

EyeBreak 是一个面向 Windows 中文用户的护眼休息提醒工具。

它用 Python、Tkinter 和 `pystray` 开发。程序会按设定间隔提醒用户休息眼睛，并提供悬浮倒计时、系统托盘菜单、暂停时长选择、开机自启和全屏延后提醒等功能。

<img src="assets/eyebreak-icon.png" alt="EyeBreak 图标" width="120">

## 当前状态

已完成：

* 悬浮倒计时显示距离下一次提醒的剩余时间。
* 悬浮倒计时可拖动，可记住上次位置。
* 悬浮倒计时贴到屏幕边缘后自动隐藏，鼠标碰到后显示。
* 悬浮窗从收起窄条展开时带约 180 毫秒的缓出滑出动画。
* 鼠标离开后，悬浮窗同样以滑出动画收回窄条，而不是瞬间消失。
* 贴边悬浮窗保留 16 像素可触达窄条，鼠标离开后延迟 200 毫秒再隐藏。
* 程序启动或通过托盘重新开启时，若悬浮窗已贴边且鼠标不在窗口内，会在一次 200 毫秒检查后自动收缩为窄条。
* 拖动悬浮窗时不会被自动隐藏，释放后再恢复贴边隐藏逻辑。
* 悬浮倒计时内容区有足够垂直空间，状态文字、倒计时数字和绿色贴边条不会互相遮挡。
* 悬浮窗按贴边方向自适应尺寸：上下贴边为 96×84 像素，左右贴边为 144×72 像素；上下贴边条为 10 像素，左右窄条为 16 像素。
* 未贴边时，悬浮倒计时保持完整显示。
* 悬浮倒计时隐藏时跳过界面数字刷新，显示时立即刷新。
* 暂停时显示“暂停中”，离开时显示“已离开”，全屏时显示“全屏中”。
* 用户离开检测：默认离开 5 分钟后自动延后提醒，返回后重新计时。
* 全屏检测：全屏应用运行时延后提醒，退出全屏后重新计时。
* 系统托盘菜单，包含立即休息、暂停、恢复、设置、开关悬浮窗、开机自启和退出。
* 开机自启开关，写入当前用户 Windows 注册表 `HKCU\...\Run`。
* Autostart synchronizes the current-user Run entry with Windows StartupApproved status.
* 悬浮倒计时启用状态会在启动时恢复；已贴边的悬浮窗显示后会自动恢复贴边隐藏。
* When EyeBreak is already running, launching it again opens and focuses the existing session's Settings window instead of starting another timer or tray session.
* On both manual launch and Windows autostart, a new countdown begins from the configured reminder interval rather than showing a reminder immediately.
* 置顶提醒弹窗和休息倒计时。
* 跳过、暂停、恢复、立即休息、退出流程。
* 提醒弹窗暂停按钮支持鼠标滚轮调整暂停时长。
* 提醒弹窗提供可见的 `−/+` 调节、延后 5/15/30 分钟和“今天不再提醒”按钮。
* 倒计时自然结束记为完成；主动跳过或关闭记为跳过；不会用键鼠、前台窗口或摄像头判断休息是否有效。
* 自定义 EyeBreak 图标：深青渐变底、薄荷色眼睛和琥珀色光点，覆盖托盘、提醒窗口和 Windows 任务栏显示。
* 托盘暂停菜单支持 5、15、30、60、120 分钟。
* JSON 配置，保存提醒间隔、休息时长、暂停时长、离开检测阈值、全屏检测开关和悬浮窗外观设置。
* 设置窗口可调整悬浮窗大小（80%–160%）、隐藏装饰条的颜色和宽度（6–40 像素），并可关闭展开/收起过渡动画。
* 配置拒绝 NaN、Infinity、负数、零值和超出范围的值；配置、状态和统计使用安全的本地 JSON 保存。
* 托盘和提醒窗口支持“今天不再提醒”；该设置按本地日期跨重启保留，跨午夜自动恢复，且不影响“立即休息”。
* 设置窗口显示计划提醒、自然完成、主动跳过、暂停和完成率；统计只保存在本地 `stats.json`。
* 托盘设置窗口，可直接修改常用配置，不需要手动编辑 `config.json`。
* 运行时文件从应用目录读取，避免开机自启时把 `config.json`、`app_state.json`、`stats.json` 或图标资源写到受保护目录。

未实现：

* 账号系统。
* 云同步。
* 每日报告。
* AI 分析。
* 摄像头检测。
* 完整番茄钟流程。

## 安装

普通用户：下载 `EyeBreak-Setup-<version>.exe` 双击安装。安装包按当前用户安装（不弹 UAC），默认目录 `%LOCALAPPDATA%\Programs\EyeBreak`，会创建开始菜单快捷方式；卸载时一并清理运行期生成的配置、统计文件和开机自启项。安装包由源码构建，见[构建](#构建)中的“生成安装包”。

安装包必须放在**不带低完整性标签**的普通目录里运行（桌面、下载目录等）。Windows 会按 exe 文件的完整性标签启动进程：如果安装包所在文件夹被 AI 工具或沙箱打上 `Low` 标签（`icacls <文件夹>` 能看到 `Mandatory Label\Low Mandatory Level`），双击后进程会以低完整性运行，无法向 `%TEMP%` 解包，报 `Setup was unable to create the directory ... Error 5: 拒绝访问`。把 exe 复制到桌面再运行即可；从 GitHub Release 下载的资产不带 NTFS 标签，不受影响。

从源码运行或开发时，按下文安装依赖。

托盘功能依赖 `pystray` 和 Pillow。

安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

如果 `python` 由 uv 管理，直接运行 `pip` 可能不在 `PATH`，而且该 Python 会被 PEP 668 标记为 externally-managed；使用上面的项目 `.venv` 可以避开这两个问题。

## 运行

启动程序：

```powershell
python main.py
```

如果依赖装在项目 `.venv` 中，使用 `.\.venv\Scripts\python main.py`，或先激活 `.venv`。

首次运行时，EyeBreak 会在应用目录旁生成 `config.json`。运行中还会生成 `app_state.json` 和 `stats.json`；这些文件属于本地运行数据，已被 Git 忽略。配置更新前会保留 `config.json.bak`，主文件损坏时尝试恢复。

## 性能监测

项目提供一个不依赖第三方包的 Windows 性能监测脚本，用于记录真实运行时的 CPU 和 RSS/工作集内存。脚本默认监测 10 分钟、每 5 秒采样一次，并把数据写入 `.tmp\performance.csv`。

监测源码运行版本：

```powershell
py scripts\monitor_performance.py --duration 600 --interval 5 --output .tmp\source-performance.csv -- python main.py
```

监测 PyInstaller 版本时，当前构建是**目录模式（onedir）**，`dist\EyeBreak\EyeBreak.exe` 就是真正的应用进程：它不再先启动引导进程再启动子进程，因此可以直接把启动返回的 PID 交给监测器，不需要再去找子进程：

```powershell
$workdir = (Get-Location).Path
$exePath = (Resolve-Path -LiteralPath 'dist\EyeBreak\EyeBreak.exe').Path
$app = Start-Process -FilePath $exePath -WorkingDirectory $workdir -PassThru
try {
    py scripts\monitor_performance.py --pid $app.Id --duration 600 --interval 5 --output .tmp\exe-performance.csv
}
finally {
    if ($app) { Stop-Process -Id $app.Id -Force -ErrorAction SilentlyContinue }
}
```

也可以监测已经运行的进程：

```powershell
py scripts\monitor_performance.py --pid 1234 --duration 600 --interval 5 --output .tmp\existing-process.csv
```

把 `1234` 换成目标进程的 PID。监测结束后脚本会输出 CPU 平均值、P95、峰值，以及内存初始值、最终值、峰值和变化量。按 `Ctrl+C` 提前停止时，已经采集的数据仍会保留在 CSV 中；脚本不会自动关闭被监测的 EyeBreak 进程。

源码监测命令请使用 `python main.py`，不要写成 `py main.py`。Windows 的 `py.exe` 可能只是启动器，监测器拿到的 PID 可能不是实际运行 EyeBreak 的 Python 进程。目录模式（onedir）的 EXE 监测可以直接使用上面启动命令返回的 PID。

为了快速验收，可以临时把 `config.json` 改成短间隔：

```json
{
  "reminder_interval_minutes": 0.1667,
  "break_duration_seconds": 10,
  "pause_minutes": 1
}
```

验收结束后建议恢复正常值：

```json
{
  "reminder_interval_minutes": 25,
  "break_duration_seconds": 20,
  "pause_minutes": 60
}
```

## 测试

运行自动化测试：

```powershell
python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest
```

最近一次回归：`302 passed in 2.31s`（2026-10-23，悬浮窗外观设置改动后；本机 `.venv` 未安装 pytest，通过临时 `PYTHONPATH` 指向 `.dsh-tmp/test_site` 提供 pytest；常规开发环境装好 pytest 后直接运行上面的命令即可）。

运行前请确保 `.tmp` 目录存在：测试夹具只创建一层临时目录，若 `.tmp` 不存在会报 `FileNotFoundError: [WinError 3]`。

## 构建

用 PyInstaller 构建 Windows 独立可执行文件：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt pyinstaller
.\.venv\Scripts\python -m PyInstaller build.spec
```

产物是目录模式（onedir）的 `dist/EyeBreak/` 文件夹，入口为 `dist/EyeBreak/EyeBreak.exe`，依赖文件在 `dist/EyeBreak/_internal/`。把整个 `dist/EyeBreak/` 文件夹复制到其他 Windows 电脑即可运行，不需要额外安装 Python。

请勿只复制 `EyeBreak.exe`：目录模式下它必须和同级的 `_internal/` 一起存在，单独移动会无法启动。

`version_info.txt` 是 Windows PE 版本资源（公司名、产品名、文件版本、版权等），由 `build.spec` 的 `version=` 参数写入 EXE。发行版必须带上它：缺少版本信息会让可执行文件被浏览器和杀毒软件的信誉机制当成匿名加壳程序，抬高误报概率。修改版本号时，`version_info.txt` 中的 `filevers`/`prodvers` 与 `FileVersion`/`ProductVersion` 需要与 `VERSION` 保持同步。

注意：`config.json`、`app_state.json` 和 `stats.json` 从应用目录读取。打包后如需预置配置，把它们放在 `EyeBreak.exe` 旁边；用安装包安装时，这些文件位于 `%LOCALAPPDATA%\Programs\EyeBreak\`。

### 生成安装包（Inno Setup）

安装包 = PyInstaller onedir 产物 + Inno Setup 外壳。Inno Setup 只是构建工具，不是运行时依赖，只有生成安装包的机器需要安装：

```powershell
winget install --id JRSoftware.InnoSetup -e
# 或从 https://jrsoftware.org/isdl.php 下载 Inno Setup 6.3+
```

然后一条命令完成 PyInstaller 构建和安装包编译：

```powershell
.\scripts\build_installer.ps1
# 只重编安装包、复用已有 dist\EyeBreak\：加 -SkipAppBuild
```

产物是 `dist\installer\EyeBreak-Setup-<version>.exe`，版本号取自 `VERSION`。脚本会先校验 `VERSION` 与 `version_info.txt` 的 `filevers` 一致（不一致直接失败），再调用 `.venv` 里的 PyInstaller 和 `ISCC.exe`，最后打印安装包大小与 SHA-256。

安装包行为：

* 按用户安装到 `{localappdata}\Programs\EyeBreak`，`PrivilegesRequired=lowest`，全程不弹 UAC。不要改成 `Program Files`：程序会往自己目录写 `config.json`，普通用户对 `Program Files` 没有写权限，改设置会失败。
* 必建开始菜单快捷方式；桌面快捷方式默认不勾选；安装完成后可勾选立即启动。
* 安装或升级时如果 EyeBreak 正在运行，安装器会通过程序的单实例互斥量提示先退出，避免覆盖被占用的文件。
* 卸载会删除运行期生成的 `config.json`、`config.json.bak`、`app_state.json`、`stats.json`，并清理 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 和 `StartupApproved\Run` 下的 `EyeBreak` 值。
* 安装向导界面是英文：Inno Setup 不自带简体中文语言文件。需要中文向导时，把 `ChineseSimplified.isl` 放进 Inno Setup 的 `Languages` 目录，并在 `installer.iss` 增加 `[Languages]` 段。
* 安装包和 EXE 一样未做代码签名，首次运行仍可能触发 SmartScreen“未知发布者”。`installer.iss` 已写入安装包的版本资源（公司、产品、版本），与 EXE 的做法一致。

环境说明：

* 建议测试时使用 `--basetemp=.tmp\pytest`，避免受限环境里的临时目录权限问题。
* 当前 Windows 沙箱下，普通权限测试可能在清理 `.tmp\pytest` 时遇到 `PermissionError: [WinError 5]`。提权重跑已通过。

## 验收清单

### 悬浮倒计时

* 启动后，若悬浮窗已贴边且鼠标不在窗口内，屏幕边缘只露出窄条。
* 鼠标移动到窄条上，倒计时面板以滑出动画展开并立即刷新。
* 把面板拖离边缘后，面板完整显示，不再自动隐藏。
* 把面板拖到左、右、上、下任意边缘后，面板贴边。
* 贴边后，鼠标离开面板，面板以滑出动画收回，只保留窄条。
* 通过托盘重新开启已贴边的悬浮窗后，鼠标不在窗口内时会自动隐藏，只保留窄条。
* 窄条宽度足够鼠标稳定触达，鼠标短暂离开时不会立即收起。
* 拖动悬浮窗时面板保持显示，释放后按新的位置或边缘状态工作。
* 上、下贴边时窗口为 96×84 像素；左、右贴边时窗口为 144×72 像素。
* 从上下贴边切换到左右贴边时，缩小动作固定在目标左右边缘，不向远离边缘的方向移动。
* 上、下贴边时，状态文字和倒计时数字完整显示，不被绿色贴边条遮挡。
* 窄条方向正确：右侧贴边时窄条在左，左侧贴边时窄条在右，顶部贴边时窄条在下，底部贴边时窄条在上。
* 面板显示距离下一次提醒的剩余时间。
* 面板可见时，倒计时每秒刷新。
* 面板隐藏时，程序继续计时，但不刷新可见数字。
* 暂停时，标题显示“暂停中”，剩余时间显示为黄色。
* 用户离开达到 `idle_threshold_minutes` 后，标题显示“已离开”。
* 全屏应用运行时，标题显示“全屏中”，提醒延后。
* 退出并重新启动后，悬浮面板回到上次保存的位置。
* 暂停结束后，提醒恢复，悬浮面板显示下一次提醒倒计时。
* 托盘“开关悬浮窗”可以隐藏或显示悬浮倒计时，不影响提醒计时。

### 基础提醒

* 倒计时归零后弹出提醒窗口。
* 提醒窗口居中并置顶。
* 提醒窗口倒计时每秒减少。
* 倒计时结束后，提醒窗口自动关闭。
* 点击跳过后关闭当前提醒，并进入下一轮提醒计时。
* 点击退出后结束程序。
* 倒计时自然结束进入“完成”路径，不复用“跳过”路径。
* 提醒窗口提供可见的暂停时长调节、5/15/30 分钟快捷暂停和“今天不再提醒”。

### 离开检测

* 用户离开达到 `idle_threshold_minutes` 后，不再弹出提醒。
* 用户移动鼠标或按键返回后，提醒间隔重新开始计时。
* 把 `idle_threshold_minutes` 设为 `0` 可以关闭离开检测。

### 全屏检测

* 全屏游戏、视频或演示运行时，不弹出提醒窗口。
* 悬浮倒计时显示“全屏中”和 `--:--`。
* 退出全屏后，下一轮提醒重新计时。
* 设置窗口里的“全屏时延后提醒”可以关闭或开启该功能。
* 普通非全屏窗口不会延后提醒。

### 暂停流程

* 提醒弹窗暂停按钮使用 `config.json` 中的默认暂停时长。
* 鼠标滚轮悬停在暂停按钮上时，可把暂停时长调整到 1 到 120 分钟。
* 点击暂停后，提醒弹窗关闭。
* 暂停期间，悬浮倒计时显示“暂停中”和剩余暂停时间。
* 暂停结束后，提醒恢复，悬浮倒计时显示下一次提醒倒计时。
* `−/+` 每次调整 5 分钟，范围为 1 到 120 分钟；滚轮仍可调节。

### 今天不再提醒

* 托盘和提醒窗口都可以执行“今天不再提醒”。
* 今日免打扰按本地日期跨重启保留，跨午夜自动解除并重新开始提醒间隔。
* 今日免打扰期间不弹出自动提醒，但“立即休息”仍可手动触发。
* “恢复”可以提前解除今日免打扰。

### 系统托盘

* Windows 系统托盘显示 EyeBreak 图标。
* “立即休息”会立刻打开提醒窗口。
* “暂停”展开 5、15、30、60、120 分钟选项。
* 每个暂停选项都按对应时长生效。
* “恢复”清除暂停，并重新开始提醒倒计时。
* “开关悬浮窗”隐藏或显示悬浮倒计时。
* “开机自启”切换 Windows 当前用户注册表启动项。
* “退出”结束程序并移除托盘图标。

如果托盘图标不显示：

1. Windows 11 默认把新图标放进任务栏的 `^` 溢出区；点击 `^`，或在“设置 > 个性化 > 任务栏 > 其他系统托盘图标”中打开 EyeBreak。
2. 不要使用“以管理员身份运行”，也不要在管理员或受限终端中启动。退出程序后，从文件资源管理器双击 `EyeBreak.exe`。
3. 如果启动时出现“Windows 没有接受 EyeBreak 的托盘图标”提示，按提示以普通用户权限重新启动；这说明当前进程的完整性级别不适合托盘图标。
4. 如果 `icacls EyeBreak.exe` 显示 `Mandatory Label\Low Mandatory Level`，说明文件位于受限工作区（例如 DSH 的 `workspace-write` 工作区）。把整个 `dist\EyeBreak` 文件夹**复制**到桌面或普通目录，再从副本启动；不要直接移动，以免 Low 标签跟着文件走。
5. 从源码运行时，工作区也可能让 `.venv\Scripts\python.exe` 继承 Low 标签，导致进程以低完整性启动、托盘图标被 Windows 拒绝。可先运行 `icacls .venv\Scripts\python.exe /setintegritylevel Medium`，再重新启动 `python main.py`；或把项目复制到桌面运行。该修复只影响本机 `.venv`，不属于项目源码。

### 设置窗口

* 托盘“设置”只打开一个设置窗口；再次点击会聚焦已有窗口。
* 设置窗口显示当前提醒间隔、休息时长、默认暂停时长、离开检测阈值和全屏检测开关。
* 设置窗口可调整悬浮窗大小（80%–160%）和隐藏装饰条宽度（6–40 像素）。
* 装饰条颜色支持手动输入 `#RRGGBB` 或通过“选择…”打开颜色选择器。
* 可关闭“启用展开/收起过渡动画”；关闭后悬浮窗立即展开或收起。
* 悬浮窗外观设置保存到 `config.json`，保存后立即应用，重启后保留。
* 调整悬浮窗大小后，状态文字和倒计时数字随尺寸缩放，不被裁切。
* 调整装饰条颜色和宽度后，隐藏状态露出的窄条立即使用新颜色和宽度。
* 关闭过渡动画后，悬浮窗展开和收起都立即切换，不再有滑动过程。
* 输入非法的悬浮窗大小、装饰条宽度或颜色时提示错误，不覆盖 `config.json`。
* 保存合法值后写入 `config.json`。
* 点击“保存”后设置窗口保持打开，可继续调整；需要关闭时使用“取消”、标题栏关闭按钮或系统关闭操作。
* 输入非法值时提示错误，不覆盖 `config.json`。
* 保存提醒间隔后，下一次提醒倒计时立即使用新值。
* 暂停期间保存设置时，当前暂停截止时间不变。
* `idle_threshold_minutes` 设为 `0` 后关闭离开检测。
* 取消勾选“全屏时延后提醒”后关闭全屏延后提醒。
* 设置窗口显示本地统计，完成率分母为零时显示“暂无数据”。
* 清空统计需要确认，且只影响 `stats.json`，不影响配置、悬浮窗位置和当前计时。

### 图标检查

* 托盘、标题栏和任务栏显示新版深青渐变眼睛图标，16/20/24/32 像素下仍能辨认眼睛轮廓。
* 托盘图标显示正常。
* 提醒窗口标题栏显示 EyeBreak 图标。
* Windows 任务栏显示 EyeBreak 图标，而不是默认 Python 图标。
* 图标在 Windows 上观感正常。

## 发布规则

遵循 `AGENTS.md` 中的提交、测试、验收和推送规则。

摘要：

* 用户可见行为、命令、依赖或验收状态变化时，同步更新 `README.md` 和 `HANDOFF.md`。
* 提交前运行相关测试。
* 汇报时写明实际运行的测试命令和结果。
* 没有运行测试就不能声称测试通过。
* 提交前检查 `git status`。
* 不提交临时文件、本地配置、IDE 文件、缓存和草稿。
* 用户明确说“验收没有问题”或“验收没问题”前，不推送到 GitHub。
* 只推送已验收的里程碑。

## 下一步

当前最新发布是 `V3.5`，发布记录以 [GitHub Releases](https://github.com/sAchNMN/EyeBreak/releases) 页面为准。

`V3.5` 在 `V3.4` 基础上的变化：

* 悬浮窗展开和收起增加约 180 ms 的滑出过渡动画，可在设置中关闭。
* 新增悬浮窗外观设置：大小 80%–160%、隐藏装饰条宽度 6–40 像素、装饰条颜色（`#RRGGBB` 或颜色选择器）。
* 外观设置保存后立即应用并写入 `config.json`，旧配置缺少新字段时使用默认值。
* 设置窗口点击“保存”后保持打开，方便继续调整。

发布资产与校验值：

| 资产 | 大小 | SHA-256 |
|---|---|---|
| `EyeBreak-Setup-3.5.exe` | 15,176,401 字节 | `6B76E7504E691F23D0B2471AD58FB5A4E732CCD92C7EF965CE0C7CC4B433B496` |
| `EyeBreak-v3.5-onedir.zip` | 20,021,659 字节 | `73B1C43B7E03C42FB3C83B69D07CD5B857343D2B4A9B642DC1B27D069855B4F0` |

校验下载是否完整：

```powershell
Get-FileHash .\EyeBreak-v3.5-onedir.zip -Algorithm SHA256
Get-FileHash .\EyeBreak-Setup-3.5.exe -Algorithm SHA256
```

彻底消除此类提示需要为可执行文件添加代码签名，并向杀毒软件厂商提交误报申诉。
