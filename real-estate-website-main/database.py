from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root:damnedKoraline1@localhost/realestate?charset=utf8mb4")

def load_estate_from_db(): 
    with engine.connect() as conn:
        result = conn.execute(text("select * from estate"))
        estate = []
        for row in result.fetchall():
            estate.append(row)
    return estate




    