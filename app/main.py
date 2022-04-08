import configparser
from ipaddress import ip_address
import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routers.profiles import router as profile_router
import sys

config = configparser.ConfigParser()
config.read(f"{sys.path[0]}/config.ini")

app = FastAPI()
app.include_router(profile_router)

@app.on_event("startup")
async def setup_db_client():

    db_config = config['Database']
    db_conn = f'mongodb+srv://{db_config["db_user"]}:{db_config["db_pwd"]}@{db_config["db_cluster_url"]}'

    app.db_client = AsyncIOMotorClient(db_conn, tls=True, tlsAllowInvalidCertificates=True)
    app.db = app.db_client[db_config['db_name']]

@app.on_event("shutdown")
async def lights_out():
    app.db_client.close()

if __name__ == "__main__":
    server_config = config['Server']
    uvicorn.run(
        "main:app",
        host = server_config['ip'],
        port = int(server_config['port']),
        reload = server_config.getboolean('debug_active')
    )
