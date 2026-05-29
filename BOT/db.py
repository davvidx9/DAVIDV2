"""MongoDB helpers (subscriptions + custom scripts)."""

from __future__ import annotations

import datetime
from typing import Any, Optional

from pymongo import MongoClient

from config import MONGO_DB, MONGO_URI

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
keys = db["keys"]
users = db["users"]
scripts = db["scripts"]


def check_subscription(chat_id: int) -> bool:
    doc = users.find_one({"chat_id": int(chat_id)})
    if not doc:
        return False
    exp = doc.get("expiration_date")
    if exp == "Never":
        return True
    try:
        exp_dt = datetime.datetime.strptime(exp, "%Y/%m/%d %H:%M:%S")
        return datetime.datetime.now() <= exp_dt
    except ValueError:
        return False


def get_script(script_id: str) -> Optional[dict[str, Any]]:
    return scripts.find_one({"script_id": script_id})


def save_script(script_id: str, part1: str, part2: str, part3: str, owner: int) -> None:
    scripts.update_one(
        {"script_id": script_id},
        {
            "$set": {
                "part1": part1,
                "part2": part2,
                "part3": part3,
                "owner": owner,
                "updated": datetime.datetime.utcnow(),
            }
        },
        upsert=True,
    )
