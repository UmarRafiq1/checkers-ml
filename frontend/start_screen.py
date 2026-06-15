import tkinter as tk
from frontend.config import root
from frontend.gui import CheckersGUI

game = CheckersGUI()


def start():
    root.geometry("600x600")
    root.title("Checkers by Umar Rafiq")

    for widget in root.winfo_children():
        widget.destroy()

    center_frame = tk.Frame(root)
    center_frame.pack(expand=True)

    tk.Label(center_frame, text="Checkers", font=("Arial", 28, "bold")).pack(pady=20)

    tk.Button(center_frame, text="1 v 1", width=20, font=("Arial", 12),
              command=lambda: game.start_game(is_ai_v_ai=False, is_player_v_ai=False)
              ).pack(pady=8)

    tk.Button(center_frame, text="Play Against AI", width=20, font=("Arial", 12),
              command=lambda: game.start_game(is_ai_v_ai=False, is_player_v_ai=True)
              ).pack(pady=8)

    tk.Button(center_frame, text="AI vs AI", width=20, font=("Arial", 12),
              command=lambda: game.start_game(is_ai_v_ai=True, is_player_v_ai=False)
              ).pack(pady=8)

    root.mainloop()
