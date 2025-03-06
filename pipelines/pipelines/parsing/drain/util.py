import os


def rename_files(root_dir: str):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".log_structured.csv") or file.endswith(
                ".log_templates.csv"
            ):
                new_name = file.replace(
                    ".log_structured.csv", "_structured.csv"
                ).replace(".log_templates.csv", "_templates.csv")

                old_file = os.path.join(subdir, file)
                new_file = os.path.join(subdir, new_name)

                os.rename(old_file, new_file)
