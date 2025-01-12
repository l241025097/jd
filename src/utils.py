import os
import re
import sys
import logging
import paramiko
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from datetime import datetime, timedelta
from requests import get, post
from json import dumps, loads, JSONEncoder
from pymysql import Connect
from pymysql.cursors import DictCursor

from xml.etree.ElementTree import Element, tostring


def current_path():
    this_path = os.path.dirname(os.path.abspath(__file__))
    if not this_path:
        return os.getcwd()
    return this_path


def get_log(mission_name):
    log_obj = logging.getLogger(mission_name)
    log_path = os.path.join(current_path(), "datas", "logs", f"{mission_name}.log")
    formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s]: %(message)s')
    file_handler = TimedRotatingFileHandler(log_path, when="MIDNIGHT", backupCount=7, encoding="utf-8")
    file_handler.setFormatter(formatter)
    log_obj.addHandler(file_handler)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    log_obj.addHandler(stdout_handler)
    log_obj.setLevel(logging.INFO)
    return log_obj


def connect_mysql(host="101.33.240.185", port=60001, user="lyn", password="S198641cn@", database="rich"):
    connect_dict = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "charset": "utf8",
        "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION",
    }
    dbh = Connect(**connect_dict)
    sth = dbh.cursor(cursor=DictCursor)
    return dbh, sth


def connect_ftp(host="10.160.54.100", port=22, user="xxx", passwd="xxx"):
    Link = paramiko.Transport((host, port))
    Link.connect(username=user, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(Link, window_size=(10 * 1024 * 1024))
    return sftp


def get_ssh(host, port, user, passwd):
    tran = paramiko.Transport((host, port))
    tran.start_client()
    tran.auth_password(user, passwd)
    return tran


def modify_fly(dbh, sth, sql, data_list, log_obj, pid=0):
    try:
        sth.executemany(sql, data_list)
        dbh.commit()
        row_count = sth.rowcount
        # log_obj.info("{0}: modify rows: {1}".format(pid, row_count))
        return row_count
    except Exception as err:
        dbh.rollback()
        # log_obj.info("{0}: modify error: {1}".format(pid, err))
        # log_obj.info("{0}: modify one by one ...".format(pid))
        row_count = 0
        for data in data_list:
            try:
                sth.execute(sql, data)
                dbh.commit()
                row_count += sth.rowcount
                # log_obj.info(f"{pid}: modify {row_count} ...")
            except Exception as err:
                dbh.rollback()
                log_obj.error("{0}: modify one by one error: {1}, {2}".format(pid, err, str(data)))
        return row_count


def modify_fly_many(dbh, sth, sql, data_list, log_obj, batch=10000, pid=0):
    all_num = len(data_list)
    if all_num <= batch:
        return modify_fly(dbh, sth, sql, data_list, log_obj, pid)
    loop_num = int(all_num / batch)
    loop_num = loop_num if all_num % batch == 0 else loop_num + 1
    insert_num = 0
    for i in range(loop_num):
        begin = i * batch
        end = (i + 1) * batch
        end = all_num if end >= all_num else end
        row_count = modify_fly(dbh, sth, sql, data_list[begin: end], log_obj, pid)
        if row_count:
            insert_num += row_count
    return insert_num


def get_insert_sql(table, key_list, db=None, update_list=None, add_list=None):
    if not update_list:
        update_list = key_list
    update_str = ",".join([f"`{key}`=VALUES(`{key}`)" for key in update_list])
    if add_list:
        value_func = lambda x: f"`{x}`+VALUES(`{x}`)" if x in add_list else f"VALUES(`{x}`)"
        update_str = ",".join([f"`{key}`={value_func(key)}" for key in update_list])
    sql_dict = {
        "table": f"{db}.{table}" if db else table,
        "key": ",".join(f"`{key}`" for key in key_list),
        "update": update_str,
        "placeholder": ",".join(("%s" for _ in key_list))
    }
    sql = """
        INSERT INTO {table} ({key})
        VALUES ({placeholder})
        ON DUPLICATE KEY
        UPDATE {update}
    """.format(**sql_dict)
    return sql


def dict_to_xml(tag, use_dict, attrib={}):
    elem = Element(tag, attrib=attrib)
    for key, val in use_dict.items():
        key = str(key).replace("_", "")
        child = Element(key)
        child.text = str(val)
        elem.append(child)
    return elem


class ComplexEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return JSONEncoder.default(self, obj)
