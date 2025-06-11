import pymongo


def pedidos_IOP(store_ids, conn):

    # Cadena de conexión
    db_connections = {
        "BQ": {
            "conn_str": "mongodb://192.168.1.3:27017/",
            "db_name": "PedidosBK"
        },
        "MA": {
            "conn_str": "mongodb://192.168.1.3:27017/",
            "db_name": "PedidosMC"
        }
    }

    # Conexión a MongoDB
    conn_str = db_connections[conn]["conn_str"]
    client = pymongo.MongoClient(conn_str)
    db = client[db_connections[conn]["db_name"]]
    orders = db.pedidos

    # Valores de storeId separados por comas
    store_ids_list = [int(store_id) for store_id in store_ids.split(",")]
    # Ejecución de las consultas
    for store_id in store_ids_list:
        # Construcción de la consulta
        pipeline = [
            {"$match": {"id": store_id, "estado": {"$nin": ["ANULADO", "FINALIZADO"]}}},
            {"$group": {"_id": {"estado": "$estado", "operativa": "$operativa"}, "total": {"$sum": 1}}},
            {"$sort": {"total": -1}}
        ]

        # Ejecución de la consulta
        result = orders.aggregate(pipeline)
        # Imprimir los resultados formateados
        print(f"Pedidos IOP store {store_id}:")
        resultado = ''
        resultado = f"Pedidos IOP:"
        for doc in result:
            status = doc["_id"]["operativa"]
            total = doc["total"]
            print(f"{status}, Pedidos: {total}")
            resultado = resultado + f"\n{status}, Pedidos: {total}"
        print()

        return resultado