from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_cors import CORS
import os

app = Flask(__name__)

# Habilitar CORS para toda la aplicación
CORS(app)

# Configura la conexión a la base de datos MySQL en tu instancia EC2
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa la base de datos
db = SQLAlchemy(app)

# Define el modelo de usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __init__(self, first_name, last_name, birth_date, password):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.password_hash = generate_password_hash(password)

# Crea las tablas
with app.app_context():
    db.create_all()

# Ruta para registrar un nuevo usuario
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    birth_date = data.get('birth_date')  # formato 'YYYY-MM-DD'
    password = data.get('password')

    if not all([first_name, last_name, birth_date, password]):
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    # Crea un nuevo usuario
    new_user = User(first_name=first_name, last_name=last_name, birth_date=birth_date, password=password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Usuario registrado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Ruta para "Hola Mundo"
@app.route('/test', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hola Mundo"}), 200

# Ruta para obtener first_name, last_name y birth_date de todos los usuarios
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.with_entities(User.first_name, User.last_name, User.birth_date).all()
        users_list = [{"first_name": user.first_name, "last_name": user.last_name, "birth_date": user.birth_date.strftime('%Y-%m-%d')} for user in users]
        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Inicia la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 
