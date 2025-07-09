@echo off
REM build.bat - Windows build script for testing

echo 🚀 Starting RedditTUI build process...

REM Create build directory
if not exist build mkdir build
cd build

REM Copy source files
echo 📂 Copying source files...
xcopy /E /I /Y ..\new-textual\* . >nul 2>&1
if exist ..\README.md copy ..\README.md . >nul 2>&1
if exist ..\build-requirements.txt copy ..\build-requirements.txt . >nul 2>&1
if exist .git rmdir /S /Q .git >nul 2>&1
if exist build rmdir /S /Q build >nul 2>&1
if exist dist rmdir /S /Q dist >nul 2>&1
if exist __pycache__ rmdir /S /Q __pycache__ >nul 2>&1

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install -r requirements.txt
python -m pip install -r build-requirements.txt

REM Create hooks directory and Windows manifest
if not exist hooks mkdir hooks

REM Create Windows UAC manifest file for admin privileges
echo 🔧 Creating Windows UAC manifest...
(
echo ^<?xml version="1.0" encoding="UTF-8" standalone="yes"?^>
echo ^<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"^>
echo   ^<assemblyIdentity
echo     version="1.0.0.0"
echo     processorArchitecture="*"
echo     name="RedditTUI"
echo     type="win32"
echo   /^>
echo   ^<description^>RedditTUI - Terminal User Interface for Reddit^</description^>
echo   ^<trustInfo xmlns="urn:schemas-microsoft-com:asm.v3"^>
echo     ^<security^>
echo       ^<requestedPrivileges^>
echo         ^<requestedExecutionLevel level="requireAdministrator" uiAccess="false"/^>
echo       ^</requestedPrivileges^>
echo     ^</security^>
echo   ^</trustInfo^>
echo   ^<compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1"^>
echo     ^<application^>
echo       ^<!-- Windows 10 and 11 --^>
echo       ^<supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/^>
echo       ^<!-- Windows 8.1 --^>
echo       ^<supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/^>
echo       ^<!-- Windows 8 --^>
echo       ^<supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/^>
echo       ^<!-- Windows 7 --^>
echo       ^<supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"/^>
echo     ^</application^>
echo   ^</compatibility^>
echo ^</assembly^>
) > reddittui.exe.manifest

REM Create hook files
echo 🔧 Creating PyInstaller hooks...
(
echo # PyInstaller hook for Textual framework
echo from PyInstaller.utils.hooks import collect_all, collect_data_files
echo.
echo # Collect all textual modules and data
echo datas, binaries, hiddenimports = collect_all^('textual'^)
echo.
echo # Add additional textual modules that might be missed
echo hiddenimports += [
echo     'textual.app', 'textual.screen', 'textual.widget', 'textual.widgets',
echo     'textual.containers', 'textual.dom', 'textual.events', 'textual.keys',
echo     'textual.message', 'textual.reactive', 'textual.binding', 'textual.css',
echo     'textual.geometry', 'textual.color', 'textual.strip', 'textual.renderables',
echo     'textual.driver', 'textual.drivers', 'textual.file_monitor', 'textual.filter',
echo     'textual.fuzzy', 'textual.logging', 'textual.pilot', 'textual.query',
echo     'textual.signal', 'textual.suggester', 'textual.timer', 'textual.theme',
echo     'textual._context', 'textual._compositor', 'textual._types', 'textual.widgets.widget',
echo     'textual.widgets.input', 'textual.widgets.button', 'textual.widgets.static',
echo     'textual.widgets.progress_bar', 'textual.widgets.progress', 'textual.widgets.label',
echo     'textual.widgets.text_log', 'textual.widgets.text_area', 'textual.widgets.text_input',
echo     'textual.widgets._input', 'textual.widgets._text_input', 'textual._input',
echo     'textual.actions', 'textual._on', 'textual.on', 'textual._callback',
echo     'textual._compose', 'textual._wait', 'textual._timer', 'textual._task',
echo     'textual.widgets._button', 'textual.widgets._static', 'textual.widgets._widget',
echo     'textual._keyboard', 'textual._cursor', 'textual._clipboard',
echo     'textual.widgets._text_area', 'textual.widgets._select', 'textual.widgets._switch',
echo     'textual.widgets._textarea', 'textual._driver', 'textual._terminal',
echo     'textual._ansi_sequences', 'textual._system_clipboard', 'textual._xterm_parser',
echo     'textual._modal', 'textual._screen_stack', 'textual._focus', 'textual._modal_screen',
echo     'textual.screen._modal_screen', 'textual._screen', 'textual._path', 'textual._runner',
echo ]
echo.
echo # Collect CSS files and other data files
echo datas += collect_data_files^('textual', includes=['*.css', '*.tcss', '*.py']^)
echo.
echo # Add Rich dependencies
echo rich_datas, rich_binaries, rich_hiddenimports = collect_all^('rich'^)
echo datas += rich_datas
echo binaries += rich_binaries
echo hiddenimports += rich_hiddenimports
) > hooks\hook-textual.py

(
echo # PyInstaller hook for PRAW
echo from PyInstaller.utils.hooks import collect_all, collect_data_files
echo.
echo # Collect all PRAW modules and data
echo datas, binaries, hiddenimports = collect_all^('praw'^)
echo.
echo # Add additional PRAW modules
echo hiddenimports += [
echo     'praw', 'prawcore', 'requests', 'urllib3', 'certifi', 'charset_normalizer',
echo     'idna', 'websocket', 'update_checker',
echo ]
echo.
echo # Collect certificates and data files
echo datas += collect_data_files^('certifi'^)
echo datas += collect_data_files^('requests'^)
) > hooks\hook-praw.py

REM Analyze dependencies
echo 🔍 Analyzing dependencies...
python -m pipreqs --force --mode no-pin .
echo Generated requirements:
type requirements.txt

REM Create spec file
echo ⚙️  Creating PyInstaller spec file...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo import os
echo import sys
echo from PyInstaller.utils.hooks import collect_all, collect_data_files
echo.
echo # Determine platform-specific settings
echo is_windows = sys.platform.startswith^('win'^)
echo is_macos = sys.platform.startswith^('darwin'^)
echo is_linux = sys.platform.startswith^('linux'^)
echo.
echo # Collect all dependencies
echo textual_datas, textual_binaries, textual_hiddenimports = collect_all^('textual'^)
echo rich_datas, rich_binaries, rich_hiddenimports = collect_all^('rich'^)
echo praw_datas, praw_binaries, praw_hiddenimports = collect_all^('praw'^)
echo.
echo # Collect data files
echo datas = []
echo datas += textual_datas
echo datas += rich_datas
echo datas += praw_datas
echo.
echo # Add any config or data files from your project ^(NOT Python modules^)
echo if os.path.exists^('themes'^):
echo     datas += [^('themes', 'themes'^)]
echo if os.path.exists^('config'^):
echo     datas += [^('config', 'config'^)]
echo if os.path.exists^('assets'^):
echo     datas += [^('assets', 'assets'^)]
echo.
echo # Windows manifest for admin privileges
echo manifest_file = None
echo if is_windows and os.path.exists^('reddittui.exe.manifest'^):
echo     manifest_file = 'reddittui.exe.manifest'
echo.
echo # Base hidden imports
echo base_hiddenimports = [
echo     'textual.app', 'textual.widgets', 'textual.screen', 'textual.containers',
echo     'textual.query', 'textual.message', 'textual.binding', 'textual.reactive',
echo     'textual._app', 'textual._screen_stack', 'textual._modal', 'textual._focus',
echo     'textual.theme', 'textual.css', 'textual.geometry', 'textual.events',
echo     'textual.keys', 'textual.dom', 'textual.strip', 'textual.renderables',
echo     'textual.driver', 'textual.drivers', 'textual.file_monitor', 'textual.filter',
echo     'textual.fuzzy', 'textual.logging', 'textual.pilot', 'textual.signal',
echo     'textual.suggester', 'textual.timer', 'textual._context', 'textual._compositor',
echo     'textual._types', 'textual.widget', 'textual.color', 'textual._keyboard',
echo     'textual._input_handler', 'textual._event_broker', 'textual._work_decorator',
echo     'textual._cursor', 'textual._clipboard', 'textual._driver', 'textual._terminal',
echo     'textual._ansi_sequences', 'textual._system_clipboard', 'textual._xterm_parser',
echo     'textual.widgets._input', 'textual.widgets._text_input', 'textual._input',
echo     'textual.widgets._text_area', 'textual.widgets._textarea', 'textual.widgets._select',
echo     'textual._modal', 'textual._screen_stack', 'textual._focus', 'textual._modal_screen',
echo     'textual.screen._modal_screen', 'textual._screen', 'textual._path', 'textual._runner',
echo     'textual._compose', 'textual._wait', 'textual._timer', 'textual._task',
echo     'rich.console', 'rich.text', 'rich.markup', 'rich.table', 'rich.tree',
echo     'rich.panel', 'rich.progress', 'rich.syntax', 'rich.markdown', 'rich.style',
echo     'rich.segment', 'rich.measure', 'rich.protocol', 'rich._loop', 'rich.control',
echo     'praw', 'prawcore', 'requests', 'urllib3', 'certifi', 'charset_normalizer',
echo     'idna', 'websocket', 'asyncio', 'asyncio.events', 'asyncio.futures', 'asyncio.tasks', 
echo     'asyncio.coroutines', 'json', 'datetime', 'os', 'sys', 'pathlib',
echo     'configparser', 'base64', 'hashlib', 'hmac', 'secrets', 'threading',
echo     'queue', 'time', 'logging', 'traceback', 'typing', 'dataclasses',
echo     'enum', 'functools', 'itertools', 'collections', 'weakref', 'copy',
echo     'pickle', 'sqlite3', 'platform', 'socket', 'ssl', 'email', 'html',
echo     'xml', 'zlib', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile', 'tempfile',
echo     'shutil', 'glob', 'fnmatch', 'linecache', 'inspect', 'ast', 'dis',
echo     'importlib', 'pkgutil', 'atexit', 'signal', 'subprocess', 'select', 'termios', 'tty',
echo     'services', 'services.reddit_service', 'components', 'utils', 'utils.logger',
echo     'components.post_list', 'components.sidebar', 'components.account_management_screen',
echo     'components.post_view_screen', 'components.settings_screen', 'components.user_profile_screen',
echo     'components.comment_screen', 'components.qr_screen', 'components.subreddit_screen',
echo     'components.post_creation_screen', 'components.credits_screen', 'components.rate_limit_screen',
echo     'components.theme_creation_screen', 'components.messages_screen', 'components.advanced_search_screen',
echo     'components.subreddit_management_screen', 'components.help_screen',
echo ]
echo.
echo # Platform-specific hidden imports
echo platform_hiddenimports = []
echo if is_windows:
echo     platform_hiddenimports += [
echo         'win32api', 'win32con', 'win32file', 'win32pipe', 'win32process',
echo         'win32security', 'pywintypes', 'winerror', 'winreg', 'msvcrt',
echo         'ctypes', 'ctypes.wintypes'
echo     ]
echo elif is_macos:
echo     platform_hiddenimports += [
echo         'select', 'fcntl', 'termios', 'tty', 'pty', 'grp', 'pwd', 'resource',
echo         'syslog', 'mmap', 'curses', 'curses.ascii', 'curses.panel', 'curses.textpad'
echo     ]
echo elif is_linux:
echo     platform_hiddenimports += [
echo         'select', 'fcntl', 'termios', 'tty', 'pty', 'grp', 'pwd', 'spwd',
echo         'crypt', 'posix', 'resource', 'syslog', 'mmap', 'curses',
echo         'curses.ascii', 'curses.panel', 'curses.textpad'
echo     ]
echo.
echo # Combine all hidden imports
echo all_hiddenimports = ^(textual_hiddenimports + rich_hiddenimports + 
echo                     praw_hiddenimports + base_hiddenimports + platform_hiddenimports^)
echo.
echo # Remove duplicates
echo all_hiddenimports = list^(set^(all_hiddenimports^)^)
echo.
echo # Entry point - adjust this to match your main file
echo entry_point = 'main.py'
echo.
echo a = Analysis^(
echo     [entry_point],
echo     pathex=[],
echo     binaries=textual_binaries + rich_binaries + praw_binaries,
echo     datas=datas,
echo     hiddenimports=all_hiddenimports,
echo     hookspath=['hooks'],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=None,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=None^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='reddittui',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=True,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     icon=None,
echo     uac_admin=True,
echo     uac_uiaccess=False,
echo     manifest=manifest_file,
echo ^)
) > reddittui.spec

REM Build the application
echo 🔨 Building standalone executable...
pyinstaller --clean reddittui.spec

REM Check if build was successful
if exist "dist\reddittui.exe" (
    echo ✅ Build successful!
    echo 📦 Executable created in: %CD%\dist\
    dir dist\
) else (
    echo ❌ Build failed!
    exit /b 1
)

echo 🎉 Build complete!
pause