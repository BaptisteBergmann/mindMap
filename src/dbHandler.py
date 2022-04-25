'''
Filename: dbHandler.py
Path: ./src/
Created Date: Monday, April 25rd 2022, 10:41:08 am
Author: Baptiste Bergmann
'''

import sqlite3
from flask import g

from src.error import LeafExist, LeafNotFound, MapNotFound, PathNotValid

DATABASE = './database.db'

def get_db() -> sqlite3.Connection:
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    con = get_db()
    cur = con.cursor()
    # Create tables
    try: 
        cur.execute('''CREATE TABLE nodes (
            node_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name text, 
            info text, 
            isMaster INTEGER
            )''')
        cur.execute('''CREATE TABLE nodes_link (
            parent_id INTEGER NOT NULL,
            child_id INTEGER NOT NULL,
            FOREIGN KEY(parent_id) REFERENCES nodes(node_id),
            FOREIGN KEY(child_id) REFERENCES nodes(node_id),
            primary key (parent_id, child_id))
            ''')
        # Save (commit) the changes
        con.commit()
    except:
        pass

def add_master_leaf(name: str):
    con = get_db()
    cur = con.cursor()
    cur.execute("INSERT INTO nodes VALUES (?,?,?,1)",(None, name, 'MASTERLEAF'))
    con.commit()

def get_master_leaf(name: str):
    con = get_db()
    cur = con.cursor()
    ## Get the master node
    row = query_db('SELECT * FROM nodes WHERE isMaster=1 AND name = ?', [name], one=True)
    if row is None: raise MapNotFound()
    return row

def add_leaf(mapId: str,name: list[str], info = ''):
    
    ## Get the master node
    idToFetch = get_master_leaf(mapId)['node_id']

    ## Go to the bottom leaf if path exist:
    while len(name) > 1:
        nameToFetch = name.pop(0)
        row = query_db('SELECT * FROM nodes INNER JOIN nodes_link ON nodes_link.child_id = nodes.node_id WHERE parent_id=? AND name=?', (idToFetch,nameToFetch), one=True)
        if row is None: raise PathNotValid()
        """
        Might be an option to add path from start to end
        if row is None:
            cur.execute("INSERT INTO nodes VALUES (?,?,?,0)",(None, nameToFetch, info))
            row = query_db('SELECT name, info FROM nodes WHERE node_id=last_insert_rowid()',one=True)
            cur.execute("INSERT INTO nodes_link VALUES (?,?)",(idToFetch, cur.lastrowid))
        """
        idToFetch = row['node_id']
    leafNameToAdd = name.pop(0)
    row = query_db('SELECT * FROM nodes INNER JOIN nodes_link ON nodes_link.child_id = nodes.node_id WHERE parent_id=? AND name=?', (idToFetch,leafNameToAdd), one=True)
    if row : raise LeafExist()

    con = get_db()
    cur = con.cursor()
    cur.execute("INSERT INTO nodes VALUES (?,?,?,0)",(None, leafNameToAdd, info))
    row = query_db('SELECT name, info FROM nodes WHERE node_id=last_insert_rowid()',one=True)
    cur.execute("INSERT INTO nodes_link VALUES (?,?)",(idToFetch, cur.lastrowid))
    con.commit()

    return """{{"leaf": "{name}", "text": "{info}"}}""".format(
            name=row['name'], info=row['info'])

def get_leaf(mapId: str, name: list[str], toString=False):
    idToFetch = get_master_leaf(mapId)['node_id']
    while len(name) > 0:
        nameToFetch = name.pop(0)
        row = query_db('SELECT * FROM nodes INNER JOIN nodes_link ON nodes_link.child_id = nodes.node_id WHERE parent_id=? AND name=?', (idToFetch,nameToFetch), one=True)
        if row is None: raise LeafNotFound()
        idToFetch = row['node_id']
    row = query_db('SELECT * FROM nodes WHERE node_id=?', [idToFetch], one=True)
    if toString:
        if row is None: raise LeafNotFound()
        return """{{"leaf": "{name}", "text": "{info}"}}""".format(
            name=row['name'], info=row['info'])
    return row

def print_leafs(path: str):
    row = get_leaf(path[0],path[1:])
    output = print_leaf(row[0], 0)
    return output

def print_leaf(id:int, deap:int):
    row = query_db('SELECT name FROM nodes WHERE node_id=?', [id], one=True)
    output = '\t' * deap + row['name']+'/\n'
    rows = query_db('SELECT * FROM nodes INNER JOIN nodes_link ON nodes_link.child_id = nodes.node_id WHERE parent_id=?', [id])
    for i in range(0, len(rows)):
        output += print_leaf(rows[i]['node_id'], deap+1)
    return output
    

def query_db(query:str, args = [], one=False):
    con = get_db()
    cur = con.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows