const sections = [
  ['puzzles', '🧩 Головоломки'],
  ['music', '🎵 Музыка'],
  ['videos', '🎬 Видео'],
  ['photos', '🖼 Картинки'],
  ['chat', '💬 ИИ психолог']
];
const menuGrid = document.getElementById('menuGrid');
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

let photos = []; let photoIndex = 0;
const photoView = document.getElementById('photoView');
const caption = document.getElementById('photoCaption');
loadMedia('photos', document.createElement('div'), (_, idx, list) => { photos = list; photoIndex = idx; renderPhoto(); }).then((list) => { photos = list; renderPhoto(); });
function renderPhoto() {
  if (!photos.length) { caption.textContent = 'Добавьте изображения в media/photos'; return; }
  const p = photos[(photoIndex + photos.length) % photos.length];
  photoView.src = p.url; caption.textContent = p.name;
}
document.getElementById('prevPhoto').onclick = () => { photoIndex--; renderPhoto(); };
document.getElementById('nextPhoto').onclick = () => { photoIndex++; renderPhoto(); };
let startX = 0;
photoView.addEventListener('touchstart', (e) => startX = e.changedTouches[0].screenX);
photoView.addEventListener('touchend', (e) => {
  const dx = e.changedTouches[0].screenX - startX;
  if (dx > 40) photoIndex--; if (dx < -40) photoIndex++; renderPhoto();
});

const chatLog = document.getElementById('chatLog');
const addMsg = (t, cls) => { const d = document.createElement('div'); d.className = `msg ${cls}`; d.textContent = t; chatLog.append(d); chatLog.scrollTop = chatLog.scrollHeight; };
addMsg('Привет! Я рядом. Расскажи, что тебя тревожит.', 'bot');
document.getElementById('chatForm').onsubmit = async (e) => {
  e.preventDefault();
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;
  addMsg(text, 'user'); input.value = '';
  try {
    const r = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text }) });
    const d = await r.json();
    addMsg(d.reply || d.error || 'Ошибка', 'bot');
  } catch { addMsg('Проблема связи с сервером.', 'bot'); }
};

const difficulty = document.getElementById('difficulty');
const puzzleTabs = document.getElementById('puzzleTabs');
const puzzleArea = document.getElementById('puzzleArea');
const games = {
  'Крестики-нолики': renderTicTacToe,
  'Камень-ножницы-бумага': renderRPS,
  'Быки и коровы': renderBulls,
  'Виселица': renderHangman,
  'Угадай число': renderGuess
};
Object.keys(games).forEach((name, i) => { const b = document.createElement('button'); b.textContent = name; b.onclick = () => games[name](); puzzleTabs.append(b); if (!i) games[name](); });

function level() { return difficulty.value; }
function botChance() { return ({ easy: 0.35, medium: 0.6, hard: 0.85 })[level()]; }

function renderTicTacToe() {
  const board = Array(9).fill('');
  puzzleArea.innerHTML = '<h3>Крестики-нолики</h3><div class="board"></div><p id="tmsg"></p>';
  const grid = puzzleArea.querySelector('.board'); const msg = document.getElementById('tmsg');
  const wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
  const winner = () => wins.find(([a,b,c])=>board[a]&&board[a]===board[b]&&board[b]===board[c]);
  function draw(){grid.innerHTML=''; board.forEach((v,i)=>{const c=document.createElement('button');c.className='cell';c.textContent=v;c.onclick=()=>move(i);grid.append(c);});}
  function move(i){if(board[i]||winner())return;board[i]='X';if(winner())return msg.textContent='Ты победил!';bot();draw();}
  function bot(){const free=board.map((v,i)=>v?null:i).filter(v=>v!==null);if(!free.length)return msg.textContent='Ничья';let pick=free[Math.floor(Math.random()*free.length)];if(Math.random()<botChance()){for(const [a,b,c] of wins){const line=[a,b,c];const o=line.filter(i=>board[i]==='O');const e=line.filter(i=>!board[i]);if(o.length===2&&e.length===1)pick=e[0];}}
  board[pick]='O'; if(winner()) msg.textContent='Бот победил';}
  draw();
}

function renderRPS(){puzzleArea.innerHTML='<h3>Камень-ножницы-бумага</h3><div id="rps"></div><p id="rmsg"></p>';const opts=['камень','ножницы','бумага'];const d=puzzleArea.querySelector('#rps');const m=puzzleArea.querySelector('#rmsg');opts.forEach(o=>{const b=document.createElement('button');b.textContent=o;b.onclick=()=>{const bot=opts[Math.floor(Math.random()*3)];const win=(o==='камень'&&bot==='ножницы')||(o==='ножницы'&&bot==='бумага')||(o==='бумага'&&bot==='камень');const lose=!win&&o!==bot;m.textContent=`Бот: ${bot}. `+(win?'Ты победил!':lose?'Бот победил':'Ничья');};d.append(b);});}

function renderBulls(){const secret=String(Math.floor(1000+Math.random()*9000));puzzleArea.innerHTML='<h3>Быки и коровы</h3><input id="binput" maxlength="4"/><button id="bgo">Проверить</button><p id="bmsg"></p>';document.getElementById('bgo').onclick=()=>{const g=document.getElementById('binput').value;let bulls=0,cows=0;for(let i=0;i<4;i++){if(g[i]===secret[i])bulls++;else if(secret.includes(g[i]))cows++;}document.getElementById('bmsg').textContent=bulls===4?'Ты угадал число!':`Быки: ${bulls}, Коровы: ${cows}`;};}

function renderHangman(){const words=['школа','дружба','надежда','улыбка','поддержка'];const word=words[Math.floor(Math.random()*words.length)];let hp=({easy:8,medium:6,hard:4})[level()];const open=new Set();puzzleArea.innerHTML='<h3>Виселица</h3><input id="hchar" maxlength="1"/><button id="hgo">Буква</button><p id="hmsg"></p>';const msg=document.getElementById('hmsg');const draw=()=>{const masked=word.split('').map(ch=>open.has(ch)?ch:'_').join(' ');msg.textContent=`${masked} | Попытки: ${hp}`;if(!masked.includes('_'))msg.textContent='Победа!';if(hp<=0)msg.textContent=`Проигрыш. Слово: ${word}`;};draw();document.getElementById('hgo').onclick=()=>{const c=document.getElementById('hchar').value.toLowerCase();if(!c||hp<=0)return;if(word.includes(c))open.add(c);else hp--;draw();};}

function renderGuess(){const max=({easy:30,medium:70,hard:120})[level()];const num=1+Math.floor(Math.random()*max);let tries=({easy:8,medium:6,hard:5})[level()];puzzleArea.innerHTML=`<h3>Угадай число (1-${max})</h3><input id="gnum" type="number"/><button id="ggo">Проверить</button><p id="gmsg"></p>`;document.getElementById('ggo').onclick=()=>{const g=Number(document.getElementById('gnum').value);tries--;if(g===num)return document.getElementById('gmsg').textContent='Отлично, угадал!';if(tries<=0)return document.getElementById('gmsg').textContent=`Бот выиграл. Было ${num}`;document.getElementById('gmsg').textContent=`${g<num?'Больше':'Меньше'} | осталось ${tries}`;};}
