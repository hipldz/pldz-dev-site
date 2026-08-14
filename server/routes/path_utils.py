import os

from fastapi import HTTPException, status

INVALID_PATH_SEPARATORS = ("..", "/", "\\")


def has_invalid_path_part(value: str) -> bool:
    return any(sep in value for sep in INVALID_PATH_SEPARATORS)


def resolve_safe_file_path(base_path: str, requested_path: str, empty_detail: str) -> tuple[str, str]:
    normalized_path = requested_path.strip().lstrip('/\\')
    if not normalized_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=empty_detail,
        )

    root_path = os.path.realpath(base_path)
    target_path = os.path.realpath(os.path.join(root_path, normalized_path))
    if os.path.commonpath([root_path, target_path]) != root_path:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this file path is not allowed.",
        )
    return normalized_path, target_path
