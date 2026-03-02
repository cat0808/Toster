const data = window.__DATA__;
const tabs = document.querySelectorAll('.tabs button');
const sections = document.querySelectorAll('.tab');

for (const t of tabs) t.onclick = () => {
  tabs.forEach(b => b.classList.remove('active'));
  sections.forEach(s => s.classList.remove('active'));
  t.classList.add('active');
  const sec = document.getElementById(t.dataset.tab);
  sec.classList.add('active');
};

const themes = {
  'Светлая':['#eef2fb','#1b1f2b','#ffffff','#4a78d6','#355db0','#dbe4f5','#ffffff','#f8fbff','#ffffff'],
  'Тёмная':['#171b25','#eef2ff','#232a39','#5d9bff','#467ed5','#30384a','#101725','#111a2a','#1a2334'],
  'Фиолетовая':['#efe5ff','#2a1748','#ffffff','#7a46f2','#6438cc','#d9c9ff','#ffffff','#f7f1ff','#ffffff'],
  'Зелёная':['#e7f7ee','#123624','#ffffff','#1f9a64','#1b7f54','#c8ead8','#ffffff','#f3fff8','#ffffff'],
  'Оранжевая':['#fff2e6','#4a2913','#ffffff','#e97833','#c96325','#ffd9bd','#ffffff','#fff7f2','#ffffff'],
  'Бирюзовая':['#e8fbfb','#113b3d','#ffffff','#1aa3a8','#128489','#bfecee','#ffffff','#f3ffff','#ffffff'],
  'Розовая':['#ffeef6','#4a1d33','#ffffff','#d9468f','#b83273','#ffd0e5','#ffffff','#fff4fa','#ffffff'],
  'Графит':['#22252c','#f1f3f8','#2b303a','#7c8aa5','#69778f','#404756','#1f232b','#252b35','#343b49'],
  'Лимонная':['#fffde8','#3b3a12','#ffffff','#b3a700','#8f8500','#e9e28f','#ffffff','#fffef2','#ffffff']
};
document.getElementById('themeSelect').onchange = e => {
  const [bg,fg,card,acc,acc2,border,inputBg,mutedBg,btnBg]=themes[e.target.value];
  document.documentElement.style.setProperty('--bg',bg);
  document.documentElement.style.setProperty('--fg',fg);
  document.documentElement.style.setProperty('--card',card);
  document.documentElement.style.setProperty('--acc',acc);
  document.documentElement.style.setProperty('--acc-2',acc2);
  document.documentElement.style.setProperty('--border',border);
  document.documentElement.style.setProperty('--input-bg',inputBg);
  document.documentElement.style.setProperty('--muted-bg',mutedBg);
  document.documentElement.style.setProperty('--btn-bg',btnBg);
};

let aIdx=-1; const audio=document.getElementById('audioPlayer'); const mLabel=document.getElementById('musicLabel');
function setMusic(i){ if(!data.audio.length){mLabel.textContent='Аудио не найдено';return;} aIdx=(i+data.audio.length)%data.audio.length; const p=data.audio[aIdx]; mLabel.textContent='Аудио: '+p.split('/').pop(); audio.src='/media/' + p; }
document.getElementById('startMusic').onclick=()=>setMusic(0);
document.getElementById('nextMusic').onclick=()=>setMusic(aIdx<0?0:aIdx+1);
document.getElementById('prevMusic').onclick=()=>setMusic(aIdx<0?data.audio.length-1:aIdx-1);

const vSel=document.getElementById('videoSelect'); const vInfo=document.getElementById('videoInfo');
data.video.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;vSel.appendChild(o)});
vSel.onchange=()=>{vInfo.textContent='Видео: '+(vSel.value||'не выбрано')};

let iIdx=-1; const img=document.getElementById('imageView'); const iLabel=document.getElementById('imageLabel');
function setImage(i){ if(!data.images.length){iLabel.textContent='Картинки не найдены';return;} iIdx=(i+data.images.length)%data.images.length; const p=data.images[iIdx]; iLabel.textContent='Картинка: '+p.split('/').pop(); img.src='/media/' + p; }
document.getElementById('startImage').onclick=()=>setImage(0);
document.getElementById('nextImage').onclick=()=>setImage(iIdx<0?0:iIdx+1);
document.getElementById('prevImage').onclick=()=>setImage(iIdx<0?data.images.length-1:iIdx-1);

const status = document.getElementById('puzzleStatus');
const pzBtns = document.querySelectorAll('.pz');
const boards = {
  '15': document.getElementById('board15'),
  mem: document.getElementById('boardMem'),
  ttt: document.getElementById('boardTtt'),
  math: document.getElementById('boardMath'),
  reaction: document.getElementById('boardReaction')
};
let pz='15';
pzBtns.forEach(b=>b.onclick=()=>{
  pzBtns.forEach(x=>x.classList.remove('active')); b.classList.add('active'); pz=b.dataset.pz;
  Object.entries(boards).forEach(([k,v])=>v.classList.toggle('hidden',k!==pz));
  status.textContent='Выбрана игра: '+b.textContent;
});

let board=[];
function moves(e){const r=Math.floor(e/4),c=e%4,m=[];if(r>0)m.push(e-4);if(r<3)m.push(e+4);if(c>0)m.push(e-1);if(c<3)m.push(e+1);return m}
function render15(){boards['15'].innerHTML='';board.forEach((v,idx)=>{const bt=document.createElement('button');bt.textContent=v||'';bt.disabled=v===0;bt.onclick=()=>{const e=board.indexOf(0);if(!moves(e).includes(idx))return;[board[e],board[idx]]=[board[idx],board[e]];render15();if(board.every((x,i)=>x===((i+1)%16))){status.textContent='Пятнашки: победа. Нажмите «Новая игра»';}};boards['15'].appendChild(bt)})}
function new15(){board=[...Array(15).keys()].map(x=>x+1).concat(0);for(let k=0;k<200;k++){const e=board.indexOf(0);const m=moves(e);const c=m[Math.floor(Math.random()*m.length)];[board[e],board[c]]=[board[c],board[e]]}render15();status.textContent='Пятнашки: новая игра';}

let mem=[],open=[];
function renderMem(){boards.mem.innerHTML='';mem.forEach((v,i)=>{const bt=document.createElement('button');bt.textContent=open.includes(i)||v.done?v.val:'❓';bt.disabled=v.done;bt.onclick=()=>{if(open.includes(i)||v.done||open.length===2)return;open.push(i);renderMem();if(open.length===2){const [a,b]=open;if(mem[a].val===mem[b].val){mem[a].done=mem[b].done=true;open=[];renderMem();if(mem.every(x=>x.done))status.textContent='Найди пару: победа. Нажмите «Новая игра»';}else setTimeout(()=>{open=[];renderMem()},350)}};boards.mem.appendChild(bt)});}
function newMem(){const s=['🍎','🍌','🍇','🍒','🍉','🥝','🍍','🍓'];mem=[...s,...s].sort(()=>Math.random()-0.5).map(v=>({val:v,done:false}));open=[];renderMem();status.textContent='Найди пару: новая игра';}

let ttt=Array(9).fill(''), human='X', bot='O', cur='X';
const lines=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
function winner(){for(const [a,b,c] of lines) if(ttt[a]&&ttt[a]===ttt[b]&&ttt[a]===ttt[c]) return ttt[a]; return null;}
function renderTtt(){boards.ttt.innerHTML='';ttt.forEach((v,i)=>{const bt=document.createElement('button');bt.textContent=v;bt.onclick=()=>{if(ttt[i]||cur!==human)return;ttt[i]=human;cur=bot;renderTtt();const w=winner();if(w){status.textContent='Крестики-нолики: победа. Нажмите «Новая игра»';return;}if(ttt.every(Boolean)){status.textContent='Крестики-нолики: ничья. Нажмите «Новая игра»';return;}setTimeout(botMove,250)};boards.ttt.appendChild(bt)});}
function botMove(){const free=ttt.map((v,i)=>v?null:i).filter(x=>x!==null);if(!free.length)return;ttt[free[Math.floor(Math.random()*free.length)]]=bot;cur=human;renderTtt();const w=winner();if(w){status.textContent='Крестики-нолики: поражение. Нажмите «Новая игра»';return;}if(ttt.every(Boolean))status.textContent='Крестики-нолики: ничья. Нажмите «Новая игра»';}
function newTtt(){human=Math.random()<.5?'X':'O';bot=human==='X'?'O':'X';ttt=Array(9).fill('');cur='X';renderTtt();status.textContent=`Крестики-нолики: новая игра (вы ${human})`;if(cur===bot)setTimeout(botMove,250)}

let mathA=0, mathB=0, mathOp='+', mathLevel='easy', mathStreak=0, mathScore=0;
const mathQuestionEl = document.getElementById('mathQuestion');
const mathInputEl = document.getElementById('mathInput');
const mathStatsEl = document.getElementById('mathStats');

function pickByLevel(level){
  if(level==='easy') return [1,20];
  if(level==='medium') return [10,80];
  return [20,150];
}

function updateMathStats(){
  mathStatsEl.textContent = `Серия: ${mathStreak} | Очки: ${mathScore} | Уровень: ${mathLevel}`;
}

function calcAnswer(){
  if(mathOp==='+') return mathA + mathB;
  if(mathOp==='-') return mathA - mathB;
  if(mathOp==='×') return mathA * mathB;
  return Math.floor(mathA / mathB);
}

function newMath(){
  const [min,max] = pickByLevel(mathLevel);
  mathA = Math.floor(Math.random()*(max-min+1))+min;
  mathB = Math.floor(Math.random()*(max-min+1))+min;

  const ops = mathLevel==='easy' ? ['+','-'] : (mathLevel==='medium' ? ['+','-','×'] : ['+','-','×','÷']);
  mathOp = ops[Math.floor(Math.random()*ops.length)];

  if(mathOp==='÷'){
    mathB = Math.max(2, Math.floor(Math.random()*12)+2);
    const q = Math.max(2, Math.floor(Math.random()*12)+2);
    mathA = mathB * q;
  }

  mathQuestionEl.textContent = `Сколько будет ${mathA} ${mathOp} ${mathB}?`;
  mathInputEl.value='';
  updateMathStats();
  status.textContent='Математика: новая задача';
}

function setMathLevel(level){
  mathLevel = level;
  mathStreak = 0;
  status.textContent = `Математика: выбран уровень ${level}`;
  newMath();
}

document.getElementById('mathEasy').onclick = () => setMathLevel('easy');
document.getElementById('mathMedium').onclick = () => setMathLevel('medium');
document.getElementById('mathHard').onclick = () => setMathLevel('hard');

document.getElementById('mathSubmit').onclick=()=>{
  const v = Number(mathInputEl.value);
  const ans = calcAnswer();
  mathQuestionEl.classList.remove('math-success','math-error');
  void mathQuestionEl.offsetWidth;

  if(v===ans){
    mathStreak += 1;
    mathScore += (mathLevel==='easy' ? 10 : mathLevel==='medium' ? 20 : 35) + Math.min(mathStreak,10);
    status.textContent='Математика: верно! +очки, новая задача';
    mathQuestionEl.classList.add('math-success');
    updateMathStats();
    setTimeout(newMath, 350);
  } else {
    mathStreak = 0;
    mathScore = Math.max(0, mathScore - (mathLevel==='hard' ? 8 : 4));
    status.textContent=`Математика: неверно. Правильный ответ ${ans}`;
    mathQuestionEl.classList.add('math-error');
    updateMathStats();
  }
};

let reactionTimer=null, reactionStart=0;
const reactionBtn=document.getElementById('reactionBtn');
function newReaction(){reactionBtn.style.background='var(--btn-bg)'; reactionBtn.style.color='var(--fg)'; reactionBtn.disabled=true; document.getElementById('reactionText').textContent='Ждите зелёный цвет...';
  const delay=1200+Math.random()*2200; clearTimeout(reactionTimer);
  reactionTimer=setTimeout(()=>{reactionBtn.style.background='#2ea043'; reactionBtn.style.color='#fff'; reactionBtn.disabled=false; reactionStart=performance.now();},delay);
}
reactionBtn.onclick=()=>{if(reactionBtn.disabled) return; const ms=Math.round(performance.now()-reactionStart); document.getElementById('reactionText').textContent=`Ваше время реакции: ${ms} мс`; status.textContent='Реакция: завершено. Нажмите «Новая игра»'; reactionBtn.disabled=true;};

document.getElementById('newPuzzle').onclick=()=>{ if(pz==='15') new15(); else if(pz==='mem') newMem(); else if(pz==='ttt') newTtt(); else if(pz==='math') newMath(); else newReaction(); };
new15(); newMem(); newTtt(); newMath();

// ai
document.getElementById('sendAi').onclick = async ()=>{
  const prompt=document.getElementById('prompt').value.trim();
  const out=document.getElementById('answer');
  if(!prompt){out.textContent='Введите запрос'; return;}
  out.textContent='Отправка...';
  const r=await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})});
  const j=await r.json(); out.textContent=j.answer||('Ошибка: '+j.error);
};
