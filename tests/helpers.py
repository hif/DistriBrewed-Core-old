import os


def get_full_file_path(relative_path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), relative_path)