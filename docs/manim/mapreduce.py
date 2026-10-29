"""MapReduce behind-the-scenes animation for the README."""

from manim import *


def box(label: str, color=BLUE, width=2.4, height=1.0) -> VGroup:
    rect = RoundedRectangle(corner_radius=0.15, width=width, height=height, color=color)
    text = Text(label, font_size=22)
    text.move_to(rect.get_center())
    return VGroup(rect, text)


class MapReduceFlow(Scene):
    def construct(self):
        title = Text("MapReduce", font_size=42, weight=BOLD)
        subtitle = Text("coordinator · workers · files", font_size=22, color=GRAY_B)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.2)
        header.to_edge(UP, buff=0.35)

        self.play(FadeIn(header, shift=DOWN * 0.2))
        self.wait(0.3)

        coord = box("Coordinator", color=GOLD_D, width=3.2, height=0.9)
        coord.next_to(header, DOWN, buff=0.55)

        workers = VGroup(
            box("Worker 0", color=TEAL_D),
            box("Worker 1", color=TEAL_D),
            box("Worker 2", color=TEAL_D),
        ).arrange(RIGHT, buff=0.45)
        workers.next_to(coord, DOWN, buff=1.1)

        self.play(FadeIn(coord, shift=UP * 0.15), LaggedStart(*[FadeIn(w, shift=UP * 0.1) for w in workers], lag_ratio=0.15))
        self.wait(0.2)

        phase = Text("MAP phase", font_size=26, color=YELLOW_B)
        phase.next_to(workers, DOWN, buff=0.55)
        self.play(Write(phase))

        # Request / assign map tasks
        arrows = VGroup()
        for w in workers:
            a = Arrow(w.get_top(), coord.get_bottom(), buff=0.12, stroke_width=2, color=GRAY_B)
            arrows.add(a)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1), run_time=0.8)
        assigns = Text("RequestTask → MAP(file)", font_size=20, color=GRAY_A)
        assigns.next_to(phase, DOWN, buff=0.25)
        self.play(FadeIn(assigns))
        self.wait(0.4)

        # Intermediate files appear
        intermediates = VGroup(
            Text("mr-0-0.json", font_size=16, color=BLUE_B),
            Text("mr-0-1.json", font_size=16, color=BLUE_B),
            Text("mr-1-0.json", font_size=16, color=BLUE_B),
            Text("mr-1-1.json", font_size=16, color=BLUE_B),
            Text("mr-2-0.json", font_size=16, color=BLUE_B),
            Text("mr-2-1.json", font_size=16, color=BLUE_B),
        ).arrange_in_grid(rows=2, cols=3, buff=(0.35, 0.2))
        intermediates.next_to(assigns, DOWN, buff=0.35)

        self.play(
            FadeOut(arrows),
            LaggedStart(*[FadeIn(f, scale=0.85) for f in intermediates], lag_ratio=0.08),
        )
        finish = Text("FinishTask  (timeout → retry)", font_size=18, color=GRAY_A)
        finish.next_to(intermediates, DOWN, buff=0.25)
        self.play(FadeIn(finish))
        self.wait(0.6)

        # Transition to reduce
        self.play(
            FadeOut(assigns),
            FadeOut(finish),
            Transform(phase, Text("REDUCE phase", font_size=26, color=ORANGE).move_to(phase)),
        )

        reduce_note = Text("RequestTask → REDUCE(Y)  ·  read mr-*-Y.json", font_size=18, color=GRAY_A)
        reduce_note.next_to(phase, DOWN, buff=0.25)
        self.play(FadeIn(reduce_note))

        outs = VGroup(
            Text("mr-out-0", font_size=20, color=GREEN_B),
            Text("mr-out-1", font_size=20, color=GREEN_B),
        ).arrange(RIGHT, buff=0.8)
        outs.next_to(intermediates, DOWN, buff=0.15)

        # Flow intermediates into outputs
        self.play(
            intermediates.animate.set_opacity(0.35).scale(0.92),
            LaggedStart(*[FadeIn(o, shift=UP * 0.15) for o in outs], lag_ratio=0.2),
        )
        self.wait(0.5)

        # Done
        self.play(
            FadeOut(reduce_note),
            FadeOut(intermediates),
            FadeOut(outs),
            Transform(phase, Text("DONE", font_size=28, color=GREEN).move_to(phase)),
        )
        done = Text("workers exit · coordinator Done()", font_size=20, color=GRAY_A)
        done.next_to(phase, DOWN, buff=0.3)
        self.play(FadeIn(done))
        self.wait(1.2)

        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.2)
