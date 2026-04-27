[Setup]
; Basic App Info
AppName=Minesweeper
AppVersion=1.0
AppPublisher=rohanvk
DefaultDirName={autopf}\Minesweeper
DefaultGroupName=Minesweeper
UninstallDisplayIcon={app}\Minesweeper.exe
Compression=lzma2
SolidCompression=yes
OutputDir=Output
OutputBaseFilename=Minesweeper_Setup

; This tells it to use the icon you made for the installer file itself
SetupIconFile=images\minesweeper.ico

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