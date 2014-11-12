from flask import Flask
from config import Config
from handler import user_handler
from handler import project_handler
from handler import organization_handler

app = Flask(__name__)
app.debug = True
app.config.from_object(Config)
app.register_blueprint(user_handler.user)
app.register_blueprint(project_handler.project)
app.register_blueprint(organization_handler.organization)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
