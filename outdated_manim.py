import os
import subprocess
import openai
from datetime import datetime
import re

model = "gpt-4o"
reasoning = "high"

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
        model="o3-mini",  # Use your desired chat model
        messages=[
            {
                "role": "system",
                "content": (
                    "You will be given a normal prompt from a user that they would put into ChatGPT "
                    "to help them understand a certain topic or problem. Your output will be given to another "
                    "model that will actually create the Manim code for an animation to help the user. "
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
        reasoning_effort = "low"
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
    model="o3-mini",  # Use your desired chat model
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

                "Your code that you produce will be ran on Manim Community v0.18.0"
                # ---------------------------------------------------------
                # 2) Manim v0.19.0 Compliance
                # ---------------------------------------------------------
                # "You must adhere to Manim Community v0.19.0. Always follow the official docs at https://docs.manim.community/en/stable/reference.html. "
                # "Avoid any deprecated or invalid parameters. Use only supported keyword arguments (e.g., 'color', 'stroke_width', 'fill_opacity'). "
                # "Do NOT use 'fill_color'. Do NOT use 'direction' in methods (use to_corner(UR) instead). "
                # "Do NOT reference 'self.camera.frame' in a default Scene. For camera animations, use 'MovingCameraScene' as the base class. "
                # "If you call 'move_camera', ensure the scene inherits from 'ThreeDScene', because 'move_camera' is unavailable in 'MovingCameraScene'. "
                # "Never set an animation's run_time to 0. If you need no pause, omit self.wait entirely. "
                # "Use 'move_camera' instead of 'set_camera_orientation'. "
                # "Do NOT call add_fixed_in_frame_mobjects if the scene inherits from MovingCameraScene; that method is only in ThreeDScene. "
                # "Do NOT use 'TransformMatchingParts'; use 'TransformMatchingShapes' instead. "

                # ---------------------------------------------------------
                # 3) Graph & Surface Methods
                # ---------------------------------------------------------
                # "When plotting graphs, replace any 'get_graph' calls with 'axes.plot' and proper keyword arguments (e.g., color='BLUE'). "
                # "For specialized 3D classes like ParametricSurface, explicitly import them from their submodules. "
                # "Do NOT assume 'from manim import *' includes them. If they're missing, avoid using them. "
                # "Do NOT use 'x_range' or 'y_range' in VectorField, as it causes TypeError in v0.19.0. "

                # ---------------------------------------------------------
                # 4) Color Rules
                # ---------------------------------------------------------
                # "Do NOT use color constants that don't exist in Manim v0.19.0: e.g., LIGHT_BLUE, DARK_GREEN, DARK_GRAY, DarkGreen, DarkGray, "
                # "LightBlue, LightGreen, DarkBlue, DarkBrown, LightCyan, LightMagenta, LightYellow, LightGrey, or DarkGrey. "
                # "Only use the built-in colors (WHITE, BLACK, GREY_A, ..., BROWN, BROWN_A, etc.), or define custom colors with Color(rgb=(r,g,b)). "
                # "Do NOT use 'dash_array' with 'set_style()'; use DashedVMobject or DashedLine for dashed lines. "
                # "Do NOT import 'Color' from 'manim.utils.color'. Manim v0.19.0 does not provide that class. Instead, use 'rgb_to_color((r,g,b))', a hex string, or a recognized built-in color constant. "

                # ---------------------------------------------------------
                # 5) Other Prohibitions
                # ---------------------------------------------------------
                # "Do NOT use 'Pyramid'. If you need a pyramid, build it manually or use an existing shape in manim.mobject.three_d.polyhedra. "

                # ---------------------------------------------------------
                # 6) Final Instruction: Use the Provided Animation Plan
                # ---------------------------------------------------------
                "\n\nUse the following animation plan as the basis for the animation:\n"
                + animation_plan
            )
        },
        {"role": "user", "content": "Generate the Manim code for the above animation plan."}
    ],
    reasoning_effort="low"
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
                    "Put a single, random digit at the end of each name to futher ensure uniqueness. "
                    "Only output the name, no explanations."
                )
            },
            {"role": "user", "content": animation_plan}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

def main():
    # Example user prompt

    #############################################################
    #############################################################
    user_prompt = "I am struggling to understand what a double integral looks like."
    #############################################################
    #############################################################

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

    # Run Manim to compile the animation
    subprocess.run(["manim", filename, new_scene_name, "--format=mp4"])

if __name__ == "__main__":
    main()




##  Old system prompt:
'''
       messages=[
            {
                "role": "system",
                "content": (
                    "You are a coding assistant specialized in generating Manim animations. Your output must be strictly raw, valid Python code "
                    "that can be saved directly as a .py file and executed with Manim. Do not wrap the code in markdown fences or include any explanations. "
                    "Only output the code, starting with all necessary import statements and defining exactly one Scene class named 'MyScene'. "
                    "Ensure that all LaTeX expressions in MathTex objects are valid. " 
                    "Ensure that you never have text or animation that overlap one another or that go off the screen. "
                    "Also, make the animations slower to make the easier to follow and understand. Don't have super fast animations. "
                    "Use words to briefly explain what the animation you are making is showing at the top of the video. "
                    "If you ever show transformations on a plane and move the whole plane to visual it, keep the original gridlines before the transformation to help the user more clearly see the difference in the new grid plane. "
                    "You are a coding assistant specialized in Manim Community v0.19.0. When generating or updating Manim code, replace any usage of `get_graph` with the newer `axes.plot` method. Ensure that all graph-plotting code uses `axes.plot` with appropriate keyword arguments (like `color`) so that no unexpected keyword errors occur. "
                    "Do NOT use 'TransformMatchingParts': use 'TransformMatchingShapes' for matching transformations. Always verify against the official Manim documentation at https://docs.manim.community/en/stable/reference.html. "
                    "IMPORTANT: Ensure that all API calls and parameters (e.g., for get_graph, get_riemann_rectangles, etc.) strictly follow the Manim Community v0.19.0 documentation. Do not use any deprecated or invalid keyword arguments such as 'x_range' if they are not supported. Also do not use unsupported parameters like 'fill_color'; only use supported ones such as 'stroke_width' and 'fill_opacity'. "
                    "Do NOT use unsupported keyword arguments like 'direction' in methods (e.g., use to_corner(UR) instead of to_corner(direction=[1,1,0])). Always follow the official Manim API documentation. "
                    "Do NOT use unsupported attributes like `self.camera.frame` from the default Scene class. For camera animations, use `MovingCameraScene` as the base class. "
                    "You are a coding assistant specialized in Manim Community v0.19.0. When generating or updating Manim code, ensure strict compliance with the official v0.19.0 API. Follow these guidelines: for graph plotting, use the new Axes API with 'axes.plot' instead of deprecated methods like 'get_graph'; for matching transformations, use 'TransformMatchingShapes' instead of 'TransformMatchingParts'; for camera animations, do not reference 'self.camera.frame' from the default Scene—inherit from 'MovingCameraScene' instead; when aligning objects to corners, use predefined constants (e.g., UR, UL) as positional arguments rather than unsupported keyword arguments like 'direction'; use 'move_camera' instead of 'set_camera_orientation'; for 3D objects such as Arrow3D, do not use unsupported keyword arguments like 'buff' (remove them); and only use supported keyword arguments (e.g., 'color', 'stroke_width', 'fill_opacity') as specified in the official documentation. "
                    "Do NOT call add_fixed_in_frame_mobjects if the scene inherits from MovingCameraScene. That method is only available in ThreeDScene. If you need pinned 2D objects, either inherit from ThreeDScene or use a method compatible with MovingCameraScene. "
                    "If the code calls 'move_camera', ensure the scene inherits from 'ThreeDScene' instead of 'MovingCameraScene'. 'move_camera' is not available in 'MovingCameraScene'. "
                    "Do NOT set any animation's run_time to 0 in Manim. All animations, including move_camera, must have a strictly positive run_time. If an instant change is needed, either use a minimal positive run_time (like 0.1) or switch to a non-animated method (e.g., set_camera_orientation). "
                    "Do NOT use 'Pyramid'. If a pyramid is needed, either construct it manually or use a shape that actually exists in the manim.mobject.three_d or manim.mobject.three_d.polyhedra modules. "
                    "When using ParametricSurface (or any specialized 3D classes), make sure to import them properly from the submodule in Manim v0.19.0. Do not assume they're included in 'from manim import *'. If the class doesn't exist, avoid using it. "
                    "Do NOT use color constants like LIGHT_BLUE, DARK_GREEN, DARK_GRAY, DarkGreen, DarkGray, LightBlue, LightGreen, DarkBlue, DarkBrown, LightCyan, LightMagenta, LightYellow, LightGrey, or DarkGrey. They are invalid in Manim v0.19.0. "
                    "Use only the following built-in colors: WHITE, BLACK, GREY_A, GREY_B, GREY_C, GREY_D, GREY_E, GREY_F, RED, RED_A, ..., BROWN, BROWN_A, ..., etc. If you need something else, define it via Color(rgb=(r,g,b)) or use a recognized color from the Manim v0.19.0 list above. "
                    "Do NOT use 'dash_array' with 'set_style()' in Manim v0.19.0. If you need dashed lines or arrows, use 'DashedVMobject' or 'DashedLine'. "
                    "Do NOT use 'x_range' or 'y_range' when constructing VectorField in Manim v0.19.0. Those arguments are unsupported and cause a TypeError. "
                    "Do NOT use 'self.camera.animate' in ThreeDScene. For animated camera movement in v0.19.0, call 'self.move_camera(...)' directly. "
                    "Do NOT call self.wait(0) or self.wait(0.0). All waits must have a strictly positive duration. If you need no waiting, omit self.wait entirely. "
                    "When using ParametricSurface in Manim v0.19.0, explicitly import it, for example: \n"
                    "from manim.mobject.three_d.three_dimensions import ParametricSurface "
                    "Do not assume from manim import * includes it. If it's not available, avoid using it. "
                    "\n\nUse the following animation plan as the basis for the animation: \n"
                    + animation_plan
                )
'''