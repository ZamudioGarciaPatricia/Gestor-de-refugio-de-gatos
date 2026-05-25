from pymongo import MongoClient
from bson.objectid import ObjectId 

class GestorTareas:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client['sistema_tareas']
        self.usuarios = self.db['usuarios']
        self.gatos = self.db['gatos']

    def crear_usuario(self, usuario, nombre_completo, email, password_encriptada):
        if self.usuarios.find_one({"user": usuario}) or self.usuarios.find_one({"email": email}):
            return False
        self.usuarios.insert_one({
            "user": usuario,
            "nombre_completo": nombre_completo,
            "email": email,
            "secreto": password_encriptada
        })
        return True

    def obtener_usuario(self, usuario):
        return self.usuarios.find_one({"user": usuario})

    def obtener_usuario_por_correo(self, correo):
        try:
            return self.usuarios.find_one({"email": correo})
        except Exception as e:
            print(f"Error al buscar usuario por correo: {e}")
            return None

    def actualizar_contrasena_por_correo(self, correo, nueva_contrasena_hash):
        try:
            resultado = self.usuarios.update_one(
                {"email": correo},
                {"$set": {"secreto": nueva_contrasena_hash}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar la contraseña: {e}")
            return False

    
    def guardar_gato(self, datos_gato):
        try:
            self.gatos.insert_one(datos_gato)
            return True
        except Exception as e:
            print(f"Error al guardar gato: {e}")
            return False

    def obtener_gatos(self):
        try:
            return list(self.gatos.find())
        except Exception as e:
            print(f"Error al obtener gatos: {e}")
            return []
        



    def obtener_gato_por_id(self, gato_id):
        try:
            return self.gatos.find_one({"_id": ObjectId(gato_id)})
        except Exception as e:
            print(f"Error al obtener gato por ID: {e}")
            return None

    def actualizar_gato(self, gato_id, datos_actualizados):
        try:
            resultado = self.gatos.update_one(
                {"_id": ObjectId(gato_id)},
                {"$set": datos_actualizados}
            )
            return resultado.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar gato: {e}")
            return False