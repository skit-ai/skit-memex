import os
import tempfile
from threading import Event

import requests
from openai import OpenAI
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient

from skit_memex.models import image_to_explanation

oai_client = OpenAI()


def download_image(url: str) -> str:
    headers = {"Authorization": "Bearer {}".format(os.environ["SLACK_BOT_TOKEN"])}
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        with open(temp_file.name, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(":: Image downloaded successfully")
        return temp_file.name
    else:
        raise IOError("Failed to download image")


def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type == "events_api":
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))

        event = req.payload["event"]

        if event.get("type") == "message" and "files" in event:
            try:
                output_path = download_image(event["files"][0]["url_private_download"])
                web_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
                web_client.chat_postMessage(channel=event["channel"], text=image_to_explanation(oai_client, output_path))
            except Exception as e:
                print(f"Exception: {e}")


def main():
    client = SocketModeClient(
        app_token=os.environ["SLACK_APP_TOKEN"],
        web_client=WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    )

    client.socket_mode_request_listeners.append(process)
    client.connect()
    Event().wait()
