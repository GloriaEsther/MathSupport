#aqui esta la conexion de mongodb
from pymongo import MongoClient
import bcrypt
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "mathsupport_db"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Colecciones
usuarios_collection = db["Usuario"]
#problemas_collection = db["Problemas"]#este aun no existe xd
# Verificar conexión
print(db.list_collection_names()) 


class UsuarioModel:
    @staticmethod
    def registrar_usuario(email, password):
        """Registra un nuevo usuario en la base de datos."""
        if usuarios_collection.find_one({"email": email}):
            print(f"⚠ El usuario con email {email} ya existe.") 
            return {"error": "El correo ya está registrado"}

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        usuario = {
            "email": email,
            "password": hashed_password.decode("utf-8"),
        }
        resultado = usuarios_collection.insert_one(usuario)
        print(f"✅ Usuario guardado con ID: {resultado.inserted_id}")  # 🔍 Debug
        return {"mensaje": "Registro exitoso", "id": str(resultado.inserted_id)}

    @staticmethod
    def autenticar_usuario(email, password):
        """Autentica al usuario con email y contraseña."""
        usuario = usuarios_collection.find_one({"email": email})

        if usuario and bcrypt.checkpw(password.encode("utf-8"), usuario["password"].encode("utf-8")):
            return usuario
        return None
