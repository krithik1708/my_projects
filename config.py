from dotenv import load_dotenv
import os

load_dotenv()

secret_key= os.getenv("secret_key")
url= os.getenv("database_url")
enviroment= os.getenv("environment")

Debug= enviroment== "development"

if not secret_key:
    raise RuntimeError("secret_key is missing")

if not Debug:
    raise RuntimeError("environment is missing")

if not url:
    raise RuntimeError("url is missing")


