[Setup]
; Basic App Info
AppName=Minesweeper
AppVersion=1.0.1
VersionInfoVersion=1.0.1
AppPublisher=rohanvk
AppCopyright=Copyright (C) 2026 rohanvk
AppPublisherURL=https://github.com/rohanvk/112-Final-Project
AppSupportURL=https://github.com/rohanvk/112-Final-Project/issues
AppUpdatesURL=https://github.com/rohanvk/112-Final-Project/releases
AppId={{B8F3A1E2-9C4D-4F6B-A7E1-3D5C8F2B9A4E}
DefaultDirName={autopf}\Minesweeper
DefaultGroupName=Minesweeper
UninstallDisplayIcon={app}\Minesweeper.exe
Compression=lzma2
SolidCompression=yes
OutputDir=Output
OutputBaseFilename=Minesweeper_Setup

; This tells it to use the icon you made for the installer file itself
SetupIconFile=images\minesweeper.ico

; Automatically uninstall old version before installing the new one
CloseApplications=yes
RestartApplications=no

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; This grabs the compiled .exe from PyInstaller's dist folder
Source: "dist\Minesweeper.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Creates the Start Menu and Desktop shortcuts
Name: "{group}\Minesweeper"; Filename: "{app}\Minesweeper.exe"
Name: "{group}\Uninstall Minesweeper"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Minesweeper"; Filename: "{app}\Minesweeper.exe"; Tasks: desktopicon

[Run]
; Option to launch Minesweeper after installer closes (checked by default)
Filename: "{app}\Minesweeper.exe"; Description: "Launch Minesweeper"; Flags: nowait postinstall skipifsilent

[Code]
// Automatically uninstall old version before installing new one
function GetUninstallString(): String;
var
  sUninstallString: String;
begin
  Result := '';
  if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{B8F3A1E2-9C4D-4F6B-A7E1-3D5C8F2B9A4E}_is1',
    'UninstallString', sUninstallString) then
    Result := sUninstallString
  else if RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{B8F3A1E2-9C4D-4F6B-A7E1-3D5C8F2B9A4E}_is1',
    'UninstallString', sUninstallString) then
    Result := sUninstallString;
end;

function InitializeSetup(): Boolean;
var
  sUninstallString: String;
  iResultCode: Integer;
begin
  Result := True;
  sUninstallString := GetUninstallString();
  if sUninstallString <> '' then begin
    // Run the old uninstaller silently
    sUninstallString := RemoveQuotes(sUninstallString);
    Exec(sUninstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES', '', SW_HIDE, ewWaitUntilTerminated, iResultCode);
  end;
end;