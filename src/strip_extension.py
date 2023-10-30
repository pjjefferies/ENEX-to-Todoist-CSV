def strip_extension(path_name: str) -> str:
    if "." not in path_name:
        return path_name
    base_name_list: list[str] = path_name.split(".")[:-1]
    base_name: str = ".".join(base_name_list)
    return base_name
