"""Concrete walkthrough of kvsrv1: versioned Put and ErrMaybe."""

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


def store_box(content: str, title: str = "server map") -> VGroup:
    header = Text(title, font_size=18, color=PURPLE_B)
    body = pill(content, color=PURPLE_B, font_size=22)
    box = RoundedRectangle(
        width=max(body.width + 0.8, 4.2),
        height=2.0,
        color=PURPLE_B,
        corner_radius=0.15,
    )
    body.move_to(box.get_center())
    header.next_to(box, UP, buff=0.15)
    return VGroup(header, box, body)


class KVServerFlow(Scene):
    def construct(self):
        title = Text("KV server: versioned Put", font_size=36, weight=BOLD)
        title.to_edge(UP, buff=0.3)
        self.play(FadeIn(title))
        self.wait(0.25)

        # 1. Create key with version 0
        step = Text("1. Put(key, value, version=0) creates", font_size=24, color=YELLOW_B)
        step.next_to(title, DOWN, buff=0.35)
        self.play(Write(step))

        client = pill("Clerk", color=TEAL_D, font_size=22)
        client.move_to(LEFT * 4.2 + DOWN * 0.2)
        call = Text('Put("x", "a", 0)', font_size=22, color=GRAY_A)
        call.next_to(client, DOWN, buff=0.35)

        empty = store_box("{ }")
        empty.move_to(RIGHT * 2.6 + DOWN * 0.1)

        self.play(FadeIn(client), FadeIn(empty))
        self.play(FadeIn(call))
        arrow = Arrow(call.get_right(), empty.get_left(), buff=0.2, stroke_width=2, color=TEAL_D)
        self.play(GrowArrow(arrow))

        filled = store_box('x → ("a", v=1)')
        filled.move_to(empty.get_center())
        ok = pill("OK", color=GREEN, font_size=22)
        ok.next_to(client, UP, buff=0.35)
        self.play(Transform(empty, filled), FadeIn(ok, shift=LEFT * 0.1))
        self.wait(0.9)

        # 2. Conditional put
        self.play(
            FadeOut(title),
            FadeOut(call),
            FadeOut(arrow),
            FadeOut(ok),
            Transform(
                step,
                Text("2. Put only if version matches", font_size=24, color=YELLOW_B).to_edge(UP, buff=0.35),
            ),
            client.animate.move_to(LEFT * 4.2 + UP * 0.3),
            empty.animate.move_to(RIGHT * 2.6 + UP * 0.2),
        )

        good = Text('Put("x", "b", 1)  →  OK', font_size=22, color=GREEN_B)
        bad = Text('Put("x", "c", 0)  →  ErrVersion', font_size=22, color=RED_B)
        checks = VGroup(good, bad).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        checks.next_to(client, DOWN, buff=0.55).align_to(client, LEFT)
        self.play(FadeIn(good))

        updated = store_box('x → ("b", v=2)')
        updated.move_to(empty.get_center())
        self.play(Transform(empty, updated))
        self.wait(0.4)
        self.play(FadeIn(bad))
        note = Text("version is a compare-and-swap token", font_size=18, color=GRAY_A)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note))
        self.wait(1.0)

        # 3. Dropped reply
        self.play(
            FadeOut(checks),
            FadeOut(note),
            FadeOut(client),
            FadeOut(empty),
            Transform(
                step,
                Text("3. Reply dropped on the wire", font_size=24, color=YELLOW_B).to_edge(UP, buff=0.35),
            ),
        )

        clerk = pill("Clerk", color=TEAL_D, font_size=20).move_to(LEFT * 4.5 + UP * 0.6)
        server = store_box('x → ("b", v=2)', title="KVServer").move_to(RIGHT * 2.8 + UP * 0.4)
        req = Text('Put("x", "d", 2)', font_size=20, color=GRAY_A)
        req.next_to(clerk, DOWN, buff=0.4)
        self.play(FadeIn(clerk), FadeIn(server), FadeIn(req))

        wire = Arrow(req.get_right(), server.get_left() + DOWN * 0.2, buff=0.15, stroke_width=2, color=TEAL_D)
        self.play(GrowArrow(wire))
        applied = store_box('x → ("d", v=3)', title="KVServer")
        applied.move_to(server.get_center())
        self.play(Transform(server, applied))

        reply = pill("OK", color=GREEN, font_size=20)
        reply.move_to(ORIGIN + UP * 0.15)
        self.play(FadeIn(reply, shift=LEFT * 0.4))
        lost = Text("✕ reply lost", font_size=22, color=RED_B)
        lost.next_to(reply, DOWN, buff=0.25)
        self.play(FadeIn(lost), reply.animate.set_opacity(0.25))
        self.wait(0.8)

        # 4. Retry → ErrMaybe
        self.play(
            FadeOut(wire),
            FadeOut(reply),
            FadeOut(lost),
            FadeOut(req),
            Transform(
                step,
                Text("4. Clerk retries → ambiguous ErrVersion", font_size=24, color=YELLOW_B).to_edge(
                    UP, buff=0.35
                ),
            ),
        )

        retry = Text('retry Put("x", "d", 2)', font_size=20, color=GRAY_A)
        retry.next_to(clerk, DOWN, buff=0.4)
        self.play(FadeIn(retry))
        wire2 = Arrow(retry.get_right(), server.get_left() + DOWN * 0.2, buff=0.15, stroke_width=2, color=ORANGE)
        self.play(GrowArrow(wire2))

        err_ver = pill("ErrVersion", color=RED_B, font_size=20)
        err_ver.move_to(ORIGIN + UP * 0.1)
        self.play(FadeIn(err_ver, shift=LEFT * 0.3))

        maybe = pill("Clerk returns ErrMaybe", color=GOLD_D, font_size=22)
        maybe.next_to(clerk, DOWN, buff=1.2)
        why = Text("first RPC may have run; reply was lost", font_size=18, color=GRAY_A)
        why.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(maybe), FadeIn(why))
        self.wait(1.2)

        # 5. Lock uses the same CAS
        self.play(
            FadeOut(clerk),
            FadeOut(server),
            FadeOut(retry),
            FadeOut(wire2),
            FadeOut(err_ver),
            FadeOut(maybe),
            FadeOut(why),
            Transform(
                step,
                Text("5. Lock = CAS on a lock key", font_size=24, color=YELLOW_B).to_edge(UP, buff=0.35),
            ),
        )

        lock_steps = VGroup(
            Text("Acquire: Get(lock) → empty?", font_size=24),
            Text('         Put(lock, clientId, ver) == OK', font_size=24),
            Text("Release: Put(lock, \"\", ver) when we hold it", font_size=24),
            Text("ErrMaybe → re-Get; if value == us, we won", font_size=22, color=GOLD_D),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        lock_steps.next_to(step, DOWN, buff=0.7)
        self.play(LaggedStart(*[FadeIn(line, shift=UP * 0.08) for line in lock_steps], lag_ratio=0.25))

        caption = Text("at-most-once Put · linearizable Get/Put · lock on top", font_size=18, color=GRAY_A)
        caption.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(caption))
        self.wait(1.6)

        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.15)
