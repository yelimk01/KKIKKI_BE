import json
from pathlib import Path

from app.database import SessionLocal
from app.models import TourContent


DATA_DIR = Path("app/data")


# ==========================================
# 서울 자치구 추출
# ==========================================

def get_district_name(address: str | None):
    """
    주소에서 서울 자치구명을 추출한다.

    예:
    서울특별시 종로구 사직로 161 (세종로)
    -> 종로구
    """

    if not address:
        return None

    districts = [
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
    ]

    for district in districts:
        if district in address:
            return district

    return None



# ==========================================
# JSON → SQLite 저장
# ==========================================

def load_json_to_db():

    db = SessionLocal()

    try:
        json_files = DATA_DIR.glob("*.json")

        for file_path in json_files:

            print(f"Loading {file_path.name}...")

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)


            items = data.get(
                "items",
                []
            )


            for item in items:

                # 이미 존재하는 데이터는 건너뜀
                exists = (
                    db.query(TourContent)
                    .filter(
                        TourContent.contentid
                        == item.get("contentid")
                    )
                    .first()
                )

                if exists:
                    continue


                content = TourContent(

                    # ==========================
                    # 기본 정보
                    # ==========================

                    contentid=item.get(
                        "contentid"
                    ),

                    contenttypeid=int(
                        item.get(
                            "contenttypeid",
                            0
                        )
                    ),

                    title=item.get(
                        "title"
                    ),


                    # ==========================
                    # 주소
                    # ==========================

                    addr1=item.get(
                        "addr1"
                    ),

                    addr2=item.get(
                        "addr2"
                    ),

                    zipcode=item.get(
                        "zipcode"
                    ),


                    # 자치구 저장
                    district_name=get_district_name(
                        item.get("addr1")
                    ),



                    # ==========================
                    # 연락처
                    # ==========================

                    tel=item.get(
                        "tel"
                    ),



                    # ==========================
                    # 위치 정보
                    # ==========================

                    mapx=(
                        float(item["mapx"])
                        if item.get("mapx")
                        else None
                    ),

                    mapy=(
                        float(item["mapy"])
                        if item.get("mapy")
                        else None
                    ),

                    mlevel=(
                        int(item["mlevel"])
                        if item.get("mlevel")
                        else None
                    ),



                    # ==========================
                    # 지역 코드
                    # ==========================

                    areacode=item.get(
                        "areacode"
                    ),

                    sigungucode=item.get(
                        "sigungucode"
                    ),

                    lDongRegnCd=item.get(
                        "lDongRegnCd"
                    ),

                    lDongSignguCd=item.get(
                        "lDongSignguCd"
                    ),



                    # ==========================
                    # 분류
                    # ==========================

                    cat1=item.get(
                        "cat1"
                    ),

                    cat2=item.get(
                        "cat2"
                    ),

                    cat3=item.get(
                        "cat3"
                    ),


                    lclsSystm1=item.get(
                        "lclsSystm1"
                    ),

                    lclsSystm2=item.get(
                        "lclsSystm2"
                    ),

                    lclsSystm3=item.get(
                        "lclsSystm3"
                    ),



                    # ==========================
                    # 이미지
                    # ==========================

                    firstimage=item.get(
                        "firstimage"
                    ),

                    firstimage2=item.get(
                        "firstimage2"
                    ),



                    # ==========================
                    # 저작권
                    # ==========================

                    cpyrhtDivCd=item.get(
                        "cpyrhtDivCd"
                    ),



                    # ==========================
                    # 날짜
                    # ==========================

                    createdtime=item.get(
                        "createdtime"
                    ),

                    modifiedtime=item.get(
                        "modifiedtime"
                    ),
                )


                db.add(content)



        db.commit()

        print(
            "Tour data loaded successfully!"
        )


    except Exception as e:

        db.rollback()

        print(
            "JSON LOAD ERROR:",
            e
        )


    finally:

        db.close()