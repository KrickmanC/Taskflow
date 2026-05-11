#define MyAppName "Taskflow"
#define MyAppVersion "1.3.0"
#define MyAppPublisher "Taskflow"
#define MyAppURL "https://taskflow.so"

[Setup]
AppId={{6D3F79C6-2E21-4A6C-8C12-7A5CF1000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\Taskflow
DefaultGroupName=Taskflow
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=TaskflowSetup-{#MyAppVersion}-x64
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Files]
Source: "..\..\..\*"; DestDir: "{app}\repo"; Flags: recursesubdirs ignoreversion; Excludes: ".git,node_modules,.turbo,dist"
Source: "winsw\WinSW-x64.exe"; DestDir: "{app}\winsw"; Flags: ignoreversion
Source: "minio\minio.exe"; DestDir: "{app}\minio"; Flags: ignoreversion
Source: "redis\*"; DestDir: "{app}\redis"; Flags: recursesubdirs ignoreversion skipifsourcedoesntexist

[Dirs]
Name: "{commonappdata}\Taskflow"
Name: "{commonappdata}\Taskflow\logs"
Name: "{commonappdata}\Taskflow\backups"
Name: "{commonappdata}\Taskflow\minio"
Name: "{commonappdata}\Taskflow\uploads"

[Icons]
Name: "{group}\Taskflow Web"; Filename: "http://localhost:3000"
Name: "{group}\Taskflow Admin"; Filename: "http://localhost:3001/god-mode/"
Name: "{group}\Taskflow Logs"; Filename: "{commonappdata}\Taskflow\logs"
Name: "{group}\Uninstall Taskflow"; Filename: "{uninstallexe}"

[Run]
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\repo\tools\install\windows\preflight.ps1"""; Flags: runhidden
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\repo\tools\install\windows\install.ps1"""; Flags: runhidden

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\repo\tools\install\windows\unregister-services.ps1"""; Flags: runhidden
