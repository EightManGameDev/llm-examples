import requests

PROACTIVE_MESSAGE_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/7337a77e-1ec8-45da-86b9-c06628865d86"

response = requests.get(PROACTIVE_MESSAGE_WEBHOOK)
print(response.json())  # This should print the expected message
