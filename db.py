# -*- coding: UTF-8 -*-

import pymysql


def connect_df():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        passwd='root',
        db='testdatabase',
        charset='utf8'
        )
    cur = conn.cursor()
    return conn, cur


def exe_update(cur, query):
    return cur.execute(query)
    


if __name__ == "__main__":
    conn, cur = connect_df()

    query = """
        CREATE TABLE GDP (
        截止时间                VARCHAR(10) NOT NULL,
        公布日期                DATE,
        公布时间                TIME,
        国内生产总值_本季值	    FLOAT,
        国内生产总值_累计值	    FLOAT,
        国内生产总值_本季同比   FLOAT,
        国内生产总值_累计同比	FLOAT,
        第一产业_本季值			FLOAT,
        第一产业_累计值			FLOAT,
        第一产业_本季同比		FLOAT,
        第一产业_累计同比		FLOAT,
        第二产业_本季值			FLOAT,
        第二产业_累计值			FLOAT,
        第二产业_本季同比		FLOAT,
        第二产业_累计同比		FLOAT,
        第三产业_本季值			FLOAT,
        第三产业_累计值			FLOAT,
        第三产业_本季同比		FLOAT,
        第三产业_累计同比		FLOAT
        );
    """

    exe_update(cur, query)
    
