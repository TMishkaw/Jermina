"""
Procedural Vector Stickman Scene for Manim Community (manimce).
Usage:
  manim -pql stickman_scene.py StickmanExplainerScene
"""

from manim import *
import numpy as np


class Stickman(VGroup):
    """
    Articulated 2D Stickman vector object for mathematical & explainer animations.
    Supports individual limb pivoting around joints.
    """
    def __init__(self, color=WHITE, stroke_width=6, scale_factor=1.0, **kwargs):
        super().__init__(**kwargs)
        self.stick_color = color
        self.sw = stroke_width

        # Coordinate references (origin at Hips/Root)
        self.hip_pos = ORIGIN
        self.torso_len = 1.5 * scale_factor
        self.shoulder_pos = self.hip_pos + UP * self.torso_len
        self.head_radius = 0.4 * scale_factor
        self.limb_len = 1.0 * scale_factor

        # Head
        self.head = Circle(
            radius=self.head_radius,
            color=self.stick_color,
            stroke_width=self.sw,
            fill_color=BLACK,
            fill_opacity=1
        ).move_to(self.shoulder_pos + UP * (self.head_radius + 0.15))

        # Face Elements
        left_eye = Dot(self.head.get_center() + LEFT * 0.15 + UP * 0.05, radius=0.04, color=self.stick_color)
        right_eye = Dot(self.head.get_center() + RIGHT * 0.15 + UP * 0.05, radius=0.04, color=self.stick_color)
        mouth = Line(
            self.head.get_center() + LEFT * 0.1 + DOWN * 0.15,
            self.head.get_center() + RIGHT * 0.1 + DOWN * 0.15,
            stroke_width=self.sw * 0.6,
            color=self.stick_color
        )
        self.face = VGroup(left_eye, right_eye, mouth)

        # Torso
        self.torso = Line(
            self.hip_pos,
            self.shoulder_pos,
            color=self.stick_color,
            stroke_width=self.sw
        )

        # Arms (Upper & Lower)
        self.left_arm = Line(
            self.shoulder_pos,
            self.shoulder_pos + DL * self.limb_len,
            color=self.stick_color,
            stroke_width=self.sw
        )
        self.right_arm = Line(
            self.shoulder_pos,
            self.shoulder_pos + DR * self.limb_len,
            color=self.stick_color,
            stroke_width=self.sw
        )

        # Legs
        self.left_leg = Line(
            self.hip_pos,
            self.hip_pos + DOWN * self.limb_len + LEFT * 0.4,
            color=self.stick_color,
            stroke_width=self.sw
        )
        self.right_leg = Line(
            self.hip_pos,
            self.hip_pos + DOWN * self.limb_len + RIGHT * 0.4,
            color=self.stick_color,
            stroke_width=self.sw
        )

        self.add(
            self.torso,
            self.left_leg,
            self.right_leg,
            self.left_arm,
            self.right_arm,
            self.head,
            self.face
        )

    def point_at(self, target_point):
        """Points right arm towards target coordinates."""
        dir_vector = normalize(target_point - self.shoulder_pos)
        new_right_arm = Line(
            self.shoulder_pos,
            self.shoulder_pos + dir_vector * self.limb_len,
            color=self.stick_color,
            stroke_width=self.sw
        )
        return Transform(self.right_arm, new_right_arm)

    def wave_gesture(self):
        """Waving right arm greeting animation."""
        up_arm = Line(
            self.shoulder_pos,
            self.shoulder_pos + UR * self.limb_len,
            color=self.stick_color,
            stroke_width=self.sw
        )
        wave_left = Line(
            self.shoulder_pos,
            self.shoulder_pos + UP * self.limb_len + RIGHT * 0.3,
            color=self.stick_color,
            stroke_width=self.sw
        )
        return Succession(
            Transform(self.right_arm, up_arm),
            Transform(self.right_arm, wave_left),
            Transform(self.right_arm, up_arm)
        )


class StickmanExplainerScene(Scene):
    def construct(self):
        # Background
        self.camera.background_color = "#0D0E15"

        # Initialize Stickman
        char = Stickman(color="#00FFAA", scale_factor=0.9).shift(LEFT * 3 + DOWN * 0.5)

        title = Text("Штучний Інтелект пояснює:", font_size=36, color=WHITE).to_edge(UP)
        formula = MathTex(r"E = mc^2", font_size=54, color=YELLOW).shift(RIGHT * 2 + UP * 0.5)

        # Entrance
        self.play(Write(title))
        self.play(FadeIn(char, shift=RIGHT * 1.5))
        self.wait(0.5)

        # Stickman waves greeting
        self.play(char.wave_gesture(), run_time=1.2)
        self.wait(0.3)

        # Point at the formula
        self.play(Write(formula), char.point_at(formula.get_left()))
        self.wait(1.5)

        # Stickman jumps with joy
        self.play(char.animate.shift(UP * 0.8), run_time=0.3, rate_func=ease_out_quad)
        self.play(char.animate.shift(DOWN * 0.8), run_time=0.3, rate_func=ease_in_quad)
        self.wait(1)
