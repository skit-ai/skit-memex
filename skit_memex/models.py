import base64


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
        model = "gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a meme assistant. \
                    Consider the text input provided,recommend the name of a \
                    common meme that could be associated with the message"}
                {"role": "user", "content": text}
        ],
        response_format={ "type": "json_object" }
    )

    return response.choices[0].message
