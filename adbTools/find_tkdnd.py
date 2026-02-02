import tkinterdnd2
import os

package_path = os.path.dirname(tkinterdnd2.__file__)
tkdnd_path = os.path.join(package_path, 'tkdnd')

if os.path.exists(tkdnd_path):
    print(f"FOUND_TKDND_PATH: {tkdnd_path}")
else:
    # Try looking one level up or elsewhere if needed, but usually it's here
    print(f"TKDND_NOT_FOUND_AT: {tkdnd_path}")
    # List dir to see what's there
    print(f"CONTENTS_OF_{package_path}: {os.listdir(package_path)}")
