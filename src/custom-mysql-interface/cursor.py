import mysql.connector
from collections import OrderedDict

class CursorBase:

    user = "";
    password = "";
    database = "";
    host = "";

    def __init__(self):
        pass;


    @classmethod
    def open_connection(cls):
        conn = mysql.connector.connect(
            user = cls.user,
            password = cls.password,
            host = cls.host,
            database = cls.database);
        return conn;


    @classmethod
    def create_cursor(cls):
        conn = cls.open_connection();
        cursor = conn.cursor();
        return conn, cursor;


    @staticmethod
    def close(conn, cursor):
        cursor.close();
        conn.close();


    @staticmethod
    def record_to_ordereddict(record, column_names):
        od = OrderedDict();
        for i, col in enumerate(column_names):
            od[col] = record[i];
        return od;


    @staticmethod
    def parse_records(records, column_names):
        parsed = [];
        for record in records:
            parsed.append(CursorBase.record_to_ordereddict(record,
                                                           column_names));
        return parsed;


    @staticmethod
    def create_empty_ordereddict(describe):
        empty_od = OrderedDict();
        empty_od["id"] = 0;

        for col in describe:
            if str(col[0]) == "id":
                continue;
            dtype = "text";
            val = "";
            if "int" in str(col[1]):
                dtype = "int";
                val = "";
            elif "decimal" in str(col[1]):
                dtype = "float"
                val = "";
            else:
                val = "";
            if col[4] != None:
                if dtype == "int":
                    val = int(col[4]);
                elif dtype == "float":
                    val = float(col[4]);
                elif dtype == "text":
                    val = str(col[4]);
            empty_od[str(col[0])] = val;

        return empty_od;


    @staticmethod
    def clean_value(value):
        if isinstance(value, str):
            value = value.strip();
        return value;


    @classmethod
    def describe(cls, table_name, cursor=None):
        sql = "DESCRIBE `{:s}`".format(table_name);
        if cursor == None:
            conn, c = cls.create_cursor();
        else:
            conn = None;
            c = cursor;
        c.execute(sql);
        raw = c.fetchall();
        if cursor == None:
            cls.close(conn, c);
        return raw;


    @classmethod
    def column_names(cls, table_name):
        conn, c = cls.create_cursor();
        describe = cls.describe(table_name, cursor=c);
        column_names = [str(col[0]).strip() for col in describe];
        cls.close(conn, c);
        return column_names;


    @classmethod
    def empty_ordereddict(cls, table_name, fields=[], cursor=None):
        describe = cls.describe(table_name, cursor=cursor);
        if len(fields) > 0:
            describe_trunc = [];
            for field in fields:
                for dfield in describe:
                    if field == dfield[0]:
                        describe_trunc.append(dfield);
            describe = describe_trunc;
        return cls.create_empty_ordereddict(describe);


    @classmethod
    def select(cls, table_name, fields=[], clauses=""):
        sql = "SELECT ";
        if len(fields) == 0:
            sql+= "*";
        else:
            sql+= ", ".join(f"`{field}`" for field in fields);
        sql+= f" FROM `{table_name}` " + clauses;

        conn, cursor = cls.create_cursor();
        cursor.execute(sql);
        records = cursor.fetchall();
        column_names = cursor.column_names;

        result = cls.parse_records(records, column_names);
        if len(result) == 0:
            result = [cls.empty_ordereddict(table_name, fields=fields,
                                            cursor=cursor)];

        cls.close(conn, cursor);
        return result;


    @classmethod
    def select_all(cls, table_name, clauses=""):
        return cls.select(table_name, clauses=clauses);


    @staticmethod
    def values_dict_to_tuple(values_dict):
        return tuple([CursorBase.clean_value(values_dict[key])
                      for key in values_dict
                      if key != "id"]);


    @classmethod
    def update_row(cls, table_name, where_clause, values_dict, id_col="id"):
        conn, cursor = cls.create_cursor();
        cursor.execute("SELECT {:s} FROM {:s} {:s}".format(
            id_col, table_name, where_clause));
        update_id = int(cursor.fetchone()[0]);
        sql = "UPDATE `{:s}` SET ".format(table_name);
        values = cls.values_dict_to_tuple(values_dict);
        for key in values_dict:
            if key == "id":
                continue;
            sql += "{:s}=%s, ".format(key);
        sql = sql[:-2] + " " + where_clause;
        cursor.execute(sql, tuple(values));
        conn.commit();
        cls.close(conn, cursor);
        return update_id;


    @classmethod
    def insert_row(cls, table_name, values_dict):
        sql = "INSERT INTO {:s} (".format(table_name);
        values = cls.values_dict_to_tuple(values_dict);
        values_sql = "(";
        for key in values_dict:
            if key == "id":
                continue;
            sql += "{:s}, ".format(str(key));
            values_sql+= "%s, ";
        sql = sql[:-2] +  ") VALUES ";
        sql+= values_sql[:-2] + ")";
        conn, cursor = cls.create_cursor();
        cursor.execute(sql, tuple(values));
        conn.commit();
        last_id = cls.last_insert_id(table_name, cursor=cursor);
        cls.close(conn, cursor);
        return last_id;


    @classmethod
    def call_procedure(cls, procedure, args=(), commit=False):
        conn, cursor = cls.create_cursor();

        if len(args) == 0:
            res = cursor.callproc(procedure);
        else:
            res = cursor.callproc(procedure, args);

        if commit:
            conn.commit();

        cls.close(conn, cursor);
        return res;

    @classmethod
    def last_insert_id(cls, table_name, cursor=None):
        no_cursor = False;
        if cursor == None:
            no_cursor = True;
            conn, cursor = cls.create_cursor();
        cursor.execute("SELECT last_insert_id();");
        record = cursor.fetchone();
        if no_cursor:
            cls.close(conn, cursor);
        return int(record[0]);





