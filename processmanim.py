import os
import subprocess
import openai
from datetime import datetime
import re

# Set your OpenAI API key (make sure it's set in your environment)
with open("key.env") as f:
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
                    "You will be given a problem or concept to create an animation plan for. "
                    "Your output will be given to another "
                    "model that will actually create the Manim code for an animation. "
                    "Your job is to determine what brief (5-30 second) animation should be created to best help the user understand the concept that they are asking about, "
                    "and then explain that animation in a concise manner (a brief explanation). "
                    "Tell the manim-generating model to include certain helpful equations and words that will more fully explain what is happening in the video. "
                    "Also tell the model to ensure that it doesn't generate animations that will overlap or go off the screen. As you explain the duration of specific parts of the animation such as how long words and equations should stay on the screen, be specific as to how long they should be and ensure that there is no overlap of different parts of the animation. Also specify exactly where each aspect (equation, word, sentence, shape, etc.) should appear on the screen. "
                    "Also make sure to tell the model to not make animations move too fast, make sure that you specifiy the length of them and that they are slow enough for people to follow and understand what is going on. "
                    "Be very detailed and specific in how you explain the animation. Specify which colors to use to understand what is happening. For example, if a certain part of the equation is moving around, make it a seperate color. "
                    "The objective of your described animation is to show something that can't be described easily with just an equation or words. You are to determine a visual animation that will help the learner visualize and comprehend the intuition of what is moving and the impact that it has. For example, with solving basic equations, show the numbers or variables moving around as you manipulate the equations instead of just having different equations appear. Another example is when describing what the determinat is, create an example of a shape on a plane being manipulated by a matrix that demonstrates what the determinat means. "
                    "Tell the model to always include a very brief description of what the animation is showing. "
                    "Output only plain text without any markdown formatting."
                    ""
                )
            },
            {"role": "user", "content": user_prompt}
        ],
        reasoning_effort = "high"
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
                # ---------------------------------------------------------
                # 1) Output Requirements
                # ---------------------------------------------------------
                "You are a coding assistant specialized in generating Manim animations. "
                "Your output must be strictly raw, valid Python code (no markdown fences, no extra explanations). "
                "Only output the code, starting with all necessary import statements and defining exactly one Scene class named 'MyScene'. "
                "Ensure that all LaTeX expressions in MathTex objects are valid. "
                "Animations must be slow enough to follow; do not create super fast animations. "
                "Never let text or shapes overlap or go off-screen. "
                "If you transform a plane, keep its original gridlines visible. "
                "Use words to briefly explain at the top what the animation is showing. "

                # ---------------------------------------------------------
                # 2) Manim v0.19.0 Compliance
                # ---------------------------------------------------------
                "You must adhere to Manim Community v0.19.0. Always follow the official docs at https://docs.manim.community/en/stable/reference.html. "
                "Avoid any deprecated or invalid parameters. Use only supported keyword arguments (e.g., 'color', 'stroke_width', 'fill_opacity'). "
                "Do NOT use 'fill_color'. Do NOT use 'direction' in methods (use to_corner(UR) instead). "
                "Do NOT reference 'self.camera.frame' in a default Scene. For camera animations, use 'MovingCameraScene' as the base class. "
                "If you call 'move_camera', ensure the scene inherits from 'ThreeDScene', because 'move_camera' is unavailable in 'MovingCameraScene'. "
                "Never set an animation's run_time to 0. If you need no pause, omit self.wait entirely. "
                "Use 'move_camera' instead of 'set_camera_orientation'. "
                "Do NOT call add_fixed_in_frame_mobjects if the scene inherits from MovingCameraScene; that method is only in ThreeDScene. "
                "Do NOT use 'TransformMatchingParts'; use 'TransformMatchingShapes' instead. "

                # ---------------------------------------------------------
                # 3) Graph & Surface Methods
                # ---------------------------------------------------------
                "When plotting graphs, replace any 'get_graph' calls with 'axes.plot' and proper keyword arguments (e.g., color='BLUE'). "
                "For specialized 3D classes like ParametricSurface, explicitly import them from their submodules. "
                "Do NOT assume 'from manim import *' includes them. If they're missing, avoid using them. "
                "Do NOT use 'x_range' or 'y_range' in VectorField, as it causes TypeError in v0.19.0. "

                # ---------------------------------------------------------
                # 4) Color Rules
                # ---------------------------------------------------------
                "Do NOT use color constants that don't exist in Manim v0.19.0: e.g., LIGHT_BLUE, DARK_GREEN, DARK_GRAY, DarkGreen, DarkGray, "
                "LightBlue, LightGreen, DarkBlue, DarkBrown, LightCyan, LightMagenta, LightYellow, LightGrey, or DarkGrey. "
                "Only use the built-in colors (WHITE, BLACK, GREY_A, ..., BROWN, BROWN_A, etc.), or define custom colors with Color(rgb=(r,g,b)). "
                "Do NOT use 'dash_array' with 'set_style()'; use DashedVMobject or DashedLine for dashed lines. "
                "Do NOT import 'Color' from 'manim.utils.color'. Manim v0.19.0 does not provide that class. Instead, use 'rgb_to_color((r,g,b))', a hex string, or a recognized built-in color constant. "

                # ---------------------------------------------------------
                # 5) Other Prohibitions
                # ---------------------------------------------------------
                "Do NOT use 'Pyramid'. If you need a pyramid, build it manually or use an existing shape in manim.mobject.three_d.polyhedra. "

                # ---------------------------------------------------------
                # 6) Final Instruction: Use the Provided Animation Plan
                # ---------------------------------------------------------
                "\n\nUse the following animation plan as the basis for the animation:\n"
                + animation_plan
            )
        },
        {"role": "user", "content": "Generate the Manim code for the above animation plan."}
    ],
    reasoning_effort="high"
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

def determine_simple_name(animation_plan):
    """
    Uses a gpt-4o model to generate a short, unique, human-readable name
    based on the animation plan. This ensures each animation file has a
    concise and distinct title.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # or your chosen GPT-4 variant
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a naming assistant specialized in generating short, unique names for animations. "
                    "The user will provide an animation plan, and you must return a concise, human-readable name. "
                    "No punctuation besides underscores, letters, or digits. "
                    "Only output the name, no explanations."
                )
            },
            {"role": "user", "content": animation_plan}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

def main():
    # Example user prompt
    user_prompt = "Give me a simple and brief animation of an integral on a graph."

    # Step 1: Generate an animation plan
    animation_plan = determine_animation_plan(user_prompt)
    print("Generated Animation Plan:")
    print(animation_plan)

    # Step 2: Use the animation plan to get a short name from GPT-4o
    short_name = determine_simple_name(animation_plan)
    print(short_name)
    # Sanitize the short name (remove spaces or special chars)
    short_name_clean = re.sub(r'[^a-zA-Z0-9_]+', '_', short_name).strip('_')
    print(short_name_clean)
    if not short_name_clean:
        short_name_clean = "Scene"

    # Step 3: Generate Manim code
    manim_code = generate_manim_code(animation_plan)

    # Ensure that there are no 0 wait times
    manim_code = manim_code.replace("self.wait(0)", "self.wait(0.1)")

    print("\nGenerated Manim Code:")
    print(manim_code)

    # Step 4: Create a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Combine short name + timestamp
    new_scene_name = f"{short_name_clean}_{timestamp}"

    # Replace the class definition from "MyScene" to new scene name
    modified_code = re.sub(
        r'class\s+MyScene\s*\((.*?)\):',
        rf'class {new_scene_name}(\1):',
        manim_code
    )

    # Save the modified code
    filename = "generated_manim.py"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(modified_code)

    # Step 5: Run Manim to compile the animation, specifying an output MP4
    mp4_filename = f"{new_scene_name}.mp4"
    subprocess.run(["manim", filename, new_scene_name, "--format=mp4", "-o", mp4_filename])

    # Step 6 (ADDED): Extract 1 frame per second with ffmpeg into <SceneName>/frames folder
    frames_folder = os.path.join(new_scene_name, "frames")
    os.makedirs(frames_folder, exist_ok=True)
    subprocess.run([
        "ffmpeg",
        "-i", mp4_filename,
        "-vf", "fps=1",
        os.path.join(frames_folder, "frame_%03d.png")
    ])

    print(f"\nAnimation rendered to {mp4_filename}.")
    print(f"Frames extracted to {frames_folder}.")

if __name__ == "__main__":
    main()