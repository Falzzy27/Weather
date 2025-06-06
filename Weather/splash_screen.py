import tkinter as tk
import itertools

class SplashScreen(tk.Toplevel):
    def __init__(self, parent, bg="white", fg="black"):
        super().__init__(parent)
        self.geometry("300x100+800+500")
        self.overrideredirect(True)
        self.configure(bg=bg)
        
        self.label = tk.Label(self, 
                            text="Подождите, программа запускается",
                            font=('Arial', 12),
                            bg=bg,
                            fg=fg)
        self.label.pack(expand=True)
        
        self.dots = itertools.cycle(["", ".", "..", "..."])
        self.animate()
    
    def animate(self):
        current_text = self.label.cget("text").rstrip(".")
        self.label.config(text=current_text + next(self.dots))
        self.after(500, self.animate) 