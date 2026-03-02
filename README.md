# webhook-repo
A Flask-based GitHub webhook receiver that captures Push, Pull Request and Merge events from `action-repo`, stores them in MongoDB and displays them in a live-polling UI.

## Tech Stack
- Python / Flask
- MongoDB Atlas (via Flask-PyMongo)
- GitHub Webhooks
- ngrok (for local development)

## Setup Instructions

1. Clone the repo and create a virtual environment:
    ```bash
       python -m venv venv
       venv\Scripts\activate
       pip install -r requirements.txt
    ```

2. Create a `.env` file:
    ```
       MONGO_URI=your_mongodb_connection_string
    ```

3. Run the Flask app:
    ```bash
       python run.py
    ```

4. Expose it with ngrok:
    ```bash
       ngrok http 5000
    ```

5. Register the ngrok URL as a webhook on `action-repo` (Github Settings → Webhooks) for Push and Pull Request events. Select only PUSH and PULL Request.

## Event Formats
| Action | Display |
|---|---|
| PUSH | `{author}` pushed to `{branch}` on `{timestamp}` |
| PULL REQUEST | `{author}` submitted a pull request from `{from}` to `{to}` on `{timestamp}` |
| MERGE | `{author}` merged branch `{from}` to `{to}` on `{timestamp}` |

## Application Flow

action-repo → GitHub Webhook → Flask /webhook endpoint → MongoDB → UI (polls every 15s)
