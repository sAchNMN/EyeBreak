# EyeBreak

EyeBreak 是一个面向 Windows 中文用户的护眼休息提醒工具。

它用 Python、Tkinter 和 `pystray` 开发。程序会按设定间隔提醒用户休息眼睛，并提供悬浮倒计时、系统托盘菜单、暂停时长选择、开机自启和全屏延后提醒等功能。

## 当前状态

已完成：

* 悬浮倒计时显示距离下一次提醒的剩余时间。
* 悬浮倒计时可拖动，可记住上次位置。
* 悬浮倒计时贴到屏幕边缘后自动隐藏，鼠标碰到后显示。
* 未贴边时，悬浮倒计时保持完整显示。
* 悬浮倒计时隐藏时跳过界面数字刷新，显示时立即刷新。
* 暂停时显示“暂停中”，离开时显示“已离开”，全屏时显示“全屏中”。
* 用户离开检测：默认离开 5 分钟后自动延后提醒，返回后重新计时。
* 全屏检测：全屏应用运行时延后提醒，退出全屏后重新计时。
* 系统托盘菜单，包含立即休息、暂停、恢复、设置、开关悬浮窗、开机自启和退出。
* 开机自启开关，写入当前用户 Windows 注册表 `HKCU\...\Run`。
* When EyeBreak is already running, launching it again opens and focuses the existing session's Settings window instead of starting another timer or tray session.
* On both manual launch and Windows autostart, a new countdown begins from the configured reminder interval rather than showing a reminder immediately.
* 置顶提醒弹窗和休息倒计时。
* 跳过、暂停、恢复、立即休息、退出流程。
* 提醒弹窗暂停按钮支持鼠标滚轮调整暂停时长。
* 自定义 EyeBreak 图标，覆盖托盘、提醒窗口和 Windows 任务栏显示。
* 托盘暂停菜单支持 5、15、30、60、120 分钟。
* JSON 配置，保存提醒间隔、休息时长、暂停时长、离开检测阈值和全屏检测开关。
* 托盘设置窗口，可直接修改常用配置，不需要手动编辑 `config.json`。
* 运行时文件从应用目录读取，避免开机自启时把 `config.json`、`app_state.json` 或图标资源写到受保护目录。

未实现：

* 账号系统。
* 云同步。
* 每日报告。
* AI 分析。
* 摄像头检测。
* 完整番茄钟流程。

## 安装

托盘功能依赖 `pystray` 和 Pillow。

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

## 运行

启动程序：

```powershell
python main.py
```

首次运行时，EyeBreak 会在应用目录旁生成 `config.json`。这个文件属于本地运行配置，已被 Git 忽略。

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

最近一次结果：提权重跑后 `73 passed in 0.40s`。

## 构建

用 PyInstaller 构建 Windows 独立可执行文件：

```powershell
pip install pyinstaller
python -m PyInstaller build.spec
```

产物是 `dist/EyeBreak.exe`。把整个 `dist/` 文件夹复制到其他 Windows 电脑即可运行，不需要额外安装 Python。

注意：`config.json` 和 `app_state.json` 从应用目录读取。打包后如需预置配置，把它们放在 `EyeBreak.exe` 旁边。

环境说明：

* 建议测试时使用 `--basetemp=.tmp\pytest`，避免受限环境里的临时目录权限问题。
* 当前 Windows 沙箱下，普通权限测试可能在清理 `.tmp\pytest` 时遇到 `PermissionError: [WinError 5]`。提权重跑已通过。

## 验收清单

### 悬浮倒计时

* 启动后，屏幕边缘只露出窄条。
* 鼠标移动到窄条上，倒计时面板显示并立即刷新。
* 把面板拖离边缘后，面板完整显示，不再自动隐藏。
* 把面板拖到左、右、上、下任意边缘后，面板贴边。
* 贴边后，鼠标离开面板，面板自动隐藏，只保留窄条。
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

### 系统托盘

* Windows 系统托盘显示 EyeBreak 图标。
* “立即休息”会立刻打开提醒窗口。
* “暂停”展开 5、15、30、60、120 分钟选项。
* 每个暂停选项都按对应时长生效。
* “恢复”清除暂停，并重新开始提醒倒计时。
* “开关悬浮窗”隐藏或显示悬浮倒计时。
* “开机自启”切换 Windows 当前用户注册表启动项。
* “退出”结束程序并移除托盘图标。

### 设置窗口

* 托盘“设置”只打开一个设置窗口；再次点击会聚焦已有窗口。
* 设置窗口显示当前提醒间隔、休息时长、默认暂停时长、离开检测阈值和全屏检测开关。
* 保存合法值后写入 `config.json`。
* 输入非法值时提示错误，不覆盖 `config.json`。
* 保存提醒间隔后，下一次提醒倒计时立即使用新值。
* 暂停期间保存设置时，当前暂停截止时间不变。
* `idle_threshold_minutes` 设为 `0` 后关闭离开检测。
* 取消勾选“全屏时延后提醒”后关闭全屏延后提醒。

### 图标检查

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

当前 v1 已发布，发布记录以 GitHub Releases 页面为准。下一步可以继续做更细的用户体验优化，或准备 Windows 安装包。
