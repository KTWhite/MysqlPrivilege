import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from python.app import create_app,db
# from app.models import User,Role
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand
app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)
migrate=Migrate(app,db)

def make_shell_context():
    return dict(app=app,db=db)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)
if __name__ =="__main__":
    app.run(debug=True,host='0.0.0.0', port=8090,threaded=True)
    manager.run()
