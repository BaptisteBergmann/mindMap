import json
import os
from src.dbHandler import add_leaf, add_master_leaf, init_db, query_db

def test_add_master_leaf(client, app):
    assert client.get('/my-map').status_code == 404, 'Map should not exist'
    assert client.get('/my-map2').status_code == 404, 'Map should not exist'
    with app.app_context():
        add_master_leaf('my-map')
        assert client.get('/my-map').status_code == 200 , 'Map should have been created with func'
        client.post('/',
                data='{"id": "my-map2"}',
                headers={'content-type': 'application/json'})
        assert client.get('/my-map2').status_code == 200, 'Map should have been created with http'
        
    os.remove("./database.db")
    

def test_add_leaf(client, app):
    with app.app_context():
        add_master_leaf('my-map')
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 404, 'Leaf should not exist'
        add_leaf('my-map', ['newLeaf'],info='test')
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200, 'Leaf should be created by func'
        add_leaf('my-map', ['newLeafFromPost'],info='test')
        client.post('/my-map',
                data='{"path": "newLeafFromPost", "text": "2"}',
                headers={'content-type': 'application/json'})
        assert client.get('/my-map/newLeafFromPost',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200, 'Leaf should be created by http'

        add_leaf('my-map', ['newLeaf','sub'],info='test')
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200, 'Sub Leaf should be created by func'
        
        try:
            add_leaf('my-map', ['newLea','e'],info='test')
        except BaseException as err:
            assert err.code == 509, 'Should return error 509 leaf already exist'
        assert client.get('/my-map/newLea/e',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 404, 'Should return error 404 leaf not founf'
        try:
            add_leaf('my-map', ['newLeaf'],info='test')
        except BaseException as err:
            assert err.code == 510, 'Should return error 510 leaf already there'
    os.remove("./database.db")
    
def test_get_leaf(client, app):
    with app.app_context():
        add_master_leaf('my-map')
        add_leaf('my-map', ['newLeaf'],info='test')
        response = client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'})
        data = json.loads(response.data.decode("utf-8") )
        assert data['leaf'] == 'newLeaf', 'Leaf name should be "newLeaf"'
        assert data['text'] == 'test', 'Leaf text should be "test"'
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
        assert data == 'my-map/\n\tnewLeaf/\n\t\tsub/\n\totherLeaf/\n\t\tsub/\n', 'Should return the verbose path'
    os.remove("./database.db")

def test_reinit(client, app):
    with app.app_context():
        add_master_leaf('my-map')
        add_leaf('my-map', ['newLeaf'],info='test')
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200, 'Leaf should be found'
        init_db()
        assert client.get('/my-map/newLeaf',
                data=None,
                headers={'content-type': 'application/json'}).status_code == 200, 'Leaf should still be there'
    os.remove("./database.db")

def test_query_db(client, app):
    with app.app_context():
        add_master_leaf('my-map')
        add_leaf('my-map', ['newLeaf'],info='test')
        dbRep = query_db('SELECT name FROM nodes WHERE name=?',['newLeaf'],one=True)
        assert dbRep['name'] == 'newLeaf', 'Leaf name should be "newLeaf" inside one object'
        dbRep = query_db('SELECT name FROM nodes WHERE name=?',['newLeaf'])
        assert dbRep[0]['name'] == 'newLeaf', 'Leaf name should be "newLeaf" inside array'
    os.remove("./database.db")