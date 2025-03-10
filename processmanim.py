import os
import subprocess
import openai
from datetime import datetime
import re

# Set your OpenAI API key (make sure it's set in your environment)
with open("manim/MANIM/key.env") as f:
    openai.api_key = f.read().strip()

def determine_animation_plan(user_prompt):
    """
    Analyzes the user's prompt and returns an animation plan.
    The output will include two parts:
      1. Animation Plan: a detailed plan for a brief (15-30 sec) animation.
      2. Brief Explanation: a very short summary of what the animation does.
    """
    response = openai.ChatCompletion.create(
        model="o1",  # Use your desired chat model
        messages=[
            {
                "role": "system",
                "content": (
                    "You will be given a normal prompt from a user that they would put into ChatGPT "
                    "to help them understand a certain topic or problem. Your output will be given to another "
                    "model that will actually create the Manim code for an animation to help the user. "
                    "Your job is to determine what brief (15-30 second) animation should be created to best help the user, "
                    "and then explain that animation in a concise manner (a brief explanation). Try to make your animation description "
                    "similar to how 3Blue1Brown the youtuber would format his animations. "
                    "You won't need to explain the whole concept in the video because this same prompt will be given to another vanilla model that will explain the concept using text. So you just need to make a supplemental video that will add to what another model will already explain."
                    "However, include helpful equations and words that will more fully explain what is happening in the video."
                    "Output only plain text without any markdown formatting."
                    "IMPORTANT: For get_riemann_rectangles, use 'x_range' (a two-element list, e.g., x_range=[0,2]) instead of 'x_min' and 'x_max'. Ensure all parameters strictly follow the Manim Community v0.19.0 documentation."
                )
            },
            {"role": "user", "content": user_prompt}
        ],
    )
    return response['choices'][0]['message']['content'].strip()

def generate_manim_code(animation_plan):
    """
    Uses the animation plan to generate raw Manim code.
    The code output must be strictly valid Python code (no markdown fences or extra explanations),
    starting with the necessary import statements and defining exactly one Scene class named 'MyScene'.
    Ensure that all LaTeX expressions in MathTex commands use valid syntax.
    """
    response = openai.ChatCompletion.create(
        model="o1",  # Use your desired chat model
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a coding assistant specialized in generating Manim animations. Your output must be strictly raw, valid Python code "
                    "that can be saved directly as a .py file and executed with Manim. Do not wrap the code in markdown fences or include any explanations. "
                    "Only output the code, starting with all necessary import statements and defining exactly one Scene class named 'MyScene'. "
                    "Ensure that all LaTeX expressions in MathTex objects are valid. " 
                    "You are a coding assistant specialized in Manim Community v0.19.0. When generating or updating Manim code, replace any usage of `get_graph` with the newer `axes.plot` method. Ensure that all graph-plotting code uses `axes.plot` with appropriate keyword arguments (like `color`) so that no unexpected keyword errors occur. "
                    "IMPORTANT: Ensure that all API calls and parameters (e.g., for get_graph, get_riemann_rectangles, etc.) strictly follow the Manim Community v0.19.0 documentation. Do not use any deprecated or invalid keyword arguments such as 'x_range' if they are not supported. Also do not use unsupported parameters like 'fill_color'; only use supported ones such as 'stroke_width' and 'fill_opacity'."
                    "Use the following animation plan as the basis for the animation: "
                    + animation_plan
                )
            },
            {"role": "user", "content": "Generate the Manim code for the above animation plan."}
        ]
    )
    code = response['choices'][0]['message']['content'].strip()
    
    # Strip out markdown fences if they're present
    if code.startswith("```"):
        lines = code.splitlines()
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().endswith("```"):
            lines = lines[:-1]
        code = "\n".join(lines)
    return code

def main():
    # Get a user prompt (explanation request) from the learner
    user_prompt = "Help me understand how to do simple equations to solve for y."

    # Step 1: Generate an animation plan and brief explanation based on the user prompt
    animation_plan = determine_animation_plan(user_prompt)
    print("Generated Animation Plan and Brief Explanation:")
    print(animation_plan)

    # Step 2: Generate the Manim code from the animation plan
    manim_code = generate_manim_code(animation_plan)
    print("\nGenerated Manim Code:")
    print(manim_code)

    # Create a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Modify the scene class name in the generated code to include the timestamp
    new_scene_name = f"MyScene_{timestamp}"
    # Replace the class definition from "MyScene" to our new scene name
    modified_code = re.sub(r'class\s+MyScene\s*\(Scene\):', f'class {new_scene_name}(Scene):', manim_code)

    # Save the modified code to a Python file with UTF-8 encoding
    filename = "generated_manim.py"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(modified_code)

    # Run Manim to compile the animation into an mp4 file using the new scene class name
    subprocess.run(["manim", filename, new_scene_name, "--format=mp4"])

if __name__ == "__main__":
    main()