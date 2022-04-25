'''
Filename: app.py
Path: ./src/
Created Date: Monday, April 25rd 2022, 10:41:08 am
Author: Baptiste Bergmann
'''

from flask import Flask,request
# from dbHandler import add_leaf, add_master_leaf, close_connection, get_leaf, init_db, print_leafs
from src.error import CustomExeptions, LeafNotFound
from src.dbHandler import add_leaf, add_master_leaf, close_connection, get_leaf, init_db, print_leafs

def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__)
    app.app_context()
    with app.app_context():
        init_db()
        print('Db initialised')

    @app.route('/', methods=['POST'])
    def addMap():
        '''
        Route to add a new mind map inside the database
        TODO might be useful to return a uuid so that mindmap wont otherlaps other routes and be more secure 
        '''
        ## if content empty this route will not be used 
        content = request.json
        id = content.get('id')
        if (id != None):
            if (id == 'init'): return 'Map cant overlap init' ## uuid will resolve this
            add_master_leaf(id)
            return 'New mindMap: "'+ id +'" created\n'

    @app.route('/<path:subpath>', methods=['GET', 'POST'])
    def leaf(subpath : str):
        '''
        Route to:
        add leaf if POST
        get leaf if GET with data
        print leafs if other
        '''
        mapId:str = subpath.rstrip('/').split(sep='/')[0]
        if request.method == 'POST':
            content = request.json
            path:list[str] = content['path'].split(sep='/')
            text:str  = content['text']
            return add_leaf(mapId,path,text)
        if request.method == 'GET':
            path:str = subpath.rstrip('/').split(sep='/')
            if (request.content_type != None):
                return get_leaf(mapId, path[1:], toString=True)
            else:
                return print_leafs(path)

    @app.teardown_appcontext
    def endApp(exception):
        '''
        Close all when ending app
        '''
        close_connection(exception)

    @app.errorhandler(CustomExeptions)
    def handle_Unexpected(error):
        '''
        Error Handler
        '''
        response = {
            'success': False,
            'statu_code': error.__class__.code,
            'error': {
                'type': error.__class__.__name__,
                'message': error.__class__.description
            }
        }
        return response, error.__class__.code


    return app
