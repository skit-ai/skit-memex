import os
import tempfile
from threading import Event

import requests
import json
from openai import OpenAI
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient

from models import *

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

IMGFLIP_USERNAME = os.environ["IMGFLIP_USERNAME"]
IMGFLIP_PASSWORD = os.environ["IMGFLIP_PASSWORD"]

text = "Stepping out for an hour"

def generate():
   meme = meme_recommender(oai_client, text)
   meme = list(dict(json.loads(meme)).values())[0]
   print(meme)

   # Search the meme on imgflip and get count of boxes

   headers = {
       'Content-Type': 'application/x-www-form-urlencoded',
   }

   data = f'username={IMGFLIP_USERNAME}&password={IMGFLIP_PASSWORD}&query={meme}'
   response = requests.post('https://api.imgflip.com/search_memes', headers=headers, data=data)

   resp = response.json()['data']['memes'][0]

   template_id = resp['id']
   box_count = resp['box_count']

   if box_count!=2:
       generate()

   print(template_id, box_count)

   captions = json.loads(meme_text_generator(oai_client, meme, text, box_count))
   caption_list = list(dict(captions).values())

   data = {
       'username': IMGFLIP_USERNAME,
       'password': IMGFLIP_PASSWORD,
       'template_id': template_id,
       'text0': caption_list[0],
       'text1': caption_list[1]
   }

   response = requests.post('https://api.imgflip.com/caption_image', headers=headers, data=data)
   resp = response.json()['data']['url']
   return resp

if __name__ == "__main__":
    generate()
