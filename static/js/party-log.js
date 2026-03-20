// ══════════════════════════════════════════════════════════════════
// PARTY ROLL LOG (SSE)
// ══════════════════════════════════════════════════════════════════
const partyLog = [];

function connectPartyRollLog(){
  const statusEl=document.getElementById('party-log-status');
  const es=new EventSource('/api/rolls/stream');
  es.onopen=()=>{if(statusEl){statusEl.textContent='● live';statusEl.style.color='var(--green-b)';}};
  es.onerror=()=>{if(statusEl){statusEl.textContent='● disconnected';statusEl.style.color='var(--red-b)';}};
  es.onmessage=(e)=>{
    try{
      const roll=JSON.parse(e.data);
      partyLog.unshift(roll);
      if(partyLog.length>50) partyLog.pop();
      renderPartyLog();
    }catch(_){}
  };
}

function renderPartyLog(){
  const el=document.getElementById('party-roll-log');
  if(!el) return;
  if(!partyLog.length){
    el.innerHTML='<div style="color:var(--text-d);font-size:.8rem;font-style:italic;padding:12px;text-align:center;">No party rolls yet.</div>';
    return;
  }
  el.innerHTML=partyLog.map(r=>{
    const totalCls=r.isCrit?'roll-hist-crit':r.isFail?'roll-hist-fail':'';
    const parts=(r.parts||[]).join(' + ');
    return `<div class="roll-hist-entry" style="flex-direction:column;align-items:flex-start;gap:2px;">
      <div style="display:flex;justify-content:space-between;align-items:center;width:100%;">
        <span class="roll-hist-label" style="color:var(--text-d);">${r.character} · ${r.label}</span>
        <span class="roll-hist-total ${totalCls}">${r.total}</span>
      </div>
      <div style="font-size:.7rem;color:var(--text-d);font-style:italic;">${parts}</div>
    </div>`;
  }).join('');
}
