import json
import os
import random
import re
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

import requests
from PIL import Image, ImageTk

try:
    import vlc  # type: ignore
except Exception:
    vlc = None


class MultimediaHub(tk.Tk):
    """Desktop-приложение: музыка, видео, головоломки, картинки и чат с GigaChat."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Multimedia Hub")
        self.geometry("1100x760")
        self.minsize(980, 680)

        self.player: Any = None
        self.current_media_path: Path | None = None
        self.image_tk: ImageTk.PhotoImage | None = None
        self.image_path: Path | None = None
        self.vlc_ready = vlc is not None

        self.board: list[int] = []
        self.board_buttons: list[tk.Button] = []

        self._create_styles()
        self._build_ui()
        self._init_puzzle()

        if not self.vlc_ready:
            self.after(
                250,
                lambda: messagebox.showwarning(
                    "VLC не найден",
                    "Не удалось загрузить libVLC. Установите VLC Media Player и перезапустите приложение.\n"
                    "Программа продолжит работу, но локальное воспроизведение музыки будет недоступно.",
                ),
            )

    # ------------------------------ UI ---------------------------------
    def _create_styles(self) -> None:
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TNotebook.Tab", padding=(16, 10), font=("Segoe UI", 11, "bold"))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))

    def _build_ui(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.music_tab = ttk.Frame(self.notebook)
        self.video_tab = ttk.Frame(self.notebook)
        self.puzzle_tab = ttk.Frame(self.notebook)
        self.image_tab = ttk.Frame(self.notebook)
        self.ai_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.music_tab, text="Музыка")
        self.notebook.add(self.video_tab, text="Видео")
        self.notebook.add(self.puzzle_tab, text="Головоломка")
        self.notebook.add(self.image_tab, text="Картинки")
        self.notebook.add(self.ai_tab, text="ИИ / GigaChat")

        self._build_music_tab()
        self._build_video_tab()
        self._build_puzzle_tab()
        self._build_image_tab()
        self._build_ai_tab()

    # ----------------------------- MUSIC --------------------------------
    def _build_music_tab(self) -> None:
        frame = ttk.LabelFrame(self.music_tab, text="Управление музыкой")
        frame.pack(fill="x", padx=14, pady=14)

        self.music_file_var = tk.StringVar(value="Файл не выбран")
        ttk.Label(frame, textvariable=self.music_file_var, wraplength=900).pack(anchor="w", padx=10, pady=8)

        controls = ttk.Frame(frame)
        controls.pack(fill="x", padx=10, pady=6)

        ttk.Button(controls, text="Открыть аудио", command=self.open_audio_file).grid(row=0, column=0, padx=4, pady=4)
        ttk.Button(controls, text="▶ Старт", command=self.play_media).grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(controls, text="⏸ Пауза", command=self.pause_media).grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(controls, text="⏹ Стоп", command=self.stop_media).grid(row=0, column=3, padx=4, pady=4)

        ttk.Label(controls, text="Громкость").grid(row=1, column=0, sticky="w", padx=4)
        self.volume_scale = ttk.Scale(controls, from_=0, to=100, value=70, command=self.on_volume_change)
        self.volume_scale.grid(row=1, column=1, columnspan=2, sticky="ew", padx=4)

        ttk.Label(controls, text="Скорость").grid(row=2, column=0, sticky="w", padx=4)
        self.speed_scale = ttk.Scale(controls, from_=0.5, to=2.0, value=1.0, command=self.on_speed_change)
        self.speed_scale.grid(row=2, column=1, columnspan=2, sticky="ew", padx=4)

        ttk.Label(controls, text="EQ пресет").grid(row=3, column=0, sticky="w", padx=4)
        self.eq_var = tk.StringVar(value="Flat")
        eq_menu = ttk.Combobox(
            controls,
            state="readonly",
            textvariable=self.eq_var,
            values=["Flat", "Rock", "Pop", "Techno", "Classical", "Dance"],
            width=15,
        )
        eq_menu.grid(row=3, column=1, sticky="w", padx=4)
        eq_menu.bind("<<ComboboxSelected>>", lambda _e: self.apply_equalizer())

        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(2, weight=1)

        if not self.vlc_ready:
            self.music_file_var.set("VLC/libVLC не найдены — установите VLC для работы вкладки музыки")

    # ----------------------------- VIDEO --------------------------------
    def _build_video_tab(self) -> None:
        frame = ttk.LabelFrame(self.video_tab, text="Просмотр видео")
        frame.pack(fill="both", expand=True, padx=14, pady=14)

        self.video_file_var = tk.StringVar(value="Видео не выбрано")
        ttk.Label(frame, textvariable=self.video_file_var, wraplength=900).pack(anchor="w", padx=10, pady=8)

        btns = ttk.Frame(frame)
        btns.pack(fill="x", padx=10)
        ttk.Button(btns, text="Открыть видео", command=self.open_video_file).pack(side="left", padx=4, pady=4)
        ttk.Button(btns, text="Открыть во внешнем плеере", command=self.open_video_external).pack(side="left", padx=4, pady=4)

        info = (
            "Для корректного воспроизведения видео используйте системный плеер "
            "(кнопка выше) или доработайте встраивание VLC окна под вашу ОС."
        )
        ttk.Label(frame, text=info, foreground="#555", wraplength=900, justify="left").pack(anchor="w", padx=10, pady=16)

    # ----------------------------- PUZZLE -------------------------------
    def _build_puzzle_tab(self) -> None:
        outer = ttk.Frame(self.puzzle_tab)
        outer.pack(fill="both", expand=True, padx=14, pady=14)

        top = ttk.Frame(outer)
        top.pack(fill="x")
        ttk.Button(top, text="Новая игра", command=self.shuffle_puzzle).pack(side="left", padx=6)

        self.puzzle_status = tk.StringVar(value="Соберите пазл 4x4")
        ttk.Label(top, textvariable=self.puzzle_status).pack(side="left", padx=12)

        board_frame = ttk.Frame(outer)
        board_frame.pack(pady=20)

        self.board_buttons.clear()
        for i in range(4):
            for j in range(4):
                btn = tk.Button(
                    board_frame,
                    text="",
                    width=6,
                    height=3,
                    font=("Segoe UI", 13, "bold"),
                    command=lambda idx=i * 4 + j: self.move_tile(idx),
                )
                btn.grid(row=i, column=j, padx=3, pady=3)
                self.board_buttons.append(btn)

    def _init_puzzle(self) -> None:
        self.board = list(range(1, 16)) + [0]
        self.shuffle_puzzle()

    def shuffle_puzzle(self) -> None:
        self.board = list(range(1, 16)) + [0]
        for _ in range(200):
            empty = self.board.index(0)
            for move in self._possible_moves(empty):
                if random.random() < 0.25:
                    self.board[empty], self.board[move] = self.board[move], self.board[empty]
                    empty = move
        self.puzzle_status.set("Соберите пазл 4x4")
        self._render_puzzle()

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
        self._render_puzzle()
        if self.board == list(range(1, 16)) + [0]:
            self.puzzle_status.set("Победа! 🎉")

    def _render_puzzle(self) -> None:
        for idx, val in enumerate(self.board):
            btn = self.board_buttons[idx]
            if val == 0:
                btn.configure(text="", bg="#d9d9d9", state="disabled")
            else:
                btn.configure(text=str(val), bg="#f2f7ff", state="normal")

    # ----------------------------- IMAGES -------------------------------
    def _build_image_tab(self) -> None:
        frame = ttk.LabelFrame(self.image_tab, text="Просмотр картинок")
        frame.pack(fill="both", expand=True, padx=14, pady=14)

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", padx=10, pady=8)
        ttk.Button(toolbar, text="Открыть изображение", command=self.open_image_file).pack(side="left", padx=4)

        self.image_info = tk.StringVar(value="Картинка не выбрана")
        ttk.Label(frame, textvariable=self.image_info).pack(anchor="w", padx=10, pady=6)

        self.image_canvas = tk.Canvas(frame, bg="#1f1f1f", highlightthickness=0)
        self.image_canvas.pack(fill="both", expand=True, padx=10, pady=10)

    def open_image_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")],
        )
        if not file_path:
            return

        self.image_path = Path(file_path)
        self.image_info.set(f"Файл: {self.image_path.name}")
        self._show_image(self.image_path)

    def _show_image(self, path: Path) -> None:
        img = Image.open(path)
        canvas_w = max(self.image_canvas.winfo_width(), 400)
        canvas_h = max(self.image_canvas.winfo_height(), 300)
        img.thumbnail((canvas_w - 20, canvas_h - 20))
        self.image_tk = ImageTk.PhotoImage(img)
        self.image_canvas.delete("all")
        self.image_canvas.create_image(canvas_w // 2, canvas_h // 2, image=self.image_tk)

    # ----------------------------- AI -----------------------------------
    def _build_ai_tab(self) -> None:
        config_frame = ttk.LabelFrame(self.ai_tab, text="Настройки GigaChat")
        config_frame.pack(fill="x", padx=14, pady=(14, 8))

        ttk.Label(config_frame, text="Client ID").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        ttk.Label(config_frame, text="Client Secret").grid(row=1, column=0, padx=6, pady=4, sticky="w")

        self.client_id_var = tk.StringVar(value=os.getenv("GIGACHAT_CLIENT_ID", ""))
        self.client_secret_var = tk.StringVar(value=os.getenv("GIGACHAT_CLIENT_SECRET", ""))

        ttk.Entry(config_frame, textvariable=self.client_id_var, width=50).grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        ttk.Entry(config_frame, textvariable=self.client_secret_var, width=50, show="*").grid(
            row=1, column=1, padx=6, pady=4, sticky="ew"
        )

        self.filter_profanity = tk.BooleanVar(value=True)
        self.filter_pii = tk.BooleanVar(value=True)
        self.filter_length = tk.BooleanVar(value=False)

        ttk.Checkbutton(config_frame, text="Убирать нецензурные слова", variable=self.filter_profanity).grid(
            row=0, column=2, padx=8, sticky="w"
        )
        ttk.Checkbutton(config_frame, text="Скрывать телефоны/e-mail", variable=self.filter_pii).grid(
            row=1, column=2, padx=8, sticky="w"
        )
        ttk.Checkbutton(config_frame, text="Обрезать ответ до 500 символов", variable=self.filter_length).grid(
            row=2, column=2, padx=8, sticky="w"
        )

        config_frame.columnconfigure(1, weight=1)

        chat_frame = ttk.LabelFrame(self.ai_tab, text="Диалог")
        chat_frame.pack(fill="both", expand=True, padx=14, pady=(8, 14))

        self.prompt_text = tk.Text(chat_frame, height=6, font=("Segoe UI", 11))
        self.prompt_text.pack(fill="x", padx=10, pady=8)

        ttk.Button(chat_frame, text="Отправить в GigaChat", command=self.send_to_gigachat).pack(anchor="w", padx=10, pady=4)

        self.answer_text = tk.Text(chat_frame, wrap="word", font=("Segoe UI", 11))
        self.answer_text.pack(fill="both", expand=True, padx=10, pady=(8, 10))

    def _apply_input_filters(self, text: str) -> str:
        if self.filter_profanity.get():
            bad_words = ["дурак", "идиот", "черт"]
            for word in bad_words:
                text = re.sub(fr"\b{word}\b", "***", text, flags=re.IGNORECASE)
        if self.filter_pii.get():
            text = re.sub(r"\+?\d[\d\-\s]{8,}\d", "[PHONE_HIDDEN]", text)
            text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL_HIDDEN]", text)
        return text

    def _apply_output_filters(self, text: str) -> str:
        if self.filter_length.get() and len(text) > 500:
            return text[:500] + "\n\n[Ответ был обрезан фильтром длины]"
        return text

    def send_to_gigachat(self) -> None:
        user_prompt = self.prompt_text.get("1.0", "end").strip()
        if not user_prompt:
            messagebox.showwarning("Пустой запрос", "Введите текст запроса")
            return

        filtered_prompt = self._apply_input_filters(user_prompt)
        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("1.0", "Отправка запроса...\n")
        self.update_idletasks()

        try:
            token = self._gigachat_token()
            answer = self._gigachat_chat(token, filtered_prompt)
            answer = self._apply_output_filters(answer)
            self.answer_text.delete("1.0", "end")
            self.answer_text.insert("1.0", answer)
        except Exception as exc:
            self.answer_text.delete("1.0", "end")
            self.answer_text.insert("1.0", f"Ошибка: {exc}")

    def _gigachat_token(self) -> str:
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        if not client_id or not client_secret:
            raise ValueError("Укажите Client ID и Client Secret для GigaChat")

        response = requests.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                "Authorization": f"Basic {client_id}:{client_secret}",
                "RqUID": "multimedia-hub-rquid",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"scope": "GIGACHAT_API_PERS"},
            timeout=25,
            verify=False,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["access_token"]

    def _gigachat_chat(self, token: str, prompt: str) -> str:
        response = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "model": "GigaChat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 600,
                }
            ),
            timeout=40,
            verify=False,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]

    # --------------------------- MEDIA CORE -----------------------------
    def open_audio_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Выберите аудио",
            filetypes=[("Audio", "*.mp3 *.wav *.flac *.ogg *.m4a")],
        )
        if not file_path:
            return
        self.current_media_path = Path(file_path)
        self.music_file_var.set(f"Аудио: {self.current_media_path.name}")
        self._prepare_media_player(self.current_media_path)

    def open_video_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Выберите видео",
            filetypes=[("Video", "*.mp4 *.avi *.mkv *.mov *.webm")],
        )
        if not file_path:
            return
        self.current_media_path = Path(file_path)
        self.video_file_var.set(f"Видео: {self.current_media_path.name}")

    def open_video_external(self) -> None:
        if not self.current_media_path:
            messagebox.showinfo("Нет файла", "Сначала выберите видео")
            return
        if os.name == "nt":
            os.startfile(self.current_media_path)
            return
        opener = shutil.which("xdg-open") or shutil.which("open")
        if opener:
            os.system(f'{opener} "{self.current_media_path}"')
        else:
            messagebox.showerror("Ошибка", "Не удалось найти системный инструмент для открытия видео.")

    def _prepare_media_player(self, path: Path) -> None:
        if not self.vlc_ready:
            return
        if self.player is not None:
            self.player.stop()
        self.player = vlc.MediaPlayer(str(path))
        self.player.audio_set_volume(int(self.volume_scale.get()))
        self.player.set_rate(float(self.speed_scale.get()))
        self.apply_equalizer()

    def play_media(self) -> None:
        if not self.vlc_ready:
            messagebox.showwarning("VLC не установлен", "Установите VLC Media Player для воспроизведения музыки.")
            return
        if self.player is None:
            messagebox.showinfo("Нет аудио", "Сначала выберите аудио файл")
            return
        self.player.play()

    def pause_media(self) -> None:
        if self.player:
            self.player.pause()

    def stop_media(self) -> None:
        if self.player:
            self.player.stop()

    def on_volume_change(self, _value: str) -> None:
        if self.vlc_ready and self.player:
            self.player.audio_set_volume(int(self.volume_scale.get()))

    def on_speed_change(self, _value: str) -> None:
        if self.vlc_ready and self.player:
            self.player.set_rate(float(self.speed_scale.get()))

    def apply_equalizer(self) -> None:
        if not self.vlc_ready or not self.player:
            return

        preset_map = {
            "Flat": None,
            "Rock": 17,
            "Pop": 18,
            "Techno": 12,
            "Classical": 1,
            "Dance": 7,
        }
        preset = preset_map.get(self.eq_var.get())
        if preset is None:
            self.player.set_equalizer(None)
            return

        eq = vlc.AudioEqualizer(preset)
        self.player.set_equalizer(eq)


if __name__ == "__main__":
    app = MultimediaHub()
    app.mainloop()
