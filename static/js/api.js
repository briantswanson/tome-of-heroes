// ══════════════════════════════════════════════════════════════════
// API CLIENT & SHARED STATE
// ══════════════════════════════════════════════════════════════════
const API = '';
let currentChar = null, saveTimeout = null;
let gameData = null;
const gameDataCache = {};

async function apiGet(url){const r=await fetch(API+url);return r.json();}
async function apiPost(url,data){const r=await fetch(API+url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});return r.json();}
async function apiPut(url,data){const r=await fetch(API+url,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});return r.json();}
async function apiDelete(url){const r=await fetch(API+url,{method:'DELETE'});return r.json();}

async function loadGameData(edition){
  if(gameDataCache[edition]) return gameDataCache[edition];
  try{
    const r=await fetch(`/api/game-data?edition=${edition}`);
    gameDataCache[edition]=await r.json();
  }catch(e){gameDataCache[edition]={races:[],classes:[],backgrounds:[],spells:[]};}
  return gameDataCache[edition];
}

function populateSpellDatalist(edition){
  const data=gameDataCache[edition];
  if(!data||!data.spells) return;
  const dl=document.getElementById('spell-suggestions');
  if(!dl) return;
  dl.innerHTML=data.spells.map(sp=>`<option value="${sp.name}">`).join('');
}

function autofillSpell(name){
  if(!currentChar) return;
  const edition=currentChar.edition||'2024';
  const data=gameDataCache[edition];
  if(!data||!data.spells) return;
  const sp=data.spells.find(s=>s.name.toLowerCase()===name.toLowerCase());
  if(!sp) return;
  document.getElementById('new-spell-level').value=sp.level||0;
  document.getElementById('new-spell-school').value=sp.school||'';
  document.getElementById('new-spell-cast').value=sp.casting_time||'';
  document.getElementById('new-spell-range').value=sp.range||'';
  document.getElementById('new-spell-components').value=sp.components||'';
  document.getElementById('new-spell-duration').value=sp.duration||'';
  document.getElementById('new-spell-concentration').checked=!!(sp.concentration);
  document.getElementById('new-spell-ritual').checked=!!(sp.ritual);
}
