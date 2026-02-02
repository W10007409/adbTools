import tkinterdnd2
import os

package_path = os.path.dirname(tkinterdnd2.__file__)
tkdnd_path = os.path.join(package_path, 'tkdnd')

print(f"TKDND_PATH: {tkdnd_path}")
if os.path.exists(tkdnd_path):
    print(f"CONTENTS: {os.listdir(tkdnd_path)}")
