"""Concrete word-count walkthrough of MapReduce."""

from manim import *


def pill(text: str, color=BLUE, font_size=20) -> VGroup:
    label = Text(text, font_size=font_size)
    bg = RoundedRectangle(
        corner_radius=0.12,
        width=max(label.width + 0.35, 1.2),
        height=label.height + 0.25,
        color=color,
        fill_color=BLACK,
        fill_opacity=0.85,
    )
    label.move_to(bg.get_center())
    return VGroup(bg, label)


def kv(key: str, val: str, color=BLUE_B) -> VGroup:
    return pill(f"({key}, {val})", color=color, font_size=18)


def file_card(name: str, contents: str) -> VGroup:
    return VGroup(
        pill(name, color=GOLD_D, font_size=18),
        Text(contents, font_size=22),
    ).arrange(DOWN, buff=0.2)


class MapReduceFlow(Scene):
    def construct(self):
        title = Text("MapReduce: word count", font_size=36, weight=BOLD)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title))
        self.wait(0.25)

        # 1. Inputs
        step = Text("1. Input files", font_size=24, color=YELLOW_B)
        step.next_to(title, DOWN, buff=0.35)
        self.play(Write(step))

        file_a = file_card("pg-a.txt", '"hello world"')
        file_b = file_card("pg-b.txt", '"hello map"')
        files = VGroup(file_a, file_b).arrange(RIGHT, buff=1.6)
        files.next_to(step, DOWN, buff=0.55)
        self.play(LaggedStart(FadeIn(file_a, shift=UP * 0.1), FadeIn(file_b, shift=UP * 0.1), lag_ratio=0.2))
        self.wait(0.7)

        # 2. Map
        self.play(
            Transform(
                step,
                Text("2. Map each file  →  emit (word, 1)", font_size=24, color=YELLOW_B).move_to(step),
            )
        )

        pair_hello_a = kv("hello", "1")
        pair_world = kv("world", "1")
        pair_hello_b = kv("hello", "1", BLUE_C)
        pair_map = kv("map", "1", BLUE_C)
        map_a = VGroup(pair_hello_a, pair_world).arrange(DOWN, buff=0.2)
        map_b = VGroup(pair_hello_b, pair_map).arrange(DOWN, buff=0.2)
        map_a.next_to(file_a, DOWN, buff=0.55)
        map_b.next_to(file_b, DOWN, buff=0.55)

        self.play(
            GrowArrow(Arrow(file_a.get_bottom(), map_a.get_top(), buff=0.1, stroke_width=2, color=TEAL_D)),
            GrowArrow(Arrow(file_b.get_bottom(), map_b.get_top(), buff=0.1, stroke_width=2, color=TEAL_D)),
        )
        self.play(
            LaggedStart(FadeIn(pair_hello_a, scale=0.9), FadeIn(pair_world, scale=0.9), lag_ratio=0.15),
            LaggedStart(FadeIn(pair_hello_b, scale=0.9), FadeIn(pair_map, scale=0.9), lag_ratio=0.15),
        )
        map_fn = Text('Map: "hello world" → (hello,1), (world,1)', font_size=18, color=GRAY_A)
        map_fn.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(map_fn))
        self.wait(1.0)

        # Clear for partition — keep the four pairs
        self.play(
            FadeOut(title),
            FadeOut(files),
            FadeOut(map_fn),
            *[FadeOut(m) for m in self.mobjects if isinstance(m, Arrow)],
            step.animate.to_edge(UP, buff=0.35),
            pair_hello_a.animate.move_to(LEFT * 3.3 + UP * 1.3),
            pair_world.animate.move_to(LEFT * 1.1 + UP * 1.3),
            pair_hello_b.animate.move_to(RIGHT * 1.1 + UP * 1.3),
            pair_map.animate.move_to(RIGHT * 3.3 + UP * 1.3),
        )

        # 3. Partition
        self.play(
            Transform(
                step,
                Text("3. Partition: ihash(key) % 2", font_size=24, color=YELLOW_B).to_edge(UP, buff=0.35),
            )
        )
        hint = Text("same key → same reduce bucket", font_size=18, color=GRAY_A)
        hint.next_to(step, DOWN, buff=0.25)
        self.play(FadeIn(hint))

        b0_label = Text("bucket 0  →  mr-*-0.json", font_size=18, color=PURPLE_B)
        b1_label = Text("bucket 1  →  mr-*-1.json", font_size=18, color=PURPLE_B)
        b0_box = RoundedRectangle(width=3.6, height=2.2, color=PURPLE_B, corner_radius=0.15)
        b1_box = RoundedRectangle(width=3.6, height=2.2, color=PURPLE_B, corner_radius=0.15)
        b0 = VGroup(b0_label, b0_box).arrange(DOWN, buff=0.15).move_to(LEFT * 2.4 + DOWN * 1.1)
        b1 = VGroup(b1_label, b1_box).arrange(DOWN, buff=0.15).move_to(RIGHT * 2.4 + DOWN * 1.1)
        self.play(FadeIn(b0), FadeIn(b1))

        t0a = b0_box.get_center() + UP * 0.35
        t0b = b0_box.get_center() + DOWN * 0.35
        t1a = b1_box.get_center() + UP * 0.35
        t1b = b1_box.get_center() + DOWN * 0.35
        self.play(
            pair_hello_a.animate.move_to(t0a),
            pair_hello_b.animate.move_to(t0b),
            pair_world.animate.move_to(t1a),
            pair_map.animate.move_to(t1b),
            run_time=1.3,
        )
        self.wait(0.9)

        # 4. Reduce
        self.play(
            FadeOut(hint),
            FadeOut(b0),
            FadeOut(b1),
            FadeOut(pair_hello_a),
            FadeOut(pair_hello_b),
            FadeOut(pair_world),
            FadeOut(pair_map),
            Transform(
                step,
                Text("4. Reduce: group by key, then reducef", font_size=24, color=YELLOW_B).to_edge(UP, buff=0.35),
            ),
        )

        left = VGroup(
            Text("Reduce 0", font_size=22, color=ORANGE),
            Text("hello → [1, 1]", font_size=24),
            Text("↓ sum", font_size=18, color=GRAY_B),
            pill("hello 2", color=GREEN, font_size=24),
            Text("mr-out-0", font_size=18, color=GREEN_B),
        ).arrange(DOWN, buff=0.25)

        right = VGroup(
            Text("Reduce 1", font_size=22, color=ORANGE),
            Text("world → [1]", font_size=24),
            Text("map → [1]", font_size=24),
            Text("↓ identity counts", font_size=18, color=GRAY_B),
            pill("world 1", color=GREEN, font_size=22),
            pill("map 1", color=GREEN, font_size=22),
            Text("mr-out-1", font_size=18, color=GREEN_B),
        ).arrange(DOWN, buff=0.18)

        cols = VGroup(left, right).arrange(RIGHT, buff=2.2)
        cols.next_to(step, DOWN, buff=0.55)

        # Reveal step-by-step per column
        self.play(FadeIn(left[0]), FadeIn(right[0]))
        self.play(FadeIn(left[1]), FadeIn(right[1]), FadeIn(right[2]))
        self.wait(0.4)
        self.play(FadeIn(left[2]), FadeIn(right[3]))
        self.play(FadeIn(left[3]), FadeIn(right[4]), FadeIn(right[5]))
        self.play(FadeIn(left[4]), FadeIn(right[6]))
        self.wait(0.5)

        reduce_note = Text('reducef("hello", ["1","1"]) → "2"', font_size=20, color=GRAY_A)
        reduce_note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(reduce_note))
        self.wait(1.2)

        # 5. Done
        self.play(
            FadeOut(cols),
            FadeOut(reduce_note),
            Transform(
                step,
                Text("5. Final merged view", font_size=24, color=YELLOW_B).to_edge(UP, buff=0.35),
            ),
        )
        final = VGroup(
            Text("hello 2", font_size=28),
            Text("map 1", font_size=28),
            Text("world 1", font_size=28),
        ).arrange(DOWN, buff=0.3)
        final.next_to(step, DOWN, buff=0.8)
        caption = Text("workers · coordinator · retries — same flow at scale", font_size=18, color=GRAY_A)
        caption.to_edge(DOWN, buff=0.4)
        self.play(LaggedStart(*[FadeIn(line, shift=UP * 0.1) for line in final], lag_ratio=0.2))
        self.play(FadeIn(caption))
        self.wait(1.6)

        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.15)
