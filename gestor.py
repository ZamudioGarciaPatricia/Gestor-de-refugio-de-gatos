from pymongo import MongoClient

class GestorTareas:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client['sistema_tareas']
        self.usuarios = self.db['usuarios']

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