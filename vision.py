import openai

with open("key.env") as f:
    openai.api_key = f.read().strip()

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://hips.hearstapps.com/hmg-prod/images/four-ducklings-on-grass-royalty-free-image-1732103736.jpg?crop=0.670xw:1.00xh;0.0830xw,0&resize=640:*",
                },
            },
        ],
    }],
)

print(response.choices[0].message.content)