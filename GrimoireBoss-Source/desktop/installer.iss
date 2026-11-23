; Installateur de Grimoire Boss (Inno Setup 6). Compilé par build.bat.
; Installation pour l'utilisateur seul : pas besoin d'être administrateur.
#define AppName "Grimoire Boss"
#define AppVersion "0.1.0"
#define AppExe "GrimoireBoss.exe"

[Setup]
AppId={{4E1B7C2A-9D35-4F80-B6A2-7C51E0D93F48}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Rubicon
AppPublisherURL=https://bworkshop.app/plugins/fiche/?slug=grimoire-boss
DefaultDirName={autopf}\GrimoireBoss
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=GrimoireBoss-Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "build\GrimoireBoss\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
