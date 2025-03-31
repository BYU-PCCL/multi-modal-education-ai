import math
from manim import (
    Scene,
    NumberPlane,
    Arrow,
    MathTex,
    Text,
    VGroup,
    Rectangle,
    FadeIn,
    FadeOut,
    Create,
    TransformMatchingShapes,
    WHITE,
    BLACK,
    RED_E,
    GREEN_E,
    BLUE_E,
    UR,
    UP,
    LEFT,
    DOWN
)

# This scene demonstrates vector addition in a 2D plane using the tip-to-tail method.
class Vector_Merge3(Scene):
    def construct(self):
        # 1) Create a NumberPlane and center it on the screen so it is fully visible
        plane = NumberPlane(
            x_range=[-1, 6, 1],
            y_range=[-1, 6, 1]
        )
        plane.center()
        self.play(FadeIn(plane, run_time=1))
        self.wait(0.5)

        # Helper function to place a semi-opaque background behind labels
        def make_label_group(label_mob, label_color=BLACK, fill_opacity=0.8, buff=0.15):
            bg = Rectangle(color=label_color, fill_opacity=fill_opacity, stroke_width=0)
            bg.surround(label_mob, buff=buff)
            return VGroup(bg, label_mob)

        # 2) Draw vector A with a thicker stroke, add a more visible label with background
        A_vector = Arrow(
            start=plane.c2p(0, 0),
            end=plane.c2p(3, 2),
            color=GREEN_E
        )
        A_vector.set_stroke(width=6)
        A_label_tex = MathTex(r"A = (3, 2)", color=GREEN_E).scale(1.2)
        A_label_group = make_label_group(A_label_tex)
        # Position label so it does not risk overlapping the path of the next vector
        A_label_group.next_to(A_vector.get_end(), UP + LEFT, buff=0.4)

        self.play(Create(A_vector, run_time=2), FadeIn(A_label_group, run_time=1))
        self.wait(0.5)

        # 3) Draw vector B with a thicker stroke, label with background
        B_vector = Arrow(
            start=plane.c2p(0, 0),
            end=plane.c2p(1, 3),
            color=RED_E
        )
        B_vector.set_stroke(width=6)
        B_label_tex = MathTex(r"B = (1, 3)", color=RED_E).scale(1.2)
        B_label_group = make_label_group(B_label_tex)
        B_label_group.next_to(B_vector.get_end(), UR, buff=0.4)

        self.play(Create(B_vector, run_time=2), FadeIn(B_label_group, run_time=1))
        self.wait(0.5)

        # 4) Show instructions with a properly sized rectangle background
        tip_text = Text("Add the vectors tip-to-tail", color=WHITE).scale(0.9)
        tip_bg = Rectangle(color=BLACK, fill_opacity=1, stroke_width=0)
        tip_bg.surround(tip_text, buff=0.2)
        tip_group = VGroup(tip_bg, tip_text)
        tip_group.to_edge(UP, buff=0.3)

        self.play(FadeIn(tip_group, run_time=1))
        self.wait(1)
        self.play(FadeOut(tip_group, run_time=1))
        self.wait(0.5)

        # 5) Move vector B tip-to-tail, then update its label if desired
        shift_vec = plane.c2p(3, 2) - plane.c2p(0, 0)
        self.play(
            B_vector.animate.shift(shift_vec),
            B_label_group.animate.shift(shift_vec),
            run_time=2
        )
        self.wait(0.5)

        new_B_label_tex = MathTex(r"B = (4, 5)", color=RED_E).scale(1.2)
        new_B_label_group = make_label_group(new_B_label_tex)
        new_B_label_group.next_to(B_vector.get_end(), UR, buff=0.4)
        self.play(TransformMatchingShapes(B_label_group, new_B_label_group, run_time=1))
        B_label_group = new_B_label_group
        self.wait(0.5)

        # 6) Draw resultant vector R with a thicker stroke, label it
        R_vector = Arrow(
            start=plane.c2p(0, 0),
            end=plane.c2p(4, 5),
            color=BLUE_E
        )
        R_vector.set_stroke(width=6)
        R_label_tex = MathTex(r"R = (4, 5)", color=BLUE_E).scale(1.2)
        R_label_group = make_label_group(R_label_tex)
        R_label_group.next_to(R_vector.get_end(), UR, buff=0.4)

        self.play(Create(R_vector, run_time=2), FadeIn(R_label_group, run_time=1))
        self.wait(0.5)

        # 7) Display "A + B = R" at the top with a visible background
        sum_text = Text("A + B = R", color=WHITE).scale(1.2)
        sum_bg = Rectangle(color=BLACK, fill_opacity=1, stroke_width=0)
        sum_bg.surround(sum_text, buff=0.2)
        sum_group = VGroup(sum_bg, sum_text)
        sum_group.to_edge(UP, buff=0.7)

        self.play(FadeIn(sum_group, run_time=1))
        self.wait(9)