import os
import io
import shutil
import zipfile
import subprocess
import urllib.request

from .display import print_info
from .utils import makedirs
from .exceptions import PowerMakeRuntimeError
from .__version__ import __version__

def download_android_sdk(sdk_path: str, verbosity: int) -> None:
    lock_file = os.path.join(sdk_path, ".lock")
    if os.path.exists(lock_file):
        return
    
    shutil.rmtree(sdk_path, ignore_errors=True)

    print_info("Downloading android SDK", verbosity)

    makedirs(sdk_path)
    with urllib.request.urlopen("https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip?hl=fr") as response:
        with zipfile.ZipFile(io.BytesIO(response.read())) as zip_file:
            for info in zip_file.infolist():
                extracted_file_path = zip_file.extract(info, path=sdk_path)
                
                # The top 16 bits of external_attr hold the UNIX permissions
                # A create_system of 3 means the ZIP was created on a UNIX system
                if info.create_system == 3:
                    unix_attributes = info.external_attr >> 16
                    if unix_attributes > 0:
                        os.chmod(extracted_file_path, unix_attributes)
    
    if subprocess.run([os.path.join(sdk_path, "cmdline-tools/bin/android"), "--no-metrics", f"--sdk={sdk_path}", "sdk", "install", "platforms/android-35", "build-tools/35.0.1", "ndk/27.3.13750724"]).returncode != 0:
        raise PowerMakeRuntimeError("Android SDK download failed")
    
    with open(lock_file, "w") as file:
        file.write(__version__)
