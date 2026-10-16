from math import ceil

import pandas as pd
import requests

BASE_URL = "http://20.228.134.116:8000/antojitos"
MAX_LIMIT_ORDENES = 200


def get_num_batches(path: str):
    # Solicitud de metadata
    res = requests.get(f"{BASE_URL}{path}", params={"limit": 1}).json()

    # Extraer el total de items
    total: int = res["total"]

    # Calcualar cantidad de batchs
    num_batchs = ceil(total / MAX_LIMIT_ORDENES)

    return num_batchs


def get_data(path: str):
    dfs = []
    num_batchs = get_num_batches(path)

    for i in range(num_batchs):
        offset = i * MAX_LIMIT_ORDENES

        params = {"offset": offset, "limit": MAX_LIMIT_ORDENES}

        print(f"{i}| Obteniendo datos de {path} con: {params}")

        res = requests.get(f"{BASE_URL}{path}", params=params).json()

        # crear batch_df
        batch_df = pd.DataFrame(res["items"])

        dfs.append(batch_df)

    df = pd.concat(dfs)

    return df


def main():
    RAW_FOLDER = "./data/raw"

    endpoints = [
    # "zonas",
    # "repartidores",
    # "categorias",
    # "platillos",
    # "promociones",
    # "clima",
    # "ordenes",
    "detalles"
    ]


    for endpoint in endpoints:
        df = get_data(f"/{endpoint}")
        df.to_parquet(f"{RAW_FOLDER}/{endpoint}.parquet")



if __name__ == "__main__":
    main()
