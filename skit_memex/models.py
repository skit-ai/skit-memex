import base64
import json
import os

def b64_encode_image(image_path: str):
    with open(image_path, "rb") as fp:
        return base64.b64encode(fp.read()).decode("utf-8")


def image_to_explanation(oai_client, image_path: str) -> str:
    """
    Do image explanation using GPT4V
    """

    base64_image = b64_encode_image(image_path)

    response = oai_client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Here is a meme image. Provide explanation of this to people who might not have so much context around this."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content

def meme_recommender(oai_client, text: str):

    response = oai_client.chat.completions.create(
        model = "gpt-4-1106-preview",
        messages=[
                {"role": "system", "content": "You are a meme assistant. \
                    Consider the text input provided,recommend the name of a \
                    common meme that could be associated with the message. Only return a valid json with key meme_r"},
                {"role": "user", "content": text}
        ],
        response_format={ "type": "json_object" }
    )

    return response.choices[0].message.content

def meme_text_generator(oai_client, meme, text, boxcount):
    content_msg = f"meme is {meme}, text is {text} and text_areas are {boxcount}"

    response = oai_client.chat.completions.create(
        model = "gpt-4-1106-preview",
        messages=[
                {"role": "system", "content": "You are a meme captioning assistant. \
                    Consider the input provided with name of the meme, text for which the meme should be captioned\
                    and available number of text areas, \
                    recommend the text for each text area. Only return a valid json with numeric ordered keys"},
                {"role": "user", "content":content_msg
                }
        ],
        response_format={ "type": "json_object" }
    )

    return response.choices[0].message.content
