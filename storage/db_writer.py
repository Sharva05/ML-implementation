from sqlalchemy import create_engine
from common.config import DB_URL

engine = create_engine(DB_URL)

def write_dataframe(df, table_name):
    try:
        df.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"Inserted into {table_name}")
    except Exception as e:
        print("Error:", e)