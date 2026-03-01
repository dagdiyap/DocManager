; DocManager CA Desktop - Inno Setup Installer Script
; Production-grade Windows installer with auto-start and clean uninstall

#define MyAppName "DocManager CA Desktop"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "DocManager Team"
#define MyAppURL "http://localhost:5174"
#define MyAppExeName "DocManager.exe"
#define MyBackendExeName "DocManager.exe"

[Setup]
; App identity
AppId={{A8B9C3D4-E5F6-4A7B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories
DefaultDirName={autopf}\DocManager
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=..\..\..\dist_installer
OutputBaseFilename=DocManagerSetup-v{#MyAppVersion}
SetupIconFile=..\assets\icon.ico
Compression=lzma2/max
SolidCompression=yes

; Windows version requirements
MinVersion=10.0
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; User interface
WizardStyle=modern
DisableWelcomePage=no

; Uninstall
UninstallDisplayIcon={app}\backend\{#MyBackendExeName}
UninstallFilesDir={app}\uninstall

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Start DocManager automatically with Windows"; GroupDescription: "Additional options:"; Flags: unchecked

[Files]
; Backend executable
Source: "..\..\..\dist_package\DocManager-v1.0.0\backend\DocManager"; DestDir: "{app}\backend"; DestName: "{#MyBackendExeName}"; Flags: ignoreversion

; Frontend build
Source: "..\..\..\dist_package\DocManager-v1.0.0\frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration files
Source: "..\..\..\dist_package\DocManager-v1.0.0\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs

; Scripts
Source: "..\..\..\dist_package\DocManager-v1.0.0\scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "..\..\..\dist_package\DocManager-v1.0.0\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; README
Source: "..\..\..\dist_package\DocManager-v1.0.0\README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Dirs]
; Create data directories (with full permissions for app data)
Name: "{app}\data"; Permissions: users-full
Name: "{app}\data\uploads"; Permissions: users-full
Name: "{app}\data\logs"; Permissions: users-full

[Icons]
; Start Menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\scripts\start_backend.bat"; IconFilename: "{app}\backend\{#MyBackendExeName}"; Comment: "Start DocManager Backend Server"
Name: "{group}\Open DocManager Dashboard"; Filename: "{#MyAppURL}/ca"; IconFilename: "{sys}\ieframe.dll"; IconIndex: 0; Comment: "Open CA Dashboard in Browser"
Name: "{group}\Documentation"; Filename: "{app}\docs\guides\USER_GUIDE.md"; Comment: "User Guide"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\scripts\start_backend.bat"; IconFilename: "{app}\backend\{#MyBackendExeName}"; Tasks: desktopicon

; Quick Launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\scripts\start_backend.bat"; Tasks: quicklaunchicon

[Registry]
; Auto-start registry entry (if selected)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "DocManager"; ValueData: """{app}\scripts\start_backend.bat"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
; Initialize database on first install
Filename: "{cmd}"; Parameters: "/C echo Initializing DocManager database..."; StatusMsg: "Setting up database..."; Flags: runhidden

; Option to start application after install
Filename: "{app}\scripts\start_backend.bat"; Description: "Start {#MyAppName} now"; Flags: nowait postinstall skipifsilent shellexec

; Open browser to dashboard
Filename: "{#MyAppURL}/ca"; Description: "Open DocManager Dashboard"; Flags: nowait postinstall skipifsilent shellexec

[UninstallRun]
; Stop any running instances before uninstall
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM {#MyBackendExeName} /T"; Flags: runhidden; RunOnceId: "StopDocManager"

[UninstallDelete]
; Clean up data directory
Type: filesandordirs; Name: "{app}\data\logs"
Type: filesandordirs; Name: "{app}\data\uploads"

[Code]
var
  DataDirPage: TInputDirWizardPage;
  PreserveDataCheckBox: TNewCheckBox;
  
procedure InitializeWizard;
begin
  // Add custom page for data directory selection
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Select Data Directory', 'Where should DocManager store data?',
    'Select the folder where DocManager will store the database and uploaded documents, then click Next.',
    False, 'DocManagerData');
  DataDirPage.Add('');
  DataDirPage.Values[0] := ExpandConstant('{localappdata}\DocManager');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Create .env file if it doesn't exist
    if not FileExists(ExpandConstant('{app}\data\.env')) then
    begin
      FileCopy(ExpandConstant('{app}\config\.env.template'), 
               ExpandConstant('{app}\data\.env'), False);
    end;
    
    // Set up data directory
    CreateDir(DataDirPage.Values[0]);
    
    // Create desktop shortcut that opens browser
    // (additional to the backend start shortcut)
  end;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check if DocManager is already running
  if CheckForMutexes('DocManagerBackendRunning') then
  begin
    if MsgBox('DocManager is currently running. Please close it before continuing.' + #13#10 + #13#10 + 
              'Do you want to try closing it automatically?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Try to kill the process
      Exec('taskkill', '/F /IM DocManager.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end
    else
    begin
      Result := False;
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Response: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    // Ask if user wants to preserve data
    Response := MsgBox('Do you want to keep your data (database and documents)?' + #13#10 + #13#10 +
                       'Click Yes to keep your data.' + #13#10 +
                       'Click No to delete everything.',
                       mbConfirmation, MB_YESNO or MB_DEFBUTTON1);
    
    if Response = IDNO then
    begin
      // User wants to delete everything
      DelTree(ExpandConstant('{app}\data'), True, True, True);
    end;
  end;
end;

[Messages]
WelcomeLabel1=Welcome to [name] Setup
WelcomeLabel2=This will install DocManager CA Desktop on your computer.%n%nDocManager is a professional document management system designed specifically for Chartered Accountants.%n%nIt is recommended that you close all other applications before continuing.
FinishedHeadingLabel=Completing [name] Setup
FinishedLabel=[name] has been installed on your computer.%n%nThe application is now ready to use. Click Finish to exit Setup.
