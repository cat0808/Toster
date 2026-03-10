document.addEventListener('DOMContentLoaded', () => {
const sections = [
  ['puzzles', '🧩 Головоломки'],
  ['music', '🎵 Музыка'],
  ['videos', '🎬 Видео'],
  ['photos', '🖼 Картинки'],
  ['chat', '💬 ИИ психолог']
];

let menu = document.getElementById('menu');
if (!menu) {
  menu = document.createElement('nav');
  menu.id = 'menu';
  menu.className = 'menu';
  document.body.prepend(menu);
}
sections.forEach(([id, title]) => {
  const b = document.createElement('button');
  b.textContent = title;
  b.onclick = () => show(id);
  appendIfExists(menu, b);
});

function show(id) {
  document.querySelectorAll('.panel').forEach((p) => p.classList.add('hidden'));
  const panel = document.getElementById(`${id}Panel`);
  if (panel) panel.classList.remove('hidden');
}


function appendIfExists(parent, child) {
  if (parent && child) parent.append(child);
}

const themeToggle = document.getElementById('themeToggle');
document.body.dataset.theme = localStorage.getItem('theme') || 'dark';
function syncThemeBtn() { if (themeToggle) themeToggle.textContent = document.body.dataset.theme === 'light' ? '☀️ Дневная' : '🌙 Ночная'; }
syncThemeBtn();
if (themeToggle) {
  themeToggle.onclick = () => {
    document.body.dataset.theme = document.body.dataset.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', document.body.dataset.theme);
    syncThemeBtn();
  };
}

async function fetchJson(url) {
  const r = await fetch(url);
  return r.json();
}

const RUTUBE_VIDEOS = [
  { title: 'Спокойная музыка и природа', embed: 'https://rutube.ru/play/embed/5f3b6fbe9b2b2ba44ca6203f7af579a3/' },
  { title: 'Расслабляющее видео для отдыха', embed: 'https://rutube.ru/play/embed/6a4d1f7c01f43084f0ddf7d77be66ef4/' },
  { title: 'Мотивационное видео для школьников', embed: 'https://rutube.ru/play/embed/8ad0f4e6df4e73f6efd6a838f438e2d5/' }
];

(async function initMedia() {
  const manifest = await fetchJson('./media-manifest.json').catch(() => ({ music: [], photos: [] }));

  const player = document.getElementById('musicPlayer');
  const list = document.getElementById('musicList');
  manifest.music.forEach((m) => {
    const b = document.createElement('button');
    b.textContent = m;
    b.onclick = () => { if (!player) return; player.src = m; player.play(); };
    appendIfExists(list, b);
  });

  const feed = document.getElementById('photoFeed');
  manifest.photos.forEach((p) => {
    const fig = document.createElement('figure');
    fig.innerHTML = `<img src="${p}" alt="photo"/><figcaption>${p}</figcaption>`;
    appendIfExists(feed, fig);
  });

  const vlist = document.getElementById('rutubeList');
  const frame = document.getElementById('rutubeFrame');
  RUTUBE_VIDEOS.forEach((v, i) => {
    const b = document.createElement('button');
    b.textContent = v.title;
    b.onclick = () => { if (frame) frame.src = v.embed; };
    appendIfExists(vlist, b);
    if (i === 0 && frame) frame.src = v.embed;
  });
})();

const AI_BACKEND_URL = window.AI_BACKEND_URL || ''; // empty means same origin
const chatLog = document.getElementById('chatLog');
function addMsg(text, cls) {
  const d = document.createElement('div');
  d.className = `msg ${cls}`;
  d.textContent = text;
  appendIfExists(chatLog, d);
  if (chatLog) chatLog.scrollTop = chatLog.scrollHeight;
}
if (chatLog) addMsg('Привет! Я рядом 🌿', 'bot');

const chatForm = document.getElementById('chatForm');
if (chatForm) {
chatForm.onsubmit = async (e) => {
  e.preventDefault();
  const input = document.getElementById('chatInput');
  const text = input ? input.value.trim() : '';
  if (!text) return;
  addMsg(text, 'user');
  input.value = '';
  const chatUrl = `${AI_BACKEND_URL}/api/chat`;
  try {
    const r = await fetch(chatUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text }) });
    const data = await r.json();
    addMsg(data.reply || 'Ошибка', 'bot');
  } catch (err) {
    addMsg('Сервер чата недоступен. Проверьте AI_BACKEND_URL или доступность /api/chat.', 'bot');
  }
};
}

const difficulty = document.getElementById('difficulty');
const tabs = document.getElementById('puzzleTabs');
const area = document.getElementById('puzzleArea');
const games = {
  'Крестики-нолики': tic,
  'Камень-ножницы-бумага': rps,
  'Виселица': hangman,
  'Угадай число': guess,
  'Память: Найди пару': memory,
};
let current = Object.keys(games)[0];

Object.keys(games).forEach((name) => {
  const b = document.createElement('button');
  b.textContent = name;
  b.onclick = () => { current = name; games[current](); };
  appendIfExists(tabs, b);
});

const newGameBtn = document.getElementById('newGame');
if (newGameBtn) newGameBtn.onclick = () => games[current]();
if (difficulty) difficulty.onchange = () => games[current]();

if (tabs && area && difficulty) games[current]();

function tic() {
  const b = Array(9).fill('');
  const win = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
  area.innerHTML = '<div class="board"></div><p id="m"></p>';
  const board = area.querySelector('.board');
  const msg = area.querySelector('#m');
  const w = () => win.some(([a,c,d]) => b[a] && b[a]===b[c] && b[c]===b[d]);
  const draw = () => { board.innerHTML=''; b.forEach((v,i)=>{const c=document.createElement('button'); c.className='cell'; c.textContent=v; c.onclick=()=>mv(i); board.append(c);}); };
  const mv = (i)=>{ if(b[i]||w())return; b[i]='X'; if(w()) return msg.textContent='Победа!'; bot(); draw(); };
  const bot = ()=>{ const f=b.map((v,i)=>v?'':i).filter(x=>x!==''); if(!f.length){msg.textContent='Ничья'; return;} b[f[Math.floor(Math.random()*f.length)]]='O'; if(w()) msg.textContent='Бот победил';};
  draw();
}

function rps() {
  area.innerHTML = '<div class="row" id="r"></div><p id="m"></p>';
  const opts=['камень','ножницы','бумага']; const r=document.getElementById('r'); const m=document.getElementById('m');
  opts.forEach(o=>{const b=document.createElement('button');b.textContent=o;b.onclick=()=>{const q=opts[Math.floor(Math.random()*3)];m.textContent=`Ты: ${o}, бот: ${q}`};r.append(b)});
}

function hangman() {
  const words={easy:['дом','мир','кот'],medium:['дружба','улыбка','надежда'],hard:['вдохновение','самооценка','уверенность']}[difficulty.value];
  const word=words[Math.floor(Math.random()*words.length)]; let hp={easy:8,medium:6,hard:4}[difficulty.value]; const open=new Set();
  area.innerHTML='<input id="h" maxlength="1"/><button id="go">Буква</button><p id="m"></p>';
  const m=document.getElementById('m'); const draw=()=>{const s=word.split('').map(c=>open.has(c)?c:'_').join(' ');m.textContent=`${s} | попытки ${hp}`};
  draw(); document.getElementById('go').onclick=()=>{const c=document.getElementById('h').value.toLowerCase();if(word.includes(c))open.add(c);else hp--;draw();};
}

function guess() {
  const cfg={easy:[1,30,8],medium:[10,90,6],hard:[50,200,5]}[difficulty.value]; const n=cfg[0]+Math.floor(Math.random()*(cfg[1]-cfg[0]+1)); let t=cfg[2];
  area.innerHTML=`<p>Число от ${cfg[0]} до ${cfg[1]}</p><input id="g" type="number"/><button id="go">Проверить</button><p id="m"></p>`;
  document.getElementById('go').onclick=()=>{const v=Number(document.getElementById('g').value);t--;document.getElementById('m').textContent=v===n?'Угадал!':t<=0?`Проигрыш: ${n}`:(v<n?'Больше':'Меньше')+` | осталось ${t}`};
}

function memory() {
  const pairs={easy:6,medium:8,hard:10}[difficulty.value]; const all=['🍎','🌟','🎈','🐬','🍀','🚲','🎵','🦋','⚽','🧩','🎯','🌈'];
  const d=[...all.slice(0,pairs),...all.slice(0,pairs)].sort(()=>Math.random()-0.5).map(v=>({v,o:false,d:false}));
  let first=-1, lock=false, player=true, ps=0, bs=0;
  area.innerHTML='<div id="mb" class="memory-board"></div><p id="m"></p>';
  const mb=document.getElementById('mb'); mb.style.setProperty('--cols', String(Math.ceil(Math.sqrt(d.length)))); const m=document.getElementById('m');
  const status=()=>m.textContent=`${player?'Твой':'Бота'} ход | Ты ${ps} : ${bs} Бот`;
  const render=()=>{mb.innerHTML='';d.forEach((c,i)=>{const b=document.createElement('button');b.className='memory-card';b.disabled=c.d||lock||!player;b.textContent=(c.o||c.d)?c.v:'❔';b.onclick=()=>open(i);mb.append(b)});status();};
  const done=()=>d.every(x=>x.d);
  const resolve=(a,b)=>{lock=true;setTimeout(()=>{if(d[a].v===d[b].v){d[a].d=d[b].d=true; player?ps++:bs++;}else{d[a].o=d[b].o=false;player=!player;} first=-1; lock=false; render(); if(done()) m.textContent=ps===bs?'Ничья':ps>bs?'Ты победил':'Бот победил'; if(!player&&!done()) bot();},450)};
  const open=(i)=>{if(lock||d[i].o||d[i].d)return; d[i].o=true; render(); if(first<0){first=i; return;} resolve(first,i);};
  const bot=()=>{const ids=d.map((c,i)=>!c.d&&!c.o?i:null).filter(i=>i!==null); if(ids.length<2) return; const a=ids[Math.floor(Math.random()*ids.length)]; const rest=ids.filter(x=>x!==a); const b=rest[Math.floor(Math.random()*rest.length)]; d[a].o=true; d[b].o=true; render(); resolve(a,b);};
  render();
}

});
