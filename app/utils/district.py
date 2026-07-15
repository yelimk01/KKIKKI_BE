SEOUL_DISTRICTS = {
    "종로구",
    "중구",
    "용산구",
    "성동구",
    "광진구",
    "동대문구",
    "중랑구",
    "성북구",
    "강북구",
    "도봉구",
    "노원구",
    "은평구",
    "서대문구",
    "마포구",
    "양천구",
    "강서구",
    "구로구",
    "금천구",
    "영등포구",
    "동작구",
    "관악구",
    "서초구",
    "강남구",
    "송파구",
    "강동구",
}


def extract_district(addr1: str | None) -> str | None:
    """
    주소에서 서울시 자치구명을 추출한다.

    예:
    '서울특별시 종로구 사직로 161' -> '종로구'
    """

    if not addr1:
        return None

    for word in addr1.split():
        cleaned_word = word.strip()

        if cleaned_word in SEOUL_DISTRICTS:
            return cleaned_word

    return None