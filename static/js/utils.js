// ══════════════════════════════════════════════════════════════════
// CONSTANTS & MATH HELPERS
// ══════════════════════════════════════════════════════════════════
const ABILITIES = ['STR','DEX','CON','INT','WIS','CHA'];
const ABILITY_NAMES = {STR:'Strength',DEX:'Dexterity',CON:'Constitution',INT:'Intelligence',WIS:'Wisdom',CHA:'Charisma'};
const ORDINALS = ['','1st','2nd','3rd','4th','5th','6th','7th','8th','9th'];
const CURRENCIES = [{key:'pp',label:'PP',color:'#b0c4de'},{key:'gp',label:'GP',color:'#ffd700'},{key:'ep',label:'EP',color:'#c0c0c0'},{key:'sp',label:'SP',color:'#aaa'},{key:'cp',label:'CP',color:'#cd7f32'}];
const EXHAUSTION_EFFECTS = ['None','Disadvantage on ability checks','Speed halved','Disadvantage on attacks and saves','Max HP halved','Speed reduced to 0','Death'];

const SKILLS_DEF = [
  {name:'Acrobatics',stat:'DEX'},{name:'Animal Handling',stat:'WIS'},
  {name:'Arcana',stat:'INT'},{name:'Athletics',stat:'STR'},
  {name:'Deception',stat:'CHA'},{name:'History',stat:'INT'},
  {name:'Insight',stat:'WIS'},{name:'Intimidation',stat:'CHA'},
  {name:'Investigation',stat:'INT'},{name:'Medicine',stat:'WIS'},
  {name:'Nature',stat:'INT'},{name:'Perception',stat:'WIS'},
  {name:'Performance',stat:'CHA'},{name:'Persuasion',stat:'CHA'},
  {name:'Religion',stat:'INT'},{name:'Sleight of Hand',stat:'DEX'},
  {name:'Stealth',stat:'DEX'},{name:'Survival',stat:'WIS'}
];

function getMod(s){return Math.floor((s-10)/2);}
function fmtMod(m){return(m>=0?'+':'')+m;}
function getProfBonus(lvl){return Math.ceil(lvl/4)+1;}
function escHtml(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
