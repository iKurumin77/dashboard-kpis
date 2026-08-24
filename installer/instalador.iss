[Setup]
AppId={{60C4EC6C-784E-495F-800C-505AAFCFBE16}
AppName=Dashboard KPIs
AppVersion=1.0
DefaultDirName={autopf}\Dashboard KPIs
DefaultGroupName=Dashboard KPIs
DisableProgramGroupPage=no
OutputDir=Output
OutputBaseFilename=DashboardKPIsInstaller
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\assets\icono.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\DashboardKPIs.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\locales\*"; DestDir: "{app}\locales"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\run_app.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Dashboard KPIs"; Filename: "{app}\DashboardKPIs.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icono.ico"
Name: "{commondesktop}\Dashboard KPIs"; Filename: "{app}\DashboardKPIs.exe"; IconFilename: "{app}\assets\icono.ico"

[Run]
Filename: "{app}\DashboardKPIs.exe"; Description: "Launch Dashboard KPIs"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{%USERPROFILE}\.dashboard_kpis"
