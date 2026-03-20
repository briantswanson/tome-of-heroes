// ══════════════════════════════════════════════════════════════════
// SHEET MUTATIONS (user input handlers)
// ══════════════════════════════════════════════════════════════════
function fieldUpdate(key,value){
  const keys=key.split('.');
  let obj=currentChar;
  for(let i=0;i<keys.length-1;i++) obj=obj[keys[i]];
  obj[keys[keys.length-1]]=value;
  scheduleSave();
}
function levelUpdate(val){
  currentChar.level=+val||1;
  currentChar.proficiency_bonus=getProfBonus(currentChar.level);
  document.getElementById('f-profbonus').value='+'+currentChar.proficiency_bonus;
  renderSavingThrows(); renderSkills(); renderClassFeatures();
  scheduleSave();
}
function abilityUpdate(ab,val){
  if(!currentChar.stats) currentChar.stats={};
  currentChar.stats[ab]=+val||10;
  document.querySelectorAll('.ability-box').forEach((box,i)=>{
    if(ABILITIES[i]===ab) box.querySelector('.ability-mod').textContent=fmtMod(getMod(+val||10));
  });
  renderSavingThrows(); renderSkills();
  scheduleSave();
}
function toggleSavingThrow(ab){
  if(!currentChar.saving_throws) currentChar.saving_throws={};
  currentChar.saving_throws[ab]=!currentChar.saving_throws[ab];
  renderSavingThrows(); scheduleSave();
}
function cycleSkillProf(name){
  const sk=currentChar.skills[name];
  if(!sk.prof&&!sk.expert) sk.prof=true;
  else if(sk.prof&&!sk.expert){sk.prof=false;sk.expert=true;}
  else{sk.prof=false;sk.expert=false;}
  renderSkills(); scheduleSave();
}
function hpUpdate(field,val){
  if(!currentChar.hp) currentChar.hp={current:0,max:0,temp:0};
  currentChar.hp[field]=+val||0;
  if(field==='max') document.getElementById('hp-max-display').textContent=currentChar.hp.max;
  scheduleSave();
}
function adjustHP(delta){
  if(!currentChar.hp) currentChar.hp={current:0,max:0,temp:0};
  const mx=currentChar.hp.max+(currentChar.hp.temp||0);
  currentChar.hp.current=Math.max(0,Math.min(mx,(currentChar.hp.current||0)+delta));
  document.getElementById('hp-current').textContent=currentChar.hp.current;
  scheduleSave();
}
function toggleInspiration(){
  currentChar.inspiration=!currentChar.inspiration;
  document.getElementById('inspiration-btn').classList.toggle('active',currentChar.inspiration);
  scheduleSave();
}
function toggleDeathSave(type,idx){
  if(!currentChar.death_saves) currentChar.death_saves={successes:0,failures:0};
  const key=type==='success'?'successes':'failures';
  const cur=currentChar.death_saves[key]||0;
  currentChar.death_saves[key]=cur>idx?idx:idx+1;
  document.querySelectorAll(`#death-${type}s .death-pip`).forEach((pip,i)=>pip.classList.toggle('filled',i<currentChar.death_saves[key]));
  scheduleSave();
}
function toggleSlot(level,idx){
  const sl=currentChar.spell_slots[level];
  sl.used=sl.used===idx+1?idx:idx+1;
  renderSpellSlots(); scheduleSave();
}
function slotTotalUpdate(level,val){
  if(!currentChar.spell_slots[level]) currentChar.spell_slots[level]={total:0,used:0};
  currentChar.spell_slots[level].total=Math.min(9,+val||0);
  currentChar.spell_slots[level].used=Math.min(currentChar.spell_slots[level].used,currentChar.spell_slots[level].total);
  renderSpellSlots(); scheduleSave();
}
function setExhaustion(i){
  const current=currentChar.exhaustion||0;
  currentChar.exhaustion=current===i?i-1:i;
  renderExhaustion();
  scheduleSave();
}
function addSpell(){
  const name=document.getElementById('new-spell-name').value.trim();
  if(!name) return;
  if(!currentChar.spells) currentChar.spells=[];
  currentChar.spells.push({
    name,
    level:+document.getElementById('new-spell-level').value,
    school:document.getElementById('new-spell-school').value.trim(),
    casting_time:document.getElementById('new-spell-cast').value.trim(),
    range:document.getElementById('new-spell-range').value.trim(),
    components:document.getElementById('new-spell-components').value.trim(),
    duration:document.getElementById('new-spell-duration').value.trim(),
    concentration:document.getElementById('new-spell-concentration').checked,
    ritual:document.getElementById('new-spell-ritual').checked,
    prepared:false
  });
  ['new-spell-name','new-spell-school','new-spell-cast','new-spell-range','new-spell-components','new-spell-duration'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('new-spell-level').value='0';
  document.getElementById('new-spell-concentration').checked=false;
  document.getElementById('new-spell-ritual').checked=false;
  renderSpellList(); scheduleSave();
}
function toggleSpellPrepared(idx){currentChar.spells[idx].prepared=!currentChar.spells[idx].prepared;renderSpellList();scheduleSave();}
function removeSpell(idx){currentChar.spells.splice(idx,1);renderSpellList();scheduleSave();}
function addItem(){
  const name=document.getElementById('new-item-name').value.trim();
  if(!name) return;
  if(!currentChar.inventory) currentChar.inventory=[];
  currentChar.inventory.push({name,qty:+document.getElementById('new-item-qty').value||1,weight:document.getElementById('new-item-weight').value.trim(),desc:document.getElementById('new-item-desc').value.trim()});
  ['new-item-name','new-item-weight','new-item-desc'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('new-item-qty').value='1';
  renderInventory(); scheduleSave();
}
function adjustItemQty(idx,delta){currentChar.inventory[idx].qty=Math.max(1,(currentChar.inventory[idx].qty||1)+delta);renderInventory();scheduleSave();}
function removeItem(idx){currentChar.inventory.splice(idx,1);renderInventory();scheduleSave();}
function currencyUpdate(key,val){if(!currentChar.currency)currentChar.currency={};currentChar.currency[key]=+val||0;scheduleSave();}
function addFeature(){
  const name=document.getElementById('new-feat-name').value.trim();
  if(!name) return;
  if(!currentChar.features) currentChar.features=[];
  currentChar.features.push({name,desc:document.getElementById('new-feat-desc').value.trim()});
  document.getElementById('new-feat-name').value='';
  document.getElementById('new-feat-desc').value='';
  renderFeatures(); scheduleSave();
}
function removeFeature(idx){currentChar.features.splice(idx,1);renderFeatures();scheduleSave();}
function addAttack(){
  if(!currentChar.attacks) currentChar.attacks=[];
  currentChar.attacks.push({name:'',atk_bonus:'',damage:''});
  renderAttacks(); scheduleSave();
}
function updateAttack(idx,field,val){
  if(!currentChar.attacks?.[idx]) return;
  currentChar.attacks[idx][field]=val;
  scheduleSave();
}
function removeAttack(idx){
  currentChar.attacks.splice(idx,1);
  renderAttacks(); scheduleSave();
}
