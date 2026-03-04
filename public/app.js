const random = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

// --- Themes ---
document.querySelectorAll('[data-set-theme]').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.body.dataset.theme = btn.dataset.setTheme;
  });
});

// --- Puzzle 1: Guess number ---
const secretNumber = random(1, 100);
document.getElementById('guess-btn').addEventListener('click', () => {
  const guess = Number(document.getElementById('guess-input').value);
  const result = document.getElementById('guess-result');

  if (!guess) return (result.textContent = 'Введите число.');
  if (guess === secretNumber) return (result.textContent = 'Верно!');
  result.textContent = guess < secretNumber ? 'Больше.' : 'Меньше.';
});

// --- Puzzle 2: Anagram ---
const anagrams = [
  { shuffled: 'книшга', answer: 'книга' },
  { shuffled: 'лшкоа', answer: 'школа' },
  { shuffled: 'аткмеимаат', answer: 'математика' }
];
const currentAnagram = anagrams[random(0, anagrams.length - 1)];
document.getElementById('anagram-word').textContent = currentAnagram.shuffled;
document.getElementById('anagram-btn').addEventListener('click', () => {
  const input = document.getElementById('anagram-input').value.trim().toLowerCase();
  document.getElementById('anagram-result').textContent =
    input === currentAnagram.answer ? 'Отлично!' : `Неверно. Ответ: ${currentAnagram.answer}`;
});

// --- Puzzle 3: Memory ---
let memorySequence = [];
document.getElementById('memory-start-btn').addEventListener('click', () => {
  memorySequence = Array.from({ length: 4 }, () => random(1, 9));
  const output = document.getElementById('memory-sequence');
  output.textContent = memorySequence.join('-');
  setTimeout(() => {
    output.textContent = '***';
  }, 1800);
});
document.getElementById('memory-check-btn').addEventListener('click', () => {
  const input = document
    .getElementById('memory-input')
    .value.split('-')
    .map((n) => Number(n.trim()));
  const ok = input.length === memorySequence.length && input.every((n, i) => n === memorySequence[i]);
  document.getElementById('memory-result').textContent = ok
    ? 'Верно!'
    : `Неверно. Было: ${memorySequence.join('-')}`;
});

// --- Puzzle 4: Math blitz ---
let mathAnswer = null;
document.getElementById('math-new-btn').addEventListener('click', () => {
  const a = random(5, 40);
  const b = random(2, 12);
  const op = Math.random() > 0.5 ? '+' : '*';
  mathAnswer = op === '+' ? a + b : a * b;
  document.getElementById('math-task').textContent = `Решите: ${a} ${op} ${b}`;
  document.getElementById('math-result').textContent = '';
});
document.getElementById('math-check-btn').addEventListener('click', () => {
  const input = Number(document.getElementById('math-input').value);
  if (mathAnswer === null) {
    document.getElementById('math-result').textContent = 'Сначала создайте пример.';
    return;
  }
  document.getElementById('math-result').textContent = input === mathAnswer ? 'Правильно!' : `Ответ: ${mathAnswer}`;
});

// --- Puzzle 5: Logic ---
document.querySelectorAll('.logic-choice').forEach((btn) => {
  btn.addEventListener('click', () => {
    const text = btn.dataset.answer === 'равны' ? 'Верно! Они равны.' : 'Подумайте ещё 🙂';
    document.getElementById('logic-result').textContent = text;
  });
});

// --- Gallery ---
const galleryImages = [
  'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=600&q=80',
  'https://images.unsplash.com/photo-1588072432904-843af37f03ed?auto=format&fit=crop&w=600&q=80',
  'https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=600&q=80',
  'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=600&q=80',
  'https://images.unsplash.com/photo-1460518451285-97b6aa326961?auto=format&fit=crop&w=600&q=80',
  'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=600&q=80'
];

const gallery = document.getElementById('gallery');
galleryImages.forEach((src) => {
  const img = document.createElement('img');
  img.src = src;
  img.alt = 'Изображение из школьной галереи';
  gallery.appendChild(img);
});

// --- GigaChat ---
const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');

function addMessage(text, role) {
  const node = document.createElement('div');
  node.className = `msg ${role}`;
  node.textContent = text;
  chatBox.appendChild(node);
  chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById('chat-send-btn').addEventListener('click', async () => {
  const prompt = chatInput.value.trim();
  if (!prompt) return;

  addMessage(prompt, 'user');
  chatInput.value = '';

  try {
    const response = await fetch('/api/gigachat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });

    const data = await response.json();

    if (!response.ok) {
      addMessage(data.error || 'Ошибка запроса к серверу.', 'bot');
      return;
    }

    addMessage(data.answer, 'bot');
  } catch (error) {
    addMessage(`Сетевая ошибка: ${error.message}`, 'bot');
  }
});
