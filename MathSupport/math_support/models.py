'''

esto en teoria debe servir pero como en django cuando usas 
pymongo en lugar del ORM de Django, no necesitas un archivo models.py tradicional porque pymongo maneja la base de datos directamente sin la capa de abstracción de Django.
entonces la conexion a la base de datos estara en el archivo db.py
:)

from django.db import models
from pymongo import MongoClient
import bcrypt
#import datetime
#esta madre es para manejar la base de datos (models.py)
#la estruc de los modelos dependen si usas sql con el orm de django(mysql,phpmyadmin,etc) o como en este caso NoSQL (mongodb) 

# Conectar a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mathsupport_db"]
usuarios_collection = db["Usuario"]

#  Modelo para manejar los usuarios
class UsuarioModel:

    @staticmethod
    def registrar_usuario(email, password):
        """Registra un nuevo usuario en la base de datos."""
        if usuarios_collection.find_one({"email": email}):
            return {"error": "El correo ya está registrado"}

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        usuario = {
            "email": email,
            "password": hashed_password.decode("utf-8"),
            #"fecha_registro": datetime.datetime.utcnow(),
        }
        resultado = usuarios_collection.insert_one(usuario)
        print("Usuario registrado:", resultado.inserted_id)  # 🔍 Verificar si se guarda
        return {"mensaje": "Registro exitoso"}

    @staticmethod
    def autenticar_usuario(email, password):#login
        """Autentica al usuario con email y contraseña."""
        usuario = usuarios_collection.find_one({"email": email})
        
        if usuario and bcrypt.checkpw(password.encode("utf-8"), usuario["password"].encode("utf-8")):
            return usuario
        return None
'''