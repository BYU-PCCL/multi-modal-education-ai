from manim import *

class MyScene_20250310_153143(Scene):
    def construct(self):
        # Equations
        eq1 = MathTex("2","x","+","3","y","=","12")
        eq2 = MathTex("3","y","=","12","-","2","x")
        eq3 = MathTex("y","=","4","-",r"\frac{2}{3}","x")

        # Position them
        eq1.move_to(ORIGIN)
        eq2.move_to(ORIGIN)
        eq3.move_to(ORIGIN)

        # Text prompts
        text_sub = Tex("Subtract 2x from both sides").scale(0.7).next_to(eq1, UP)
        text_div = Tex("Divide by 3").scale(0.7)

        # Show initial equation
        self.play(Write(eq1))
        self.play(Indicate(VGroup(eq1[0], eq1[1])))  # Highlight "2x"
        self.play(FadeIn(text_sub))
        self.wait(1)
        self.play(FadeOut(text_sub))

        # Transform to second equation
        self.play(TransformMatchingTex(eq1, eq2))

        # Highlight "3" and show division text
        text_div.next_to(eq2, UP)
        self.play(Indicate(eq2[0]))  # Highlight the "3"
        self.play(FadeIn(text_div))
        self.wait(1)
        self.play(FadeOut(text_div))

        # Transform to final equation
        self.play(TransformMatchingTex(eq2, eq3))
        self.wait(2)