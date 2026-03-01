import json
import os
import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any

import requests
from PIL import Image, ImageTk

try:
    import vlc  # type: ignore
except Exception:
    vlc = None


GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID", "")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET", "")
GIGACHAT_MODEL = "GigaChat"

PROJECT_ROOT = Path(__file__).resolve().parent
AUDIO_EXT = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
VIDEO_EXT = {".mp4", ".avi", ".mkv", ".mov", ".webm"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
MEMORY_SYMBOLS = ["🍎", "🍌", "🍇", "🍒", "🍉", "🥝", "🍍", "🍓"]


class MultimediaHub(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Multimedia Hub")
        self.geometry("1240x860")
        self.minsize(1060, 740)

        self.player: Any = None
        self.current_audio_path: Path | None = None
        self.current_video_path: Path | None = None
        self.current_image_path: Path | None = None
        self.image_tk: ImageTk.PhotoImage | None = None
        self.vlc_ready = vlc is not None

        self.theme_var = tk.StringVar(value="Светлая")
        self.dark_mode = False

        # puzzle data
        self.board: list[int] = []
        self.board_buttons: list[tk.Button] = []

        self.memory_values: list[str] = []
        self.memory_buttons: list[tk.Button] = []
        self.memory_opened: list[int] = []
        self.memory_locked = False

        self.ttt_board = ["" for _ in range(9)]
        self.ttt_buttons: list[tk.Button] = []
        self.ttt_current = "X"
        self.ttt_human = "X"
        self.ttt_bot = "O"

        self._apply_theme("Светлая")
        self._build_ui()
        self._init_number_puzzle()
        self._init_memory_puzzle()
        self._init_ttt_puzzle()

        # обновление файлов только при запуске
        self.refresh_file_lists()

        if not self.vlc_ready:
            self.after(
                250,
                lambda: messagebox.showwarning(
                    "VLC не найден",
                    "Не удалось загрузить libVLC. Установите VLC Media Player для воспроизведения музыки.",
                ),
            )

    # -------------------------- STYLE ---------------------------------
    def _palette(self, theme_name: str) -> dict[str, str | bool]:
        palettes = {
            "Светлая": {"bg": "#eef2fb", "fg": "#1b1f2b", "accent": "#4a78d6", "text_bg": "#ffffff", "list_bg": "#ffffff", "canvas_bg": "#f5f8ff", "select_bg": "#a7c0fb", "dark": False},
            "Тёмная": {"bg": "#1f2330", "fg": "#f2f5ff", "accent": "#5d9bff", "text_bg": "#151925", "list_bg": "#222736", "canvas_bg": "#0f1320", "select_bg": "#4d77d0", "dark": True},
            "Фиолетовая": {"bg": "#f4edff", "fg": "#2b1d45", "accent": "#8b5cf6", "text_bg": "#ffffff", "list_bg": "#ffffff", "canvas_bg": "#f7f1ff", "select_bg": "#c8a9ff", "dark": False},
            "Зелёная": {"bg": "#ecf8f0", "fg": "#133122", "accent": "#2d9d62", "text_bg": "#ffffff", "list_bg": "#ffffff", "canvas_bg": "#f2fff6", "select_bg": "#9eddb7", "dark": False},
        }
        return palettes.get(theme_name, palettes["Светлая"])

    def _create_styles(self, palette: dict[str, str | bool]) -> None:
        bg = str(palette["bg"])
        fg = str(palette["fg"])
        accent = str(palette["accent"])

        self.configure(bg=bg)
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=bg, foreground=fg, font=("Segoe UI", 13, "bold"))
        style.configure("TButton", padding=7, font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("!disabled", accent)], foreground=[("!disabled", "white")])
        style.configure("TLabelframe", background=bg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg, font=("Segoe UI", 11, "bold"))
        style.configure("TNotebook", background=bg)
        style.configure("TNotebook.Tab", padding=(16, 10), font=("Segoe UI", 10, "bold"))

        self.dark_mode = bool(palette["dark"])

    def _apply_theme(self, theme_name: str) -> None:
        palette = self._palette(theme_name)
        self._create_styles(palette)

        text_bg = str(palette["text_bg"])
        text_fg = str(palette["fg"])
        list_bg = str(palette["list_bg"])
        select_bg = str(palette["select_bg"])
        canvas_bg = str(palette["canvas_bg"])

        if hasattr(self, "prompt_text") and hasattr(self, "answer_text"):
            for text_widget in [self.prompt_text, self.answer_text]:
                text_widget.configure(bg=text_bg, fg=text_fg, insertbackground=text_fg)

        if hasattr(self, "audio_listbox"):
            for lb in [self.audio_listbox, self.video_listbox, self.image_listbox]:
                lb.configure(bg=list_bg, fg=text_fg, selectbackground=select_bg, relief="flat", activestyle="none")

        if hasattr(self, "image_canvas"):
            self.image_canvas.configure(bg=canvas_bg)

    def toggle_theme(self) -> None:
        self._apply_theme(self.theme_var.get())

    # ---------------------------- UI ----------------------------------
    def _build_ui(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x", padx=14, pady=(12, 8))

        ttk.Label(top, text="Multimedia Hub", style="Header.TLabel").pack(side="left")
        ttk.Label(top, text="Тема:").pack(side="right", padx=(8, 4))

        theme_combo = ttk.Combobox(top, textvariable=self.theme_var, state="readonly", values=["Светлая", "Тёмная", "Фиолетовая", "Зелёная"], width=13)
        theme_combo.pack(side="right")
        theme_combo.bind("<<ComboboxSelected>>", lambda _e: self.toggle_theme())

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.music_tab = ttk.Frame(self.notebook)
        self.video_tab = ttk.Frame(self.notebook)
        self.image_tab = ttk.Frame(self.notebook)
        self.puzzle_tab = ttk.Frame(self.notebook)
        self.ai_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.music_tab, text="Музыка")
        self.notebook.add(self.video_tab, text="Видео")
        self.notebook.add(self.image_tab, text="Картинки")
        self.notebook.add(self.puzzle_tab, text="Головоломки")
        self.notebook.add(self.ai_tab, text="ИИ")

        self._build_music_tab()
        self._build_video_tab()
        self._build_image_tab()
        self._build_puzzle_tab()
        self._build_ai_tab()
        self._apply_theme(self.theme_var.get())

    # ---------------------- FILES -------------------------------------
    def _scan_project_files(self, exts: set[str]) -> list[Path]:
        files = []
        for path in PROJECT_ROOT.rglob("*"):
            if path.is_file() and path.suffix.lower() in exts:
                files.append(path)
        return sorted(files)

    def refresh_file_lists(self) -> None:
        self.audio_files = self._scan_project_files(AUDIO_EXT)
        self.video_files = self._scan_project_files(VIDEO_EXT)
        self.image_files = self._scan_project_files(IMAGE_EXT)

        self._fill_listbox(self.audio_listbox, self.audio_files)
        self._fill_listbox(self.video_listbox, self.video_files)
        self._fill_listbox(self.image_listbox, self.image_files)

    def _fill_listbox(self, listbox: tk.Listbox, files: list[Path]) -> None:
        listbox.delete(0, "end")
        for item in files:
            listbox.insert("end", str(item.relative_to(PROJECT_ROOT)))

    # ---------------------- MUSIC -------------------------------------
    def _build_music_tab(self) -> None:
        frame = ttk.LabelFrame(self.music_tab, text="Музыка")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        left = ttk.Frame(frame)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.audio_listbox = tk.Listbox(left, height=20, font=("Segoe UI", 10), relief="flat")
        self.audio_listbox.pack(fill="both", expand=True)
        self.audio_listbox.bind("<<ListboxSelect>>", lambda _e: self.select_audio())

        right = ttk.Frame(frame)
        right.pack(side="right", fill="y", padx=10, pady=10)

        self.music_label = tk.StringVar(value="Выберите аудио из списка")
        ttk.Label(right, textvariable=self.music_label, wraplength=300).pack(anchor="w", pady=(0, 10))
        ttk.Button(right, text="▶ Старт", style="Accent.TButton", command=self.play_media).pack(fill="x", pady=4)
        ttk.Button(right, text="⏸ Пауза", command=self.pause_media).pack(fill="x", pady=4)
        ttk.Button(right, text="⏹ Стоп", command=self.stop_media).pack(fill="x", pady=4)

        ttk.Label(right, text="Громкость").pack(anchor="w", pady=(14, 4))
        self.volume_scale = ttk.Scale(right, from_=0, to=100, value=70, command=self.on_volume_change)
        self.volume_scale.pack(fill="x")

        if not self.vlc_ready:
            self.music_label.set("VLC/libVLC не найдены — музыка недоступна")

    def select_audio(self) -> None:
        idx = self._selected_index(self.audio_listbox)
        if idx is None:
            return
        self.current_audio_path = self.audio_files[idx]
        self.music_label.set(f"Аудио: {self.current_audio_path.name}")
        self._prepare_media_player(self.current_audio_path)

    # ---------------------- VIDEO -------------------------------------
    def _build_video_tab(self) -> None:
        frame = ttk.LabelFrame(self.video_tab, text="Видео")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.video_listbox = tk.Listbox(frame, height=20, font=("Segoe UI", 10), relief="flat")
        self.video_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.video_listbox.bind("<<ListboxSelect>>", lambda _e: self.select_video())

        info = ttk.Frame(frame)
        info.pack(fill="x", padx=10, pady=(0, 10))
        self.video_label = tk.StringVar(value="Выберите видео")
        ttk.Label(info, textvariable=self.video_label, wraplength=900).pack(anchor="w")

    def select_video(self) -> None:
        idx = self._selected_index(self.video_listbox)
        if idx is None:
            return
        self.current_video_path = self.video_files[idx]
        size_mb = self.current_video_path.stat().st_size / (1024 * 1024)
        self.video_label.set(f"Видео: {self.current_video_path.name} | Размер: {size_mb:.2f} MB")

    # ---------------------- IMAGES ------------------------------------
    def _build_image_tab(self) -> None:
        frame = ttk.LabelFrame(self.image_tab, text="Картинки")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        left = ttk.Frame(frame)
        left.pack(side="left", fill="y", padx=10, pady=10)
        self.image_listbox = tk.Listbox(left, width=42, font=("Segoe UI", 10), relief="flat")
        self.image_listbox.pack(fill="y")
        self.image_listbox.bind("<<ListboxSelect>>", lambda _e: self.select_image())

        right = ttk.Frame(frame)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.image_label = tk.StringVar(value="Выберите изображение")
        ttk.Label(right, textvariable=self.image_label).pack(anchor="w")

        self.image_canvas = tk.Canvas(right, bg="#f5f8ff", highlightthickness=0)
        self.image_canvas.pack(fill="both", expand=True, pady=(8, 0))

    def select_image(self) -> None:
        idx = self._selected_index(self.image_listbox)
        if idx is None:
            return
        self.current_image_path = self.image_files[idx]
        self.image_label.set(f"Картинка: {self.current_image_path.name}")
        self._show_image(self.current_image_path)

    def _show_image(self, path: Path) -> None:
        img = Image.open(path)
        w = max(self.image_canvas.winfo_width(), 540)
        h = max(self.image_canvas.winfo_height(), 380)
        img.thumbnail((w - 24, h - 24))
        self.image_tk = ImageTk.PhotoImage(img)
        self.image_canvas.delete("all")
        self.image_canvas.create_image(w // 2, h // 2, image=self.image_tk)

    # ---------------------- WIN EFFECT --------------------------------
    def _win_effect(self, title: str, text: str, widgets: list[tk.Widget] | None = None) -> None:
        targets = widgets or []
        colors = ["#d9ffd9", "#fff7c9"]

        def blink(step: int = 0) -> None:
            if step >= 6:
                return
            color = colors[step % 2]
            for widget in targets:
                try:
                    widget.configure(bg=color)
                except Exception:
                    pass
            self.after(120, lambda: blink(step + 1))

        blink()
        messagebox.showinfo(title, text)

    # ---------------------- PUZZLES -----------------------------------
    def _build_puzzle_tab(self) -> None:
        container = ttk.Frame(self.puzzle_tab)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        self.puzzle_notebook = ttk.Notebook(container)
        self.puzzle_notebook.pack(fill="both", expand=True)

        self.number_tab = ttk.Frame(self.puzzle_notebook)
        self.memory_tab = ttk.Frame(self.puzzle_notebook)
        self.ttt_tab = ttk.Frame(self.puzzle_notebook)

        self.puzzle_notebook.add(self.number_tab, text="Пятнашки")
        self.puzzle_notebook.add(self.memory_tab, text="Найди пару")
        self.puzzle_notebook.add(self.ttt_tab, text="Крестики-нолики")

        self._build_number_tab()
        self._build_memory_tab()
        self._build_ttt_tab()

    def _build_number_tab(self) -> None:
        top = ttk.Frame(self.number_tab)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Новая игра", command=self.shuffle_number_puzzle).pack(side="left")
        self.puzzle_status = tk.StringVar(value="Соберите цифры в правильный порядок")
        ttk.Label(top, textvariable=self.puzzle_status).pack(side="left", padx=10)

        board = ttk.Frame(self.number_tab)
        board.pack(pady=12)

        for i in range(4):
            for j in range(4):
                btn = tk.Button(
                    board,
                    text="",
                    width=5,
                    height=2,
                    font=("Segoe UI", 16, "bold"),
                    command=lambda idx=i * 4 + j: self.move_number_tile(idx),
                )
                btn.grid(row=i, column=j, padx=3, pady=3)
                self.board_buttons.append(btn)

    def _init_number_puzzle(self) -> None:
        self.board = list(range(1, 16)) + [0]
        self.shuffle_number_puzzle()

    def shuffle_number_puzzle(self) -> None:
        self.board = list(range(1, 16)) + [0]
        for _ in range(250):
            empty = self.board.index(0)
            move = random.choice(self._possible_moves(empty))
            self.board[empty], self.board[move] = self.board[move], self.board[empty]
        self.puzzle_status.set("Соберите цифры в правильный порядок")
        self._render_number_board()

    def _possible_moves(self, empty_idx: int) -> list[int]:
        row, col = divmod(empty_idx, 4)
        moves: list[int] = []
        if row > 0:
            moves.append(empty_idx - 4)
        if row < 3:
            moves.append(empty_idx + 4)
        if col > 0:
            moves.append(empty_idx - 1)
        if col < 3:
            moves.append(empty_idx + 1)
        return moves

    def move_number_tile(self, idx: int) -> None:
        empty = self.board.index(0)
        if idx not in self._possible_moves(empty):
            return

        self.board[empty], self.board[idx] = self.board[idx], self.board[empty]
        self._render_number_board()

        if self.board == list(range(1, 16)) + [0]:
            self.puzzle_status.set("Победа! 🎉")
            self._win_effect("Пятнашки", "Вы собрали пазл!", self.board_buttons)

    def _render_number_board(self) -> None:
        for i, value in enumerate(self.board):
            btn = self.board_buttons[i]
            if value == 0:
                btn.configure(text="", state="disabled", bg="#bdbdbd")
            else:
                btn.configure(text=str(value), state="normal", bg="#e8f1ff")

    # memory
    def _build_memory_tab(self) -> None:
        top = ttk.Frame(self.memory_tab)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Новая игра", command=self._init_memory_puzzle).pack(side="left")
        self.memory_status = tk.StringVar(value="Открывайте карточки и ищите пары")
        ttk.Label(top, textvariable=self.memory_status).pack(side="left", padx=10)

        board = ttk.Frame(self.memory_tab)
        board.pack(pady=12)

        for i in range(4):
            for j in range(4):
                idx = i * 4 + j
                btn = tk.Button(
                    board,
                    text="❓",
                    width=5,
                    height=2,
                    font=("Segoe UI Emoji", 16),
                    command=lambda x=idx: self.memory_click(x),
                )
                btn.grid(row=i, column=j, padx=3, pady=3)
                self.memory_buttons.append(btn)

    def _init_memory_puzzle(self) -> None:
        symbols = MEMORY_SYMBOLS * 2
        random.shuffle(symbols)
        self.memory_values = symbols
        self.memory_opened = []
        self.memory_locked = False

        if hasattr(self, "memory_buttons"):
            for btn in self.memory_buttons:
                btn.configure(text="❓", state="normal", bg="#f4f4f4")

        if hasattr(self, "memory_status"):
            self.memory_status.set("Открывайте карточки и ищите пары")

    def memory_click(self, idx: int) -> None:
        if self.memory_locked or idx in self.memory_opened:
            return

        btn = self.memory_buttons[idx]
        if btn.cget("state") == "disabled":
            return

        btn.configure(text=self.memory_values[idx], bg="#fff4cc")
        self.memory_opened.append(idx)

        if len(self.memory_opened) == 2:
            self.memory_locked = True
            self.after(550, self._resolve_memory_pair)

    def _resolve_memory_pair(self) -> None:
        i1, i2 = self.memory_opened
        b1, b2 = self.memory_buttons[i1], self.memory_buttons[i2]

        if self.memory_values[i1] == self.memory_values[i2]:
            b1.configure(state="disabled", bg="#d9ffd9")
            b2.configure(state="disabled", bg="#d9ffd9")
            self.memory_status.set("Пара найдена")
        else:
            b1.configure(text="❓", bg="#f4f4f4")
            b2.configure(text="❓", bg="#f4f4f4")

        self.memory_opened = []
        self.memory_locked = False

        if all(btn.cget("state") == "disabled" for btn in self.memory_buttons):
            self.memory_status.set("Победа! 🎉")
            self._win_effect("Найди пару", "Все пары собраны!", self.memory_buttons)

    # tic-tac-toe
    def _build_ttt_tab(self) -> None:
        top = ttk.Frame(self.ttt_tab)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Button(top, text="Новая игра", command=self._init_ttt_puzzle).pack(side="left")
        self.ttt_status = tk.StringVar(value="Ход: X")
        ttk.Label(top, textvariable=self.ttt_status).pack(side="left", padx=10)

        board = ttk.Frame(self.ttt_tab)
        board.pack(pady=20)

        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                btn = tk.Button(
                    board,
                    text="",
                    width=6,
                    height=3,
                    font=("Segoe UI", 18, "bold"),
                    command=lambda x=idx: self.ttt_click(x),
                )
                btn.grid(row=i, column=j, padx=4, pady=4)
                self.ttt_buttons.append(btn)

    def _init_ttt_puzzle(self) -> None:
        self.ttt_board = ["" for _ in range(9)]
        self.ttt_current = self.ttt_human
        if hasattr(self, "ttt_status"):
            self.ttt_status.set("Ваш ход: X")
        for btn in self.ttt_buttons:
            btn.configure(text="", state="normal", bg="#f4f4f4")

    def ttt_click(self, idx: int) -> None:
        if self.ttt_board[idx] or self.ttt_current != self.ttt_human:
            return

        self.ttt_board[idx] = self.ttt_current
        self.ttt_buttons[idx].configure(text=self.ttt_current)

        winner = self._ttt_winner()
        if winner:
            self.ttt_status.set("Вы победили")
            for btn in self.ttt_buttons:
                btn.configure(state="disabled")
            self._win_effect("Крестики-нолики", "Вы победили!", self.ttt_buttons)
            return

        if all(cell for cell in self.ttt_board):
            self.ttt_status.set("Ничья")
            self._win_effect("Крестики-нолики", "Ничья!", self.ttt_buttons)
            return

        self.ttt_current = self.ttt_bot
        self.ttt_status.set("Ход бота...")
        self.after(250, self._ttt_bot_move)

    def _ttt_bot_move(self) -> None:
        if self._ttt_winner() or all(self.ttt_board):
            return

        best_idx = self._ttt_find_winning_move(self.ttt_bot)
        if best_idx is None:
            best_idx = self._ttt_find_winning_move(self.ttt_human)
        if best_idx is None and self.ttt_board[4] == "":
            best_idx = 4
        if best_idx is None:
            corners = [i for i in [0, 2, 6, 8] if self.ttt_board[i] == ""]
            if corners:
                best_idx = random.choice(corners)
        if best_idx is None:
            free = [i for i, value in enumerate(self.ttt_board) if value == ""]
            best_idx = random.choice(free)

        self.ttt_board[best_idx] = self.ttt_bot
        self.ttt_buttons[best_idx].configure(text=self.ttt_bot)

        winner = self._ttt_winner()
        if winner:
            self.ttt_status.set("Победил бот")
            for btn in self.ttt_buttons:
                btn.configure(state="disabled")
            self._win_effect("Крестики-нолики", "Бот победил!", self.ttt_buttons)
            return

        if all(cell for cell in self.ttt_board):
            self.ttt_status.set("Ничья")
            self._win_effect("Крестики-нолики", "Ничья!", self.ttt_buttons)
            return

        self.ttt_current = self.ttt_human
        self.ttt_status.set("Ваш ход: X")

    def _ttt_find_winning_move(self, symbol: str) -> int | None:
        for idx, value in enumerate(self.ttt_board):
            if value:
                continue
            self.ttt_board[idx] = symbol
            if self._ttt_winner() == symbol:
                self.ttt_board[idx] = ""
                return idx
            self.ttt_board[idx] = ""
        return None

    def _ttt_winner(self) -> str | None:
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6),
        ]
        for a, b, c in lines:
            if self.ttt_board[a] and self.ttt_board[a] == self.ttt_board[b] == self.ttt_board[c]:
                return self.ttt_board[a]
        return None

    # ---------------------- AI ----------------------------------------
    def _build_ai_tab(self) -> None:
        frame = ttk.LabelFrame(self.ai_tab, text="ИИ ассистент")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        subtitle = (
            "Введите запрос и получите ответ от ИИ."
        )
        ttk.Label(frame, text=subtitle, wraplength=980).pack(anchor="w", padx=12, pady=(10, 8))

        input_card = ttk.Frame(frame)
        input_card.pack(fill="x", padx=10, pady=(0, 8))
        ttk.Label(input_card, text="Ваш запрос:").pack(anchor="w")

        self.prompt_text = tk.Text(input_card, height=7, font=("Segoe UI", 11), relief="flat", padx=10, pady=8)
        self.prompt_text.pack(fill="x", pady=(4, 0))

        actions = ttk.Frame(frame)
        actions.pack(fill="x", padx=10, pady=(0, 8))
        ttk.Button(actions, text="Отправить", style="Accent.TButton", command=self.send_to_gigachat).pack(side="left")
        ttk.Button(actions, text="Очистить", command=self.clear_ai_fields).pack(side="left", padx=8)

        output_card = ttk.Frame(frame)
        output_card.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        ttk.Label(output_card, text="Ответ:").pack(anchor="w")

        self.answer_text = tk.Text(output_card, wrap="word", font=("Segoe UI", 11), relief="flat", state="disabled", padx=10, pady=8)
        self.answer_text.pack(fill="both", expand=True, pady=(4, 0))

    def clear_ai_fields(self) -> None:
        self.prompt_text.delete("1.0", "end")
        self._set_answer_text("")

    def _set_answer_text(self, text: str) -> None:
        self.answer_text.configure(state="normal")
        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("1.0", text)
        self.answer_text.configure(state="disabled")

    def send_to_gigachat(self) -> None:
        prompt = self.prompt_text.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning("Пустой запрос", "Введите текст запроса")
            return

        self._set_answer_text("Отправка запроса...")
        self.update_idletasks()

        try:
            token = self._gigachat_token()
            answer = self._gigachat_chat(token, prompt)
            self._set_answer_text(answer)
        except Exception as exc:
            self._set_answer_text(f"Ошибка: {exc}")

    def _gigachat_token(self) -> str:
        if not GIGACHAT_CLIENT_ID or not GIGACHAT_CLIENT_SECRET:
            raise ValueError("Заполните GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET в переменных окружения")

        response = requests.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                "Authorization": f"Basic {GIGACHAT_CLIENT_ID}:{GIGACHAT_CLIENT_SECRET}",
                "RqUID": "multimedia-hub-rquid",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"scope": "GIGACHAT_API_PERS"},
            timeout=25,
            verify=False,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _gigachat_chat(self, token: str, prompt: str) -> str:
        response = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            data=json.dumps(
                {
                    "model": GIGACHAT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 600,
                }
            ),
            timeout=40,
            verify=False,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    # ---------------------- MEDIA CORE --------------------------------
    def _selected_index(self, listbox: tk.Listbox) -> int | None:
        selected = listbox.curselection()
        if not selected:
            return None
        return int(selected[0])

    def _prepare_media_player(self, path: Path) -> None:
        if not self.vlc_ready:
            return
        if self.player is not None:
            self.player.stop()
        self.player = vlc.MediaPlayer(str(path))
        self.player.audio_set_volume(int(self.volume_scale.get()))

    def play_media(self) -> None:
        if not self.vlc_ready:
            messagebox.showwarning("VLC не установлен", "Установите VLC Media Player для воспроизведения музыки")
            return
        if self.player is None:
            messagebox.showinfo("Нет аудио", "Выберите аудио файл из списка")
            return
        self.player.play()

    def pause_media(self) -> None:
        if self.player:
            self.player.pause()

    def stop_media(self) -> None:
        if self.player:
            self.player.stop()

    def on_volume_change(self, _value: str) -> None:
        if self.player:
            self.player.audio_set_volume(int(self.volume_scale.get()))


if __name__ == "__main__":
    app = MultimediaHub()
    app.mainloop()
