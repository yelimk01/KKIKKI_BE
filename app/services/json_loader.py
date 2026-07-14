import json
from pathlib import Path

from app.database import SessionLocal
from app.models import TourContent


DATA_DIR = Path("app/data")


def load_json_to_db():
    db = SessionLocal()

    try:
        json_files = DATA_DIR.glob("*.json")

        for file_path in json_files:
            print(f"Loading {file_path.name}...")

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = data.get("items", [])

            for item in items:

                # 이미 저장된 데이터인지 확인
                exists = db.query(TourContent).filter(
                    TourContent.contentid == item["contentid"]
                ).first()

                if exists:
                    continue

                content = TourContent(
                    contentid=item.get("contentid"),
                    contenttypeid=int(item.get("contenttypeid", 0)),
                    title=item.get("title"),

                    addr1=item.get("addr1"),
                    addr2=item.get("addr2"),
                    zipcode=item.get("zipcode"),

                    tel=item.get("tel"),

                    mapx=float(item["mapx"]) if item.get("mapx") else None,
                    mapy=float(item["mapy"]) if item.get("mapy") else None,

                    mlevel=int(item["mlevel"]) if item.get("mlevel") else None,

                    areacode=item.get("areacode"),
                    sigungucode=item.get("sigungucode"),

                    lDongRegnCd=item.get("lDongRegnCd"),
                    lDongSignguCd=item.get("lDongSignguCd"),

                    cat1=item.get("cat1"),
                    cat2=item.get("cat2"),
                    cat3=item.get("cat3"),

                    lclsSystm1=item.get("lclsSystm1"),
                    lclsSystm2=item.get("lclsSystm2"),
                    lclsSystm3=item.get("lclsSystm3"),

                    firstimage=item.get("firstimage"),
                    firstimage2=item.get("firstimage2"),

                    cpyrhtDivCd=item.get("cpyrhtDivCd"),

                    createdtime=item.get("createdtime"),
                    modifiedtime=item.get("modifiedtime"),
                )

                db.add(content)

        db.commit()
        print("Tour data loaded successfully!")

    except Exception as e:
        db.rollback()
        print(e)

    finally:
        db.close()