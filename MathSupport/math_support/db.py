#aqui esta la conexion de mongodb
from pymongo import MongoClient
import bcrypt
from datetime import datetime
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "mathsupport_db"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Colecciones
usuarios_collection = db["Usuario"]
problemas_collection = db["Problemas"]
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

class ProblemaModel:#se pudo usar mongoengine parea llenar los problemas automaticamente ptm
    @staticmethod
    def guardar_problema(usuario_email, ecuacion, imagen_url, resultado, pasos):
        problema = {
            "usuario_email": usuario_email,
            "ecuacion": ecuacion,
            "imagen_url": imagen_url,
            "resultado": resultado,
            "pasos": pasos,
            "fecha": datetime.utcnow()
        }
        resultado_insert = problemas_collection.insert_one(problema)
        print(f"✅ Problema guardado con ID: {resultado_insert.inserted_id}")
        return {"mensaje": "Problema guardado", "id": str(resultado_insert.inserted_id)}

    @staticmethod#aqui serviria como historial para el usuario
    def obtener_problemas_por_usuario(usuario_email):
        problemas = list(problemas_collection.find({"usuario_email": usuario_email}))
        for p in problemas:
            p["_id"] = str(p["_id"])  # Convertir ObjectId a string para evitar errores al serializar
        return problemas

    @staticmethod
    def buscar_problemas_por_ecuacion(ecuacion):
        problemas = list(problemas_collection.find({"ecuacion": ecuacion}))
        for p in problemas:
            p["_id"] = str(p["_id"])
        return problemas
 
    @staticmethod
    def cargar_problemas_iniciales():
        problemas_iniciales = [
            {
                "usuario_email": "mimi@gmail.com",  # puedes poner "base" si no hay usuario  te quedaste aqui
                "ecuacion": "2x + 3 = 7",
                "imagen_url": "",  # vacío porque es manual
                "resultado": "x = 2",
                "pasos": ["2x + 3 = 7", "2x = 4", "x = 2"],
                "fecha": datetime.utcnow()
            },
            {
                "usuario_email": "admin@math.com",
                "ecuacion": "x^2 - 4 = 0",
                "imagen_url": "",
                "resultado": "x = ±2",
                "pasos": ["x^2 - 4 = 0", "x^2 = 4", "x = ±2"],
                "fecha": datetime.utcnow()
            }
        ]
        return problemas_iniciales
    
    #problemas_collection.insert_many(cargar_problemas_iniciales)
    #print("✅ Problemas iniciales insertados.")

