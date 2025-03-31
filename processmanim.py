import os
import subprocess
from openai import OpenAI

with open("key.env") as f:
    client = OpenAI(api_key=f.read().strip())
from datetime import datetime
import re
import sys
import base64
import mimetypes

 # Find a 2 × 2 diagonal matrices A that have the property A^2 = I . Geometrically interpret this example as a linear map. I want you to show the matrix and that the matrix multiplcation turns into the identity matrix, then the matrix geometrically. 
user_prompt = "Create an animation showing a solution to this problem:  Find a 2 x 2 matrix that rotates the plane by 45 degrees counterclockwise followed by a reflection across the horizontal axis."
core_model = "o3-mini"
image_model = "o1"
reasoning_level = "low"
num_of_improvements = 0

fine_tuned_system_prompt = (
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
                "Ensure that for any calls to to_edge, you pass a valid direction (e.g., UP, DOWN) and use the buff parameter for spacing. Do not pass raw numerical values as the direction. "
                "If you want to color text in a MathTex expression, do NOT use \\textcolor{...}{...}. Instead, use {\\color{...}...}, because Manim's default LaTeX template doesn't support \\textcolor. "
                "When including text or punctuation in a MathTex expression, use \\text{} (e.g., \\text{Shear:}) instead of raw text. Also, use braces for subscripts (e.g., M_{1}) to avoid LaTeX errors. "
                "In a MathTex expression, never nest curly braces after \\color. For instance, use {\\color{red}1}, not {\\color{red}{1}}. Also, if you have words or punctuation, wrap them in \\text{}, e.g., \\text{Shear:} "
                "In Manim v0.19.0, VMobject.set_stroke() must use width=, not stroke_width=. "
                "If you want to reference constants like RIGHT, UP, DOWN, UL, or MED_SMALL_BUFF, explicitly import them. Do not assume they are already in scope. "

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
)

def determine_animation_plan_old(user_prompt):
    response = client.chat.completions.create(model=core_model,  # Use your desired chat model
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
                "Tell the model that your output will be passed to to always include a very brief description of what the animation is showing. "
                "Output only plain text without any markdown formatting."
                ""
            )
        },
        {"role": "user", "content": user_prompt}
    ],
    reasoning_effort = reasoning_level)
    return response.choices[0].message.content.strip()

def determine_animation_plan(user_prompt):
    input_text = (
        "You will be given a problem or concept to create an animation plan for. "
        "Your output will be given to another "
        "model that will actually create the Manim code for an animation. "
        "Your job is to determine what brief (10-30 second) animation should be created to best help the user understand the concept that they are asking about, "
        "and then explain that animation in a concise manner (a brief explanation). "
        "Tell the manim-generating model to include certain helpful equations and words that will more fully explain what is happening in the video. "
        "Also tell the model to ensure that it doesn't generate animations that will overlap or go off the screen. As you explain the duration of specific parts of the animation such as how long words and equations should stay on the screen, be specific as to how long they should be and ensure that there is no overlap of different parts of the animation. Also specify exactly where each aspect (equation, word, sentence, shape, etc.) should appear on the screen. "
        "Also make sure to tell the model to not make animations move too fast, make sure that you specifiy the length of them and that they are slow enough for people to follow and understand what is going on. "
        "Be very detailed and specific in how you explain the animation. Specify which colors to use to understand what is happening. For example, if a certain part of the equation is moving around, make it a seperate color. "
        "The objective of your described animation is to show something that can't be described easily with just an equation or words. You are to determine a visual animation that will help the learner visualize and comprehend the intuition of what is moving and the impact that it has. For example, with solving basic equations, show the numbers or variables moving around as you manipulate the equations instead of just having different equations appear. Another example is when describing what the determinat is, create an example of a shape on a plane being manipulated by a matrix that demonstrates what the determinat means. "
        "Tell the model that your output will be passed to to always include a very brief description of what the animation is showing. "
        "Output only plain text without any markdown formatting."
        "User Prompt: " + user_prompt
    )

    response = openai.responses.create(
        model=core_model,
        input=input_text,
        reasoning={'effort': reasoning_level},
        max_output_tokens=4000,
    )

    generated_text = response.output[1].content[0].text.strip()

    return generated_text


def generate_manim_code(animation_plan):
    response = client.chat.completions.create(model=core_model,  # Use your desired chat model
    messages=[
        {
            "role": "system",
            "content": (
                fine_tuned_system_prompt +
                # ---------------------------------------------------------
                # 6) Final Instruction: Use the Provided Animation Plan
                # ---------------------------------------------------------
                "\n\nUse the following animation plan as the basis for the animation:\n"
                + animation_plan
            )
        },
        {"role": "user", "content": "Generate the Manim code for the above animation plan."}
    ],
    reasoning_effort=reasoning_level)
    code = response.choices[0].message.content.strip()

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
    response = openai.chat.completions.create(
        model="gpt-4o",  # or your chosen GPT-4 variant
        temperature=0.8,
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
    return response.choices[0].message.content.strip()


def fix_manim_code(error_message, current_code):
    """
    Given the error message and the current generated code, return fixed code.
    """
    prompt = (
        "You are a debugging assistant for Manim animations. "
        "The following code produces an error when executed.\n\n"
        "Error:\n" + error_message + "\n\n"
        "Current code:\n" + current_code + "\n\n"
        "Please fix the error in the code. Only output the corrected code with no extra commentary. "
        "DO NOT CHANGE THE NAME OF THE CLASS. In the fixed code that you produce, keep the exact same name as the original code that you are given. "
        "Most errors that you will see will come from using old syntax from previous manim versions that no longer work in manim 0.19.0 which I am using. "
        "Here are some common problems and solutions that may help you: "

        + fine_tuned_system_prompt
    )
    response = client.chat.completions.create(model=core_model,
    messages=[
        {"role": "system", "content": "You are a debugging assistant for Manim animations."},
        {"role": "user", "content": prompt}
    ],
    reasoning_effort=reasoning_level)
    fixed_code = response.choices[0].message.content.strip()
    return fixed_code

def log_fix_attempt(retry_count, error_message, current_code, fixed_code):
    """
    Logs the error and fix attempt to a log file.
    """
    log_entry = (
        f"--- Retry Attempt {retry_count} ---\n"
        f"Error Message:\n{error_message}\n\n"
        f"Current Code:\n{current_code}\n\n"
        f"Fixed Code:\n{fixed_code}\n"
        f"{'-'*80}\n\n"
    )
    with open("fix_attempts.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)


def image_to_data_url(image_path):
    """
    Reads the image file, encodes it to Base64, and returns a data URL.
    """
    with open(image_path, "rb") as img_file:
        data = img_file.read()
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"  # Fallback if not detected
    encoded_str = base64.b64encode(data).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_str}"

def get_animation_feedback(animation_plan, current_code, frames_folder):
    """
    Processes the images in the frames folder and calls the model to get feedback
    on how the animation can be improved to better align with the animation plan.
    """
    valid_extensions = {".png", ".jpg", ".jpeg"}
    image_files = [
        f for f in os.listdir(frames_folder)
        if os.path.splitext(f)[1].lower() in valid_extensions
    ]
    if not image_files:
        print("No valid image files found in the frames folder.")
        return "No images found for feedback."

    message_content = [{
        "type": "text",
        "text": (
            "You are given multiple images, each representing one frame per second from an animation created by Manim. "
            "The animation was generated based on the following animation plan and code. "
            "Your job is to provide very detailed, clear, and specific feedback on how the animation can be improved to better align with the animation plan. "
            "Identify any issues such as elements going off screen, overlapping parts, or any visual inconsistencies. " # Add more here- 
            "If there are major problems with the timing that greatly reduce the quality of the animation, you can address them, but do not hyperfocus on the exact timing given in the instructions. These times are merely a rough estimate. "
            "Your focus is to address main problems that you visually can see in the animation. For example, pay close attention to vectors that aren't in the exact correct locations, animations that overlap or go off the screen, animations that disappear correctly, text that is not easily visable, animations that aren't centered in the screen, etc. "
            "Look through each part of the manim code and ensure that all pieces are working properly. "
            "Provide your feedback in clear text that can be used by another model to modify the code.\n\n"
            "Animation Plan:\n" + animation_plan + "\n\n"
            "Manim Code:\n" + current_code
        )
    }]
    for image_file in image_files:
        image_path = os.path.join(frames_folder, image_file)
        data_url = image_to_data_url(image_path)
        message_content.append({
            "type": "image_url",
            "image_url": {"url": data_url}
        })
    response = client.chat.completions.create(model=image_model,
    messages=[{
        "role": "user",
        "content": message_content
    }],
    reasoning_effort=reasoning_level)
    feedback = response.choices[0].message.content.strip()
    return feedback

def improve_manim_code(feedback, current_code, new_scene_name):
    """
    Uses the feedback to improve the current Manim code.
    """
    prompt = (
        "You are an assistant specialized in improving Manim animation code based on feedback. "
        "The following is the feedback provided on the animation, followed by the current code that generated the animation.\n\n"
        "Feedback:\n" + feedback + "\n\n"
        "Current Code:\n" + current_code + "\n\n"
        "Please update the code to address the feedback and improve the animation accordingly. "
        "Only output the corrected code that can be ran immediately. Do not give any additional commentary"
        "Here are specific guideline for writing the code for the manim version 0.19.0 that I am running:\n"
        + fine_tuned_system_prompt
    )
    response = client.chat.completions.create(model=core_model,
    messages=[
        {"role": "system", "content": "You are an assistant specialized in improving Manim animation code."},
        {"role": "user", "content": prompt}
    ],
    reasoning_effort=reasoning_level)
    improved_code = response.choices[0].message.content.strip()
    # Ensure the scene class name remains consistent
    improved_code = re.sub(
        r'class\s+MyScene\s*\((.*?)\):',
        rf'class {new_scene_name}(\1):',
        improved_code
    )
    return improved_code


def main():
    # Example user prompt
    #####################################################################################################
    # user_prompt = 
    #####################################################################################################

    # Step 1: Generate an animation plan
    animation_plan = determine_animation_plan(user_prompt)
    print("Generated Animation Plan:")
    print(animation_plan)

    # Step 2: Use the animation plan to get a short name from GPT-4o
    short_name = determine_simple_name(animation_plan)
    print("Short name from model:", short_name)
    short_name_clean = re.sub(r'[^a-zA-Z0-9_]+', '_', short_name).strip('_')
    if not short_name_clean:
        short_name_clean = "Scene"

    manim_code = generate_manim_code(animation_plan)
    manim_code = manim_code.replace("self.wait(0)", "self.wait(0.1)")
    print("\nGenerated Manim Code:")
    print(manim_code)

    # Step 2: Set up naming scheme (no timestamp)
    original_scene_name = short_name_clean

    # Replace the class definition for the original scene
    modified_code = re.sub(
        r'class\s+MyScene\s*\(\s*(.*?)\s*\):',
        rf'class {original_scene_name}(\1):',
        manim_code,
        flags=re.DOTALL
    )


    filename = "generated_manim.py"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(modified_code)

    # Step 3: Render original video with error handling
    max_retries = num_of_improvements
    retry_count = 0
    while retry_count < max_retries:
        try:
            print("\nRendering original animation...")
            result = subprocess.run(
                ["manim", filename, original_scene_name, "--format=mp4"],
                check=True, capture_output=True, text=True
            )
            print("Original rendering successful!")
            print(result.stdout)
            break
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr
            print("Error during original rendering:")
            print(error_msg)
            fixed_code = fix_manim_code(error_msg, modified_code)
            log_fix_attempt(retry_count + 1, error_msg, modified_code, fixed_code)
            modified_code = fixed_code
            with open(filename, "w", encoding="utf-8") as file:
                file.write(modified_code)
            retry_count += 1
            print(f"Retrying original fix attempt #{retry_count}...")
    else:
        print("Max retries reached for original video. Exiting.")
        exit(1)

    # Step 4: Extract frames from original video
    mp4_filename = os.path.join("media", "videos", "generated_manim", "1080p60", f"{original_scene_name}.mp4")
    original_frames_folder = os.path.join("media", "videos", "generated_manim", "1080p60", original_scene_name, "frames")
    os.makedirs(original_frames_folder, exist_ok=True)
    subprocess.run([
        "ffmpeg",
        "-i", mp4_filename,
        "-vf", "fps=1",
        os.path.join(original_frames_folder, "frame_%03d.png")
    ])
    print(f"\nOriginal animation rendered to {mp4_filename}.")
    print(f"Frames extracted to {original_frames_folder}.")

    # Step 5: Get feedback on the original animation
    feedback = get_animation_feedback(animation_plan, modified_code, original_frames_folder)
    print("\n👑 Feedback on Original Animation:")
    print(feedback)

    # Step 6: Loop to generate additional videos based on feedback
    max_improvement_attempts = 3  # Set number of additional videos desired
    current_code = modified_code
    for i in range(1, max_improvement_attempts + 1):
        improved_scene_name = f"{original_scene_name}{i}"  # e.g., Scene1, Scene2, etc.
        improved_code = improve_manim_code(feedback, current_code, improved_scene_name)
        log_entry = (
            f"--- Improvement Attempt {i} ---\n"
            f"Feedback:\n{feedback}\n\n"
            f"Current Code:\n{current_code}\n\n"
            f"Improved Code:\n{improved_code}\n"
            f"{'-'*80}\n\n"
        )
        with open("improvement_attempts.log", "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)

        current_code = improved_code
        with open(filename, "w", encoding="utf-8") as file:
            file.write(improved_code)

        retry_count = 0
        while retry_count < max_retries:
            try:
                print(f"\nRendering improved animation: {improved_scene_name} ...")
                result = subprocess.run(
                    ["manim", filename, improved_scene_name, "--format=mp4"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("Improved rendering successful!")
                print(result.stdout)
                break  # If we succeed, exit the retry loop
            except subprocess.CalledProcessError as e:
                print("Error during improved rendering, getting new feedback...")
                retry_count += 1
                # If the code actually compiled but manim had a visual or LaTeX error,
                # we can still try to gather feedback from the frames (if any exist).
                feedback = get_animation_feedback(
                    animation_plan,
                    current_code,
                    os.path.join(improved_scene_name, "frames")
                )

        else:
            # If we exhaust all retries, skip frames extraction & skip feedback
            print(f"Max retries reached for {improved_scene_name}. Moving to next improvement.")
            continue

        # Only run this if the improved animation was successfully rendered
        mp4_filename = os.path.join(
            "media", "videos", "generated_manim", "1080p60",
            f"{improved_scene_name}.mp4"
        )
        frames_folder = os.path.join(improved_scene_name, "frames")
        os.makedirs(frames_folder, exist_ok=True)
        subprocess.run([
            "ffmpeg",
            "-i", mp4_filename,
            "-vf", "fps=1",
            os.path.join(frames_folder, "frame_%03d.png")
        ])
        print(f"\nImproved animation rendered to {mp4_filename}.")
        print(f"Frames extracted to {frames_folder}.")

        feedback = get_animation_feedback(animation_plan, current_code, frames_folder)
        print(f"\n👑 Feedback for next improvement iteration:")
        print(feedback)


if __name__ == "__main__":
    main()