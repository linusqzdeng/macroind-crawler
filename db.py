# -*- coding: UTF-8 -*-

import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR, FLOAT


if __name__ == "__main__":
    # create sqlalchemy engine
    hostname = 'localhost'
    db = 'macro'
    user = 'root'
    pwd = 'root'
    charset='utf8'
    engine = create_engine(f"mysql+pymysql://{user}:{pwd}@{hostname}/{db}?charset={charset}")

    df = pd.read_csv('./data/industry.csv')
    tbl_types = {col_name: FLOAT for col_name in df.columns}
    tbl_types['公布日'] = VARCHAR(10)
    tbl_types['截止日'] = VARCHAR(10)
    df.to_sql('工业增加值', engine, if_exists='replace', index=False, dtype=tbl_types)

    
