from manim import Scene, Axes, VGroup, MathTex, Tex, Polygon, FadeIn, FadeOut, Create, ORIGIN, UP, DOWN, WHITE, BLUE, GREEN, YELLOW

class IntegralCurve2_20250314_185658(Scene):
    # Brief Explanation: We will show a parabola f(x)=x^2 and the area under it from x=0 to x=2,
    # then illustrate how the integral sums the area by displaying Riemann rectangles.
    def construct(self):
        # 1) Create and fade in the Cartesian plane (0s to 1s)
        axes = Axes(
            x_range=[0, 2.5, 1],
            y_range=[0, 4.5, 1],
            x_length=5,
            y_length=3,
            tips=True,
        )
        self.play(FadeIn(axes), run_time=1)

        # 2) Draw the parabola f(x)=x^2 from x=0 to x=2 (1s to 3s)
        curve = axes.plot(lambda x: x**2, x_range=[0, 2], color=BLUE, stroke_width=6)
        self.play(Create(curve), run_time=2)

        # 3) Fill the area under the parabola from x=0 to x=2 (3s to 5s)
        area = axes.get_area(curve, x_range=[0, 2], color=YELLOW, opacity=0.5)
        self.play(FadeIn(area), run_time=2)

        # 4) Display the integral expression at t=5s (remains until t=10s)
        integral_tex = MathTex(r"\int_{0}^{2} x^2 \, dx", color=WHITE)
        integral_tex.to_edge(UP, buff=0.5)
        self.play(FadeIn(integral_tex), run_time=1)

        # 5) Introduce about five green Riemann sum rectangles (6s to 9s)
        def f(x):
            return x**2

        rectangles = VGroup()
        n_rects = 5
        width = 2 / n_rects
        for i in range(n_rects):
            x0 = i * width
            x1 = (i + 1) * width
            mid = (x0 + x1) / 2
            height = f(mid)
            p0 = axes.c2p(x0, 0)
            p1 = axes.c2p(x0, height)
            p2 = axes.c2p(x1, height)
            p3 = axes.c2p(x1, 0)
            rect = Polygon(p0, p1, p2, p3, color=GREEN, fill_opacity=0.5)
            rectangles.add(rect)

        for rect in rectangles:
            self.play(FadeIn(rect), run_time=0.6)

        # 6) Merge these rectangles into the highlighted area (9s to 10s)
        self.play(FadeOut(rectangles), run_time=1)

        # 7) Fade in explanatory text below the integral (10s to 12s)
        explanation_text = Tex("The integral represents the area under the curve.", color=WHITE)
        explanation_text.scale(0.7)
        explanation_text.next_to(integral_tex, DOWN, buff=0.5)
        self.play(FadeIn(explanation_text), run_time=2)

        # 8) Fade out all elements together (12s to 13s)
        self.play(FadeOut(VGroup(axes, curve, area, integral_tex, explanation_text)), run_time=1)

        # A visual of the area under a curve and its integral.