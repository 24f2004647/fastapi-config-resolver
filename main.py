from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml
import os

load_dotenv()

app = FastAPI()

# Allow browser access for grading
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Defaults
# ------------------------
config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# ------------------------
# YAML
# ------------------------
with open("config.development.yaml") as f:
    config.update(yaml.safe_load(f))

# ------------------------
# .env
# ------------------------
if os.getenv("APP_PORT"):
    config["port"] = int(os.getenv("APP_PORT"))

if os.getenv("NUM_WORKERS"):
    config["workers"] = int(os.getenv("NUM_WORKERS"))

# ------------------------
# OS Environment (APP_*)
# ------------------------
if os.getenv("APP_API_KEY"):
    config["api_key"] = os.getenv("APP_API_KEY")


def to_bool(value):
    return str(value).lower() in ["true", "1", "yes", "on"]


@app.get("/")
def home():
    return {"message": "Config Service Running"}


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    result = config.copy()

    for item in set:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key in ["port", "workers"]:
            result[key] = int(value)

        elif key == "debug":
            result[key] = to_bool(value)

        else:
            result[key] = value

    # Mask the API key
    result["api_key"] = "****"

    return result
