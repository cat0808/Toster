const data = window.__DATA__;
const tabs = document.querySelectorAll('.tabs button');
const sections = document.querySelectorAll('.tab');

for (const t of tabs) t.onclick = () => {
  tabs.forEach(b=>b.classList.remove('active')); sections.forEach(s=>s.classList.remove('active'));
  t.classList.add('active'); document.getElementById(t.dataset.tab).classList.add('active');
};

const themes = {
  'Светлая':['#eef2fb','#1b1f2b','#fff','#4a78d6'],
  'Тёмная':['#1f2330','#f2f5ff','#222736','#5d9bff'],
  'Фиолетовая':['#efe5ff','#2a1748','#fff','#7a46f2'],
  'Зелёная':['#e7f7ee','#123624','#fff','#1f9a64'],
  'Оранжевая':['#fff2e6','#4a2913','#fff','#e97833'],
  'Бирюзовая':['#e8fbfb','#113b3d','#fff','#1aa3a8']
};
document.getElementById('themeSelect').onchange = e=>{
  const [bg,fg,card,acc]=themes[e.target.value];
  document.documentElement.style.setProperty('--bg',bg);
  document.documentElement.style.setProperty('--fg',fg);
  document.documentElement.style.setProperty('--card',card);
  document.documentElement.style.setProperty('--acc',acc);
};

// music
let aIdx=-1; const audio=document.getElementById('audioPlayer'); const mLabel=document.getElementById('musicLabel');
function setMusic(i){ if(!data.audio.length){mLabel.textContent='Аудио не найдено';return;} aIdx=(i+data.audio.length)%data.audio.length; const p=data.audio[aIdx]; mLabel.textContent='Аудио: '+p.split('/').pop(); audio.src='/media/' + p; }
document.getElementById('startMusic').onclick=()=>setMusic(0);
document.getElementById('nextMusic').onclick=()=>setMusic(aIdx<0?0:aIdx+1);
document.getElementById('prevMusic').onclick=()=>setMusic(aIdx<0?data.audio.length-1:aIdx-1);

// video
const vSel=document.getElementById('videoSelect'); const vInfo=document.getElementById('videoInfo');
data.video.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;vSel.appendChild(o)});
vSel.onchange=()=>{vInfo.textContent='Видео: '+(vSel.value||'не выбрано')};

// images
let iIdx=-1; const img=document.getElementById('imageView'); const iLabel=document.getElementById('imageLabel');
function setImage(i){ if(!data.images.length){iLabel.textContent='Картинки не найдены';return;} iIdx=(i+data.images.length)%data.images.length; const p=data.images[iIdx]; iLabel.textContent='Картинка: '+p.split('/').pop(); img.src='/media/' + p; }
document.getElementById('startImage').onclick=()=>setImage(0);
document.getElementById('nextImage').onclick=()=>setImage(iIdx<0?0:iIdx+1);
document.getElementById('prevImage').onclick=()=>setImage(iIdx<0?data.images.length-1:iIdx-1);

// puzzles
const status = document.getElementById('puzzleStatus');
const pzBtns = document.querySelectorAll('.pz');
const b15 = document.getElementById('board15');
const bMem = document.getElementById('boardMem');
const bTtt = document.getElementById('boardTtt');
let pz='15';
pzBtns.forEach(b=>b.onclick=()=>{pzBtns.forEach(x=>x.classList.remove('active'));b.classList.add('active');pz=b.dataset.pz;b15.classList.toggle('hidden',pz!=='15');bMem.classList.toggle('hidden',pz!=='mem');bTtt.classList.toggle('hidden',pz!=='ttt');status.textContent='Выбрана игра';});

let board=[];
function moves(e){const r=Math.floor(e/4),c=e%4,m=[];if(r>0)m.push(e-4);if(r<3)m.push(e+4);if(c>0)m.push(e-1);if(c<3)m.push(e+1);return m}
function render15(){b15.innerHTML='';board.forEach((v,idx)=>{const bt=document.createElement('button');bt.textContent=v||'';bt.disabled=v===0;bt.onclick=()=>{const e=board.indexOf(0);if(!moves(e).includes(idx))return;[board[e],board[idx]]=[board[idx],board[e]];render15();if(board.every((x,i)=>x===((i+1)%16))){status.textContent='Пятнашки: победа. Нажмите «Новая игра»';}};b15.appendChild(bt)});}
function new15(){board=[...Array(15).keys()].map(x=>x+1).concat(0);for(let k=0;k<200;k++){const e=board.indexOf(0);const m=moves(e);const c=m[Math.floor(Math.random()*m.length)];[board[e],board[c]]=[board[c],board[e]]}render15();status.textContent='Пятнашки: новая игра';}

let mem=[],open=[];
function renderMem(){bMem.innerHTML='';mem.forEach((v,i)=>{const bt=document.createElement('button');bt.textContent=open.includes(i)||v.done?v.val:'❓';bt.disabled=v.done;bt.onclick=()=>{if(open.includes(i)||v.done||open.length===2)return;open.push(i);renderMem();if(open.length===2){const [a,b]=open;if(mem[a].val===mem[b].val){mem[a].done=mem[b].done=true;open=[];renderMem();if(mem.every(x=>x.done))status.textContent='Найди пару: победа. Нажмите «Новая игра»';}else setTimeout(()=>{open=[];renderMem()},400)}};bMem.appendChild(bt)});}
function newMem(){const s=['🍎','🍌','🍇','🍒','🍉','🥝','🍍','🍓'];mem=[...s,...s].sort(()=>Math.random()-0.5).map(v=>({val:v,done:false}));open=[];renderMem();status.textContent='Найди пару: новая игра';}

let ttt=Array(9).fill(''), human='X', bot='O', cur='X';
const lines=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
function winner(){for(const [a,b,c] of lines) if(ttt[a]&&ttt[a]===ttt[b]&&ttt[a]===ttt[c]) return ttt[a]; return null;}
function renderTtt(){bTtt.innerHTML='';ttt.forEach((v,i)=>{const bt=document.createElement('button');bt.textContent=v;bt.onclick=()=>{if(ttt[i]||cur!==human)return;ttt[i]=human;cur=bot;renderTtt();const w=winner();if(w){status.textContent='Крестики-нолики: победа. Нажмите «Новая игра»';return;}if(ttt.every(Boolean)){status.textContent='Крестики-нолики: ничья. Нажмите «Новая игра»';return;}setTimeout(botMove,250)};bTtt.appendChild(bt)});}
function botMove(){const free=ttt.map((v,i)=>v?null:i).filter(x=>x!==null);if(!free.length)return;ttt[free[Math.floor(Math.random()*free.length)]]=bot;cur=human;renderTtt();const w=winner();if(w){status.textContent='Крестики-нолики: поражение. Нажмите «Новая игра"';return;}if(ttt.every(Boolean))status.textContent='Крестики-нолики: ничья. Нажмите «Новая игра»';}
function newTtt(){human=Math.random()<.5?'X':'O';bot=human==='X'?'O':'X';ttt=Array(9).fill('');cur='X';renderTtt();status.textContent=`Крестики-нолики: новая игра (вы ${human})`;if(cur===bot)setTimeout(botMove,250)}

document.getElementById('newPuzzle').onclick=()=>{ if(pz==='15') new15(); else if(pz==='mem') newMem(); else newTtt(); };
new15(); newMem(); newTtt();

// ai
document.getElementById('sendAi').onclick = async ()=>{
  const prompt=document.getElementById('prompt').value.trim();
  const out=document.getElementById('answer');
  if(!prompt){out.textContent='Введите запрос'; return;}
  out.textContent='Отправка...';
  const r=await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})});
  const j=await r.json(); out.textContent=j.answer||('Ошибка: '+j.error);
};
