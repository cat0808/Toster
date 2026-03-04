const data = window.__DATA__;
const tabs = document.querySelectorAll('.tabs button');
const sections = document.querySelectorAll('.tab');

for (const t of tabs) t.onclick = () => {
  tabs.forEach(b => b.classList.remove('active'));
  sections.forEach(s => s.classList.remove('active'));
  t.classList.add('active');
  document.getElementById(t.dataset.tab).classList.add('active');
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
  'Лимонная':['#fffde8','#3b3a12','#ffffff','#b3a700','#8f8500','#e9e28f','#ffffff','#fffef2','#ffffff'],
  'Синяя ночь':['#0f172a','#e2e8f0','#172033','#3b82f6','#2563eb','#334155','#111827','#1e293b','#1b2538']
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

const vSel=document.getElementById('videoSelect'); const vInfo=document.getElementById('videoInfo'); const vPlayer=document.getElementById('videoPlayer');
function setVideo(path){
  if(!path){vPlayer.removeAttribute('src'); vPlayer.load(); return;}
  const encoded = path.split('/').map(encodeURIComponent).join('/');
  vPlayer.src='/media/' + encoded;
  vPlayer.load();
}
if(!data.video.length){
  vInfo.textContent='Видео не найдено';
  setVideo('');
}else{
  data.video.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v.split('/').pop();vSel.appendChild(o)});
  vSel.onchange=()=>{vInfo.textContent='Видео: '+(vSel.value||'не выбрано'); setVideo(vSel.value);};
  vSel.value = data.video[0];
  vSel.onchange();
}
vPlayer.onerror=()=>{vInfo.textContent='Не удалось загрузить видео (проверьте формат/кодек)';};

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
const size15Controls = document.getElementById('size15Controls');
const sizeMemControls = document.getElementById('sizeMemControls');
let pz='15';
pzBtns.forEach(b=>b.onclick=()=>{
  pzBtns.forEach(x=>x.classList.remove('active')); b.classList.add('active'); pz=b.dataset.pz;
  Object.entries(boards).forEach(([k,v])=>v.classList.toggle('hidden',k!==pz));
  size15Controls.classList.toggle('hidden', pz!=='15');
  sizeMemControls.classList.toggle('hidden', pz!=='mem');
  status.textContent='Выбрана игра: '+b.textContent;
});

// 15 puzzle
let board=[];
let size15=4;
const size15Btns={
  3: document.getElementById('size15_3'),
  4: document.getElementById('size15_4'),
  5: document.getElementById('size15_5')
};
function moves(e){const r=Math.floor(e/size15),c=e%size15,m=[];if(r>0)m.push(e-size15);if(r<size15-1)m.push(e+size15);if(c>0)m.push(e-1);if(c<size15-1)m.push(e+1);return m}
function refresh15Classes(){
  boards['15'].classList.toggle('size-3', size15===3);
  boards['15'].classList.toggle('size-4', size15===4);
  boards['15'].classList.toggle('size-5', size15===5);
  Object.entries(size15Btns).forEach(([k,btn])=>btn.classList.toggle('active', Number(k)===size15));
}
function render15(){boards['15'].innerHTML='';board.forEach((v,idx)=>{const bt=document.createElement('button');bt.textContent=v||'';bt.disabled=v===0;bt.onclick=()=>{const e=board.indexOf(0);if(!moves(e).includes(idx))return;[board[e],board[idx]]=[board[idx],board[e]];render15();if(board.every((x,i)=>x===((i+1)%(size15*size15)))){status.textContent='Пятнашки: победа. Нажмите «Новая игра»';}};boards['15'].appendChild(bt)})}
function new15(){const total=size15*size15;board=[...Array(total-1).keys()].map(x=>x+1).concat(0);for(let k=0;k<200+size15*70;k++){const e=board.indexOf(0);const m=moves(e);const c=m[Math.floor(Math.random()*m.length)];[board[e],board[c]]=[board[c],board[e]]}refresh15Classes();render15();status.textContent=`Пятнашки: новая игра (${size15}×${size15})`;}
Object.entries(size15Btns).forEach(([k,btn])=>btn.onclick=()=>{size15=Number(k);new15();});

// Memory with size selector
let mem=[],open=[];
let memSize = 4; // 4x4 (8 pairs) or 6x6 (18 pairs)
const mem4Btn = document.getElementById('memSize4');
const mem6Btn = document.getElementById('memSize6');
function refreshMemClasses(){
  mem4Btn.classList.toggle('active', memSize===4);
  mem6Btn.classList.toggle('active', memSize===6);
  boards.mem.classList.toggle('size-4', memSize===4);
  boards.mem.classList.toggle('size-6', memSize===6);
}
mem4Btn.onclick=()=>{memSize=4;newMem();};
mem6Btn.onclick=()=>{memSize=6;newMem();};

function renderMem(){
  boards.mem.innerHTML='';
  mem.forEach((v,i)=>{
    const bt=document.createElement('button');
    bt.textContent=open.includes(i)||v.done?v.val:'❓';
    bt.disabled=v.done;
    bt.onclick=()=>{
      if(open.includes(i)||v.done||open.length===2) return;
      open.push(i); renderMem();
      if(open.length===2){
        const [a,b]=open;
        if(mem[a].val===mem[b].val){
          mem[a].done=mem[b].done=true;
          open=[]; renderMem();
          if(mem.every(x=>x.done)) status.textContent='Найди пару: победа. Нажмите «Новая игра»';
        } else setTimeout(()=>{open=[]; renderMem();},350);
      }
    };
    boards.mem.appendChild(bt);
  });
}
function newMem(){
  const symbols = ['🍎','🍌','🍇','🍒','🍉','🥝','🍍','🍓','🍋','🥥','🍑','🍐','🥕','🌽','🍅','🍄','🍪','🍩'];
  const pairs = memSize===4 ? 8 : 18;
  const chosen = symbols.slice(0, pairs);
  mem=[...chosen,...chosen].sort(()=>Math.random()-0.5).map(v=>({val:v,done:false}));
  open=[];
  refreshMemClasses();
  renderMem();
  status.textContent=`Найди пару: новая игра (${memSize}×${memSize})`;
}

// Tic-tac-toe
let ttt=Array(9).fill(''), human='X', bot='O', cur='X';
const lines=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
function winner(){for(const [a,b,c] of lines) if(ttt[a]&&ttt[a]===ttt[b]&&ttt[a]===ttt[c]) return ttt[a]; return null;}
function renderTtt(){boards.ttt.innerHTML='';ttt.forEach((v,i)=>{const bt=document.createElement('button');bt.textContent=v;bt.onclick=()=>{if(ttt[i]||cur!==human)return;ttt[i]=human;cur=bot;renderTtt();const w=winner();if(w){status.textContent='Крестики-нолики: победа. Нажмите «Новая игра»';return;}if(ttt.every(Boolean)){status.textContent='Крестики-нолики: ничья. Нажмите «Новая игра»';return;}setTimeout(botMove,250)};boards.ttt.appendChild(bt)});}
function botMove(){const free=ttt.map((v,i)=>v?null:i).filter(x=>x!==null);if(!free.length)return;ttt[free[Math.floor(Math.random()*free.length)]]=bot;cur=human;renderTtt();const w=winner();if(w){status.textContent='Крестики-нолики: поражение. Нажмите «Новая игра»';return;}if(ttt.every(Boolean))status.textContent='Крестики-нолики: ничья. Нажмите «Новая игра»';}
function newTtt(){human=Math.random()<.5?'X':'O';bot=human==='X'?'O':'X';ttt=Array(9).fill('');cur='X';renderTtt();status.textContent=`Крестики-нолики: новая игра (вы ${human})`;if(cur===bot)setTimeout(botMove,250)}

// Improved Math puzzle
let mathA=0, mathB=0, mathOp='+', mathLevel='easy', mathStreak=0, mathScore=0;
const mathQuestionEl = document.getElementById('mathQuestion');
const mathInputEl = document.getElementById('mathInput');
const mathStatsEl = document.getElementById('mathStats');
const lvlBtns = {
  easy: document.getElementById('mathEasy'),
  medium: document.getElementById('mathMedium'),
  hard: document.getElementById('mathHard')
};

function setLevelHighlight(){
  Object.entries(lvlBtns).forEach(([lvl,btn]) => btn.classList.toggle('active', lvl===mathLevel));
}
function pickByLevel(level){ if(level==='easy') return [1,20]; if(level==='medium') return [10,80]; return [20,150]; }
function updateMathStats(){ mathStatsEl.textContent = `Серия: ${mathStreak} | Очки: ${mathScore} | Уровень: ${mathLevel}`; }
function calcAnswer(){ if(mathOp==='+') return mathA+mathB; if(mathOp==='-') return mathA-mathB; if(mathOp==='×') return mathA*mathB; return Math.floor(mathA/mathB); }

function newMath(){
  const [min,max] = pickByLevel(mathLevel);
  mathA = Math.floor(Math.random()*(max-min+1))+min;
  mathB = Math.floor(Math.random()*(max-min+1))+min;
  const ops = mathLevel==='easy' ? ['+','-'] : (mathLevel==='medium' ? ['+','-','×'] : ['+','-','×','÷']);
  mathOp = ops[Math.floor(Math.random()*ops.length)];
  if(mathOp==='÷'){ mathB = Math.max(2, Math.floor(Math.random()*12)+2); const q = Math.max(2, Math.floor(Math.random()*12)+2); mathA = mathB*q; }
  mathQuestionEl.textContent = `Сколько будет ${mathA} ${mathOp} ${mathB}?`;
  mathInputEl.value='';
  updateMathStats();
  setLevelHighlight();
  status.textContent='Математика: новая задача';
}

function setMathLevel(level){ mathLevel=level; mathStreak=0; status.textContent=`Математика: выбран уровень ${level}`; newMath(); }
lvlBtns.easy.onclick=()=>setMathLevel('easy');
lvlBtns.medium.onclick=()=>setMathLevel('medium');
lvlBtns.hard.onclick=()=>setMathLevel('hard');

document.getElementById('mathSubmit').onclick=()=>{
  const v = Number(mathInputEl.value);
  const ans = calcAnswer();
  mathQuestionEl.classList.remove('math-success','math-error');
  void mathQuestionEl.offsetWidth;
  if(v===ans){
    mathStreak += 1;
    mathScore += (mathLevel==='easy'?10:mathLevel==='medium'?20:35) + Math.min(mathStreak,10);
    status.textContent='Математика: верно! +очки, новая задача';
    mathQuestionEl.classList.add('math-success');
    updateMathStats();
    setTimeout(newMath, 350);
  } else {
    mathStreak = 0;
    mathScore = Math.max(0, mathScore - (mathLevel==='hard'?8:4));
    status.textContent=`Математика: неверно. Правильный ответ ${ans}`;
    mathQuestionEl.classList.add('math-error');
    updateMathStats();
  }
};

// Improved Reaction: starts paused
let reactionTimer=null, reactionStart=0, reactionState='paused';
const reactionBtn=document.getElementById('reactionBtn');
const reactionText=document.getElementById('reactionText');
const reactionStartBtn=document.getElementById('reactionStart');
const reactionResetBtn=document.getElementById('reactionReset');

function setReactionVisual(state){
  reactionBtn.classList.remove('waiting','ready','too-early');
  if(state==='waiting') reactionBtn.classList.add('waiting');
  if(state==='ready') reactionBtn.classList.add('ready');
  if(state==='too-early') reactionBtn.classList.add('too-early');
}

function reactionPause(){
  clearTimeout(reactionTimer);
  reactionState='paused';
  reactionBtn.disabled=true;
  setReactionVisual('');
  reactionText.textContent='Игра на паузе. Нажмите «Старт»';
}

function newReaction(){
  clearTimeout(reactionTimer);
  reactionState='waiting';
  reactionBtn.disabled=false;
  setReactionVisual('waiting');
  reactionText.textContent='Ждите зелёный цвет...';
  const delay=1200+Math.random()*2500;
  reactionTimer=setTimeout(()=>{
    reactionState='ready';
    setReactionVisual('ready');
    reactionText.textContent='ЖМИ!';
    reactionStart=performance.now();
  },delay);
}

reactionStartBtn.onclick = () => { status.textContent='Реакция: старт'; newReaction(); };
reactionResetBtn.onclick = () => { status.textContent='Реакция: пауза'; reactionPause(); };

reactionBtn.onclick=()=>{
  if(reactionState==='paused') return;
  if(reactionState==='waiting'){
    clearTimeout(reactionTimer);
    reactionState='paused';
    setReactionVisual('too-early');
    reactionText.textContent='Слишком рано! Нажмите «Старт»';
    status.textContent='Реакция: фальстарт';
    setTimeout(()=>setReactionVisual(''), 500);
    return;
  }
  if(reactionState==='ready'){
    const ms=Math.round(performance.now()-reactionStart);
    reactionState='paused';
    setReactionVisual('');
    reactionText.textContent=`Ваше время реакции: ${ms} мс`;
    status.textContent='Реакция: завершено. Нажмите «Старт»';
  }
};

document.getElementById('newPuzzle').onclick=()=>{
  if(pz==='15') new15();
  else if(pz==='mem') newMem();
  else if(pz==='ttt') newTtt();
  else if(pz==='math') newMath();
  else reactionPause();
};

new15();
newMem();
newTtt();
newMath();
reactionPause();

// ai
document.getElementById('sendAi').onclick = async ()=>{
  const prompt=document.getElementById('prompt').value.trim();
  const out=document.getElementById('answer');
  if(!prompt){out.textContent='Введите запрос'; return;}
  out.textContent='Отправка...';
  const r=await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})});
  const j=await r.json(); out.textContent=j.answer||('Ошибка: '+j.error);
};
