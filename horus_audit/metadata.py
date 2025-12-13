from importlib.metadata import PackageNotFoundError, version


def get_version() -> str:
    try:
        return version("horus")
    except PackageNotFoundError:
        return ""
