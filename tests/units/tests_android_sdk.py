import os
import time
import shutil
import powermake.cache
import powermake.android_sdk

def run_tests():
    sdk_path = os.path.expanduser("~/.powermake/android-sdk")
    if os.path.exists(sdk_path):
        sdk_path = os.path.join(powermake.cache.get_cache_dir(), "android-sdk")
    env = powermake.android_sdk.download_android_sdk(sdk_path, 3)

    assert(shutil.which("javac", path=env["PATH"]) is not None)
    assert(shutil.which(os.path.join(sdk_path, "build-tools/35.0.1/zipalign")) is not None)

    start_time = time.time()
    powermake.android_sdk.download_android_sdk(sdk_path, 3)
    assert(time.time() - start_time < 1.0)  # The SDK is installed, it should definitely take less than a second
