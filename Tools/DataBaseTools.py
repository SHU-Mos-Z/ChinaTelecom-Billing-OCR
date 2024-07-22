from sqlalchemy import and_
from cryptography.fernet import Fernet
import pandas as pd
import io
from sqlalchemy import create_engine
SQL_PWD = 'zsqlmm'
engine = create_engine(url='mysql://root:' + SQL_PWD + '@localhost/ChinaTelecom')


def generate_key():
    return Fernet.generate_key()


def encrypt_string(input_string, key):
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(input_string.encode())
    return cipher_text


def decrypt_string(cipher_text, key):
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(cipher_text).decode()
    return plain_text


def get_where_conditions_wide(table_col_list, *args):
    if args[0] is not None:
        bool_list = table_col_list[0] == args[0]
    else:
        bool_list = table_col_list[0] == table_col_list[0]
    for i in range(1, len(args)):
        if args[i] is not None:
            bool_list = (bool_list and (table_col_list[i] == args[i]))
    return bool_list


def get_where_conditions(table_col_list, *args):
    conditions = [table_col_list[0] == table_col_list[0]]
    for i in range(len(args)):
        if args[i] is not None:
            conditions.append(table_col_list[i] == args[i])
    return and_(*conditions)


def get_empty_json(*args):
    dict_ = dict()
    for arg in args:
        dict_[str(arg)] = []
    return dict_


def get_update_dict(col_name_list, update_info_list):
    dict_ = dict()
    for name, info in zip(col_name_list, update_info_list):
        if info is not None:
            dict_[name] = info
    return dict_


def generate_excel_content(data: pd.DataFrame):
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer
