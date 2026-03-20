// ══════════════════════════════════════════════════════════════════
// SHEET RENDERING
// ══════════════════════════════════════════════════════════════════
function renderSheet(){
  const c=currentChar;
  const ed=c.edition||'2024';
  const pb=getProfBonus(c.level||1);
  const badge=document.getElementById('sheet-edition-badge');
  badge.textContent=ed==='2014'?'5e 2014':'5e 2024';
  badge.className='edition-badge '+(ed==='2014'?'e2014':'e2024');
  document.getElementById('f-name').value=c.name||'';
  document.getElementById('f-class').value=c.class||'';
  document.getElementById('f-subclass').value=c.subclass||'';
  document.getElementById('f-level').value=c.level||1;
  document.getElementById('f-profbonus').value='+'+pb;
  document.getElementById('f-race').value=c.race||'';
  document.getElementById('f-background').value=c.background||'';
  document.getElementById('f-alignment').value=c.alignment||'';
  document.getElementById('f-xp').value=c.xp||0;
  document.getElementById('f-ac').value=c.ac||10;
  document.getElementById('f-init').value=c.initiative_bonus||0;
  document.getElementById('f-speed').value=c.speed||30;
  document.getElementById('f-hp-max').value=c.hp?.max||0;
  document.getElementById('f-hp-temp').value=c.hp?.temp||0;
  document.getElementById('f-hitdie').value=c.hit_dice?.die||'d8';
  document.getElementById('hp-current').textContent=c.hp?.current??0;
  document.getElementById('hp-max-display').textContent=c.hp?.max??0;
  document.getElementById('notes-area').value=c.notes||'';
  document.getElementById('backstory-area').value=c.backstory||'';
  document.getElementById('allies-area').value=c.allies||'';
  document.getElementById('f-proficiencies').value=c.proficiencies||'';
  document.getElementById('f-age').value=c.age||'';
  document.getElementById('f-height').value=c.height||'';
  document.getElementById('f-weight').value=c.weight||'';
  document.getElementById('f-eyes').value=c.eyes||'';
  document.getElementById('f-skin').value=c.skin||'';
  document.getElementById('f-hair').value=c.hair||'';
  renderAttacks();
  renderSpellStats();
  updatePassivePerception();
  document.getElementById('inspiration-btn').classList.toggle('active',!!c.inspiration);
  ['success','failure'].forEach(type=>{
    const key=type==='success'?'successes':'failures';
    const count=c.death_saves?.[key]||0;
    document.querySelectorAll(`#death-${type}s .death-pip`).forEach((pip,i)=>pip.classList.toggle('filled',i<count));
  });
  const is2014=ed==='2014';
  document.getElementById('section-personality').style.display=is2014?'block':'none';
  document.getElementById('section-exhaustion').style.display=is2014?'block':'none';
  if(is2014){
    document.getElementById('f-personality').value=c.personality_traits||'';
    document.getElementById('f-ideals').value=c.ideals||'';
    document.getElementById('f-bonds').value=c.bonds||'';
    document.getElementById('f-flaws').value=c.flaws||'';
    renderExhaustion();
  }
  renderRestButtons();
  renderAbilities();
  renderSavingThrows();
  renderSkills();
  renderSpellSlots();
  renderSpellList();
  renderInventory();
  renderCurrency();
  renderFeatures();
  renderClassFeatures();
}

function renderAbilities(){
  const c=currentChar;
  const grid=document.getElementById('ability-grid');
  grid.innerHTML=ABILITIES.map(ab=>{
    const score=c.stats?.[ab]||10;
    return `<div class="ability-box">
      <label>${ab}</label>
      <input class="ability-score-input" type="number" value="${score}" min="1" max="30" oninput="abilityUpdate('${ab}',this.value)">
      <span class="ability-mod">${fmtMod(getMod(score))}</span>
    </div>`;
  }).join('');
}

function renderSavingThrows(){
  const c=currentChar;
  const pb=getProfBonus(c.level||1);
  document.getElementById('saving-throws-list').innerHTML=ABILITIES.map(ab=>{
    const mod=getMod(c.stats?.[ab]||10);
    const prof=c.saving_throws?.[ab]||false;
    const total=mod+(prof?pb:0);
    return `<div class="skill-row">
      <button class="prof-toggle ${prof?'proficient':''}" onclick="toggleSavingThrow('${ab}')">✓</button>
      <span class="skill-value">${fmtMod(total)}</span>
      <span class="skill-name">${ABILITY_NAMES[ab]}</span>
      <span class="skill-stat">${ab}</span>
    </div>`;
  }).join('');
}

function renderSkills(){
  const c=currentChar;
  const pb=getProfBonus(c.level||1);
  const skills=c.skills||{};
  updatePassivePerception();
  document.getElementById('skills-list').innerHTML=Object.entries(skills).sort(([a],[b])=>a.localeCompare(b)).map(([name,sk])=>{
    const mod=getMod(c.stats?.[sk.stat]||10);
    const bonus=sk.expert?pb*2:sk.prof?pb:0;
    const total=mod+bonus;
    const cls=sk.expert?'expert':sk.prof?'proficient':'';
    return `<div class="skill-row">
      <button class="prof-toggle ${cls}" onclick="cycleSkillProf('${name}')">✓</button>
      <span class="skill-value">${fmtMod(total)}</span>
      <span class="skill-name">${name}</span>
      <span class="skill-stat">${sk.stat}</span>
    </div>`;
  }).join('');
}

function renderSpellSlots(){
  const c=currentChar;
  document.getElementById('spell-slot-grid').innerHTML=Object.entries(c.spell_slots||{}).map(([level,sl])=>{
    const total=sl.total||0;
    const used=sl.used||0;
    let pips='';
    for(let i=0;i<total;i++) pips+=`<div class="slot-pip ${i<used?'used':'available'}" onclick="toggleSlot(${level},${i})"></div>`;
    return `<div class="spell-slot-row">
      <span class="slot-level">${level==0?'Cantrip':ORDINALS[level]+' Lvl'}</span>
      <div class="slot-pips">${pips}</div>
      <input class="slot-total-input" type="number" value="${total}" min="0" max="9" oninput="slotTotalUpdate(${level},this.value)">
    </div>`;
  }).join('');
}

function renderSpellList(){
  const spells=currentChar.spells||[];
  const container=document.getElementById('spell-list');
  if(!spells.length){container.innerHTML='<p style="color:var(--text-d);font-size:.85rem;padding:8px 0;">No spells known.</p>';return;}
  container.innerHTML=[...spells].sort((a,b)=>a.level-b.level).map((sp,i)=>{
    const origIdx=currentChar.spells.indexOf(sp);
    const levelStr=sp.level==0?'Cantrip':ORDINALS[sp.level]+' level';
    const meta=[levelStr,sp.school,sp.casting_time,sp.range,sp.duration].filter(Boolean).join(' · ');
    const badges=(sp.concentration?'<span style="font-size:.7rem;background:var(--accent2);color:#fff;border-radius:3px;padding:1px 4px;margin-left:4px;">C</span>':'')
               +(sp.ritual?'<span style="font-size:.7rem;background:var(--text-d);color:#fff;border-radius:3px;padding:1px 4px;margin-left:4px;">R</span>':'');
    return `<div class="spell-entry">
      <button class="spell-prepared-toggle ${sp.prepared?'prepared':''}" onclick="toggleSpellPrepared(${origIdx})">✓</button>
      <div style="flex:1;"><div class="spell-name">${sp.name}${badges}</div><div class="spell-meta">${meta}${sp.components?' · '+sp.components:''}</div></div>
      <button class="spell-del" onclick="removeSpell(${origIdx})">✕</button>
    </div>`;
  }).join('');
}

function renderInventory(){
  const items=currentChar.inventory||[];
  const container=document.getElementById('item-list');
  if(!items.length){container.innerHTML='<p style="color:var(--text-d);font-size:.85rem;padding:8px 0;">Your pack is empty.</p>';return;}
  container.innerHTML=items.map((item,i)=>`
    <div class="item-entry">
      <div class="item-info">
        <div class="item-name">${item.name}</div>
        <div class="item-meta">${[item.weight?item.weight+' lbs':'',item.desc].filter(Boolean).join(' · ')}</div>
      </div>
      <button style="background:none;border:none;color:var(--text-d);cursor:pointer;font-size:1.1rem;" onclick="adjustItemQty(${i},-1)">−</button>
      <span class="item-qty">${item.qty||1}</span>
      <button style="background:none;border:none;color:var(--text-d);cursor:pointer;font-size:1.1rem;" onclick="adjustItemQty(${i},1)">+</button>
      <button class="item-del" onclick="removeItem(${i})">✕</button>
    </div>`).join('');
}

function renderCurrency(){
  const cur=currentChar.currency||{};
  document.getElementById('currency-row').innerHTML=CURRENCIES.map(c=>`
    <div class="currency-box">
      <div style="font-size:1rem;margin-bottom:3px;">${c.label==='GP'?'💰':c.label==='PP'?'💎':'🪙'}</div>
      <input type="number" value="${cur[c.key]||0}" min="0" style="color:${c.color};" oninput="currencyUpdate('${c.key}',this.value)">
      <div>${c.label}</div>
    </div>`).join('');
}

function renderFeatures(){
  const features=currentChar.features||[];
  const container=document.getElementById('feature-list');
  if(!features.length){container.innerHTML='';return;}
  container.innerHTML=features.map((f,i)=>`
    <div class="feature-card">
      <div class="feature-card-name">
        ${f.name}
        <button class="feature-del" onclick="removeFeature(${i})">✕</button>
      </div>
      ${f.desc?`<div class="feature-card-desc">${f.desc}</div>`:''}
    </div>`).join('');
}

function updatePassivePerception(){
  const c=currentChar;
  if(!c) return;
  const pb=getProfBonus(c.level||1);
  const sk=c.skills?.['Perception'];
  const wisMod=getMod(c.stats?.WIS||10);
  const bonus=sk?.expert?pb*2:sk?.prof?pb:0;
  const passive=10+wisMod+bonus;
  const el=document.getElementById('passive-perception');
  if(el) el.textContent=passive;
}

function renderSpellStats(){
  const c=currentChar;
  if(!c||!gameData) return;
  const cls=(gameData.classes||[]).find(cl=>cl.name===c.class);
  if(!cls||cls.caster_type==='none'){
    document.getElementById('spell-class').textContent='—';
    document.getElementById('spell-save-dc').textContent='—';
    document.getElementById('spell-atk-bonus').textContent='—';
    return;
  }
  const castAbilityMap={
    'Bard':'CHA','Cleric':'WIS','Druid':'WIS','Paladin':'CHA',
    'Ranger':'WIS','Sorcerer':'CHA','Warlock':'CHA','Wizard':'INT',
    'Artificer':'INT','Monk':'WIS'
  };
  const castAb=castAbilityMap[c.class]||'INT';
  const abMod=getMod(c.stats?.[castAb]||10);
  const pb=getProfBonus(c.level||1);
  document.getElementById('spell-class').textContent=c.class+' ('+castAb+')';
  document.getElementById('spell-save-dc').textContent=8+pb+abMod;
  document.getElementById('spell-atk-bonus').textContent=fmtMod(pb+abMod);
}

function renderClassFeatures(){
  const c=currentChar;
  const section=document.getElementById('class-features-section');
  const list=document.getElementById('class-features-list');
  if(!gameData||!c.class){section.style.display='none';return;}
  const cls=(gameData.classes||[]).find(cl=>cl.name===c.class);
  const features=(cls?.class_features||[]).filter(f=>f.level<=(c.level||1));
  if(!features.length){section.style.display='none';return;}
  section.style.display='block';
  list.innerHTML=features.map(f=>`
    <div class="feature-card">
      <div class="feature-card-name">
        ${f.name}
        <span class="feature-card-level">Level ${f.level}</span>
      </div>
      <div class="feature-card-desc">${f.desc}</div>
    </div>`).join('');
}

function renderExhaustion(){
  const c=currentChar;
  const level=c.exhaustion||0;
  document.getElementById('exhaustion-level-display').textContent=level;
  const pips=document.getElementById('exhaustion-pips');
  pips.innerHTML=[1,2,3,4,5,6].map(i=>`
    <div class="exhaustion-pip ${i<=level?'active':''}" onclick="setExhaustion(${i})" title="${EXHAUSTION_EFFECTS[i]}">${i}</div>`
  ).join('');
  document.getElementById('exhaustion-effect').textContent=level>0?`Effect: ${EXHAUSTION_EFFECTS[level]}`:'No exhaustion';
}

function renderAttacks(){
  const attacks=currentChar.attacks||[];
  const tbody=document.getElementById('attacks-tbody');
  if(!tbody) return;
  if(!attacks.length){
    tbody.innerHTML=`<tr><td colspan="5" style="color:var(--text-d);font-size:.8rem;padding:8px 6px;font-style:italic;">No attacks added yet.</td></tr>`;
    return;
  }
  tbody.innerHTML=attacks.map((atk,i)=>`
    <tr>
      <td><input type="text" value="${atk.name||''}" placeholder="Longsword" oninput="updateAttack(${i},'name',this.value)"></td>
      <td><input type="text" value="${atk.atk_bonus||''}" placeholder="+5" oninput="updateAttack(${i},'atk_bonus',this.value)" style="width:60px;"></td>
      <td><input type="text" value="${atk.damage||''}" placeholder="1d8+3 slashing" oninput="updateAttack(${i},'damage',this.value)"></td>
      <td style="width:44px;">
        <button class="atk-roll-btn" onclick="rollAttack(${i})">🎲 ATK</button>
        <button class="atk-roll-btn" onclick="rollDamage(${i})">💥 DMG</button>
      </td>
      <td><button class="atk-del" onclick="removeAttack(${i})">✕</button></td>
    </tr>`).join('');
}
