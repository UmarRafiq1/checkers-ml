# Checkers by Umar Rafiq

A Python checkers game with a self-improving AI opponent.

## Project Structure

```
checkers/
├── main.py                  # Entry point - run this
├── backend/                 # Pure game logic, no UI
│   ├── constants.py         # Board size, player IDs, colours
│   ├── helpers.py           # Move validation utility functions
│   ├── board.py             # Piece and Board classes
│   ├── ai.py                # Minimax algorithm and position analysis
│   └── simulator.py        # AI weight learning via linear regression
└── frontend/                # All tkinter UI code
    ├── config.py            # Tkinter root window
    ├── gui.py               # CheckersGUI class
    └── start_screen.py      # Home screen
```

## How to Run

```bash
python main.py
```

## Requirements

```bash
pip install numpy scikit-learn tabulate
```

## Game Modes

- **1 v 1** — Two human players on the same machine
- **Play Against AI** — Human vs minimax AI (choose difficulty depth)
- **AI vs AI** — Watch two AI opponents play each other

## Self-Improving AI

The AI uses minimax with alpha-beta pruning. Heuristic weights can be
optimised automatically using linear regression over simulated games.

To improve weights before playing, uncomment the lines in `main.py`.

## Rules

Standard checkers rules on an 8x8 board. Kings (crowns) can move
in all four diagonal directions. A draw is called after 40 moves
without a capture, or if both players repeat moves three times.
