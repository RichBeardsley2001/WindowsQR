; WindowsQR Inno Setup script
; Build: iscc /DAppVersion=1.0.0 WindowsQR.iss
; Or:    iscc WindowsQR.iss  (uses default version below)

#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

#define AppName      "WindowsQR"
#define AppPublisher "RichBeardsley2001"
#define AppURL       "https://github.com/RichBeardsley2001/WindowsQR"
#define AppExeName   "WindowsQR.exe"

[Setup]
AppId={{A3F7B2C1-4D8E-4F23-9B56-7C1E2D3A4B5C}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
; Installer output goes to Output\ directory
OutputDir=Output
OutputBaseFilename=WindowsQR-Setup-{#AppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Require Windows 10+
MinVersion=10.0
; 64-bit only (matches Python x64 build)
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; Request user elevation only if installing to Program Files
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "startup";   \
  Description: "Start &WindowsQR automatically when Windows starts"; \
  GroupDescription: "Additional options:"; \
  Flags: unchecked

[Files]
; All PyInstaller output
Source: "dist\{#AppName}\*"; DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";          Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

[Registry]
; HKCU Run key — added only when "startup" task is selected
Root: HKCU; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; \
  ValueName: "{#AppName}"; \
  ValueData: """{app}\{#AppExeName}"""; \
  Flags: uninsdeletevalue; \
  Tasks: startup

[Run]
Filename: "{app}\{#AppExeName}"; \
  Description: "Launch {#AppName} now"; \
  Flags: nowait postinstall skipifsilent

[UninstallRun]
; Stop the running instance before uninstalling
Filename: "taskkill.exe"; \
  Parameters: "/f /im {#AppExeName}"; \
  Flags: runhidden; \
  RunOnceId: "KillWindowsQR"

[UninstallDelete]
; Clean up any leftover temp update installers
Type: filesandordirs; Name: "{tmp}\WindowsQR_update_*.exe"
