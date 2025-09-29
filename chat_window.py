import tkinter as tk
from tkinter import messagebox, scrolledtext
# === Placeholder function for backend/API call ===
def fetch_bot_reply(user_message):
    # Replace this with your API call for real data!
    return "Bot reply: " + user_message
class ChatBubble(tk.Frame):
    def __init__(self, master, text, sender="user", **kwargs):
        bg_color = "#EFF7FF" if sender == "user" else "#DEEFFF"
        fg_color = "#17294D" if sender == "user" else "#1B364C"
        icon = "🧑" if sender == "user" else "🤖"
        anchor = 'e' if sender == "user" else 'w'
        super().__init__(master, bg=master["bg"], pady=2)
        label = tk.Label(self, text=f"{icon} {text}", font=("Segoe UI", 11),
                         bg=bg_color, fg=fg_color, padx=12, pady=5,
                         bd=0, relief=tk.FLAT, wraplength=410, justify="left")
        label.pack(side=tk.RIGHT if sender == "user" else tk.LEFT, anchor=anchor)
        label.config(borderwidth=0)
        self.pack(fill=tk.X, anchor=anchor, pady=2)
class ChatBotUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BU ChatBot - UNIGUIDE")
        self.geometry("530x550")
        self.configure(bg="#F6FAFC")
        self.resizable(False, False)
        # --- Deep Blue Title Bar ---
        title_frame = tk.Frame(self, bg="#16509B")
        title_label = tk.Label(title_frame, text="BU ChatBot", font=("Segoe UI", 18, "bold"),
                              fg="white", bg="#16509B", padx=12, pady=10)
        title_label.pack()
        title_frame.pack(fill=tk.X)
        # --- Chat Area: Bubbles, Scrollable ---
        self.chat_area_frame = tk.Frame(self, bg="#F6FAFC")
        self.chat_area_frame.pack(fill=tk.BOTH, expand=True, padx=0)
        self.chat_canvas = tk.Canvas(self.chat_area_frame, bg="#F6FAFC", highlightthickness=0)
        self.chat_scrollbar = tk.Scrollbar(self.chat_area_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_bubbles = tk.Frame(self.chat_canvas, bg="#F6FAFC")
        self.chat_bubbles.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.create_window((2,2), window=self.chat_bubbles, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # First system bubble
        self.add_bubble("👋 Welcome to BU ChatBot! Type your message below.", "bot")
        # --- Input Box + Gradient Send Button ---
        input_frame = tk.Frame(self, bg="#F6FAFC")
        input_frame.pack(fill=tk.X, pady=(4,8), padx=18)
        self.user_input = tk.Entry(input_frame, font=("Segoe UI", 12), bg="#E0ECFB", fg="#18345A", width=38,
                                  relief=tk.FLAT, insertbackground="#18345A", borderwidth=0)
        self.user_input.pack(side=tk.LEFT, ipady=6, ipadx=4)
        self.user_input.bind('<Return>', self.on_send)
        self.send_button = tk.Button(input_frame, text="Send", command=self.on_send,
                                    font=("Segoe UI", 11, "bold"), bg="#3D8AF7", fg="white", relief=tk.RAISED,
                                    bd=0, activebackground="#2169C4", activeforeground="white",
                                    padx=18, pady=6, cursor="hand2")
        self.send_button.pack(side=tk.LEFT, padx=10)
        self.user_input.focus_set()
        # --- Menu Bar ---
        menubar = tk.Menu(self)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=lambda: messagebox.showinfo("About",
              "BU ChatBot MVP\nDeveloped by Group 1 for Boston University\n2025."))
        helpmenu.add_command(label="Help", command=lambda: messagebox.showinfo("Help",
              "Type your course or campus question and press Send.\nChat history, bubbles, and real API integration!"))
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=menubar)
    def add_bubble(self, message, sender):
        ChatBubble(self.chat_bubbles, text=message, sender=sender)
        self.chat_canvas.yview_moveto(1.0) # Scroll to bottom
    def on_send(self, event=None):
        message = self.user_input.get().strip()
        if not message:
            messagebox.showerror("Input Error", "Please enter a message before sending.")
            return
        self.add_bubble(message, "user")
        self.user_input.delete(0, tk.END)
        # --- API/Backend call (modular) ---
        bot_reply = fetch_bot_reply(message)
        self.after(200, lambda: self.add_bubble(bot_reply, "bot"))
if __name__ == "__main__":
    app = ChatBotUI()
    app.mainloop()
