// ══════════════════════════════════════════════════════════════════
// SHEET CORE — load, save, nav, tab switching
// ══════════════════════════════════════════════════════════════════
async function loadCharacter(id){
  currentChar=await apiGet('/api/characters/'+encodeURIComponent(id));
  if(!currentChar.currency) currentChar.currency={pp:0,gp:0,ep:0,sp:0,cp:0};
  document.getElementById('screen-list').classList.remove('active');
  document.getElementById('screen-creator').classList.remove('active');
  document.getElementById('screen-sheet').classList.add('active');
  gameData=await loadGameData(currentChar.edition||'2024');
  populateSpellDatalist(currentChar.edition||'2024');
  renderSheet();
  switchTab('main',document.querySelector('.tab-btn'));
}

function goBack(){
  document.getElementById('screen-sheet').classList.remove('active');
  document.getElementById('screen-list').classList.add('active');
  loadCharList();
}

function scheduleSave(){clearTimeout(saveTimeout);saveTimeout=setTimeout(saveCharacter,800);}

async function saveCharacter(){
  if(!currentChar) return;
  try{
    await apiPut('/api/characters/'+encodeURIComponent(currentChar.name),currentChar);
    const ind=document.getElementById('sheet-save-indicator');
    ind.classList.add('visible');
    setTimeout(()=>ind.classList.remove('visible'),1500);
  }catch(e){console.error('Save failed',e);}
}

async function downloadPDF(){
  if(!currentChar) return;
  const btn=document.getElementById('pdf-btn');
  btn.textContent='⏳…'; btn.style.opacity='.6';
  try{
    const r=await fetch(`/api/characters/${encodeURIComponent(currentChar.name)}/pdf`);
    if(!r.ok) throw new Error('PDF generation failed');
    const blob=await r.blob();
    const a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download=`${currentChar.name.replace(/\s+/g,'_')}_sheet.pdf`;
    a.click(); URL.revokeObjectURL(a.href);
  }catch(e){alert('Could not generate PDF: '+e.message);}
  finally{btn.textContent='📄 PDF';btn.style.opacity='1';}
}

function switchTab(name,btn){
  document.querySelectorAll('.tab-content').forEach(el=>el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el=>el.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  if(btn) btn.classList.add('active');
  if(name==='dice') populateDiceSelectors();
}

function switchSubtab(name,btn){
  document.querySelectorAll('.subtab-panel').forEach(el=>el.classList.remove('active'));
  document.querySelectorAll('.subtab-btn').forEach(el=>el.classList.remove('active'));
  document.getElementById('subtab-'+name).classList.add('active');
  if(btn) btn.classList.add('active');
  if(name==='homebrew') loadHouseRules();
}
