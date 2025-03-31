from openai import OpenAI

client = OpenAI(api_key=f.read().strip())

def get_4o_response(prompt):
    with open("key.env") as f:
    response = client.chat.completions.create(model="gpt-4o-search-preview",
    messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

if __name__ == "__main__":
    user_prompt = "Can you see all the documenation for manim on here? https://docs.manim.community/en/stable/reference.html"
    print(get_4o_response(user_prompt))