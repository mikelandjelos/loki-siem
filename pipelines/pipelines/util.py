import os


def get_all_files_recursively(directory: str) -> list[str]:
    """Recursively returns a list of all files in the given directory."""
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def get_dataset_name(filepath: str) -> str:

    return os.path.splitext(os.path.basename(filepath))[0]
