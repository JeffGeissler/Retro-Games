# Build on each target OS. Both executables share the same dependency collection.
from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

root = Path(SPECPATH).parent
assets = collect_data_files('retro_play', includes=['audio/assets/*'])
assets += copy_metadata('pydraughts')
assets += [(str(root / 'README.md'), 'documentation'),
           (str(root / 'CHECKERS.md'), 'documentation'),
           (str(root / 'AUDIO.md'), 'documentation')]
hidden = collect_submodules('draughts')
# Include the optional system voice backend when installed on the build machine.
try:
    assets += copy_metadata('pyttsx3')
    hidden += collect_submodules('pyttsx3')
except Exception:
    pass
common = dict(pathex=[str(root / 'src')], datas=assets, hiddenimports=hidden,
              excludes=['tkinter', 'pytest', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets'],
              noarchive=False)
a = Analysis([str(root / 'packaging/desktop.py'), str(root / 'packaging/worker.py')], **common)
pyz = PYZ(a.pure)
runtime_hooks = [entry for entry in a.scripts if entry[0] not in ('desktop', 'worker')]
app = EXE(pyz, runtime_hooks + [entry for entry in a.scripts if entry[0] == 'desktop'], [], exclude_binaries=True,
          name='Would You Like to Play', console=False, debug=False, strip=False, upx=False)
worker = EXE(pyz, runtime_hooks + [entry for entry in a.scripts if entry[0] == 'worker'], [], exclude_binaries=True,
             name='orbit-worker', console=True, debug=False, strip=False, upx=False)
collection = COLLECT(app, worker, a.binaries, a.datas, strip=False, upx=False,
                     name='Would You Like to Play')
if sys.platform == 'darwin':
    bundle = BUNDLE(collection, name='Would You Like to Play.app',
                    bundle_identifier='com.retrogames.orbit',
                    info_plist={'CFBundleDisplayName': 'Would You Like to Play',
                                'NSHighResolutionCapable': True,
                                'CFBundleShortVersionString': '0.1.0',
                                'NSHumanReadableCopyright': 'Retro-Games — local preview'})
