import tkinter as tk
from tkinter import messagebox
import os, json, math
from reportlab.pdfgen import canvas

# File paths
FOLDER = "Patterns"
FILE = os.path.join(FOLDER, "patterns.json")
PDF = os.path.join(FOLDER, "saved_patterns.pdf")

# Ensure pattern folder exists
os.makedirs(FOLDER, exist_ok=True)

def load_patterns():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_patterns(patterns):
    with open(FILE, "w") as f:
        json.dump(patterns, f, indent=2)

class PatternApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pattern Lock")

        self.canvas = tk.Canvas(root, width=300, height=300, bg="white")
        self.canvas.pack()
        
        tk.Button(root, text="Reset Patterns", command=self.reset_patterns).pack(pady=5)
        tk.Button(root, text="Download Patterns as PDF", command=self.export_pdf).pack(pady=5)

        self.stored = load_patterns()
        self.selected, self.lines = [], []

        self.setup_grid()
        self.canvas.bind("<Button-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end)

    def setup_grid(self):
        self.nodes = []
        self.positions = {}
        idx = 1
        for i in range(3):
            for j in range(3):
                x, y = 50 + j * 100, 50 + i * 100
                node = self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="gray")
                self.nodes.append(node)
                self.positions[node] = (idx, x, y)
                idx += 1

    def start(self, e):
        self.selected.clear()
        self.canvas.delete("lines")
        self.add_node(e.x, e.y)

    def draw(self, e):
        if self.add_node(e.x, e.y) and len(self.selected) > 1:
            a, b = self.positions[self.selected[-2]][1:], self.positions[self.selected[-1]][1:]
            line = self.canvas.create_line(*a, *b, width=3, fill="black", tags="lines")
            self.lines.append(line)

    def add_node(self, x, y):
        for node in self.nodes:
            idx, cx, cy = self.positions[node]
            if math.hypot(x - cx, y - cy) <= 20 and node not in self.selected:
                self.selected.append(node)
                self.canvas.itemconfig(node, fill="blue")
                return True
        return False

    def end(self, e):
        if len(self.selected) >= 4:
            pattern = [self.positions[n][0] for n in self.selected]
            if pattern in self.stored:
                messagebox.showinfo("Info", "Pattern already exists!")
            else:
                self.stored.append(pattern)
                save_patterns(self.stored)
                messagebox.showinfo("Success", "New pattern saved!")
        else:
            messagebox.showwarning("Invalid", "Use at least 4 dots.")

        for node in self.nodes:
            self.canvas.itemconfig(node, fill="gray")
        self.canvas.delete("lines")

    def reset_patterns(self):
        if messagebox.askyesno("Confirm", "Delete all saved patterns?"):
            self.stored.clear()
            save_patterns(self.stored)
            messagebox.showinfo("Reset", "All patterns deleted.")

    def export_pdf(self):
        if not self.stored:
            messagebox.showwarning("No Patterns", "Nothing to export.")
            return

        c = canvas.Canvas(PDF, pagesize=(400, 600))
        c.setTitle("Saved Patterns")

        def draw_pattern(c, base_y, pattern):
            grid = {i: (60 + ((i - 1) % 3) * 60, base_y - ((i - 1) // 3) * 60) for i in range(1, 10)}
            for x, y in grid.values():
                c.circle(x, y, 6, fill=1)
            for i in range(len(pattern) - 1):
                x1, y1 = grid[pattern[i]]
                x2, y2 = grid[pattern[i + 1]]
                c.line(x1, y1, x2, y2)

        y = 550
        for i, pattern in enumerate(self.stored, 1):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(30, y + 10, f"Pattern {i}")
            draw_pattern(c, y, pattern)
            y -= 160
            if y < 100:
                c.showPage()
                y = 550

        c.save()
        messagebox.showinfo("PDF Saved", f"Saved to:\n{PDF}")

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = PatternApp(root)
    root.mainloop()
