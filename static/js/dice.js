// ══════════════════════════════════════════════════════════════════
// DICE ROLLER
// ══════════════════════════════════════════════════════════════════
let diceState = {selectedDie: 20, mode: 'normal', advantage: 'straight', history: [], tray: [], flatBonus: 0};

function selectDie(sides){diceState.selectedDie=sides;}

function addDie(sides){
  const existing=diceState.tray.find(e=>e.sides===sides);
  if(existing){existing.count++;}else{diceState.tray.push({count:1,sides});}
  syncFormulaFromTray();
}

function clearDiceTray(){
  diceState.tray=[];
  diceState.flatBonus=0;
  document.getElementById('dice-formula').value='';
}

function syncFormulaFromTray(){
  const parts=diceState.tray.map(e=>`${e.count}d${e.sides}`);
  if(diceState.flatBonus!==0) parts.push(String(diceState.flatBonus));
  document.getElementById('dice-formula').value=parts.join(' + ');
}

function syncFormulaFromInput(){
  const str=document.getElementById('dice-formula').value;
  const result=parseDiceFormula(str);
  diceState.tray=result.tray;
  diceState.flatBonus=result.flatBonus;
}

function parseDiceFormula(str){
  const tray=[];
  let flatBonus=0;
  const tokens=str.replace(/\s+/g,'').split('+');
  for(const token of tokens){
    const m=token.match(/^(\d+)d(\d+)$/i);
    if(m){
      const count=parseInt(m[1]);
      const sides=parseInt(m[2]);
      const existing=tray.find(e=>e.sides===sides);
      if(existing){existing.count+=count;}else{tray.push({count,sides});}
    }else{
      const num=parseInt(token);
      if(!isNaN(num)) flatBonus+=num;
    }
  }
  return {tray,flatBonus};
}

function setAdvantage(mode){
  diceState.advantage=mode;
  const styles={straight:'normal',advantage:'skill',disadvantage:'save'};
  ['straight','advantage','disadvantage'].forEach(m=>{
    document.getElementById('adv-'+m).className='roll-mode-btn'+(m===mode?' active-'+styles[m]:'');
  });
}

function switchDiceMode(mode){
  diceState.mode=mode;
  ['normal','skill','save'].forEach(m=>{
    const btn=document.getElementById('mode-'+m);
    btn.className='roll-mode-btn'+(m===mode?' active-'+m:'');
  });
  document.getElementById('dice-tray-section').style.display=mode==='normal'?'block':'none';
  document.getElementById('dice-adv-section').style.display=mode!=='normal'?'block':'none';
  document.getElementById('dice-skill-row').style.display=mode==='skill'?'block':'none';
  document.getElementById('dice-save-row').style.display=mode==='save'?'block':'none';
  if(mode==='skill'||mode==='save') selectDie(20);
  populateDiceSelectors();
}

function populateDiceSelectors(){
  if(!currentChar) return;
  const skillSel=document.getElementById('dice-skill-select');
  skillSel.innerHTML=SKILLS_DEF.map(s=>{
    const p=currentChar.skills?.[s.name];
    const star=p?.expert?' ★★':p?.prof?' ★':'';
    const mod=fmtMod(getSkillMod(s.name));
    return `<option value="${s.name}">${s.name} (${s.stat}) ${mod}${star}</option>`;
  }).join('');
  const saveSel=document.getElementById('dice-save-select');
  saveSel.innerHTML=ABILITIES.map(ab=>{
    const prof=currentChar.saving_throws?.[ab];
    const mod=fmtMod(getSaveMod(ab));
    return `<option value="${ab}">${ABILITY_NAMES[ab]} (${ab}) ${mod}${prof?' ★':''}</option>`;
  }).join('');
  updateDiceModDisplay();
}

function getSkillMod(skillName){
  if(!currentChar) return 0;
  const def=SKILLS_DEF.find(s=>s.name===skillName);
  if(!def) return 0;
  const score=currentChar.stats?.[def.stat]||10;
  const pb=getProfBonus(currentChar.level||1);
  const p=currentChar.skills?.[skillName];
  return getMod(score)+(p?.expert?pb*2:p?.prof?pb:0);
}

function getSaveMod(ab){
  if(!currentChar) return 0;
  const score=currentChar.stats?.[ab]||10;
  const pb=getProfBonus(currentChar.level||1);
  return getMod(score)+(currentChar.saving_throws?.[ab]?pb:0);
}

function updateDiceModDisplay(){
  if(diceState.mode==='skill'){
    const skill=document.getElementById('dice-skill-select').value;
    document.getElementById('dice-skill-mod').textContent='Total modifier: '+fmtMod(getSkillMod(skill));
  }else if(diceState.mode==='save'){
    const ab=document.getElementById('dice-save-select').value;
    document.getElementById('dice-save-mod').textContent='Total modifier: '+fmtMod(getSaveMod(ab));
  }
}

function buildBreakdownHTML(partsData,tookDropped,critFumble,chipSize){
  const fs=chipSize||'.8rem';
  const chips=partsData.map((p,i)=>{
    const sep=i>0?'<span class="roll-plus">+</span>':'';
    return `${sep}<span class="roll-chip roll-chip-${p.type}" style="font-size:${fs};">${p.text}</span>`;
  }).join('');
  const cf=critFumble?`<span class="roll-chip roll-chip-${critFumble}" style="font-size:${fs};">${critFumble==='crit'?'CRITICAL!':'FUMBLE!'}</span>`:'';
  const td=tookDropped?`<span class="roll-took">${tookDropped}</span>`:'';
  return `<div class="roll-chips">${chips}${cf?'<span class="roll-plus">·</span>'+cf:''}</div>${td}`;
}

function _pushDiceResult(label,partsData,total,isCrit,isFail){
  const resultEl=document.getElementById('dice-tab-result');
  resultEl.textContent=total;
  resultEl.style.color=isCrit?'#ffd700':isFail?'var(--red-b)':'var(--gold)';
  resultEl.classList.remove('dice-rolling');
  void resultEl.offsetWidth;
  resultEl.classList.add('dice-rolling');
  const critFumble=isCrit?'crit':isFail?'fumble':'';
  document.getElementById('dice-tab-breakdown').innerHTML=buildBreakdownHTML(partsData,'',critFumble,'.8rem');
  diceState.history.unshift({total,label,partsData,tookDropped:'',isCrit,isFail});
  if(diceState.history.length>20) diceState.history.pop();
  renderDiceHistory();
  fetch('/api/rolls',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({character:currentChar?.name||'Unknown',label,total,isCrit,isFail,parts:partsData.map(p=>p.text)})
  }).catch(()=>{});
}

function showRollPopup(label,partsData,total,isCrit,isFail){
  document.getElementById('roll-popup-label').textContent=label;
  const totalEl=document.getElementById('roll-popup-total');
  totalEl.textContent=total;
  totalEl.style.color=isCrit?'#ffd700':isFail?'var(--red-b)':'var(--gold)';
  totalEl.classList.remove('dice-rolling');
  void totalEl.offsetWidth;
  totalEl.classList.add('dice-rolling');
  const critFumble=isCrit?'crit':isFail?'fumble':'';
  document.getElementById('roll-popup-breakdown').innerHTML=buildBreakdownHTML(partsData,'',critFumble,'.85rem');
  document.getElementById('modal-roll-result').classList.add('open');
}

function rollAttack(idx){
  const atk=currentChar.attacks?.[idx];
  if(!atk) return;
  const bonus=parseInt(atk.atk_bonus)||0;
  const roll=Math.floor(Math.random()*20)+1;
  const total=roll+bonus;
  const isCrit=roll===20,isFail=roll===1;
  const partsData=[{text:`d20 ${roll}`,type:'die'}];
  if(bonus!==0) partsData.push({text:`ATK ${fmtMod(bonus)}`,type:'ability'});
  const label=(atk.name||'Attack')+' — To Hit';
  _pushDiceResult(label,partsData,total,isCrit,isFail);
  showRollPopup(label,partsData,total,isCrit,isFail);
}

function rollDamage(idx){
  const atk=currentChar.attacks?.[idx];
  if(!atk||!atk.damage) return;
  const dmgStr=atk.damage.replace(/[a-zA-Z\s]+$/,'').trim();
  const {tray,flatBonus}=parseDiceFormula(dmgStr);
  if(!tray.length&&flatBonus===0) return;
  let total=0;
  const partsData=[];
  for(const {count,sides} of tray){
    const rolls=Array.from({length:count},()=>Math.floor(Math.random()*sides)+1);
    const sum=rolls.reduce((a,b)=>a+b,0);
    total+=sum;
    const rollStr=rolls.length>1?`[${rolls.join(', ')}]`:String(rolls[0]);
    partsData.push({text:`${count}d${sides} ${rollStr}`,type:'die'});
  }
  if(flatBonus!==0){total+=flatBonus;partsData.push({text:`+${flatBonus}`,type:'bonus'});}
  const label=(atk.name||'Attack')+' — Damage';
  _pushDiceResult(label,partsData,total,false,false);
  showRollPopup(label,partsData,total,false,false);
}

function rollDiceTab(){
  const mode=diceState.mode;
  const extra=parseInt(document.getElementById('dice-extra-bonus').value)||0;
  if(mode==='normal'){
    syncFormulaFromInput();
    const tray=diceState.tray;
    const flatBonus=diceState.flatBonus;
    if(!tray.length&&flatBonus===0&&extra===0) return;
    let total=0;
    const partsData=[];
    for(const {count,sides} of tray){
      const rolls=Array.from({length:count},()=>Math.floor(Math.random()*sides)+1);
      const sum=rolls.reduce((a,b)=>a+b,0);
      total+=sum;
      const rollStr=rolls.length>1?`[${rolls.join(', ')}]`:String(rolls[0]);
      partsData.push({text:`${count}d${sides} ${rollStr}`,type:'die'});
    }
    if(flatBonus!==0){total+=flatBonus;partsData.push({text:`+${flatBonus}`,type:'bonus'});}
    if(extra!==0){total+=extra;partsData.push({text:`Bonus ${fmtMod(extra)}`,type:'bonus'});}
    const label=document.getElementById('dice-formula').value||'Custom Roll';
    const resultEl=document.getElementById('dice-tab-result');
    resultEl.textContent=total;
    resultEl.style.color='var(--gold)';
    resultEl.classList.remove('dice-rolling');
    void resultEl.offsetWidth;
    resultEl.classList.add('dice-rolling');
    document.getElementById('dice-tab-breakdown').innerHTML=buildBreakdownHTML(partsData,'','','.8rem');
    diceState.history.unshift({total,label,partsData,tookDropped:'',isCrit:false,isFail:false});
    if(diceState.history.length>20) diceState.history.pop();
    renderDiceHistory();
    return;
  }
  const sides=diceState.selectedDie;
  const adv=diceState.advantage;
  const roll1=Math.floor(Math.random()*sides)+1;
  let roll=roll1,dieText,tookDropped='';
  if(adv!=='straight'){
    const roll2=Math.floor(Math.random()*sides)+1;
    if(adv==='advantage'){
      roll=Math.max(roll1,roll2);
      const dropped=Math.min(roll1,roll2);
      dieText=`d${sides} ${roll}, ${dropped}↑`;
      tookDropped=`took ${roll} · dropped ${dropped}`;
    }else{
      roll=Math.min(roll1,roll2);
      const dropped=Math.max(roll1,roll2);
      dieText=`d${sides} ${roll}, ${dropped}↓`;
      tookDropped=`took ${roll} · dropped ${dropped}`;
    }
  }else{
    dieText=`d${sides} ${roll}`;
  }
  let mod=0,label='',isCrit=false,isFail=false;
  const partsData=[{text:dieText,type:'die'}];
  if(mode==='skill'){
    const skill=document.getElementById('dice-skill-select').value;
    const def=SKILLS_DEF.find(s=>s.name===skill);
    const ab=def.stat;
    const abilityMod=getMod(currentChar?.stats?.[ab]||10);
    const pb=getProfBonus(currentChar?.level||1);
    const p=currentChar?.skills?.[skill];
    const profMod=p?.expert?pb*2:p?.prof?pb:0;
    mod=abilityMod+profMod;
    label=skill;
    if(abilityMod!==0) partsData.push({text:`${ab} ${fmtMod(abilityMod)}`,type:'ability'});
    if(p?.expert) partsData.push({text:`Expertise ${fmtMod(pb*2)}`,type:'exp'});
    else if(p?.prof) partsData.push({text:`Prof ${fmtMod(pb)}`,type:'prof'});
    isCrit=roll===20;isFail=roll===1;
  }else if(mode==='save'){
    const ab=document.getElementById('dice-save-select').value;
    const abilityMod=getMod(currentChar?.stats?.[ab]||10);
    const pb=getProfBonus(currentChar?.level||1);
    const proficient=currentChar?.saving_throws?.[ab];
    mod=abilityMod+(proficient?pb:0);
    label=ABILITY_NAMES[ab]+' Save';
    if(abilityMod!==0) partsData.push({text:`${ab} ${fmtMod(abilityMod)}`,type:'ability'});
    if(proficient) partsData.push({text:`Prof ${fmtMod(pb)}`,type:'prof'});
    isCrit=roll===20;isFail=roll===1;
  }else{
    label='d'+sides;
    isCrit=sides===20&&roll===20;
    isFail=sides===20&&roll===1;
  }
  if(extra!==0) partsData.push({text:`Bonus ${fmtMod(extra)}`,type:'bonus'});
  const total=roll+mod+extra;
  const critFumble=isCrit?'crit':isFail?'fumble':'';
  const resultEl=document.getElementById('dice-tab-result');
  resultEl.textContent=total;
  resultEl.style.color=isCrit?'#ffd700':isFail?'var(--red-b)':'var(--gold)';
  resultEl.classList.remove('dice-rolling');
  void resultEl.offsetWidth;
  resultEl.classList.add('dice-rolling');
  document.getElementById('dice-tab-breakdown').innerHTML=buildBreakdownHTML(partsData,tookDropped,critFumble,'.8rem');
  diceState.history.unshift({total,label,partsData,tookDropped,isCrit,isFail});
  if(diceState.history.length>20) diceState.history.pop();
  renderDiceHistory();
}

function renderDiceHistory(){
  const el=document.getElementById('dice-roll-history');
  if(!diceState.history.length){
    el.innerHTML='<div style="color:var(--text-d);font-size:.8rem;font-style:italic;padding:12px;text-align:center;">No rolls yet.</div>';
    return;
  }
  el.innerHTML=diceState.history.map(h=>{
    const totalCls=h.isCrit?'roll-hist-crit':h.isFail?'roll-hist-fail':'';
    const chipsHTML=buildBreakdownHTML(h.partsData,h.tookDropped,'','.65rem');
    return `<div class="roll-hist-entry" style="flex-direction:column;align-items:flex-start;gap:4px;">
      <div style="display:flex;justify-content:space-between;align-items:center;width:100%;">
        <span class="roll-hist-label">${h.label}</span>
        <span class="roll-hist-total ${totalCls}">${h.total}</span>
      </div>
      <div style="width:100%;">${chipsHTML}</div>
    </div>`;
  }).join('');
}
