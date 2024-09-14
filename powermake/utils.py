import os


def makedirs(path, exist_ok=True):
    if path != '':
        os.makedirs(path, exist_ok=exist_ok)
