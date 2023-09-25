from pathlib import Path


def search_folder(folder: str):
    current_path = Path(__file__).resolve()

    folders = ["sagemaker_documentation"]
    if folder in folders:
        sage_path = current_path.parent \
            .parent.parent.parent / "data" / folder
        return str(sage_path)
    else:
        return None
