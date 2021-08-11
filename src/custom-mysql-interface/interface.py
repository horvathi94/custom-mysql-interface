from .cursor.cursor import Cursor


class DBException(Exception):
    """Exception raised when database method fails"""

    def __init__(self, message=""):
        self.message = message;
        super().__init__(self.message);



class DBInterface:

    fetch_table = "";
    save_table = "";


    @classmethod
    def clean_fetched(cls, entry):
        pass;


    @classmethod
    def fetch(cls, id=0):
        where_clause = f"WHERE `id` = {id}";
        entry, = Cursor.select(cls.fetch_table,
                               clauses=where_clause);
        cls.clean_fetched(entry);
        if id != 0 and entry["id"] == 0:
            raise DBException(f"Item with id = {id} not found in databse");
        return entry;


    @classmethod
    def fetch_all(cls):
        entries = Cursor.select_all(cls.fetch_table);
        for entry in entries:
            cls.clean_fetched(entry);
        return entries;


    @classmethod
    def fetch_id_list(cls):
        id_dict_list = Cursor.select(cls.fetch_table, fields=["id"]);
        if len(id_dict_list) == 1 and id_dict_list[0]["id"] == 0:
            return [];
        return [d["id"] for d in id_dict_list];


    @classmethod
    def clean_submitted(cls, submitted):
        pass;


    @classmethod
    def save(cls, submitted):
        cls.clean_submitted(submitted);
        if submitted["id"] == 0:
            last_id = Cursor.insert_row(cls.save_table, submitted);
        else:
            where_clause = f"WHERE `id` = {submitted['id']}";
            last_id = Cursor.update_row(cls.save_table,
                                        where_clause, submitted);
        return last_id


