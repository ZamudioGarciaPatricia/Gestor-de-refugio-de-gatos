from pymongo import MongoClient

class GestorTareas:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client['sistema_tareas']
        self.usuarios = self.db['usuarios']

    def crear_usuario(self, usuario, nombre_completo, password_encriptada):

        if self.usuarios.find_one({"user": usuario}):
            return False
        
        self.usuarios.insert_one({
            "user": usuario,
            "nombre_completo": nombre_completo,
            "secreto": password_encriptada
        })
        return True

    def obtener_usuario(self, usuario):
        return self.usuarios.find_one({"user": usuario})