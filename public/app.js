const sections = [
  ['puzzles', '🧩 Головоломки'],
  ['music', '🎵 Музыка'],
  ['videos', '🎬 Видео'],
  ['photos', '🖼 Картинки'],
  ['chat', '💬 ИИ психолог']
];

const menuGrid = document.getElementById('menuGrid');
const difficulty = document.getElementById('difficulty');
const puzzleTabs = document.getElementById('puzzleTabs');
const puzzleArea = document.getElementById('puzzleArea');

const themeToggle = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('theme') || 'dark';
document.body.dataset.theme = savedTheme === 'light' ? 'light' : 'dark';
updateThemeButton();
themeToggle.onclick = () => {
  document.body.dataset.theme = document.body.dataset.theme === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', document.body.dataset.theme);
  updateThemeButton();
};
function updateThemeButton() {
  themeToggle.textContent = document.body.dataset.theme === 'light' ? '☀️ Дневная' : '🌙 Ночная';
}

sections.forEach(([id, name]) => {
  const btn = document.createElement('button');
  btn.className = 'menu-btn';
  btn.textContent = name;
  btn.onclick = () => showPanel(id);
  menuGrid.append(btn);
});

function showPanel(id) {
  document.querySelectorAll('.panel').forEach((p) => p.classList.add('hidden'));
  document.getElementById(`${id}Panel`).classList.remove('hidden');
}

async function loadMedia(type, el, onPick) {
  const res = await fetch(`/api/media/${type}`);
  const data = await res.json();
  el.innerHTML = '';
  data.items.forEach((item, idx) => {
    const b = document.createElement('button');
    b.textContent = item.name;
    b.onclick = () => onPick(item, idx, data.items);
    el.append(b);
  });
  return data.items;
}

const audio = document.getElementById('musicPlayer');
loadMedia('music', document.getElementById('musicList'), (item) => { audio.src = item.url; audio.play(); });

const video = document.getElementById('videoPlayer');
loadMedia('videos', document.getElementById('videoList'), (item) => { video.src = item.url; video.play(); });

let photos = [];
let photoIndex = 0;
const photoView = document.getElementById('photoView');
const caption = document.getElementById('photoCaption');
loadMedia('photos', document.createElement('div'), (_, idx, list) => {
  photos = list;
  photoIndex = idx;
  renderPhoto();
}).then((list) => {
  photos = list;
  renderPhoto();
});

function renderPhoto() {
  if (!photos.length) {
    caption.textContent = 'Добавьте изображения в media/photos';
    photoView.removeAttribute('src');
    return;
  }
  const p = photos[(photoIndex + photos.length) % photos.length];
  photoView.src = p.url;
  caption.textContent = p.name;
}

document.getElementById('prevPhoto').onclick = () => { photoIndex -= 1; renderPhoto(); };
document.getElementById('nextPhoto').onclick = () => { photoIndex += 1; renderPhoto(); };
let startX = 0;
photoView.addEventListener('touchstart', (e) => { startX = e.changedTouches[0].screenX; });
photoView.addEventListener('touchend', (e) => {
  const dx = e.changedTouches[0].screenX - startX;
  if (dx > 40) photoIndex -= 1;
  if (dx < -40) photoIndex += 1;
  renderPhoto();
});

const chatLog = document.getElementById('chatLog');
const addMsg = (text, cls) => {
  const d = document.createElement('div');
  d.className = `msg ${cls}`;
  d.textContent = text;
  chatLog.append(d);
  chatLog.scrollTop = chatLog.scrollHeight;
};
addMsg('Привет! Я рядом. Расскажи, что тебя тревожит.', 'bot');

document.getElementById('chatForm').onsubmit = async (e) => {
  e.preventDefault();
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;
  addMsg(text, 'user');
  input.value = '';
  try {
    const r = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const d = await r.json();
    addMsg(d.reply || d.error || 'Ошибка', 'bot');
  } catch {
    addMsg('Проблема связи с сервером.', 'bot');
  }
};

const games = {
  'Крестики-нолики': renderTicTacToe,
  'Камень-ножницы-бумага': renderRPS,
  'Быки и коровы': renderBulls,
  'Виселица': renderHangman,
  'Угадай число': renderGuess
};

Object.keys(games).forEach((name, i) => {
  const b = document.createElement('button');
  b.textContent = name;
  b.onclick = () => games[name]();
  puzzleTabs.append(b);
  if (!i) games[name]();
});

function level() { return difficulty.value; }
function botChance() { return ({ easy: 0.35, medium: 0.6, hard: 0.85 })[level()]; }

function renderTicTacToe() {
  const board = Array(9).fill('');
  const wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];

  puzzleArea.innerHTML = `
    <h3>Крестики-нолики</h3>
    <div class="puzzle-help">Правила: ставь <b>X</b> и собери 3 в ряд раньше бота. Бот играет <b>O</b>.</div>
    <div class="board"></div>
    <p id="tmsg">Твой ход.</p>
  `;

  const grid = puzzleArea.querySelector('.board');
  const msg = document.getElementById('tmsg');

  const winner = () => wins.find(([a,b,c]) => board[a] && board[a] === board[b] && board[b] === board[c]);
  const boardFull = () => board.every(Boolean);

  function draw() {
    grid.innerHTML = '';
    board.forEach((v, i) => {
      const c = document.createElement('button');
      c.className = 'cell';
      c.textContent = v;
      c.onclick = () => move(i);
      grid.append(c);
    });
  }

  function move(i) {
    if (board[i] || winner()) return;
    board[i] = 'X';
    draw();
    if (winner()) return (msg.textContent = '✅ Победа! Ты собрал линию из 3 X.');
    if (boardFull()) return (msg.textContent = '🤝 Ничья. Попробуй ещё раз!');
    botMove();
    draw();
    if (winner()) msg.textContent = '🤖 Бот победил. Не сдавайся!';
    else if (boardFull()) msg.textContent = '🤝 Ничья. Вы хорошо сыграли!';
    else msg.textContent = 'Твой ход.';
  }

  function botMove() {
    const free = board.map((v, i) => (v ? null : i)).filter((v) => v !== null);
    if (!free.length) return;
    let pick = free[Math.floor(Math.random() * free.length)];

    if (Math.random() < botChance()) {
      for (const [a,b,c] of wins) {
        const line = [a,b,c];
        const oo = line.filter((i) => board[i] === 'O');
        const empty = line.filter((i) => !board[i]);
        if (oo.length === 2 && empty.length === 1) pick = empty[0];
      }
    }
    board[pick] = 'O';
  }

  draw();
}

function renderRPS() {
  puzzleArea.innerHTML = `
    <h3>Камень-ножницы-бумага</h3>
    <div class="puzzle-help">Выбери жест: камень бьёт ножницы, ножницы бьют бумагу, бумага бьёт камень.</div>
    <div id="rps" class="game-row"></div>
    <p id="rmsg">Сделай выбор.</p>
  `;
  const opts = ['камень', 'ножницы', 'бумага'];
  const d = puzzleArea.querySelector('#rps');
  const m = puzzleArea.querySelector('#rmsg');

  opts.forEach((o) => {
    const b = document.createElement('button');
    b.textContent = o;
    b.onclick = () => {
      const bot = opts[Math.floor(Math.random() * 3)];
      const win = (o === 'камень' && bot === 'ножницы') || (o === 'ножницы' && bot === 'бумага') || (o === 'бумага' && bot === 'камень');
      const lose = !win && o !== bot;
      m.textContent = `Ты: ${o}, Бот: ${bot}. ${win ? '✅ Ты победил!' : lose ? '🤖 Победил бот.' : '🤝 Ничья.'}`;
    };
    d.append(b);
  });
}

function renderBulls() {
  const secret = String(Math.floor(1000 + Math.random() * 9000));
  puzzleArea.innerHTML = `
    <h3>Быки и коровы</h3>
    <div class="puzzle-help">Угадай 4-значное число. <b>Бык</b> — верная цифра на верном месте, <b>корова</b> — цифра есть, но место другое.</div>
    <div class="game-row">
      <input id="binput" maxlength="4" placeholder="1234" />
      <button id="bgo">Проверить</button>
    </div>
    <p id="bmsg">Введи 4 цифры.</p>
  `;

  document.getElementById('bgo').onclick = () => {
    const g = document.getElementById('binput').value.trim();
    if (!/^\d{4}$/.test(g)) {
      document.getElementById('bmsg').textContent = 'Введите ровно 4 цифры.';
      return;
    }

    let bulls = 0;
    let cows = 0;
    for (let i = 0; i < 4; i += 1) {
      if (g[i] === secret[i]) bulls += 1;
      else if (secret.includes(g[i])) cows += 1;
    }
    document.getElementById('bmsg').textContent = bulls === 4 ? '✅ Отлично! Ты угадал число.' : `Быки: ${bulls}, коровы: ${cows}`;
  };
}

function renderHangman() {
  const words = ['школа', 'дружба', 'надежда', 'улыбка', 'поддержка'];
  const word = words[Math.floor(Math.random() * words.length)];
  let hp = ({ easy: 8, medium: 6, hard: 4 })[level()];
  const open = new Set();

  puzzleArea.innerHTML = `
    <h3>Виселица</h3>
    <div class="puzzle-help">Открывай буквы в слове. Ошибки уменьшают попытки.</div>
    <div class="game-row">
      <input id="hchar" maxlength="1" placeholder="буква" />
      <button id="hgo">Проверить</button>
    </div>
    <p id="hmsg"></p>
  `;

  const msg = document.getElementById('hmsg');

  function draw() {
    const masked = word.split('').map((ch) => (open.has(ch) ? ch : '_')).join(' ');
    msg.textContent = `${masked} | Попытки: ${hp}`;
    if (!masked.includes('_')) msg.textContent = '✅ Победа! Ты открыл всё слово.';
    if (hp <= 0) msg.textContent = `🤖 Попытки закончились. Слово: ${word}`;
  }

  draw();
  document.getElementById('hgo').onclick = () => {
    const c = document.getElementById('hchar').value.toLowerCase().trim();
    if (!c || hp <= 0) return;
    if (word.includes(c)) open.add(c);
    else hp -= 1;
    draw();
  };
}

function renderGuess() {
  const max = ({ easy: 30, medium: 70, hard: 120 })[level()];
  const num = 1 + Math.floor(Math.random() * max);
  let tries = ({ easy: 8, medium: 6, hard: 5 })[level()];

  puzzleArea.innerHTML = `
    <h3>Угадай число</h3>
    <div class="puzzle-help">Я загадал число от 1 до ${max}. После каждой попытки будет подсказка: больше или меньше.</div>
    <div class="game-row">
      <input id="gnum" type="number" placeholder="Введите число" />
      <button id="ggo">Проверить</button>
    </div>
    <p id="gmsg">Попыток: ${tries}</p>
  `;

  document.getElementById('ggo').onclick = () => {
    const g = Number(document.getElementById('gnum').value);
    if (!Number.isFinite(g)) {
      document.getElementById('gmsg').textContent = 'Введите число.';
      return;
    }

    tries -= 1;
    if (g === num) {
      document.getElementById('gmsg').textContent = '✅ Отлично, ты угадал!';
      return;
    }

    if (tries <= 0) {
      document.getElementById('gmsg').textContent = `🤖 Бот выиграл. Было число ${num}.`;
      return;
    }

    document.getElementById('gmsg').textContent = `${g < num ? 'Загаданное число больше' : 'Загаданное число меньше'} | Осталось попыток: ${tries}`;
  };
}
