// ══════════════════════════════════════════════════════════════════
// STRETCH TRACKER
// ══════════════════════════════════════════════════════════════════
let stretchState = {
  current: 1,
  total: 24,
  area: 'dangerous',
  freq: 'medium',
  cells: [],
  log: [],
  wmTable: [
    {roll:'1', monster:''},
    {roll:'2', monster:''},
    {roll:'3', monster:''},
    {roll:'4', monster:''},
    {roll:'5', monster:''},
    {roll:'6', monster:''},
    {roll:'7', monster:''},
    {roll:'8', monster:''},
  ]
};

function openStretchTracker() {
  document.getElementById('screen-list').classList.remove('active');
  document.getElementById('screen-stretch').classList.add('active');
  initStretchTracker();
}
function closeStretchTracker() {
  document.getElementById('screen-stretch').classList.remove('active');
  document.getElementById('screen-list').classList.add('active');
}

function initStretchTracker() {
  if (!stretchState.cells.length) {
    stretchState.cells = Array(stretchState.total).fill(null).map(() => ({state:'empty'}));
  }
  setArea(stretchState.area);
  setFreq(stretchState.freq);
  renderStretchGrid();
  renderWMTable();
  renderStretchLog();
}

function setArea(area) {
  stretchState.area = area;
  ['wilderness','dangerous','treacherous'].forEach(a => {
    const btn = document.getElementById('area-'+a);
    if (btn) btn.className = 'rest-system-btn' + (a === area ? ' active-standard' : '');
  });
}

function setFreq(freq) {
  stretchState.freq = freq;
  ['constant','medium','hourly'].forEach(f => {
    const btn = document.getElementById('freq-'+f);
    if (btn) btn.className = 'rest-system-btn' + (f === freq ? ' active-standard' : '');
  });
}

function renderStretchGrid() {
  const grid = document.getElementById('stretch-grid');
  const cur = stretchState.current;
  grid.innerHTML = stretchState.cells.map((cell, i) => {
    const n = i + 1;
    const isCur = n === cur;
    const icon = cell.state === 'done' ? '✓' : cell.state === 'encounter' ? '⚔️' : isCur ? '●' : '';
    return `<div class="stretch-cell ${cell.state} ${isCur ? 'current' : ''}" onclick="toggleStretchCell(${i})">
      <span class="sc-icon">${icon}</span>
      <span class="sc-num">${n}</span>
    </div>`;
  }).join('');
  document.getElementById('stretch-num').textContent = cur;
}

function toggleStretchCell(i) {
  const states = ['empty','done','encounter'];
  const cell = stretchState.cells[i];
  const idx = states.indexOf(cell.state);
  cell.state = states[(idx + 1) % states.length];
  renderStretchGrid();
}

function shouldRollMonsters() {
  const cur = stretchState.current;
  const freq = stretchState.freq;
  if (freq === 'constant') return true;
  if (freq === 'medium')   return cur % 3 === 0;
  if (freq === 'hourly')   return cur % 6 === 0;
  return false;
}

function getMonsterThreshold() {
  const area = stretchState.area;
  if (area === 'wilderness')  return [6];
  if (area === 'dangerous')   return [5, 6];
  if (area === 'treacherous') return [4, 5, 6];
  return [6];
}

function rollMonsterCheck() {
  const roll = Math.floor(Math.random() * 6) + 1;
  const threshold = getMonsterThreshold();
  const isEncounter = threshold.includes(roll);

  const dieEl = document.getElementById('monster-die-result');
  dieEl.classList.remove('dice-rolling');
  void dieEl.offsetWidth;
  dieEl.classList.add('dice-rolling');
  dieEl.style.color = isEncounter ? 'var(--red-b)' : 'var(--green-b)';
  dieEl.textContent = roll;

  const resultEl = document.getElementById('monster-result-text');
  if (isEncounter) {
    resultEl.style.color = 'var(--red-b)';
    resultEl.textContent = '⚔️ Encounter! Roll on monster table.';
    if (stretchState.current <= stretchState.cells.length) {
      stretchState.cells[stretchState.current - 1].state = 'encounter';
      renderStretchGrid();
    }
  } else {
    resultEl.style.color = 'var(--green-b)';
    resultEl.textContent = `No encounter (needed ${threshold.join(' or ')}).`;
  }
}

function advanceStretch() {
  const cur = stretchState.current;
  if (stretchState.cells[cur - 1].state !== 'encounter') {
    stretchState.cells[cur - 1].state = 'done';
  }

  const shouldRoll = shouldRollMonsters();
  const logEntry = {stretch: cur, note: shouldRoll ? 'rolled for monsters' : 'no monster roll'};
  stretchState.log.unshift(logEntry);

  if (cur < stretchState.total) {
    stretchState.current = cur + 1;
  } else {
    stretchState.total += 12;
    stretchState.cells.push(...Array(12).fill(null).map(() => ({state:'empty'})));
    stretchState.current = cur + 1;
  }

  renderStretchGrid();
  renderStretchLog();

  if (shouldRoll) {
    setTimeout(rollMonsterCheck, 300);
  }
}

function renderStretchLog() {
  const log = document.getElementById('stretch-log');
  if (!stretchState.log.length) {
    log.innerHTML = '<div style="color:var(--text-d);font-size:.8rem;font-style:italic;">No stretches logged yet.</div>';
    return;
  }
  log.innerHTML = stretchState.log.slice(0, 30).map(e =>
    `<div class="activity-entry"><span class="ae-s">${e.stretch}</span><span>${e.note}</span></div>`
  ).join('');
}

function renderWMTable() {
  const container = document.getElementById('wm-table-editor');
  container.innerHTML = stretchState.wmTable.map((row, i) =>
    `<div class="wm-row">
      <span class="wm-num">${row.roll}</span>
      <input type="text" value="${row.monster}" placeholder="Monster or encounter…" oninput="stretchState.wmTable[${i}].monster=this.value">
    </div>`
  ).join('');
}

function addWMRow() {
  const nextRoll = stretchState.wmTable.length + 1;
  stretchState.wmTable.push({roll: String(nextRoll), monster: ''});
  renderWMTable();
}

function resetStretch() {
  if (!confirm('Reset stretch tracker? This clears all progress.')) return;
  stretchState.current = 1;
  stretchState.total = 24;
  stretchState.cells = Array(24).fill(null).map(() => ({state:'empty'}));
  stretchState.log = [];
  document.getElementById('monster-die-result').textContent = '—';
  document.getElementById('monster-result-text').textContent = 'Roll to check for wandering monsters';
  document.getElementById('monster-result-text').style.color = 'var(--text-d)';
  renderStretchGrid();
  renderStretchLog();
}
