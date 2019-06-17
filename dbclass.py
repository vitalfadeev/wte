#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sqlite3
import json
import inspect
from copy import deepcopy

_cache = {}


class DBClass:
    def connect(self):
        db = _cache.get(self.DB_NAME, None)
        
        if db is None:
            db = sqlite3.connect(self.DB_NAME, isolation_level=None)
            _cache[self.DB_NAME] = db
        
        return db
        
        
    def create_index(self, **kvargs):
        db = self.connect()
        c = db.cursor()
        
        for k,v in kvargs.items():
            c = db.cursor()
            c.execute("CREATE INDEX IF NOT EXISTS {} ON {} ({})".format(self.DB_TABLE_NAME + "_" + k, self.DB_TABLE_NAME, k))
    

    def check_table(self):
        db = self.connect()
        db.row_factory = None
        c = db.cursor()
        sql = """
            SELECT count(*) as cnt FROM sqlite_master WHERE type='table' AND name='{}';
        """.format(self.DB_TABLE_NAME)
        c.execute(sql)
        count = c.fetchone()[0]
        #db.close()
        
        #
        if count == 0:
            self.create_table()
        else:
            self.update_table()


    def create_table(self):
        fields = []
        
        for f in self.get_fields():
            if f == "id":
                continue
                
            v = getattr(self, f)
            if v is None:
                pass
            else:
                field_type = get_field_type(v)
                if field_type is None:
                    pass
                else:
                    fields.append( f + " " + field_type )
        
        #
        fields.insert(0, "id BIGINT")
         
        #         
        sql = "CREATE TABLE IF NOT EXISTS {} (".format(self.DB_TABLE_NAME)
        sql = sql + "    " + "\n,    ".join(fields)
        sql = sql + ")"

        #
        db = self.connect()
        c = db.cursor()
        c.execute(sql)
        #db.close()
        
        
    def update_table(self):
        # db_fields
        db = self.connect()
        c = db.cursor()
        c.execute("SELECT * FROM {}".format(self.DB_TABLE_NAME))
        db_fields = [description[0] for description in c.description]
        
        # object fields
        obj_fields = self.get_fields()
        
        # get new fields
        new_fields = []
        for f in obj_fields:
            if f in db_fields:
                pass
            else:
                new_fields.append(f)
        
        #
        fields = []
        for f in new_fields:
            v = getattr(self, f)
            field_type = get_field_type(v)

            if v is None:
                pass
            elif field_type is None:
                pass
            else:
                fields.append( f + " " + field_type )
        
        #         
        for field in fields:
            sql = "ALTER TABLE {} ADD {}".format(self.DB_TABLE_NAME, field)
            c = db.cursor()
            c.execute(sql)

        #db.close()
        
    
    def get_new_id(self):
        db = self.connect()
        
        c = db.cursor()

        sql = "SELECT max(id) FROM {}".format(self.DB_TABLE_NAME)

        c.execute(sql)
        rows = c.fetchall()

        if rows and rows[0][0]:
            new_id = rows[0][0] + 1

        else:
            new_id = 1

        #db.close()

        return new_id
        
        
    def get_fields(self):
        reserved = [ "DB_NAME", "DB_TABLE_NAME", "Excpla", "Explainations" ]

        result = []
        
        for name in dir(self):
            if callable(getattr(self, name)):
                pass # skip
            elif inspect.ismethod(getattr(self, name)):
                pass # skip
            elif name.startswith("_"):
                pass # skip
            elif name in reserved:
                pass # skip    
            else:
                result.append(name)
        
        return result


    def save_to_db(self, autocommit=True, db=None):
        self.check_table()
        
        db = self.connect()

        fields = []
        values = []
        placeholders = []
        
        newid = self.get_new_id()
        fields.append("id")
        values.append(newid)
        placeholders.append("?")

        for name in self.get_fields():
            value = getattr(self, name)
            
            if value:
                # list to JSON
                if isinstance(value, list):
                    value = json.dumps(value, sort_keys=False, indent=4, ensure_ascii=False)
                elif isinstance(value, dict):
                    value = json.dumps(value, sort_keys=False, indent=4, ensure_ascii=False)
                
                fields.append(name)
                values.append(value)
                placeholders.append("?")

        # insert
        c = db.cursor()
        sql = """
        INSERT INTO {}
            ({})
            VALUES
            ({})
        """.format(
            self.DB_TABLE_NAME, 
            ",".join(fields), 
            ",".join(placeholders)
            )
        c.execute(sql, values)
        
        if autocommit:
            db.commit()

        #db.close()
        
    
    def factory(self, cursor, row):
        w = deepcopy(self)
        
        for idx, col in enumerate(cursor.description):
            name = col[0]
            value = row[idx]
            
            if hasattr(w, name):
                if isinstance(getattr(w, name), (list, tuple)): # decode "" to []
                    if value:
                        value = json.loads(value)
                        
                    if isinstance(value, list):
                        pass
                    else:
                        if value:
                            value = [value] # convert to list
                        else:
                            value = getattr(w, name) # default
            
            if value is not None:
                setattr(w, name, value)
            
        return w


    def from_db(self, where=None, **kvargs):
        self.check_table()
        db = self.connect()
        db.row_factory = self.factory
        c = db.cursor()
        
        #
        conditions = []
        values = []
        
        for (field, value) in kvargs.items():
            conditions.append("{} = ?".format(field))
            values.append(value)
        
        # 
        if conditions:
            if where:
                where = where + " AND " + " AND ".join(conditions)
            else:
                where = " AND ".join(conditions)
        
        #
        if where:
            yield from c.execute( "SELECT * FROM {} WHERE {}".format(self.DB_TABLE_NAME, where), values)
        else:
            yield from c.execute( "SELECT * FROM {}".format(self.DB_TABLE_NAME))

        #db.close()


def get_field_type(v):
    if v is None:
        return None
    if isinstance(v, str):
        return "text"
    if isinstance(v, list):
        return "text"
    if isinstance(v, bool):
        return "BIGINT"
    if isinstance(v, int):
        return "BIGINT"
      

def from_db(ItemClass, **conditions):
    yield from ItemClass().from_db( **conditions )


def DBRead(ItemClass, **conditions):
    """
    for word in DBRead( WikidataItemClass ):
        print( word )
        
    for word in DBRead( WikictionaryItemClass, LabelName = WikidataItem.LabelName ):
        print( word )
    """
    yield from ItemClass().from_db( **conditions )


def DBWrite(word):
    """
    word = WikidataItemClass()
    word.LabelName = "Cat"
    DBWrite(word)
    """
    word.save_to_db()


