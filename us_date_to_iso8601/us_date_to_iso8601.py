import sqlite3
import sys
from datetime import datetime

def match_date(x):
    return "Date" in x

def fix_date_time(t):
    if not t:
        return t

    # 4 digit year, AM/PM
    try:
        dt = datetime.strptime(t, "%m/%d/%Y %I:%M:%S %p")
    except ValueError:
        try:
            dt = datetime.strptime(t, "%m/%d/%y %H:%M:%S")
        except ValueError:
            try:
                dt = datetime.strptime(t, "%m/%d/%Y %H:%M:%S")
            except ValueError:
                return None
    return dt.isoformat()


def main(dbname):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    conn.create_function("fix_date_time", 1, fix_date_time)
    cur.execute("select tbl_name from sqlite_master where type = 'table'")
    table_names = cur.fetchall()

    columns_to_fix = []
    for table_name in [t[0] for t in table_names]:
        if table_name[0] == "<":
            continue
        cur.execute("pragma table_info([{}])".format(table_name))
        date_columns = [x[1] for x in cur.fetchall() if match_date(x[1])]

        columns_to_fix.append((table_name, date_columns))

    for table_name, date_columns in columns_to_fix:
        if table_name == "Demographics":
            continue
        if date_columns:
            for column in date_columns:
                update_str = """
                update [{0}] set [{1}] = fix_date_time([{1}])
                """.format(
                    table_name, column
                )
                cur.execute(update_str)
    conn.commit()
    
if __name__ == "__main__":

    dbname = sys.argv[1]
    main(dbname)

