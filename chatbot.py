import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading, time
import sys

COLORS = {
    "window_bg": "#121212",
    "panel_bg":  "#121212",
    "bar_bg":    "#1a1a1a",
    "bar_border":"#2a2a2a",
    "title":     "#ffffff",
    "muted":     "#B3B3B3",

    "bot_bg":    "#1e293b",
    "bot_fg":    "#e6edf3",
    "err_bg":    "#2a1414",
    "err_fg":    "#ffb4b4",
    "err_border":"#5a2a2a",

    "user_bg":   "#2563EB",
    "user_fg":   "#ffffff",

    "entry_bg":  "#0d0d0d",
    "entry_fg":  "#ffffff",
    "hint_fg":   "#9aa0a6",

    "btn_bg":    "#2a2a2a",
    "btn_bg_hover":"#3a3a3a",
    "btn_fg":    "#ffffff",
    "send_bg":   "#2563EB",
    "send_fg":   "#ffffff",
}

FONT = ("Segoe UI", 11)
SMALL = ("Segoe UI", 9)

def fetch_bot_reply(text: str) -> str:
    """Simulate a network call; replace with a real API call."""
    time.sleep(1.2)
    return f"Thanks! This is a simulated reply to: “{text}”"

def format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")

def bind_mousewheel(widget, command):
    # Windows / Mac / Linux mousewheel support
    widget.bind("<Enter>", lambda e: widget.focus_set())
    widget.bind("<MouseWheel>", lambda e: command(-1 * int(e.delta / 120)))  # Win/Mac
    widget.bind("<Button-4>",   lambda e: command(-1))                       # Linux up
    widget.bind("<Button-5>",   lambda e: command(1))                        # Linux down

class TypingIndicator(tk.Label):
    def __init__(self, master):
        super().__init__(master, bg=COLORS["bot_bg"], fg=COLORS["hint_fg"],
                         font=("Segoe UI", 10), padx=12, pady=6, text="typing")
        self._running = False
        self._i = 0
        self._frames = ["typing", "typing.", "typing..", "typing..."]

    def start(self):
        self._running = True
        self._tick()

    def stop(self):
        self._running = False

    def _tick(self):
        if not self._running:
            return
        self.config(text=self._frames[self._i % len(self._frames)])
        self._i += 1
        self.after(300, self._tick)

class Bubble(tk.Frame):
    """Chat bubble with timestamp. type='user'|'bot'|'error'."""
    def __init__(self, master, text: str, mtype: str, ts: datetime):
        super().__init__(master, bg=master["bg"])
        is_user = (mtype == "user")
        is_error = (mtype == "error")

        if is_user:
            bg = COLORS["user_bg"]; fg = COLORS["user_fg"]; side = "e"
        elif is_error:
            bg = COLORS["err_bg"];  fg = COLORS["err_fg"];  side = "w"
        else:
            bg = COLORS["bot_bg"];  fg = COLORS["bot_fg"];  side = "w"

        outer = tk.Frame(self, bg=master["bg"])
        outer.pack(fill="x", pady=3)
        inner = tk.Frame(outer, bg=bg, bd=0, highlightthickness=0)
        inner.pack(anchor=side, padx=10)

        label = tk.Label(inner, text=text, bg=bg, fg=fg, font=FONT,
                         wraplength=520, justify="left", padx=12, pady=8)
        label.pack(anchor="w")

        time_lbl = tk.Label(inner, text=format_time(ts),
                            bg=bg, fg=COLORS["muted"], font=("Segoe UI", 8))
        time_lbl.pack(anchor="e", padx=6, pady=(2, 4))

        def tint(hex_color, factor=1.06):
            c = hex_color.lstrip("#")
            r,g,b = int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
            r = max(0, min(int(r*factor), 255))
            g = max(0, min(int(g*factor), 255))
            b = max(0, min(int(b*factor), 255))
            return f"#{r:02x}{g:02x}{b:02x}"

        inner.bind("<Enter>", lambda e, b=bg: inner.config(bg=tint(b)))
        inner.bind("<Leave>", lambda e, b=bg: inner.config(bg=b))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UNIGUIDE — Dark (Python)")

        self.geometry("960x720")
        self.configure(bg=COLORS["window_bg"])
        self.minsize(720, 520)
        self.resizable(True, True)
        try:        # Start maximized on Windows
            self.state('zoomed')
        except Exception:
            pass

        self.bind('<F11>', lambda e: self.attributes(
            '-fullscreen', not self.attributes('-fullscreen')))
        self.bind('<Alt-Return>', lambda e: self.state('zoomed'))

        header = tk.Frame(self, bg=COLORS["bar_bg"], bd=0, highlightthickness=0)
        header.pack(fill="x")
        title = tk.Label(header, text="Course Chatbot", bg=COLORS["bar_bg"],
                         fg=COLORS["title"], font=("Segoe UI Semibold", 14))
        title.pack(side="left", padx=12, pady=10)
        sub = tk.Label(header, text="Ask about courses, assignments, schedule",
                       bg=COLORS["bar_bg"], fg=COLORS["muted"], font=("Segoe UI", 9))
        sub.pack(side="left", pady=10)

        bar = tk.Frame(self, bg=COLORS["bar_bg"],
                       highlightbackground=COLORS["bar_border"],
                       highlightcolor=COLORS["bar_border"], highlightthickness=1)
        bar.pack(fill="x")
        self.state_lbl = tk.Label(bar, text="Current: normal", bg=COLORS["bar_bg"],
                                  fg=COLORS["muted"], font=("Segoe UI", 9))
        self.state_lbl.pack(side="right", padx=8, pady=6)

        def mk_btn(text, cmd):
            b = tk.Button(bar, text=text, command=cmd, font=("Segoe UI", 9),
                          bg=COLORS["btn_bg"], fg=COLORS["btn_fg"], bd=0,
                          padx=10, pady=4, activebackground=COLORS["btn_bg_hover"])
            b.pack(side="left", padx=6, pady=6)
            return b

        mk_btn("Normal State", self.reset_normal)
        mk_btn("Empty State", self.set_empty)
        mk_btn("Error State", self.set_error)

        middle = tk.Frame(self, bg=COLORS["panel_bg"])
        middle.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(middle, bg=COLORS["panel_bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(middle, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.stream = tk.Frame(self.canvas, bg=COLORS["panel_bg"])
        self.win_id = self.canvas.create_window((0, 0), window=self.stream, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.stream.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        middle.bind("<Configure>", lambda e: self.canvas.itemconfig(
            self.win_id, width=e.width))

        bind_mousewheel(self.canvas, lambda d: self.canvas.yview_scroll(d, "units"))

        self.typing_holder = tk.Frame(self.stream, bg=COLORS["panel_bg"])
        self.typing = TypingIndicator(self.typing_holder)

        bottom = tk.Frame(self, bg=COLORS["bar_bg"])
        bottom.pack(fill="x")
        self.entry = tk.Entry(bottom, bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
                              insertbackground=COLORS["entry_fg"], relief="flat",
                              font=FONT)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(10, 8), pady=10, ipady=8)
        self.entry.focus_set()
        self.send_btn = tk.Button(bottom, text="Send ▶", command=self.on_send,
                                  font=("Segoe UI", 10, "bold"), bg=COLORS["send_bg"],
                                  fg=COLORS["send_fg"], bd=0, padx=14, pady=8,
                                  activebackground="#1d4ed8")
        self.send_btn.grid(row=0, column=1, padx=(0, 10), pady=10)
        bottom.grid_columnconfigure(0, weight=1)

        self.entry.bind("<Return>", self.on_send)
        self.entry.bind("<Control-Return>", self.on_send)
        self.bind("<Escape>", lambda e: self.entry.delete(0, "end"))

        self.current_state = "normal"   # normal | empty | typing | error
        now = datetime.now()
        self._seed_messages([
            ("bot",  "Hi! I'm your Course Chatbot. Ask me anything about your courses, assignments, or schedule.", now - timedelta(minutes=5)),
            ("user", "What courses am I enrolled in this semester?",                                               now - timedelta(minutes=4)),
            ("bot",  "Based on your enrollment: Web Dev Fundamentals, Database Design, UX Design. Want details?",  now - timedelta(minutes=3)),
            ("user", "Tell me about Web Development Fundamentals",                                                 now - timedelta(minutes=2)),
        ])

    def _add_bubble(self, text: str, mtype: str):
        ts = datetime.now()
        Bubble(self.stream, text, mtype, ts).pack(fill="x")
        self.canvas.after(10, lambda: self.canvas.yview_moveto(1.0))

    def _seed_messages(self, items):
        for mtype, text, ts in items:
            Bubble(self.stream, text, mtype, ts).pack(fill="x")
        self.canvas.after(0, lambda: self.canvas.yview_moveto(1.0))

    def _set_state(self, s: str):
        self.current_state = s
        self.state_lbl.config(text=f"Current: {s}")

    def reset_normal(self):
        self.clear_stream()
        self._set_state("normal")
        self._seed_messages([
            ("bot",  "Hi! I'm your Course Chatbot. Ask me anything about your courses, assignments, or schedule.", datetime.now()),
        ])

    def set_empty(self):
        self.clear_stream()
        self._set_state("empty")
        tk.Label(self.stream, text="Start a conversation…",
                 bg=COLORS["panel_bg"], fg=COLORS["hint_fg"],
                 font=("Segoe UI", 11)).pack(pady=18)

    def set_error(self):
        self._set_state("error")
        self._add_bubble("Sorry, I couldn’t fetch that information right now. Please try again later.", "error")

    def clear_stream(self):
        for w in list(self.stream.children.values()):
            w.destroy()
        self.canvas.yview_moveto(0.0)

    def on_send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            messagebox.showerror("Input", "Please type a message first.")
            return
        if self.current_state == "typing":
            return

        self.entry.delete(0, "end")
        self._add_bubble(text, "user")
        self._set_state("typing")

        self.typing_holder.pack(fill="x", anchor="w")
        self.typing.pack(anchor="w", padx=10, pady=(2, 8))
        self.typing.start()

        threading.Thread(target=self._fetch_thread, args=(text,), daemon=True).start()

    def _fetch_thread(self, user_text: str):
        try:
            reply = fetch_bot_reply(user_text)
        except Exception as e:
            reply = f"Sorry, something went wrong: {e}"
            nxt = ("error", reply)
        else:
            nxt = ("bot", reply)
        self.after(60, lambda: self._finish_reply(*nxt))

    def _finish_reply(self, mtype: str, text: str):
        self.typing.stop()
        self.typing_holder.pack_forget()
        self._add_bubble(text, mtype)
        self._set_state("normal" if mtype != "error" else "error")

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print("Fatal error:", e, file=sys.stderr)
        raise
