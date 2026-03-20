// ══════════════════════════════════════════════════════════════════
// CHARACTER LIST
// ══════════════════════════════════════════════════════════════════
async function loadCharList(){
  const chars=await apiGet('/api/characters');
  const container=document.getElementById('char-list-container');
  if(!chars.length){
    container.innerHTML='<p style="color:var(--text-d);font-size:.9rem;text-align:center;padding:20px 0;">No adventurers yet. Create one to begin!</p>';
    return;
  }
  container.innerHTML=chars.map(c=>{
    const edClass=c.edition==='2014'?'e2014':'e2024';
    const edLabel=c.edition==='2014'?'5e 2014':'5e 2024';
    return `<div class="char-card ${edClass}" onclick="loadCharacter('${c.id}')">
      <div>
        <h3>${c.name||'Unnamed'}</h3>
        <p>${[c.race,c.class,c.level?'Level '+c.level:''].filter(Boolean).join(' · ')}</p>
      </div>
      <div style="display:flex;align-items:center;gap:8px;">
        <span class="edition-badge ${edClass}">${edLabel}</span>
        <button class="char-del" onclick="event.stopPropagation();deleteChar('${c.id}','${c.name}')">🗑</button>
        <span style="color:var(--gold-d);font-size:1.2rem;">›</span>
      </div>
    </div>`;
  }).join('');
}

async function deleteChar(id,name){
  if(!confirm(`Delete ${name}?`)) return;
  await apiDelete('/api/characters/'+encodeURIComponent(id));
  loadCharList();
}
