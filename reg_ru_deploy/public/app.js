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
const newPuzzleGameBtn = document.getElementById('newPuzzleGame');

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
  'Угадай число': renderGuess,
  'Память: Найди пару': renderMemoryPairs
};

let currentGameName = 'Крестики-нолики';

const generationState = {
  hangmanLastByDifficulty: {},
  bullsLastByDifficulty: {},
  guessLastByDifficulty: {}
};

function randomFromPoolWithoutImmediateRepeat(pool, lastValue) {
  if (!Array.isArray(pool) || pool.length === 0) return '';
  if (pool.length === 1) return pool[0];
  let candidate = pool[Math.floor(Math.random() * pool.length)];
  let guard = 0;
  while (candidate === lastValue && guard < 20) {
    candidate = pool[Math.floor(Math.random() * pool.length)];
    guard += 1;
  }
  return candidate;
}

function buildUniqueDigitsNumber(length) {
  const digits = ['0','1','2','3','4','5','6','7','8','9'];
  const firstPool = digits.slice(1);
  const picked = [firstPool.splice(Math.floor(Math.random() * firstPool.length), 1)[0]];
  while (picked.length < length) {
    const idx = Math.floor(Math.random() * digits.length);
    const next = digits[idx];
    if (!picked.includes(next)) picked.push(next);
  }
  return picked.join('');
}

function buildRandomNumberInRange(min, max) {
  return min + Math.floor(Math.random() * (max - min + 1));
}

function runCurrentGame() {
  const renderer = games[currentGameName];
  if (renderer) renderer();
}

Object.keys(games).forEach((name, i) => {
  const b = document.createElement('button');
  b.textContent = name;
  b.onclick = () => {
    currentGameName = name;
    runCurrentGame();
  };
  puzzleTabs.append(b);
  if (!i) runCurrentGame();
});

newPuzzleGameBtn.onclick = () => runCurrentGame();
difficulty.onchange = () => runCurrentGame();

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
  const settings = {
    easy: { len: 3 },
    medium: { len: 4 },
    hard: { len: 5 }
  }[level()];

  let secret = buildUniqueDigitsNumber(settings.len);
  while (secret === generationState.bullsLastByDifficulty[level()]) {
    secret = buildUniqueDigitsNumber(settings.len);
  }
  generationState.bullsLastByDifficulty[level()] = secret;

  puzzleArea.innerHTML = `
    <h3>Быки и коровы</h3>
    <div class="puzzle-help">Угадай ${settings.len}-значное число из разных цифр. <b>Бык</b> — верная цифра на верном месте, <b>корова</b> — цифра есть, но место другое.</div>
    <div class="game-row">
      <input id="binput" maxlength="${settings.len}" placeholder="${'12345'.slice(0, settings.len)}" />
      <button id="bgo">Проверить</button>
    </div>
    <p id="bmsg">Введи ${settings.len} цифры.</p>
  `;

  document.getElementById('bgo').onclick = () => {
    const g = document.getElementById('binput').value.trim();
    if (!new RegExp(`^\\d{${settings.len}}$`).test(g)) {
      document.getElementById('bmsg').textContent = `Введите ровно ${settings.len} цифры.`;
      return;
    }

    let bulls = 0;
    let cows = 0;
    for (let i = 0; i < settings.len; i += 1) {
      if (g[i] === secret[i]) bulls += 1;
      else if (secret.includes(g[i])) cows += 1;
    }
    document.getElementById('bmsg').textContent = bulls === settings.len ? '✅ Отлично! Ты угадал число.' : `Быки: ${bulls}, коровы: ${cows}`;
  };
}

function renderHangman() {
  const wordsByDifficulty = {
    easy: ['мир', 'кот', 'школа', 'дружба', 'улыбка'],
    medium: ['надежда', 'поддержка', 'каникулы', 'доброта', 'спокойствие'],
    hard: ['самооценка', 'вдохновение', 'взаимопомощь', 'уверенность', 'дисциплина']
  };

  function startHangmanGame() {
    const pool = wordsByDifficulty[level()];
    const word = randomFromPoolWithoutImmediateRepeat(pool, generationState.hangmanLastByDifficulty[level()]);
    generationState.hangmanLastByDifficulty[level()] = word;
    const maxHp = ({ easy: 8, medium: 6, hard: 4 })[level()];
    let hp = maxHp;
    const open = new Set();
    const used = new Set();

    puzzleArea.innerHTML = `
      <h3>Виселица</h3>
      <div class="puzzle-help">Открывай буквы в слове. Ошибки уменьшают попытки. Нажми «Новая игра», чтобы загадать другое слово.</div>
      <div class="hangman-wrap">
        <svg id="hangmanSvg" viewBox="0 0 120 140" aria-label="Человечек виселицы">
          <line x1="10" y1="130" x2="70" y2="130" class="gallow" />
          <line x1="25" y1="130" x2="25" y2="15" class="gallow" />
          <line x1="25" y1="15" x2="75" y2="15" class="gallow" />
          <line x1="75" y1="15" x2="75" y2="30" class="gallow" />
          <circle cx="75" cy="40" r="10" class="hang-part head" />
          <line x1="75" y1="50" x2="75" y2="85" class="hang-part body" />
          <line x1="75" y1="60" x2="60" y2="75" class="hang-part arm-l" />
          <line x1="75" y1="60" x2="90" y2="75" class="hang-part arm-r" />
          <line x1="75" y1="85" x2="62" y2="105" class="hang-part leg-l" />
          <line x1="75" y1="85" x2="88" y2="105" class="hang-part leg-r" />
        </svg>
      </div>
      <div class="game-row">
        <input id="hchar" maxlength="1" placeholder="буква" />
        <button id="hgo">Проверить</button>
      </div>
      <p id="hused">Использованные буквы: —</p>
      <p id="hmsg"></p>
    `;

    const msg = document.getElementById('hmsg');
    const usedEl = document.getElementById('hused');
    const hangmanSvg = document.getElementById('hangmanSvg');
    const parts = ['head', 'body', 'arm-l', 'arm-r', 'leg-l', 'leg-r'];

    function updateHangman() {
      const wrong = maxHp - hp;
      const reveal = Math.min(parts.length, Math.ceil((wrong / maxHp) * parts.length));
      parts.forEach((name, idx) => {
        const el = hangmanSvg.querySelector(`.${name}`);
        if (el) el.style.opacity = idx < reveal ? '1' : '0';
      });
    }

    function draw() {
      const masked = word.split('').map((ch) => (open.has(ch) ? ch : '_')).join(' ');
      usedEl.textContent = `Использованные буквы: ${used.size ? [...used].join(', ') : '—'}`;
      msg.textContent = `${masked} | Попытки: ${hp}`;
      if (!masked.includes('_')) msg.textContent = '✅ Победа! Ты открыл всё слово.';
      if (hp <= 0) msg.textContent = `🤖 Попытки закончились. Слово: ${word}`;
      updateHangman();
    }

    draw();

    document.getElementById('hgo').onclick = () => {
      const c = document.getElementById('hchar').value.toLowerCase().trim();
      if (!c || hp <= 0) return;
      if (used.has(c)) {
        msg.textContent = `Буква «${c}» уже была. Попробуй другую.`;
        return;
      }
      used.add(c);
      if (word.includes(c)) open.add(c);
      else hp -= 1;
      draw();
    };

  }

  startHangmanGame();
}


function renderGuess() {
  const settings = ({
    easy: { min: 1, max: 30, tries: 8 },
    medium: { min: 10, max: 90, tries: 6 },
    hard: { min: 50, max: 200, tries: 5 }
  })[level()];

  let num = buildRandomNumberInRange(settings.min, settings.max);
  while (num === generationState.guessLastByDifficulty[level()]) {
    num = buildRandomNumberInRange(settings.min, settings.max);
  }
  generationState.guessLastByDifficulty[level()] = num;

  let tries = settings.tries;

  puzzleArea.innerHTML = `
    <h3>Угадай число</h3>
    <div class="puzzle-help">Я загадал число от ${settings.min} до ${settings.max}. После каждой попытки будет подсказка: больше или меньше.</div>
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


function renderMemoryPairs() {
  const cfg = ({
    easy: { pairs: 6, symbols: ['🍎','🌟','🎈','🐬','🍀','🚲','🎵','🦋'] },
    medium: { pairs: 8, symbols: ['🍎','🌟','🎈','🐬','🍀','🚲','🎵','🦋','⚽','🧩'] },
    hard: { pairs: 10, symbols: ['🍎','🌟','🎈','🐬','🍀','🚲','🎵','🦋','⚽','🧩','🎯','🌈','🧠','📚'] }
  })[level()];

  const picked = cfg.symbols.slice(0, cfg.pairs);
  const deck = [...picked, ...picked]
    .sort(() => Math.random() - 0.5)
    .map((value, idx) => ({ id: idx, value, open: false, done: false }));

  let first = null;
  let lock = false;
  let playerScore = 0;
  let botScore = 0;
  let playerTurn = true;

  puzzleArea.innerHTML = `
    <h3>Память: Найди пару</h3>
    <div class="puzzle-help">Открывай карточки и собирай пары одинаковых символов. Ты играешь против бота: кто соберёт больше пар, тот победил.</div>
    <div id="memoryBoard" class="memory-board"></div>
    <p id="memoryMsg"></p>
  `;

  const board = document.getElementById('memoryBoard');
  const msg = document.getElementById('memoryMsg');
  const cols = Math.ceil(Math.sqrt(deck.length));
  board.style.setProperty('--cols', String(cols));

  function updateStatus(extra = '') {
    msg.textContent = `${playerTurn ? 'Твой ход' : 'Ход бота'} | Ты: ${playerScore} пар, Бот: ${botScore} пар${extra ? ` | ${extra}` : ''}`;
  }

  function renderBoard() {
    board.innerHTML = '';
    deck.forEach((card, i) => {
      const b = document.createElement('button');
      b.className = `memory-card ${card.done ? 'done' : ''}`;
      b.textContent = (card.open || card.done) ? card.value : '❔';
      b.disabled = card.done || lock || !playerTurn;
      b.onclick = () => openCard(i);
      board.append(b);
    });
  }

  function finishIfNeeded() {
    const donePairs = deck.filter((c) => c.done).length / 2;
    if (donePairs !== cfg.pairs) return false;
    if (playerScore > botScore) updateStatus('✅ Ты победил!');
    else if (playerScore < botScore) updateStatus('🤖 Победил бот.');
    else updateStatus('🤝 Ничья.');
    return true;
  }

  function resolvePair(i1, i2) {
    lock = true;
    const a = deck[i1];
    const b = deck[i2];
    const matched = a.value === b.value;

    setTimeout(() => {
      if (matched) {
        a.done = true;
        b.done = true;
        if (playerTurn) playerScore += 1;
        else botScore += 1;
      } else {
        a.open = false;
        b.open = false;
        playerTurn = !playerTurn;
      }

      first = null;
      lock = false;
      renderBoard();
      if (finishIfNeeded()) return;
      updateStatus();
      if (!playerTurn) botTurn();
    }, 550);
  }

  function openCard(i) {
    const card = deck[i];
    if (lock || card.done || card.open || !playerTurn) return;
    card.open = true;
    renderBoard();

    if (first === null) {
      first = i;
      updateStatus('Выбери вторую карточку');
      return;
    }

    resolvePair(first, i);
  }

  function botTurn() {
    const available = deck
      .map((c, i) => ({ ...c, i }))
      .filter((c) => !c.done && !c.open)
      .map((c) => c.i);
    if (available.length < 2 || lock) return;

    const i1 = available[Math.floor(Math.random() * available.length)];
    const rest = available.filter((i) => i !== i1);
    const i2 = rest[Math.floor(Math.random() * rest.length)];

    deck[i1].open = true;
    renderBoard();
    setTimeout(() => {
      deck[i2].open = true;
      renderBoard();
      resolvePair(i1, i2);
    }, 450);
  }

  renderBoard();
  updateStatus();
}

