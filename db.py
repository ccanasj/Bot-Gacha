from pymongo import MongoClient
from TOKEN import MONGO
client = MongoClient(MONGO)

cartas = client["BCBot"]["Cartas"]
players = client["BCBot"]["Players"]

async def GuardarUsuario(user,idCarta):
    if players.count_documents({ "_id": user }) != 0:
        players.update_one({ "_id": user }, {'$push': {'Cartas': idCarta}})
    else:
        usuario = {"_id": user, "Cartas": [idCarta]}
        players.insert_one(usuario)

async def GuardarCarta(datos):
    datos['_id'] = cartas.count_documents({}) + 1
    cartas.insert_one(datos)

async def ExisteJugador(user):
    return players.count_documents({ "_id": user }) != 0

async def GetCartasRareza(Rareza):
    data = cartas.find({ "rarity": {'$eq':Rareza}})
    return [carta for carta in data]

async def GetCarta(id):
    if cartas.count_documents({ "_id": id }) != 0:
        data = cartas.find_one({ "_id": id})
        return data
    return False

async def GetMazo(user):
    if players.count_documents({ "_id": user }) != 0:
        data = players.find_one({ "_id": user})
        mazo = data['Cartas']
        data = cartas.find({ "_id": {"$in" :list(set(mazo))}},{"nombre": 1, "rarity": 1 })
        return mazo,{carta['_id']:(carta['nombre'],carta['rarity']) for carta in data}
    return False

async def CerrarDB(ctx):
    client.close()