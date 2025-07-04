#!/bin/bash
# build.sh - Local build script for testing

set -e

echo "🚀 Starting RedditTUI build process..."

# Create build directory
mkdir -p build
cd build

# Copy source files
echo "📂 Copying source files..."
cp -r ../new-textual/* .
cp ../README.md . 2>/dev/null || true
[ -f ../build-requirements.txt ] && cp ../build-requirements.txt .
rm -rf .git build dist __pycache__ *.egg-info

# Install dependencies
echo "📦 Installing dependencies..."
python -m pip install -r requirements.txt
python -m pip install -r build-requirements.txt

# Create hooks directory
mkdir -p hooks

# Create hook files
echo "🔧 Creating PyInstaller hooks..."
cat > hooks/hook-textual.py << 'EOF'
# PyInstaller hook for Textual framework
from PyInstaller.utils.hooks import collect_all, collect_data_files

# Collect all textual modules and data
datas, binaries, hiddenimports = collect_all('textual')

# Add additional textual modules that might be missed
hiddenimports += [
    'textual.app', 'textual.screen', 'textual.widget', 'textual.widgets',
    'textual.containers', 'textual.dom', 'textual.events', 'textual.keys',
    'textual.message', 'textual.reactive', 'textual.binding', 'textual.css',
    'textual.geometry', 'textual.color', 'textual.strip', 'textual.renderables',
    'textual.driver', 'textual.drivers', 'textual.file_monitor', 'textual.filter',
    'textual.fuzzy', 'textual.logging', 'textual.pilot', 'textual.query',
    'textual.signal', 'textual.suggester', 'textual.timer', 'textual.theme',
    'textual._context', 'textual._compositor', 'textual._types', 'textual.widgets.widget',
    'textual.widgets.input', 'textual.widgets.button', 'textual.widgets.static',
    'textual.widgets.progress_bar', 'textual.widgets.progress', 'textual.widgets.label',
    'textual.widgets.text_log', 'textual.widgets.text_area', 'textual.widgets.text_input',
    'textual.widgets._input', 'textual.widgets._text_input', 'textual._input',
    'textual.actions', 'textual._on', 'textual.on', 'textual._callback',
    'textual._compose', 'textual._wait', 'textual._timer', 'textual._task',
    'textual.widgets._button', 'textual.widgets._static', 'textual.widgets._widget',
    'textual._keyboard', 'textual._cursor', 'textual._clipboard',
    'textual.widgets._text_area', 'textual.widgets._select', 'textual.widgets._switch',
    'textual.widgets._textarea', 'textual._driver', 'textual._terminal',
    'textual._ansi_sequences', 'textual._system_clipboard', 'textual._xterm_parser',
    'textual._modal', 'textual._screen_stack', 'textual._focus', 'textual._modal_screen',
    'textual.screen._modal_screen', 'textual._screen', 'textual._path', 'textual._runner',
]

# Collect CSS files and other data files
datas += collect_data_files('textual', includes=['*.css', '*.tcss', '*.py'])

# Add Rich dependencies
rich_datas, rich_binaries, rich_hiddenimports = collect_all('rich')
datas += rich_datas
binaries += rich_binaries
hiddenimports += rich_hiddenimports
EOF

cat > hooks/hook-praw.py << 'EOF'
# PyInstaller hook for PRAW
from PyInstaller.utils.hooks import collect_all, collect_data_files

# Collect all PRAW modules and data
datas, binaries, hiddenimports = collect_all('praw')

# Add additional PRAW modules
hiddenimports += [
    'praw', 'prawcore', 'requests', 'urllib3', 'certifi', 'charset_normalizer',
    'idna', 'websocket', 'update_checker',
]

# Collect certificates and data files
datas += collect_data_files('certifi')
datas += collect_data_files('requests')
EOF

# Analyze dependencies
echo "🔍 Analyzing dependencies..."
pipreqs --force --mode no-pin .
echo "Generated requirements:"
cat requirements.txt

# Create spec file
echo "⚙️  Creating PyInstaller spec file..."
cat > reddittui.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files

# Determine platform-specific settings
is_windows = sys.platform.startswith('win')
is_macos = sys.platform.startswith('darwin')
is_linux = sys.platform.startswith('linux')

# Collect all dependencies
textual_datas, textual_binaries, textual_hiddenimports = collect_all('textual')
rich_datas, rich_binaries, rich_hiddenimports = collect_all('rich')
praw_datas, praw_binaries, praw_hiddenimports = collect_all('praw')

# Collect data files
datas = []
datas += textual_datas
datas += rich_datas
datas += praw_datas

# Add any config or data files from your project (NOT Python modules)
if os.path.exists('themes'):
    datas += [('themes', 'themes')]
if os.path.exists('config'):
    datas += [('config', 'config')]
if os.path.exists('assets'):
    datas += [('assets', 'assets')]

# Base hidden imports
base_hiddenimports = [
    'textual.app', 'textual.widgets', 'textual.screen', 'textual.containers',
    'textual.query', 'textual.message', 'textual.binding', 'textual.reactive',
    'textual._app', 'textual._screen_stack', 'textual._modal', 'textual._focus',
    'textual.theme', 'textual.css', 'textual.geometry', 'textual.events',
    'textual.keys', 'textual.dom', 'textual.strip', 'textual.renderables',
    'textual.driver', 'textual.drivers', 'textual.file_monitor', 'textual.filter',
    'textual.fuzzy', 'textual.logging', 'textual.pilot', 'textual.signal',
    'textual.suggester', 'textual.timer', 'textual._context', 'textual._compositor',
    'textual._types', 'textual.widget', 'textual.color', 'textual._keyboard',
    'textual._input_handler', 'textual._event_broker', 'textual._work_decorator',
    'textual._cursor', 'textual._clipboard', 'textual._driver', 'textual._terminal',
    'textual._ansi_sequences', 'textual._system_clipboard', 'textual._xterm_parser',
    'textual.widgets._input', 'textual.widgets._text_input', 'textual._input',
    'textual.widgets._text_area', 'textual.widgets._textarea', 'textual.widgets._select',
    'textual._modal', 'textual._screen_stack', 'textual._focus', 'textual._modal_screen',
    'textual.screen._modal_screen', 'textual._screen', 'textual._path', 'textual._runner',
    'textual._compose', 'textual._wait', 'textual._timer', 'textual._task',
    'rich.console', 'rich.text', 'rich.markup', 'rich.table', 'rich.tree',
    'rich.panel', 'rich.progress', 'rich.syntax', 'rich.markdown', 'rich.style',
    'rich.segment', 'rich.measure', 'rich.protocol', 'rich._loop', 'rich.control',
    'praw', 'prawcore', 'requests', 'urllib3', 'certifi', 'charset_normalizer',
    'idna', 'websocket', 'asyncio', 'asyncio.events', 'asyncio.futures', 'asyncio.tasks', 
    'asyncio.coroutines', 'json', 'datetime', 'os', 'sys', 'pathlib',
    'configparser', 'base64', 'hashlib', 'hmac', 'secrets', 'threading',
    'queue', 'time', 'logging', 'traceback', 'typing', 'dataclasses',
    'enum', 'functools', 'itertools', 'collections', 'weakref', 'copy',
    'pickle', 'sqlite3', 'platform', 'socket', 'ssl', 'email', 'html',
    'xml', 'zlib', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile', 'tempfile',
    'shutil', 'glob', 'fnmatch', 'linecache', 'inspect', 'ast', 'dis',
    'importlib', 'pkgutil', 'atexit', 'signal', 'subprocess', 'select', 'termios', 'tty',
    'services', 'services.reddit_service', 'components', 'utils', 'utils.logger',
    'components.post_list', 'components.sidebar', 'components.login_screen',
    'components.post_view_screen', 'components.settings_screen', 'components.user_profile_screen',
    'components.comment_screen', 'components.qr_screen', 'components.subreddit_screen',
    'components.post_creation_screen', 'components.credits_screen', 'components.rate_limit_screen',
    'components.theme_creation_screen', 'components.messages_screen', 'components.account_management_screen',
    'components.advanced_search_screen', 'components.subreddit_management_screen', 'components.help_screen',
]

# Platform-specific hidden imports
platform_hiddenimports = []
if is_windows:
    platform_hiddenimports += [
        'win32api', 'win32con', 'win32file', 'win32pipe', 'win32process',
        'win32security', 'pywintypes', 'winerror', 'winreg', 'msvcrt',
        'ctypes', 'ctypes.wintypes'
    ]
elif is_macos:
    platform_hiddenimports += [
        'select', 'fcntl', 'termios', 'tty', 'pty', 'grp', 'pwd', 'resource',
        'syslog', 'mmap', 'curses', 'curses.ascii', 'curses.panel', 'curses.textpad'
    ]
elif is_linux:
    platform_hiddenimports += [
        'select', 'fcntl', 'termios', 'tty', 'pty', 'grp', 'pwd', 'spwd',
        'crypt', 'posix', 'resource', 'syslog', 'mmap', 'curses',
        'curses.ascii', 'curses.panel', 'curses.textpad'
    ]

# Combine all hidden imports
all_hiddenimports = (textual_hiddenimports + rich_hiddenimports + 
                    praw_hiddenimports + base_hiddenimports + platform_hiddenimports)

# Remove duplicates
all_hiddenimports = list(set(all_hiddenimports))

# Entry point - adjust this to match your main file
entry_point = 'main.py'

a = Analysis(
    [entry_point],
    pathex=[],
    binaries=textual_binaries + rich_binaries + praw_binaries,
    datas=datas,
    hiddenimports=all_hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='reddittui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
EOF

# Build the application
echo "🔨 Building standalone executable..."
pyinstaller --clean reddittui.spec

# Check if build was successful
if [ -f "dist/reddittui" ] || [ -f "dist/reddittui.exe" ]; then
    echo "✅ Build successful!"
    echo "📦 Executable created in: $(pwd)/dist/"
    ls -la dist/
else
    echo "❌ Build failed!"
    exit 1
fi

echo "🎉 Build complete!"