from pathlib import Path


def path_to_alias(path: Path) -> str:
    return path.stem.replace("___", "/").lower()
