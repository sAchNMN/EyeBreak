; EyeBreak Windows installer script (Inno Setup 6.3+)
;
; Build with:  scripts\build_installer.ps1
; Manual:      ISCC.exe /DAppVersion=3.3 installer.iss   (run from the repo root)
;
; Design notes
; * Per-user install (PrivilegesRequired=lowest) into {localappdata}\Programs.
;   EyeBreak stores config.json / app_state.json / stats.json next to the EXE,
;   so a Program Files install would be read-only for standard users and every
;   settings change would fail. A per-user directory is always writable and
;   matches the HKCU autostart entry the app writes.
; * AppMutex reuses the app's single-instance mutex, so setup refuses to
;   overwrite files while EyeBreak is running instead of silently failing.
; * Uninstall removes the runtime JSON files and the HKCU autostart values so
;   no dead entries are left behind.
; * The installer UI is English on purpose: Inno Setup does not ship a Chinese
;   Simplified messages file. To localize, drop ChineseSimplified.isl into the
;   Inno Setup "Languages" folder and add a [Languages] section here.

#define AppName "EyeBreak"
#define AppPublisher "sAchNMN"
#define AppURL "https://github.com/sAchNMN/EyeBreak"

; The build script always passes /DAppVersion (read from VERSION). The fallback
; keeps a manual ISCC run working after a build, but uses the EXE's PE version
; (3.3.0.0) instead of the short VERSION value (3.3).
#ifndef AppVersion
  #define AppVersion GetFileVersion("dist\EyeBreak\EyeBreak.exe")
#endif

[Setup]
AppId={{8E1D5B7A-3C2F-4A96-9D4B-6F0C2E8A7B31}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Setup
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoCopyright=Copyright (C) 2026 sAchNMN. MIT License.
DefaultDirName={localappdata}\Programs\EyeBreak
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist\installer
OutputBaseFilename=EyeBreak-Setup-{#AppVersion}
SetupIconFile=assets\eyebreak.ico
UninstallDisplayIcon={app}\EyeBreak.exe
UninstallDisplayName={#AppName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; The app is a tray process: let the mutex check ask the user to exit instead
; of letting Restart Manager kill a window that only hides to the tray.
CloseApplications=no
RestartApplications=no
AppMutex=EyeBreak.SingleInstance

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\EyeBreak\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "config.json,config.json.bak,app_state.json,stats.json,*.log"

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\EyeBreak.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\EyeBreak.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\EyeBreak.exe"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Runtime data the app writes next to the EXE (never shipped by [Files]).
Type: files; Name: "{app}\config.json"
Type: files; Name: "{app}\config.json.bak"
Type: files; Name: "{app}\app_state.json"
Type: files; Name: "{app}\stats.json"

[UninstallRun]
Filename: "{sys}\reg.exe"; Parameters: "delete ""HKCU\Software\Microsoft\Windows\CurrentVersion\Run"" /v ""EyeBreak"" /f"; Flags: runhidden; RunOnceId: "RemoveAutostartRun"
Filename: "{sys}\reg.exe"; Parameters: "delete ""HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"" /v ""EyeBreak"" /f"; Flags: runhidden; RunOnceId: "RemoveAutostartApproved"