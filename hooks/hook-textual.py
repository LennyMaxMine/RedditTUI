# hooks/hook-textual.py
# PyInstaller hook for Textual framework

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# Collect all textual modules and data
datas, binaries, hiddenimports = collect_all('textual')

# Add additional textual modules that might be missed
hiddenimports += [
    'textual.app',
    'textual.screen',
    'textual.widget',
    'textual.widgets',
    'textual.widgets._button',
    'textual.widgets._checkbox',
    'textual.widgets._data_table',
    'textual.widgets._directory_tree',
    'textual.widgets._footer',
    'textual.widgets._header',
    'textual.widgets._input',
    'textual.widgets._label',
    'textual.widgets._list_item',
    'textual.widgets._list_view',
    'textual.widgets._log',
    'textual.widgets._markdown',
    'textual.widgets._option_list',
    'textual.widgets._placeholder',
    'textual.widgets._pretty',
    'textual.widgets._progress_bar',
    'textual.widgets._radio_button',
    'textual.widgets._radio_set',
    'textual.widgets._rule',
    'textual.widgets._scrollbar',
    'textual.widgets._select',
    'textual.widgets._selection_list',
    'textual.widgets._sparkline',
    'textual.widgets._static',
    'textual.widgets._switch',
    'textual.widgets._tabs',
    'textual.widgets._text_area',
    'textual.widgets._text_log',
    'textual.widgets._tree',
    'textual.containers',
    'textual.containers._container',
    'textual.containers._grid',
    'textual.containers._horizontal',
    'textual.containers._scrollable_container',
    'textual.containers._vertical',
    'textual.containers._vertical_scroll',
    'textual.dom',
    'textual.events',
    'textual.keys',
    'textual.message',
    'textual.reactive',
    'textual.binding',
    'textual.css',
    'textual.css._style_sheet',
    'textual.css._styles',
    'textual.geometry',
    'textual.color',
    'textual.strip',
    'textual.renderables',
    'textual.renderables._blend_colors',
    'textual.renderables._sparkline',
    'textual.renderables._styled_text',
    'textual.renderables._text',
    'textual.renderables._tree',
    'textual.driver',
    'textual.drivers',
    'textual.drivers._driver',
    'textual.drivers._null_driver',
    'textual.drivers._posix_driver',
    'textual.drivers._windows_driver',
    'textual.drivers._web_driver',
    'textual.file_monitor',
    'textual.filter',
    'textual.fuzzy',
    'textual.logging',
    'textual.pilot',
    'textual.query',
    'textual.signal',
    'textual.suggester',
    'textual.timer',
    'textual.await_complete',
    'textual.await_remove',
    'textual.command',
    'textual.devtools',
    'textual.expand_tabs',
    'textual.features',
    'textual.notifications',
    'textual.parse',
    'textual.theme',
    'textual.tokenize',
    'textual.validation',
    'textual.walk',
    'textual.worker',
    'textual._animator',
    'textual._cache',
    'textual._callback',
    'textual._context',
    'textual._decorator',
    'textual._easing',
    'textual._lines',
    'textual._profile',
    'textual._spatial_map',
    'textual._types',
    'textual._wait',
    'textual._work_decorator',
    'textual._worker_manager',
]

# Collect CSS files and other data files
datas += collect_data_files('textual', includes=['*.css', '*.tcss', '*.py'])

# Add Rich dependencies (Textual depends on Rich)
rich_datas, rich_binaries, rich_hiddenimports = collect_all('rich')
datas += rich_datas
binaries += rich_binaries
hiddenimports += rich_hiddenimports

# Add markdown dependencies if using markdown widgets
try:
    markdown_datas, markdown_binaries, markdown_hiddenimports = collect_all('markdown')
    datas += markdown_datas
    binaries += markdown_binaries
    hiddenimports += markdown_hiddenimports
except:
    pass

# Add tree-sitter dependencies if using syntax highlighting
try:
    tree_sitter_datas, tree_sitter_binaries, tree_sitter_hiddenimports = collect_all('tree_sitter')
    datas += tree_sitter_datas
    binaries += tree_sitter_binaries
    hiddenimports += tree_sitter_hiddenimports
except:
    pass