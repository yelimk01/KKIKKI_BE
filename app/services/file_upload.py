from pathlib import Path
import uuid

from fastapi import UploadFile


# 이미지 저장 위치
UPLOAD_DIR = Path("app/static/images")


# 폴더 없으면 생성
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def save_file(file: UploadFile) -> str:
    """
    업로드된 파일을 저장하고
    접근 가능한 URL 반환
    """

    # 원본 파일 확장자
    extension = Path(file.filename).suffix

    # 중복 방지용 파일명
    filename = f"{uuid.uuid4()}{extension}"

    file_path = UPLOAD_DIR / filename


    # 파일 저장
    with open(file_path, "wb") as buffer:
        buffer.write(
            file.file.read()
        )


    # DB에 저장할 경로
    return f"/static/images/{filename}"