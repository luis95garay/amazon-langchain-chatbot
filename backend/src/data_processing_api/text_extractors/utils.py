from pathlib import Path


def search_folder(folder: str):
    """
    Search for a specific folder and return its absolute path.

    Args:
        folder (str): The name of the folder to search for.

    Returns:
        str or None: The absolute path of the folder if found,
        or None if not found.
    """
    current_path = Path(__file__).resolve()

    folders = ["sagemaker_documentation"]
    if folder in folders:
        sage_path = current_path.parent \
            .parent.parent.parent / "data" / folder
        return str(sage_path)
    else:
        return None
