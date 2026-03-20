// ══════════════════════════════════════════════════════════════════
// REST SYSTEM
// ══════════════════════════════════════════════════════════════════
function setRestSystem(sys){
  if(!currentChar) return;
  currentChar.rest_system=sys;
  renderRestButtons();
  scheduleSave();
}

function renderRestButtons(){
  const sys=currentChar?.rest_system||'standard';
  document.getElementById('rest-btns-excursion').style.display=sys==='excursion'?'block':'none';
  document.getElementById('rest-btns-standard').style.display=sys==='standard'?'block':'none';
  document.getElementById('rsb-standard').className='rest-system-btn'+(sys==='standard'?' active-standard':'');
  document.getElementById('rsb-excursion').className='rest-system-btn'+(sys==='excursion'?' active-excursion':'');
}

function closeModal(id){
  document.getElementById(id).classList.remove('open');
}

let hitDieRestGained=0;

function openRestModal(type){
  const c=currentChar;
  if(!c) return;
  if(type==='night'||type==='short'){
    hitDieRestGained=0;
    const available=(c.hit_dice?.total||c.level||1)-(c.hit_dice?.used||0);
    const die=c.hit_dice?.die||'d8';
    const conMod=getMod(c.stats?.CON||10);
    document.getElementById('hitdie-modal-title').textContent=type==='night'?"🌙 Night's Rest":"⏱️ Short Rest";
    document.getElementById('hitdie-modal-desc').textContent=type==='night'
      ?'Spend hit point dice to recover HP. Roll die + CON modifier. Recharges short-rest features.'
      :'1 hour of rest. Spend hit dice to recover HP. Recharges short-rest features.';
    document.getElementById('hitdie-available').textContent=available;
    document.getElementById('hitdie-die').textContent=die;
    document.getElementById('hitdie-con').textContent=fmtMod(conMod);
    document.getElementById('hitdie-hp-cur').textContent=c.hp?.current??0;
    document.getElementById('hitdie-hp-max').textContent=c.hp?.max??0;
    document.getElementById('dice-result').textContent='—';
    document.getElementById('dice-breakdown').textContent='';
    document.getElementById('hitdie-gained').textContent='0 HP';
    document.getElementById('roll-hitdie-btn').disabled=available<=0;
    document.getElementById('roll-hitdie-btn').style.opacity=available<=0?'.4':'1';
    document.getElementById('modal-hitdie').classList.add('open');
  }else if(type==='good'||type==='long'){
    openFullRestModal(type);
  }else if(type==='relax'){
    const used=c.hit_dice?.used||0;
    const total=c.hit_dice?.total||c.level||1;
    const available=total-used;
    document.getElementById('relax-hd-before').textContent=available+' / '+total;
    document.getElementById('relax-hd-after').textContent=Math.min(total,available+1)+' / '+total;
    document.getElementById('modal-relax').classList.add('open');
  }else if(type==='sanctuary'){
    const gp=c.currency?.gp||0;
    document.getElementById('sanctuary-gp').textContent=gp+' gp';
    const canAfford=gp>=100;
    document.getElementById('sanctuary-warning').style.display=canAfford?'none':'block';
    document.getElementById('sanctuary-confirm-btn').style.opacity=canAfford?'1':'.4';
    document.getElementById('modal-sanctuary').classList.add('open');
  }
}

function rollHitDie(){
  const c=currentChar;
  const available=(c.hit_dice?.total||c.level||1)-(c.hit_dice?.used||0);
  if(available<=0) return;
  const die=c.hit_dice?.die||'d8';
  const faces=parseInt(die.replace('d',''))||8;
  const conMod=getMod(c.stats?.CON||10);
  const roll=Math.floor(Math.random()*faces)+1;
  const total=Math.max(1,roll+conMod);
  const el=document.getElementById('dice-result');
  el.classList.remove('dice-rolling');
  void el.offsetWidth;
  el.classList.add('dice-rolling');
  el.textContent=total;
  document.getElementById('dice-breakdown').textContent=`${die} rolled ${roll} + CON ${fmtMod(conMod)} = ${total} HP`;
  c.hit_dice.used=(c.hit_dice.used||0)+1;
  const newHP=Math.min(c.hp.max,(c.hp.current||0)+total);
  hitDieRestGained+=newHP-(c.hp.current||0);
  c.hp.current=newHP;
  document.getElementById('hitdie-available').textContent=available-1;
  document.getElementById('hitdie-hp-cur').textContent=c.hp.current;
  document.getElementById('hitdie-gained').textContent=hitDieRestGained+' HP';
  document.getElementById('hp-current').textContent=c.hp.current;
  if(available-1<=0){
    document.getElementById('roll-hitdie-btn').disabled=true;
    document.getElementById('roll-hitdie-btn').style.opacity='.4';
  }
  scheduleSave();
}

function confirmHitDieRest(){
  closeModal('modal-hitdie');
  if(currentChar.death_saves){
    currentChar.death_saves={successes:0,failures:0};
    renderSheet();
  }
  scheduleSave();
}

function openFullRestModal(type){
  const c=currentChar;
  const totalDice=c.hit_dice?.total||c.level||1;
  const usedDice=c.hit_dice?.used||0;
  const missingHP=(c.hp?.max||0)-(c.hp?.current||0);
  const exhaustion=c.exhaustion||0;
  document.getElementById('fullrest-title').textContent=type==='good'?'🏰 Good Rest':'☀️ Long Rest';
  document.getElementById('fullrest-desc').textContent=type==='good'
    ?'Three consecutive nights in the same safe location fully restores all resources.'
    :'Eight hours of rest fully restores all resources.';
  let rows=`
    <div class="rp-row"><span class="rp-label">HP Restored</span><span class="rp-val" style="color:var(--green-b);">+${missingHP} (full)</span></div>
    <div class="rp-row"><span class="rp-label">Hit Dice Regained</span><span class="rp-val">${usedDice} returned (${totalDice} total)</span></div>
    <div class="rp-row"><span class="rp-label">Spell Slots</span><span class="rp-val">All restored</span></div>
    <div class="rp-row"><span class="rp-label">Death Saves</span><span class="rp-val">Reset</span></div>`;
  if(type==='good'&&exhaustion>0){
    rows+=`<div class="rp-row"><span class="rp-label">Exhaustion</span><span class="rp-val">${exhaustion} → ${exhaustion-1}</span></div>`;
  }
  document.getElementById('fullrest-preview').innerHTML=rows;
  document.getElementById('modal-fullrest').dataset.resttype=type;
  document.getElementById('modal-fullrest').classList.add('open');
}

function confirmFullRest(){
  const c=currentChar;
  const type=document.getElementById('modal-fullrest').dataset.resttype;
  c.hp.current=c.hp.max;
  c.hit_dice.used=0;
  Object.keys(c.spell_slots||{}).forEach(lvl=>{c.spell_slots[lvl].used=0;});
  c.death_saves={successes:0,failures:0};
  if(type==='good'&&c.exhaustion>0) c.exhaustion=c.exhaustion-1;
  closeModal('modal-fullrest');
  renderSheet();
  scheduleSave();
  const ind=document.getElementById('sheet-save-indicator');
  ind.textContent=type==='good'?'Good Rest taken ✓':'Long Rest taken ✓';
  ind.classList.add('visible');
  setTimeout(()=>{ind.textContent='Saved ✓';ind.classList.remove('visible');},2000);
}

function confirmRelax(){
  const c=currentChar;
  if((c.hit_dice.used||0)>0) c.hit_dice.used-=1;
  closeModal('modal-relax');
  scheduleSave();
}

function confirmSanctuary(){
  const c=currentChar;
  const gp=c.currency?.gp||0;
  if(gp<100) return;
  c.currency.gp-=100;
  closeModal('modal-sanctuary');
  setTimeout(()=>openRestModal('night'),200);
  scheduleSave();
}
