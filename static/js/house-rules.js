// ══════════════════════════════════════════════════════════════════
// HOUSE RULES
// ══════════════════════════════════════════════════════════════════
let houseRules = [];
let houseRulesEditingId = null;
const houseRulesConfirmDelete = new Set();

async function loadHouseRules() {
  try {
    const res = await fetch('/api/house-rules');
    houseRules = await res.json();
    renderHouseRules();
  } catch(e) { console.error('Failed to load house rules', e); }
}

function renderHouseRules() {
  const el = document.getElementById('house-rules-list');
  if (!el) return;
  if (!houseRules.length) {
    el.innerHTML = '<div style="color:var(--text-d);font-size:.85rem;font-style:italic;text-align:center;padding:20px 0;">No house rules yet.</div>';
    return;
  }
  const byCategory = {};
  houseRules.forEach(r => {
    const cat = r.category || 'General';
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(r);
  });
  const cats = ['General','Combat','Magic','Skills','Exploration','Character Creation','Other'];
  const sorted = Object.entries(byCategory).sort(([a],[b]) => cats.indexOf(a) - cats.indexOf(b));
  el.innerHTML = sorted.map(([cat, rules]) => `
    <div class="section-title">${escHtml(cat)}</div>
    ${rules.map(r => `
      <div class="house-rule-entry">
        ${houseRulesEditingId === r.id ? renderRuleEditForm(r) : `
          <div class="house-rule-title">
            <span>${escHtml(r.title)}</span>
            <div style="display:flex;gap:2px;align-items:center;flex-shrink:0;">
              <button class="house-rule-edit" onclick="startEditRule('${escHtml(r.id)}')" title="Edit">✎</button>
              ${houseRulesConfirmDelete.has(r.id) ? `
                <button class="house-rule-confirm-del" onclick="deleteHouseRule('${escHtml(r.id)}')">Delete?</button>
                <button class="house-rule-cancel-del" onclick="cancelDeleteRule('${escHtml(r.id)}')">Cancel</button>
              ` : `
                <button class="house-rule-del" onclick="startDeleteRule('${escHtml(r.id)}')" title="Delete">✕</button>
              `}
            </div>
          </div>
          <div class="house-rule-desc">${escHtml(r.description)}</div>
        `}
      </div>
    `).join('')}
  `).join('');
}

function renderRuleEditForm(r) {
  const cats = ['General','Combat','Magic','Skills','Exploration','Character Creation','Other'];
  return `
    <div class="house-rule-edit-form">
      <div class="field-group">
        <label>Title</label>
        <input type="text" id="edit-rule-title" value="${escHtml(r.title)}">
      </div>
      <div class="field-group" style="margin-top:8px;">
        <label>Category</label>
        <select id="edit-rule-category">
          ${cats.map(c => `<option value="${c}"${c===r.category?' selected':''}>${c}</option>`).join('')}
        </select>
      </div>
      <textarea id="edit-rule-desc">${escHtml(r.description)}</textarea>
      <div class="house-rule-edit-btns">
        <button class="confirm-btn" onclick="saveEditRule('${escHtml(r.id)}')" style="margin-top:0;">Save</button>
        <button class="cancel-btn" onclick="cancelEditRule()" style="margin-top:0;">Cancel</button>
      </div>
    </div>
  `;
}

function startDeleteRule(id) {
  houseRulesConfirmDelete.add(id);
  renderHouseRules();
}

function cancelDeleteRule(id) {
  houseRulesConfirmDelete.delete(id);
  renderHouseRules();
}

function startEditRule(id) {
  houseRulesEditingId = id;
  houseRulesConfirmDelete.clear();
  renderHouseRules();
}

function cancelEditRule() {
  houseRulesEditingId = null;
  renderHouseRules();
}

async function saveEditRule(id) {
  const title = document.getElementById('edit-rule-title').value.trim();
  const category = document.getElementById('edit-rule-category').value;
  const description = document.getElementById('edit-rule-desc').value.trim();
  if (!title || !description) return;
  try {
    await fetch('/api/house-rules/' + encodeURIComponent(id), {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({title, category, description})
    });
    houseRulesEditingId = null;
    await loadHouseRules();
  } catch(e) { console.error('Failed to update house rule', e); }
}

async function addHouseRule() {
  const title = document.getElementById('new-rule-title').value.trim();
  const category = document.getElementById('new-rule-category').value;
  const description = document.getElementById('new-rule-desc').value.trim();
  if (!title || !description) return;
  try {
    await fetch('/api/house-rules', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({title, category, description})
    });
    document.getElementById('new-rule-title').value = '';
    document.getElementById('new-rule-desc').value = '';
    await loadHouseRules();
  } catch(e) { console.error('Failed to add house rule', e); }
}

async function deleteHouseRule(id) {
  houseRulesConfirmDelete.delete(id);
  try {
    await fetch('/api/house-rules/' + encodeURIComponent(id), {method: 'DELETE'});
    await loadHouseRules();
  } catch(e) { console.error('Failed to delete house rule', e); }
}
