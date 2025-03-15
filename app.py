from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import subprocess, re
import openai
from datetime import datetime

app = FastAPI()

# Mount the "static" folder at the "/static" route
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/generate_manim")
async def generate_manim(request: Request):
    body = await request.json()
    user_prompt = body["prompt"]

    # 1) Generate plan & code
    animation_plan = determine_animation_plan(user_prompt)
    manim_code = generate_manim_code(animation_plan)

    # 2) Tweak code & write file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_scene_name = f"MyScene_{timestamp}"
    modified_code = re.sub(
        r'class\s+MyScene\s*\(Scene\):',
        f'class {new_scene_name}(Scene):',
        manim_code
    )
    filename = "generated_manim.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(modified_code)

    # 3) Generate the MP4 in your "static" folder
    #    This command will produce something like "static/MyScene_20230314.mp4"
    output_path = f"static/{new_scene_name}.mp4"
    subprocess.run([
        "manim", filename, new_scene_name, 
        "--format=mp4", 
        "-o", f"{new_scene_name}.mp4", 
        "--media_dir", "static"
    ])

    # Return the URL to that MP4
    video_url = f"http://localhost:8000/static/{new_scene_name}.mp4"
    return {"video_url": video_url}
