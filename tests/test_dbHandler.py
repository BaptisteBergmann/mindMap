import json
import os
from src.dbHandler import add_leaf, add_master_leaf, init_db, query_db
from src.error import PathNotValid


def test_add_master_leaf(client, app):
    assert client.get('/my-map').status_code == 404
    assert client.get('/my-map2').status_code == 404
    with app.app_context():
        add_master_leaf('my-map')
        assert client.get('/my-map').status_code == 200
        client.post('/',
                data='{"id": "my-map2"}',
                headers={'content-type': 'application/json'})
        assert client.get('/my-map2').status_code == 200
        
    os.remove("./database.db")
    

def test_add_leaf(client, app):
    with app.app_context():
        add_master_leaf('my-map')
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 404

        add_leaf('my-map', ['newLeaf'],info='test')
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200
        add_leaf('my-map', ['newLeafFromPost'],info='test')
        client.post('/my-map',
                data='{"path": "newLeafFromPost", "text": "2"}',
                headers={'content-type': 'application/json'})
        assert client.get('/my-map/newLeafFromPost',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200

        add_leaf('my-map', ['newLeaf','sub'],info='test')
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200
        
        try:
            add_leaf('my-map', ['newLea','e'],info='test')
        except BaseException as err:
            assert err.code == 509
        assert client.get('/my-map/newLea/e',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 404
        try:
            add_leaf('my-map', ['newLeaf'],info='test')
        except BaseException as err:
            assert err.code == 510
    os.remove("./database.db")
    
def test_get_leaf(client, app):
    with app.app_context():
        add_master_leaf('my-map')
        add_leaf('my-map', ['newLeaf'],info='test')
        response = client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'})
        data = json.loads(response.data.decode("utf-8") )
        assert data['leaf'] == 'newLeaf'
        assert data['text'] == 'test'
    os.remove("./database.db")

def test_print_leafs(client, app):
    with app.app_context():
        add_master_leaf('my-map')
        add_leaf('my-map', ['newLeaf'],info='test')
        add_leaf('my-map', ['newLeaf','sub'],info='data')
        add_leaf('my-map', ['otherLeaf'],info='test')
        add_leaf('my-map', ['otherLeaf','sub'],info='data')
        response = client.get('/my-map')
        data = response.data.decode("utf-8")
        assert data == 'my-map/\n\tnewLeaf/\n\t\tsub/\n\totherLeaf/\n\t\tsub/\n'
    os.remove("./database.db")

def test_reinit(client, app):
    with app.app_context():
        add_master_leaf('my-map')
        add_leaf('my-map', ['newLeaf'],info='test')
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200 
        init_db()
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200 
    os.remove("./database.db")

def test_query_db(client, app):
    with app.app_context():
        add_master_leaf('my-map')
        add_leaf('my-map', ['newLeaf'],info='test')
        dbRep = query_db('SELECT name FROM nodes WHERE name=?',['newLeaf'],one=True)
        assert dbRep['name'] == 'newLeaf' 
        dbRep = query_db('SELECT name FROM nodes WHERE name=?',['newLeaf'])
        assert dbRep[0]['name'] == 'newLeaf' 
    os.remove("./database.db")