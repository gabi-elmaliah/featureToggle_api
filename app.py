from flask import Flask
from flasgger import Swagger
from database.connection import MongoConnectionHolder
from routes.feature_routes import feature_toggle_blueprint
import os 

app = Flask(__name__)
Swagger(app)

MongoConnectionHolder.initialize_db()

app.register_blueprint(feature_toggle_blueprint)




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
    
