// ══════════════════════════════════════════════════════════════════
// CHARACTER CREATOR
// ══════════════════════════════════════════════════════════════════
let creatorEdition = '2024', selectedSkills = new Set();

function openCreator(){
  document.getElementById('screen-list').classList.remove('active');
  document.getElementById('screen-creator').classList.add('active');
  initCreator();
}
function closeCreator(){
  document.getElementById('screen-creator').classList.remove('active');
  document.getElementById('screen-list').classList.add('active');
}

async function initCreator(){
  creatorEdition='2024';
  selectedSkills=new Set();
  document.getElementById('creator-loading').style.display='block';
  document.getElementById('creator-form').style.display='none';
  await loadEditionData('2024');
  document.getElementById('creator-loading').style.display='none';
  document.getElementById('creator-form').style.display='block';
  selectEdition('2024');
  renderAbilityCreatorGrid();
}

async function loadEditionData(edition){
  gameData=await loadGameData(edition);
  const rSel=document.getElementById('c-race');
  rSel.innerHTML='<option value="">— choose a species —</option>';
  (gameData.races||[]).forEach(r=>{const o=document.createElement('option');o.value=r.name;o.textContent=r.name;rSel.appendChild(o);});
  const cSel=document.getElementById('c-class');
  cSel.innerHTML='<option value="">— choose a class —</option>';
  (gameData.classes||[]).forEach(c=>{const o=document.createElement('option');o.value=c.name;o.textContent=c.name;cSel.appendChild(o);});
  const bSel=document.getElementById('c-background');
  bSel.innerHTML='<option value="">— choose a background —</option>';
  (gameData.backgrounds||[]).forEach(b=>{const o=document.createElement('option');o.value=b.name;o.textContent=b.name;bSel.appendChild(o);});
  document.getElementById('c-race').value='';
  document.getElementById('c-class').value='';
  document.getElementById('c-subclass').innerHTML='<option value="">— after class —</option>';
  document.getElementById('c-background').value='';
  document.getElementById('race-preview').style.display='none';
  document.getElementById('class-preview').style.display='none';
  document.getElementById('bg-preview').style.display='none';
  document.getElementById('skill-picker').style.display='none';
  document.getElementById('char-summary').style.display='none';
  selectedSkills=new Set();
}

function selectEdition(ed){
  creatorEdition=ed;
  document.getElementById('ed-card-2024').className='edition-card'+(ed==='2024'?' selected-2024':'');
  document.getElementById('ed-card-2014').className='edition-card'+(ed==='2014'?' selected-2014':'');
  const note=document.getElementById('asi-note');
  note.textContent=ed==='2014'
    ? 'Fixed racial bonuses apply automatically. Variant Human: two stats +1 each (apply manually).'
    : 'Assign scores freely. Racial bonuses applied automatically on creation.';
  loadEditionData(ed);
}

function renderAbilityCreatorGrid(){
  const grid=document.getElementById('ability-creator-grid');
  grid.innerHTML=ABILITIES.map(ab=>`
    <div class="ability-creator-box">
      <label>${ab}</label>
      <input type="number" id="stat-${ab}" value="10" min="1" max="30" oninput="updateStatMod('${ab}')">
      <div class="amod" id="mod-${ab}">+0</div>
    </div>`).join('');
}
function updateStatMod(ab){
  const v=parseInt(document.getElementById('stat-'+ab).value)||10;
  document.getElementById('mod-'+ab).textContent=fmtMod(getMod(v));
}
function rollAllStats(){
  ABILITIES.forEach(ab=>{
    const rolls=[1,2,3,4].map(()=>Math.floor(Math.random()*6)+1).sort((a,b)=>a-b);
    rolls.shift();
    document.getElementById('stat-'+ab).value=rolls.reduce((a,b)=>a+b,0);
    updateStatMod(ab);
  });
}
function standardArray(){
  [15,14,13,12,10,8].forEach((v,i)=>{document.getElementById('stat-'+ABILITIES[i]).value=v;updateStatMod(ABILITIES[i]);});
}

function onRaceChange(){
  const name=document.getElementById('c-race').value;
  const preview=document.getElementById('race-preview');
  if(!name||!gameData){preview.style.display='none';return;}
  const race=(gameData.races||[]).find(r=>r.name===name);
  if(!race){preview.style.display='none';return;}
  const bonuses=Object.entries(race.ability_bonuses||{}).map(([k,v])=>k+' +'+v).join(', ')||'None';
  const traits=(race.traits||[]).slice(0,4).map(t=>
    `<div style="margin-bottom:5px;"><span style="color:var(--gold-d);font-family:'Cinzel',serif;font-size:.72rem;">${t.name}:</span> <span style="font-size:.8rem;color:var(--text-d);">${t.desc.slice(0,120)}${t.desc.length>120?'…':''}</span></div>`
  ).join('');
  document.getElementById('race-preview-content').innerHTML=`
    <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:7px;">
      <span class="preview-tag">Speed: ${race.speed} ft</span>
      <span class="preview-tag">${race.size}</span>
      ${race.darkvision?`<span class="preview-tag">Darkvision ${race.darkvision} ft</span>`:''}
      ${bonuses!=='None'?`<span class="preview-tag">+ASI: ${bonuses}</span>`:''}
      ${race.asi_note&&creatorEdition==='2014'?`<span class="preview-tag" style="color:#c8a8e8;border-color:var(--purple-b);">${race.asi_note}</span>`:''}
    </div>${traits}`;
  preview.style.display='block';
  const note=document.getElementById('racial-bonus-note');
  if(bonuses!=='None'){
    note.textContent=(creatorEdition==='2014'?'Fixed ASI: ':'Racial bonus: ')+bonuses+' — applied on creation';
    note.style.display='block';
  } else {
    note.style.display='none';
  }
  document.getElementById('c-speed').value=race.speed||30;
  updateCharSummary();
}

function onClassChange(){
  const name=document.getElementById('c-class').value;
  const preview=document.getElementById('class-preview');
  const subcSel=document.getElementById('c-subclass');
  subcSel.innerHTML='<option value="">— none / later —</option>';
  if(!name||!gameData){preview.style.display='none';document.getElementById('skill-picker').style.display='none';return;}
  const cls=(gameData.classes||[]).find(c=>c.name===name);
  if(!cls){preview.style.display='none';return;}
  (cls.subclasses||[]).forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=s;subcSel.appendChild(o);});
  const casterBadge=cls.caster_type!=='none'?`<span class="preview-tag">✨ ${cls.caster_type} caster</span>`:'';
  document.getElementById('class-preview-content').innerHTML=`
    <div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:7px;">
      <span class="preview-tag">Hit Die: ${cls.hit_die}</span>
      <span class="preview-tag">Saves: ${(cls.saving_throws||[]).join(', ')}</span>${casterBadge}
    </div>
    <div style="font-size:.8rem;color:var(--text-d);margin-bottom:3px;"><strong style="color:var(--gold-d);">Armor:</strong> ${(cls.armor_proficiencies||[]).join(', ')||'None'}</div>
    <div style="font-size:.8rem;color:var(--text-d);"><strong style="color:var(--gold-d);">Weapons:</strong> ${(cls.weapon_proficiencies||[]).join(', ')||'Simple'}</div>`;
  preview.style.display='block';
  selectedSkills=new Set();
  const num=cls.num_skill_choices||2;
  document.getElementById('skill-count').textContent=num;
  const opts=document.getElementById('skill-options');
  opts.innerHTML='';
  (cls.skill_choices||[]).forEach(sk=>{
    const ch=document.createElement('button');
    ch.className='skill-chip'; ch.textContent=sk;
    ch.onclick=()=>{
      if(selectedSkills.has(sk)){selectedSkills.delete(sk);ch.classList.remove('selected');}
      else if(selectedSkills.size<num){selectedSkills.add(sk);ch.classList.add('selected');}
      document.getElementById('skill-count').textContent=`${num} (${selectedSkills.size}/${num})`;
    };
    opts.appendChild(ch);
  });
  document.getElementById('skill-picker').style.display=(cls.skill_choices||[]).length?'block':'none';
  updateHPSuggestion();
  updateCharSummary();
}

function onBackgroundChange(){
  const name=document.getElementById('c-background').value;
  const preview=document.getElementById('bg-preview');
  if(!name||!gameData){preview.style.display='none';return;}
  const bg=(gameData.backgrounds||[]).find(b=>b.name===name);
  if(!bg){preview.style.display='none';return;}
  const tools=(bg.tool_proficiencies||[]).join(', ');
  const equip=(bg.equipment||[]).slice(0,5).join(', ');
  let html=`<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:7px;">${(bg.skill_proficiencies||[]).map(s=>`<span class="preview-tag">${s}</span>`).join('')}</div>`;
  if(tools) html+=`<div style="font-size:.8rem;color:var(--text-d);margin-bottom:3px;"><strong style="color:var(--gold-d);">Tools:</strong> ${tools}</div>`;
  if(equip) html+=`<div style="font-size:.8rem;color:var(--text-d);margin-bottom:3px;"><strong style="color:var(--gold-d);">Gear:</strong> ${equip}</div>`;
  if(creatorEdition==='2014'&&bg.personality_traits){
    html+=`<div style="font-size:.75rem;color:var(--purple-b);margin-top:5px;">✦ Includes Personality Traits, Ideals, Bonds &amp; Flaws</div>`;
  }
  document.getElementById('bg-preview-content').innerHTML=html;
  preview.style.display='block';
  updateCharSummary();
}

function updateHPSuggestion(){
  const clsName=document.getElementById('c-class').value;
  if(!clsName||!gameData) return;
  const cls=(gameData.classes||[]).find(c=>c.name===clsName);
  if(!cls) return;
  const level=parseInt(document.getElementById('c-level').value)||1;
  const con=parseInt(document.getElementById('stat-CON')?.value)||10;
  const conMod=getMod(con);
  const faces=cls.hit_die_faces||8;
  const hp=faces+conMod+(level-1)*(Math.floor(faces/2)+1+conMod);
  document.getElementById('c-hp').value=Math.max(1,hp);
  document.getElementById('hp-suggestion').textContent=`${faces}+CON per level = ${Math.max(1,hp)} HP at level ${level}`;
}

function updateCharSummary(){
  const name=document.getElementById('c-name')?.value?.trim();
  const race=document.getElementById('c-race')?.value;
  const cls=document.getElementById('c-class')?.value;
  const level=document.getElementById('c-level')?.value;
  const summary=document.getElementById('char-summary');
  if(!name&&!race&&!cls){summary.style.display='none';return;}
  const edLabel=creatorEdition==='2014'?'<span style="color:var(--purple-b);">5e 2014</span>':'<span style="color:#e8a0a0;">5e 2024</span>';
  const parts=[];
  if(name) parts.push(`<strong style="color:var(--ink)">${name}</strong>`);
  if(race||cls) parts.push([level?'Level '+level:'',race,cls].filter(Boolean).join(' '));
  parts.push(edLabel);
  document.getElementById('char-summary-content').innerHTML=parts.join(' — ');
  summary.style.display='block';
}

async function createCharacterFull(){
  const name=document.getElementById('c-name').value.trim();
  if(!name){alert('Please enter a character name.');return;}
  const raceName=document.getElementById('c-race').value;
  const className=document.getElementById('c-class').value;
  const bgName=document.getElementById('c-background').value;
  const level=parseInt(document.getElementById('c-level').value)||1;
  const race=(gameData?.races||[]).find(r=>r.name===raceName);
  const cls=(gameData?.classes||[]).find(c=>c.name===className);
  const bg=(gameData?.backgrounds||[]).find(b=>b.name===bgName);
  const stats={};
  ABILITIES.forEach(ab=>{
    let v=parseInt(document.getElementById('stat-'+ab)?.value)||10;
    if(race?.ability_bonuses?.[ab]) v+=race.ability_bonuses[ab];
    stats[ab]=Math.min(30,v);
  });
  const pb=getProfBonus(level);
  const skillTemplate={
    "Acrobatics":{"stat":"DEX","prof":false,"expert":false},"Animal Handling":{"stat":"WIS","prof":false,"expert":false},
    "Arcana":{"stat":"INT","prof":false,"expert":false},"Athletics":{"stat":"STR","prof":false,"expert":false},
    "Deception":{"stat":"CHA","prof":false,"expert":false},"History":{"stat":"INT","prof":false,"expert":false},
    "Insight":{"stat":"WIS","prof":false,"expert":false},"Intimidation":{"stat":"CHA","prof":false,"expert":false},
    "Investigation":{"stat":"INT","prof":false,"expert":false},"Medicine":{"stat":"WIS","prof":false,"expert":false},
    "Nature":{"stat":"INT","prof":false,"expert":false},"Perception":{"stat":"WIS","prof":false,"expert":false},
    "Performance":{"stat":"CHA","prof":false,"expert":false},"Persuasion":{"stat":"CHA","prof":false,"expert":false},
    "Religion":{"stat":"INT","prof":false,"expert":false},"Sleight of Hand":{"stat":"DEX","prof":false,"expert":false},
    "Stealth":{"stat":"DEX","prof":false,"expert":false},"Survival":{"stat":"WIS","prof":false,"expert":false}
  };
  selectedSkills.forEach(sk=>{if(skillTemplate[sk])skillTemplate[sk].prof=true;});
  (bg?.skill_proficiencies||[]).forEach(sk=>{if(skillTemplate[sk])skillTemplate[sk].prof=true;});
  const savingThrows={};
  ABILITIES.forEach(ab=>{savingThrows[ab]=(cls?.saving_throws||[]).includes(ab);});
  const slotsConfig=(cls?.spell_slots_by_level||{})[String(level)]||[];
  const spellSlots={};
  for(let i=1;i<=9;i++) spellSlots[i]={total:slotsConfig[i-1]||0,used:0};
  const inventory=(bg?.equipment||[]).filter(Boolean).map(item=>({name:item,qty:1,weight:'',desc:''}));
  const char={
    name,edition:creatorEdition,
    class:className||'',subclass:document.getElementById('c-subclass').value||'',
    race:raceName||'',background:bgName||'',alignment:document.getElementById('c-alignment').value||'',
    level,xp:0,proficiency_bonus:pb,stats,saving_throws:savingThrows,skills:skillTemplate,
    hp:{current:parseInt(document.getElementById('c-hp').value)||10,max:parseInt(document.getElementById('c-hp').value)||10,temp:0},
    hit_dice:{total:level,used:0,die:cls?.hit_die||'d8'},
    ac:parseInt(document.getElementById('c-ac').value)||10,
    initiative_bonus:getMod(stats.DEX),speed:parseInt(document.getElementById('c-speed').value)||30,
    death_saves:{successes:0,failures:0},spell_slots:spellSlots,
    spells:[],inventory,features:[],notes:'',inspiration:false,
    currency:{pp:0,gp:0,ep:0,sp:0,cp:0},
  };
  if(creatorEdition==='2014'){
    char.personality_traits=bg?.personality_traits?.[0]||'';
    char.ideals=bg?.ideals?.[0]||'';
    char.bonds=bg?.bonds?.[0]||'';
    char.flaws=bg?.flaws?.[0]||'';
    char.exhaustion=0;
    char.conditions=[];
  }
  try{
    await apiPost('/api/characters',char);
    closeCreator();
    await loadCharacter(name);
  }catch(e){alert('Failed to create character: '+e.message);}
}
