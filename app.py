import json
import os
import random
import re
import shutil
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


# Настройки GigaChat перенесены в программу (не в UI)
GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID", "")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET", "")
GIGACHAT_MODEL = "GigaChat"

PROJECT_ROOT = Path(__file__).resolve().parent
AUDIO_EXT = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
VIDEO_EXT = {".mp4", ".avi", ".mkv", ".mov", ".webm"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}


class MultimediaHub(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Multimedia Hub")
        self.geometry("1150x780")
        self.minsize(1000, 700)

        self.player: Any = None
        self.current_audio_path: Path | None = None
        self.current_video_path: Path | None = None
        self.current_image_path: Path | None = None
        self.image_tk: ImageTk.PhotoImage | None = None
        self.vlc_ready = vlc is not None

        self.theme_var = tk.StringVar(value="Светлая")
        self.board: list[int] = []
        self.board_buttons: list[tk.Button] = []
        self.memory_values: list[int] = []
        self.memory_buttons: list[tk.Button] = []
        self.memory_opened: list[int] = []
        self.memory_locked = False

        self._create_styles(dark=False)
        self._build_ui()
        self._init_puzzle_15()
        self._init_memory_puzzle()
        self.refresh_file_lists()

        if not self.vlc_ready:
            self.after(
                250,
                lambda: messagebox.showwarning(
                    "VLC не найден",
                    "Не удалось загрузить libVLC. Установите VLC Media Player,\n"
                    "чтобы работало локальное воспроизведение музыки.",
                ),
            )

    # ------------------------- THEME ---------------------------------
    def _create_styles(self, dark: bool) -> None:
        bg = "#1f1f1f" if dark else "#f3f3f3"
        fg = "#f0f0f0" if dark else "#101010"
        panel = "#2b2b2b" if dark else "#ffffff"

        self.configure(bg=bg)
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background=panel, foreground=fg, font=("Segoe UI", 10))
        style.configure("TLabelframe", background=bg)
        style.configure("TLabelframe.Label", background=bg, foreground=fg, font=("Segoe UI", 11, "bold"))
        style.configure("TNotebook", background=bg)
        style.configure("TNotebook.Tab", padding=(14, 10), font=("Segoe UI", 10, "bold"))

        self.dark_mode = dark

    def toggle_theme(self) -> None:
        dark = self.theme_var.get() == "Тёмная"
        self._create_styles(dark)

        text_bg = "#202020" if dark else "#ffffff"
        text_fg = "#f0f0f0" if dark else "#101010"
        canvas_bg = "#101010" if dark else "#e8e8e8"

        for txt in [self.prompt_text, self.answer_text]:
            txt.configure(bg=text_bg, fg=text_fg, insertbackground=text_fg)
        self.image_canvas.configure(bg=canvas_bg)

    # ------------------------- UI -------------------------------------
    def _build_ui(self) -> None:
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(top_bar, text="Тема:").pack(side="left")
        theme_combo = ttk.Combobox(top_bar, textvariable=self.theme_var, state="readonly", values=["Светлая", "Тёмная"], width=12)
        theme_combo.pack(side="left", padx=8)
        theme_combo.bind("<<ComboboxSelected>>", lambda _e: self.toggle_theme())

        ttk.Button(top_bar, text="Обновить файлы проекта", command=self.refresh_file_lists).pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.music_tab = ttk.Frame(self.notebook)
        self.video_tab = ttk.Frame(self.notebook)
        self.image_tab = ttk.Frame(self.notebook)
        self.puzzle_tab = ttk.Frame(self.notebook)
        self.ai_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.music_tab, text="Музыка")
        self.notebook.add(self.video_tab, text="Видео")
        self.notebook.add(self.image_tab, text="Картинки")
        self.notebook.add(self.puzzle_tab, text="Головоломки")
        self.notebook.add(self.ai_tab, text="ИИ / GigaChat")

        self._build_music_tab()
        self._build_video_tab()
        self._build_image_tab()
        self._build_puzzle_tab()
        self._build_ai_tab()

    # ---------------------- FILE SCAN ---------------------------------
    def _scan_project_files(self, extensions: set[str]) -> list[Path]:
        files = []
        for path in PROJECT_ROOT.rglob("*"):
            if path.is_file() and path.suffix.lower() in extensions:
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
        for f in files:
            listbox.insert("end", str(f.relative_to(PROJECT_ROOT)))

    # ---------------------- MUSIC -------------------------------------
    def _build_music_tab(self) -> None:
        frame = ttk.LabelFrame(self.music_tab, text="Музыка из корня проекта")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        left = ttk.Frame(frame)
        left.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        self.audio_listbox = tk.Listbox(left, height=18)
        self.audio_listbox.pack(fill="both", expand=True)
        self.audio_listbox.bind("<<ListboxSelect>>", lambda _e: self.select_audio())

        right = ttk.Frame(frame)
        right.pack(side="right", fill="y", padx=8, pady=8)

        self.music_label = tk.StringVar(value="Выберите аудио из списка")
        ttk.Label(right, textvariable=self.music_label, wraplength=280).pack(anchor="w", pady=6)

        ttk.Button(right, text="▶ Старт", command=self.play_media).pack(fill="x", pady=4)
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
        frame = ttk.LabelFrame(self.video_tab, text="Видео из корня проекта")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.video_listbox = tk.Listbox(frame, height=20)
        self.video_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.video_listbox.bind("<<ListboxSelect>>", lambda _e: self.select_video())

        controls = ttk.Frame(frame)
        controls.pack(fill="x", padx=10, pady=(0, 10))
        self.video_label = tk.StringVar(value="Выберите видео")
        ttk.Label(controls, textvariable=self.video_label, wraplength=700).pack(side="left")
        ttk.Button(controls, text="Открыть во внешнем плеере", command=self.open_video_external).pack(side="right")

    def select_video(self) -> None:
        idx = self._selected_index(self.video_listbox)
        if idx is None:
            return
        self.current_video_path = self.video_files[idx]
        self.video_label.set(f"Видео: {self.current_video_path.name}")

    # ---------------------- IMAGES ------------------------------------
    def _build_image_tab(self) -> None:
        frame = ttk.LabelFrame(self.image_tab, text="Картинки из корня проекта")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        left = ttk.Frame(frame)
        left.pack(side="left", fill="y", padx=8, pady=8)
        self.image_listbox = tk.Listbox(left, width=40)
        self.image_listbox.pack(fill="y", expand=False)
        self.image_listbox.bind("<<ListboxSelect>>", lambda _e: self.select_image())

        right = ttk.Frame(frame)
        right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        self.image_label = tk.StringVar(value="Выберите изображение")
        ttk.Label(right, textvariable=self.image_label).pack(anchor="w")

        self.image_canvas = tk.Canvas(right, bg="#e8e8e8", highlightthickness=0)
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
        w = max(self.image_canvas.winfo_width(), 500)
        h = max(self.image_canvas.winfo_height(), 350)
        img.thumbnail((w - 20, h - 20))
        self.image_tk = ImageTk.PhotoImage(img)
        self.image_canvas.delete("all")
        self.image_canvas.create_image(w // 2, h // 2, image=self.image_tk)

    # ---------------------- PUZZLES -----------------------------------
    def _build_puzzle_tab(self) -> None:
        outer = ttk.Frame(self.puzzle_tab)
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        left = ttk.LabelFrame(outer, text="Пятнашки 4x4")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        top = ttk.Frame(left)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Button(top, text="Новая игра", command=self.shuffle_puzzle_15).pack(side="left")
        self.puzzle_status = tk.StringVar(value="Соберите пазл")
        ttk.Label(top, textvariable=self.puzzle_status).pack(side="left", padx=10)

        board = ttk.Frame(left)
        board.pack(pady=8)

        for i in range(4):
            for j in range(4):
                btn = tk.Button(board, text="", width=5, height=2, font=("Segoe UI", 13, "bold"), command=lambda idx=i * 4 + j: self.move_tile(idx))
                btn.grid(row=i, column=j, padx=3, pady=3)
                self.board_buttons.append(btn)

        right = ttk.LabelFrame(outer, text="Найди пару (новая головоломка)")
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))

        mtop = ttk.Frame(right)
        mtop.pack(fill="x", padx=8, pady=8)
        ttk.Button(mtop, text="Новая игра", command=self._init_memory_puzzle).pack(side="left")
        self.memory_status = tk.StringVar(value="Открывайте карточки и ищите пары")
        ttk.Label(mtop, textvariable=self.memory_status).pack(side="left", padx=8)

        mboard = ttk.Frame(right)
        mboard.pack(pady=10)

        for i in range(4):
            for j in range(4):
                idx = i * 4 + j
                btn = tk.Button(mboard, text="?", width=5, height=2, font=("Segoe UI", 12, "bold"), command=lambda x=idx: self.memory_click(x))
                btn.grid(row=i, column=j, padx=3, pady=3)
                self.memory_buttons.append(btn)

    # 15 puzzle
    def _init_puzzle_15(self) -> None:
        self.board = list(range(1, 16)) + [0]
        self.shuffle_puzzle_15()

    def shuffle_puzzle_15(self) -> None:
        self.board = list(range(1, 16)) + [0]
        for _ in range(200):
            empty = self.board.index(0)
            move = random.choice(self._possible_moves(empty))
            self.board[empty], self.board[move] = self.board[move], self.board[empty]
        self.puzzle_status.set("Соберите пазл")
        self._render_15()

    def _possible_moves(self, empty_idx: int) -> list[int]:
        row, col = divmod(empty_idx, 4)
        moves = []
        if row > 0:
            moves.append(empty_idx - 4)
        if row < 3:
            moves.append(empty_idx + 4)
        if col > 0:
            moves.append(empty_idx - 1)
        if col < 3:
            moves.append(empty_idx + 1)
        return moves

    def move_tile(self, idx: int) -> None:
        empty = self.board.index(0)
        if idx not in self._possible_moves(empty):
            return
        self.board[empty], self.board[idx] = self.board[idx], self.board[empty]
        self._render_15()
        if self.board == list(range(1, 16)) + [0]:
            self.puzzle_status.set("Победа!")

    def _render_15(self) -> None:
        for i, v in enumerate(self.board):
            if v == 0:
                self.board_buttons[i].configure(text="", state="disabled", bg="#bdbdbd")
            else:
                self.board_buttons[i].configure(text=str(v), state="normal", bg="#e6f0ff")

    # memory puzzle
    def _init_memory_puzzle(self) -> None:
        values = list(range(1, 9)) * 2
        random.shuffle(values)
        self.memory_values = values
        self.memory_opened = []
        self.memory_locked = False
        if hasattr(self, "memory_buttons"):
            for btn in self.memory_buttons:
                btn.configure(text="?", state="normal", bg="#f4f4f4")
        if hasattr(self, "memory_status"):
            self.memory_status.set("Открывайте карточки и ищите пары")

    def memory_click(self, idx: int) -> None:
        if self.memory_locked or idx in self.memory_opened:
            return
        btn = self.memory_buttons[idx]
        if btn.cget("state") == "disabled":
            return

        btn.configure(text=str(self.memory_values[idx]), bg="#fff4cc")
        self.memory_opened.append(idx)

        if len(self.memory_opened) == 2:
            self.memory_locked = True
            self.after(500, self._resolve_memory_pair)

    def _resolve_memory_pair(self) -> None:
        i1, i2 = self.memory_opened
        b1, b2 = self.memory_buttons[i1], self.memory_buttons[i2]

        if self.memory_values[i1] == self.memory_values[i2]:
            b1.configure(state="disabled", bg="#d9ffd9")
            b2.configure(state="disabled", bg="#d9ffd9")
            self.memory_status.set("Пара найдена!")
        else:
            b1.configure(text="?", bg="#f4f4f4")
            b2.configure(text="?", bg="#f4f4f4")

        self.memory_opened = []
        self.memory_locked = False

        if all(btn.cget("state") == "disabled" for btn in self.memory_buttons):
            self.memory_status.set("Победа! Все пары собраны")

    # ---------------------- AI ----------------------------------------
    def _build_ai_tab(self) -> None:
        frame = ttk.LabelFrame(self.ai_tab, text="Обращение к GigaChat")
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        filters = ttk.Frame(frame)
        filters.pack(fill="x", padx=10, pady=8)

        self.filter_profanity = tk.BooleanVar(value=True)
        self.filter_pii = tk.BooleanVar(value=True)
        self.filter_length = tk.BooleanVar(value=False)

        ttk.Checkbutton(filters, text="Убирать нецензурные слова", variable=self.filter_profanity).pack(side="left", padx=8)
        ttk.Checkbutton(filters, text="Скрывать телефоны/e-mail", variable=self.filter_pii).pack(side="left", padx=8)
        ttk.Checkbutton(filters, text="Обрезать ответ до 500 символов", variable=self.filter_length).pack(side="left", padx=8)

        self.prompt_text = tk.Text(frame, height=6, font=("Segoe UI", 11))
        self.prompt_text.pack(fill="x", padx=10, pady=8)

        ttk.Button(frame, text="Отправить в GigaChat", command=self.send_to_gigachat).pack(anchor="w", padx=10)

        self.answer_text = tk.Text(frame, wrap="word", font=("Segoe UI", 11))
        self.answer_text.pack(fill="both", expand=True, padx=10, pady=10)

    def _apply_input_filters(self, text: str) -> str:
        if self.filter_profanity.get():
            for word in ["дурак", "идиот", "черт"]:
                text = re.sub(fr"\b{word}\b", "***", text, flags=re.IGNORECASE)
        if self.filter_pii.get():
            text = re.sub(r"\+?\d[\d\-\s]{8,}\d", "[PHONE_HIDDEN]", text)
            text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL_HIDDEN]", text)
        return text

    def _apply_output_filters(self, text: str) -> str:
        if self.filter_length.get() and len(text) > 500:
            return text[:500] + "\n\n[Ответ обрезан фильтром длины]"
        return text

    def send_to_gigachat(self) -> None:
        prompt = self.prompt_text.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning("Пустой запрос", "Введите текст запроса")
            return

        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("1.0", "Отправка запроса...")
        self.update_idletasks()

        try:
            token = self._gigachat_token()
            answer = self._gigachat_chat(token, self._apply_input_filters(prompt))
            answer = self._apply_output_filters(answer)
            self.answer_text.delete("1.0", "end")
            self.answer_text.insert("1.0", answer)
        except Exception as exc:
            self.answer_text.delete("1.0", "end")
            self.answer_text.insert("1.0", f"Ошибка: {exc}")

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
        sel = listbox.curselection()
        if not sel:
            return None
        return int(sel[0])

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

    def open_video_external(self) -> None:
        if not self.current_video_path:
            messagebox.showinfo("Нет файла", "Выберите видео файл из списка")
            return

        if os.name == "nt":
            os.startfile(self.current_video_path)
            return

        opener = shutil.which("xdg-open") or shutil.which("open")
        if opener:
            os.system(f'{opener} "{self.current_video_path}"')
        else:
            messagebox.showerror("Ошибка", "Не найден инструмент для открытия видео")


if __name__ == "__main__":
    app = MultimediaHub()
    app.mainloop()
