import os
import io
import shutil
import zipfile
import tarfile
import subprocess
import urllib.request
import typing as T

from .display import print_debug_info, print_info
from .utils import makedirs
from .exceptions import PowerMakeRuntimeError
from .__version__ import __version__

def download_and_extract(url: str, path: str) -> None:
    with urllib.request.urlopen(url) as response:
        if url.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(response.read())) as zip_file:
                for info in zip_file.infolist():
                    extracted_file_path = zip_file.extract(info, path=path)
                    
                    # The top 16 bits of external_attr hold the UNIX permissions
                    # A create_system of 3 means the ZIP was created on a UNIX system
                    if info.create_system == 3:
                        unix_attributes = info.external_attr >> 16
                        if unix_attributes > 0:
                            os.chmod(extracted_file_path, unix_attributes)
        elif url.endswith(".tar.gz"):
            with tarfile.open(fileobj=response, mode="r|gz") as tar:
                tar.extractall(path=path, filter="data")
        else:
            raise NotImplementedError(f"File format extraction not implemented for {url}")


def download_android_sdk(sdk_path: str, verbosity: int, jdk_filename: str = "openjdk-21.0.2_linux-x64_bin.tar.gz", sdk_filename: str = "commandlinetools-linux-15859902_latest.zip") -> T.Dict[str, str]:
    java_environ = {
        "JAVA_HOME": os.path.join(sdk_path, "jdk", "jdk-21.0.2"),
        "PATH": f"{os.path.join(sdk_path, "jdk", "jdk-21.0.2", "bin")}{os.pathsep}{os.environ["PATH"]}"
    }

    lock_file = os.path.join(sdk_path, ".lock")
    if not os.path.exists(lock_file):
        shutil.rmtree(sdk_path, ignore_errors=True)


    jdk_path = os.path.join(sdk_path, "jdk")
    if not os.path.exists(jdk_path):
        makedirs(jdk_path)
        print_info("Downloading JDK 21 for Android SDK", verbosity)
        url = f"https://download.java.net/java/GA/jdk21.0.2/f2283984656d49d69e91c558476027ac/13/GPL/{jdk_filename}"
        print_debug_info(f"Downloading {url} into {jdk_path}", verbosity)
        download_and_extract(url, jdk_path)

    if os.path.exists(lock_file):
        return java_environ



    makedirs(sdk_path)
    print_info("Downloading android SDK", verbosity)
    url = f"https://dl.google.com/android/repository/{sdk_filename}"
    print_debug_info(f"Downloading {url} into {sdk_path}", verbosity)
    download_and_extract(url, sdk_path)

    if subprocess.run([os.path.join(sdk_path, f"cmdline-tools/bin/android{'.exe' if '-win-' in sdk_filename else ''}"), "--no-metrics", f"--sdk={sdk_path}", "sdk", "install", "platforms/android-35", "build-tools/35.0.1", "ndk/27.3.13750724"]).returncode != 0:
        raise PowerMakeRuntimeError("Android SDK download failed")
    
    with open(lock_file, "w") as file:
        file.write(__version__)
    
    return java_environ
