"""Developer build command; players launch the resulting app without Python."""
from pathlib import Path
import subprocess
import sys

project = Path(__file__).resolve().parents[1]
output = project.parents[1] / 'build' / 'desktop'
subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm',
                '--distpath', str(output), '--workpath', str(output / 'work'),
                str(project / 'packaging' / 'Orbit.spec')], check=True)
print('Desktop application:', output)
