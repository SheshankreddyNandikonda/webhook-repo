from flask import Blueprint, request, jsonify, render_template
from .extensions import mongo
from datetime import datetime

main = Blueprint("main", __name__)


def format_timestamp(ts_str):
    """
    Converts GitHub ISO 8601 timestamp to:
    '1st April 2021 - 9:30 PM UTC'
    """
    # Handle both Z-suffix and offset formats
    ts_str = ts_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts_str)

    day = dt.day
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    try:
        formatted = dt.strftime(f"%-d{suffix} %B %Y - %I:%M %p UTC")
    except ValueError:
        formatted = dt.strftime(f"%#d{suffix} %B %Y - %I:%M %p UTC")

    return formatted


@main.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event", "")
    record = None

    # PUSH event
    if event_type == "push":
        # Ignoring branch deletion pushes
        if not data.get("head_commit"):
            return jsonify({"status": "ignored"}), 200

        record = {
            "request_id": data["after"],
            "author": data["pusher"]["name"],
            "action": "PUSH",
            "from_branch": None,
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": format_timestamp(data["head_commit"]["timestamp"])
        }

    # PULL REQUEST and MERGE events
    elif event_type == "pull_request":
        pr = data["pull_request"]
        action = data["action"]

        if action == "opened":
            record = {
                "request_id": str(pr["id"]),
                "author": pr["user"]["login"],
                "action": "PULL_REQUEST",
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": format_timestamp(pr["created_at"])
            }

        # MERGE = PR closed with merged == True  <- brownie points
        elif action == "closed" and pr.get("merged") is True:
            record = {
                "request_id": str(pr["id"]),
                "author": pr["merged_by"]["login"],
                "action": "MERGE",
                "from_branch": pr["head"]["ref"],
                "to_branch": pr["base"]["ref"],
                "timestamp": format_timestamp(pr["merged_at"])
            }

    # Save to MongoDB if we have a valid record, else ignore
    if record:
        mongo.db.events.insert_one(record)
        return jsonify({"status": "saved", "action": record["action"]}), 200

    return jsonify({"status": "ignored"}), 200


@main.route("/events", methods=["GET"])
def get_events():
    """The UI polls this endpoint every 15 seconds."""
    events = list(
        mongo.db.events.find({}, {"_id": 0}).sort("_id", -1).limit(20)
    )
    return jsonify(events)


@main.route("/")
def index():
    return render_template("index.html")