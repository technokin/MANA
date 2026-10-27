// Minimal DOM/canvas harness used by pytest to exercise the shipped replay UI
// without requiring a full VS Code GUI. It deliberately loads the real viewer.js.
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const recordingPath = process.argv[2];
const viewerPath = process.argv[3];
const inspectMotion = process.argv.includes('--inspect-motion');
const testVisualLab = process.argv.includes('--test-visual-lab');
const hugeViewport = process.argv.includes('--huge-viewport');
const testMotionPolicy = process.argv.includes('--test-motion-policy');
const prefersReducedMotion = process.argv.includes('--prefers-reduced-motion');
const savedReduceMotion = process.argv.includes('--saved-reduce-motion');
if (!recordingPath || !viewerPath) throw new Error('usage: node visualiser_webview_harness.js recording.jsonl viewer.js [--inspect-motion]');
const events = fs.readFileSync(recordingPath, 'utf8').split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
const canvasLabels = [];
const canvasOps = Object.create(null);

class FakeClassList {
  constructor() { this.values = new Set(); }
  add(value) { this.values.add(value); }
  remove(value) { this.values.delete(value); }
  toggle(value, enabled) {
    if (enabled === undefined) enabled = !this.values.has(value);
    enabled ? this.values.add(value) : this.values.delete(value);
    return enabled;
  }
}
class FakeElement {
  constructor(tag = 'div', id = '') {
    this.tagName = tag.toUpperCase(); this.id = id; this.children = []; this.listeners = {};
    this.dataset = {}; this.classList = new FakeClassList(); this.style = { setProperty(name,value) { this[name] = value; } };
    this.textContent = ''; this.value = ''; this.hidden = false; this.width = 900; this.height = 600;
    this.title = ''; this.tabIndex = -1; this.attributes = {}; this.checked = false;
  }
  addEventListener(name, callback) { (this.listeners[name] ||= []).push(callback); }
  setAttribute(name, value) { this.attributes[name] = value; }
  dispatch(name, event = {}) { for (const callback of this.listeners[name] || []) callback({target:this, preventDefault(){}, ...event}); }
  append(...children) { this.children.push(...children); }
  focus() { this.focused = true; }
  get options() { return this.children.filter(child => child.tagName === 'OPTION'); }
  replaceChildren(...children) { this.children = [...children]; }
  getBoundingClientRect() { const width=hugeViewport && this.id==='sceneCanvas' ? 5_000_000 : 900; const height=hugeViewport && this.id==='sceneCanvas' ? 1 : 600; return {width,height,left:0,top:0,right:width,bottom:height}; }
  getContext() { return context; }
}
const context = new Proxy({}, {
  get(target, key) {
    if (key in target) return target[key];
    target[key] = (...args) => {
      canvasOps[String(key)] = (canvasOps[String(key)] || 0) + 1;
      if (key === 'fillText' && args.length) canvasLabels.push(String(args[0]));
      if (key === 'createLinearGradient' || key === 'createRadialGradient') {
        return { addColorStop() { canvasOps.addColorStop = (canvasOps.addColorStop || 0) + 1; } };
      }
      if (key === 'measureText') return { width: String(args[0] || '').length * 6 };
      return undefined;
    };
    return target[key];
  },
  set(target,key,value){target[key]=value;return true;}
});

const ids = [
  'openVisualSettings','closeVisualSettings','visualSettings','lookPreset','palettePreset','backgroundPreset','spellStyle','trailStyle','glyphStyle','adaptiveStatus',
  'customColorTarget','customColorValue','applyCustomColor','clearCustomColors','customColorSwatches','fxColorTarget','fxColorValue','applyFxColor','clearFxColors','fxColorSwatches','effectIntensity','effectIntensityOut','glow','glowOut','trailLength','trailLengthOut','particleDensity','particleDensityOut','spellSize','spellSizeOut','weatherIntensity','weatherIntensityOut','gridOpacity','gridOpacityOut',
  'showParticles','showImpacts','showVectors','showActorAuras','showTrajectory','showGlyphs','showSpellNames','highContrastEdges','reduceMotion','resetVisualSettings','exportVisualSettings','importVisualSettings','saveVisualSettings','settingsStatus',
  'sceneCanvas','timeline','play','speed','activityList','sceneNotice','result','title','positionLabel',
  'eventLabel','timeLabel','footerStatus','detailName','detailSubtitle','detailFacts','prev','next','replay',
  'prevImpact','nextImpact','objectList','objectCount','objectSearch','objectFilter','objectLimitNote','objectsEmpty',
  'activitySearch','activityFilter','activityEmpty','worldFacts','worldSummary','spellName','spellSubtitle','spellHero','spellFacts','spellTrace','spellEmpty','toggleGrid','toggleLabels','toggleEffects','toggleWeather','toggleSpellForms','focusSelected'
];
const elements = new Map(ids.map(id => [id, new FakeElement(id === 'sceneCanvas' ? 'canvas' : 'div', id)]));
elements.get('visualSettings').hidden = true;
for (const id of ['toggleGrid','toggleLabels','toggleEffects','toggleWeather','toggleSpellForms']) elements.get(id).setAttribute('aria-pressed','true');
const tabs = ['objects','activity','spell','details','world'].map(tab => { const e=new FakeElement('button'); e.dataset.tab=tab; return e; });
const views = ['scene','objects','activity','spell','details','world'].map(id => elements.get(id) || new FakeElement('section',id));
// These three view IDs are separate from the controls.
for (const v of views) elements.set(v.id,v);
const body = new FakeElement('body','body');
const documentElement = new FakeElement('html','documentElement');
const document = {
  body, documentElement,
  getElementById(id) { if (!elements.has(id)) elements.set(id,new FakeElement('div',id)); return elements.get(id); },
  createElement(tag) { return new FakeElement(tag); },
  hidden:false,
  addEventListener(name, callback) { (document.listeners[name] ||= []).push(callback); },
  listeners:{},
  querySelectorAll(selector) { if (selector === '.tab') return tabs; if (selector === '.view') return views; return []; }
};
const listeners = {};
const window = { devicePixelRatio:1, performance:{now:()=>1000}, addEventListener(name, callback){ (listeners[name] ||= []).push(callback); }, matchMedia:()=>({matches:prefersReducedMotion, addEventListener(){}, addListener(){}}) };
if (inspectMotion) window.__MANA_VISUALISER_TEST__ = true;
const postedMessages = [];
const vscode = { setState(){}, postMessage(message){ postedMessages.push(message); } };
const sandbox = {
  document, window, console, acquireVsCodeApi: () => vscode,
  requestAnimationFrame: () => 1, cancelAnimationFrame(){}, setTimeout, clearTimeout,
  Math, Number, String, Array, Map, Set, Object, JSON, Infinity, Boolean
};
vm.runInNewContext(fs.readFileSync(viewerPath,'utf8'), sandbox, {filename:viewerPath, timeout:15000});
const deliver = data => { for (const callback of listeners.message || []) callback({data}); };
if (savedReduceMotion) deliver({type:'visualSettings',settings:{reduceMotion:true}});
deliver({type:'loadStart',title:path.basename(recordingPath),reduceMotion:false});
const records = events.filter(event => event && event.type !== 'recording');
for (let start = 0; start < records.length; start += 200) {
  deliver({type:'loadChunk',events:records.slice(start,start+200)});
}
deliver({type:'loadDone',records:records.length});
const timeline = elements.get('timeline');
// Seek to the end so the harness tests final snapshots and failure messages.
timeline.value = String(Math.max(0, events.length - 2));
timeline.dispatch('input');
const spellApi = inspectMotion && window.__MANA_VISUALISER_TEST_API__ ? window.__MANA_VISUALISER_TEST_API__ : null;
// For render metrics, inspect a frame where moving tracks have begun, rather
// than the recording's final result frame where completed projectiles vanish.
if (spellApi) {
  const moving = spellApi.tracks().filter(track => !track.isActor);
  if (moving.length) {
    timeline.value = String(Math.max(...moving.map(track => track.startIndex)));
    timeline.dispatch('input');
  }
}
const initialRenderMetrics = spellApi ? spellApi.renderMetrics() : null;
const initialMotionBoundsBuildCount = spellApi ? spellApi.motionBoundsBuildCount() : null;
const archetypes = spellApi ? { firebolt: spellApi.archetype('steering_firebolt fire bolt'), iceShield: spellApi.archetype('ice shield'), waterStream: spellApi.archetype('water stream'), summons: spellApi.archetype('summon_fire_drake') } : null;
const allActivityText = elements.get('activityList').children.map(li => li.children.map(child => child.textContent).join(' ')).join('\n');
const lastRecordingEvent = [...events].reverse().find(e => e.type === 'spell.result');
const drawnEntityLabels = canvasLabels.filter(label => label === 'Griffin').length;
const grid = elements.get('toggleGrid');
const gridInitiallyPressed = grid.attributes['aria-pressed'];
grid.dispatch('click');
const gridToggleWorks = grid.attributes['aria-pressed'] === 'false';
grid.dispatch('click');
const objectSearch = elements.get('objectSearch');
objectSearch.value = '__mana_harness_no_match__'; objectSearch.dispatch('input');
const objectNoMatchWorks = elements.get('objectsEmpty').hidden === false;
objectSearch.value = ''; objectSearch.dispatch('input');
const activitySearch = elements.get('activitySearch');
activitySearch.value = '__mana_harness_no_match__'; activitySearch.dispatch('input');
const activityNoMatchWorks = elements.get('activityEmpty').hidden === false;
activitySearch.value = ''; activitySearch.dispatch('input');
const beforeJump = Number(timeline.value);
const jumpableRow = elements.get('activityList').children.find(row => (row.listeners.click || []).length > 0);
if (jumpableRow) jumpableRow.dispatch('click', {target:jumpableRow});
const activityJumpWorks = !!jumpableRow && Number(timeline.value) < beforeJump;
const renderedObjectCount = elements.get('objectList').children.length;
const objectListSemantics = elements.get('objectList').children.every(item => item.attributes.role === 'listitem' && item.children[0] && item.children[0].tagName === 'BUTTON');
const spellToggle = elements.get('toggleSpellForms');
const spellToggleInitiallyPressed = spellToggle.attributes['aria-pressed'];
spellToggle.dispatch('click');
const spellToggleWorks = spellToggle.attributes['aria-pressed'] === 'false';
let motionPolicyTests;
if (testMotionPolicy && spellApi) {
  const motionControl = elements.get('reduceMotion');
  motionControl.checked = true; motionControl.dispatch('change');
  const pausedSettingStopsIdle = !spellApi.idleAnimationScheduled() && spellApi.effectiveReduceMotion();
  motionControl.checked = false; motionControl.dispatch('change');
  if (prefersReducedMotion) {
    elements.get('palettePreset').value = 'bloodmoon'; elements.get('palettePreset').dispatch('change');
    motionPolicyTests = { pausedSettingStopsIdle, systemPreferencePreserved: spellApi.effectiveReduceMotion() && !spellApi.idleAnimationScheduled(), idleResumesAfterToggle: false };
  } else {
    motionPolicyTests = { pausedSettingStopsIdle, systemPreferencePreserved: true, idleResumesAfterToggle: !spellApi.effectiveReduceMotion() && spellApi.idleAnimationScheduled() };
  }
}
const spellTrace = spellApi ? spellApi.spellTrace() : [];
const motionTracks = inspectMotion && window.__MANA_VISUALISER_TEST_API__
  ? window.__MANA_VISUALISER_TEST_API__.tracks().map(track => ({
      id: track.id, isActor: track.isActor, startIndex: track.startIndex, endIndex: track.endIndex, spellName: track.spellName, entityName: track.entityName, points: track.points,
      samplesAtSegments: track.points.slice(1).map((point, index) => {
        const previous = track.points[index], position = (previous.index + point.index) / 2;
        return { playback: position, ...(track.at(position) || {}) };
      })
    })) : undefined;
let visualLabTests;
if (testVisualLab && spellApi) {
  elements.get('openVisualSettings').dispatch('click');
  const panelOpened = elements.get('visualSettings').hidden === false;
  elements.get('lookPreset').value = 'glacial-cathedral'; elements.get('lookPreset').dispatch('change');
  const afterRecipe = spellApi.settings();
  const recipeApplied = afterRecipe.palettePreset === 'arcane-frost' && afterRecipe.backgroundPreset === 'moonlit' && afterRecipe.spellStyle === 'fractured-glass' && afterRecipe.trailStyle === 'afterimage';
  // Earlier in this harness, the spell-form toggle is deliberately switched off
  // to test its accessibility state. Re-enable it here and seek to a moving
  // projectile sample so the setting sweep exercises actual body rendering.
  if (elements.get('toggleSpellForms').attributes['aria-pressed'] !== 'true') elements.get('toggleSpellForms').dispatch('click');
  const timeline = elements.get('timeline');
  const movingTracks = spellApi.tracks().filter(track => !track.isActor);
  if (movingTracks.length) timeline.value = String(Math.min(...movingTracks.map(track => track.startIndex)));
  timeline.dispatch('input');
  const enums = spellApi.settingEnums();
  for (const [control, choices] of [['palettePreset',enums.palettePreset],['backgroundPreset',enums.backgroundPreset],['spellStyle',enums.spellStyle],['trailStyle',enums.trailStyle],['glyphStyle',enums.glyphStyle]]) {
    for (const choice of choices) { elements.get(control).value = choice; elements.get(control).dispatch('change'); }
  }
  const drawingModesExercised = spellApi.renderMetrics().detailedSpellBodies > 0 && spellApi.renderMetrics().visibleSpellSilhouettes >= spellApi.renderMetrics().visibleProjectileHeads && enums.spellStyle.length >= 15 && enums.trailStyle.length >= 13 && enums.glyphStyle.length >= 14 && !Object.hasOwn(spellApi.settings(),'quality');
  const adaptiveBounds = spellApi.adaptiveGraphics().pixelCount <= 4_000_000 && spellApi.adaptiveGraphics().cacheEntries <= 512 && spellApi.adaptiveGraphics().cacheChars <= 1_500_000;
  elements.get('palettePreset').value = 'bloodmoon'; elements.get('palettePreset').dispatch('change');
  elements.get('spellStyle').value = 'pixel-art'; elements.get('spellStyle').dispatch('change');
  elements.get('trailStyle').value = 'helix'; elements.get('trailStyle').dispatch('change');
  elements.get('glyphStyle').value = 'knotwork'; elements.get('glyphStyle').dispatch('change');
  elements.get('backgroundPreset').value = 'forest'; elements.get('backgroundPreset').dispatch('change');
  elements.get('gridOpacity').value = '23'; elements.get('gridOpacity').dispatch('input');
  elements.get('showGlyphs').checked = false; elements.get('showGlyphs').dispatch('change');
  elements.get('reduceMotion').checked = true; elements.get('reduceMotion').dispatch('change');
  elements.get('customColorTarget').value = 'fire';
  elements.get('customColorValue').value = '#123456';
  elements.get('applyCustomColor').dispatch('click');
  const channelColors={core:'#aabbcc',trail:'#bbaa44',glyph:'#cc88dd',impact:'#ef6633',aura:'#44cc99',accent:'#fff0aa',outline:'#171717'};
  for (const [channel,value] of Object.entries(channelColors)) { elements.get('fxColorTarget').value=channel;elements.get('fxColorValue').value=value;elements.get('applyFxColor').dispatch('click'); }
  const afterEditing = spellApi.settings();
  const customFire = spellApi.palette().fire;
  const fxCoreApplied = Object.entries(channelColors).every(([channel,value])=>afterEditing.fxColors[channel]===value&&spellApi.fxColor(channel,'#010203')===value);
  elements.get('exportVisualSettings').dispatch('click');
  const exportMessageSent = postedMessages.some(message => message.type === 'exportVisualSettings');
  elements.get('saveVisualSettings').dispatch('click');
  const savedMessage = postedMessages.find(message => message.type === 'saveVisualSettings');
  visualLabTests = {
    panelOpened,
    recipeApplied,
    drawingModesExercised,
    adaptiveBounds,
    fxCoreApplied,
    paletteThemeCount: spellApi.settingEnums().palettePreset.length,
    spellStyleCount: spellApi.settingEnums().spellStyle.length,
    trailStyleCount: spellApi.settingEnums().trailStyle.length,
    glyphStyleCount: spellApi.settingEnums().glyphStyle.length,
    fxColorChannelCount: elements.get('fxColorTarget').options.length,
    fullPresetApplied: afterEditing.palettePreset === 'bloodmoon' && afterEditing.spellStyle === 'pixel-art' && afterEditing.trailStyle === 'helix' && afterEditing.glyphStyle === 'knotwork' && afterEditing.backgroundPreset === 'forest' && !Object.hasOwn(afterEditing,'quality'),
    numericSettingApplied: afterEditing.gridOpacity === 23,
    accessibilityTogglesApplied: afterEditing.showGlyphs === false && afterEditing.reduceMotion === true,
    customColorApplied: customFire === '#123456' && afterEditing.customColors.fire === '#123456',
    exportMessageSent,
    saveMessageSent: !!savedMessage && savedMessage.settings.customColors.fire === '#123456' && savedMessage.settings.fxColors.core === '#aabbcc',
    paletteCount: Object.keys(spellApi.palette()).length,
    settingsPreset: afterEditing.palettePreset,
    customColorTargetCount: elements.get('customColorTarget').options.length
  };
}

console.log(JSON.stringify({
  ...(inspectMotion ? {motionTracks} : {}),
  canvasOps,
  inputRecords: events.length,
  timelineMax: Number(timeline.max),
  resultBadge: elements.get('result').textContent,
  selectedDetailName: elements.get('detailName').textContent,
  entityLabelsDrawn: drawnEntityLabels,
  activityContainsLimit: allActivityText.includes('active summoned-being limit (256) reached'),
  activityContainsFailure: allActivityText.includes('Spell failed'),
  sceneNotice: elements.get('sceneNotice').textContent,
  sceneNoticeVisible: !elements.get('sceneNotice').hidden,
  finalSpellOK: lastRecordingEvent ? lastRecordingEvent.ok : null,
  finalSpellCommitted: lastRecordingEvent ? lastRecordingEvent.committed : null,
  activityItems: elements.get('activityList').children.length,
  gridInitiallyPressed, gridToggleWorks, objectNoMatchWorks, activityNoMatchWorks, activityJumpWorks, renderedObjectCount, objectListSemantics,
  spellPanelTitle: elements.get('spellName').textContent,
  spellNameLabels: canvasLabels.filter(label => /ember|firebolt|steering/i.test(label)),
  spellPanelStageCount: elements.get('spellTrace').children.length,
  spellPanelHasHero: elements.get('spellHero').children.length > 0,
  spellToggleInitiallyPressed,
  spellToggleWorks, spellTraceLabels: spellTrace.map(item => item.label), spellTraceRecords: spellTrace.length,
  castRecords: spellApi ? spellApi.casts().length : 0,
  renderMetrics: spellApi ? spellApi.renderMetrics() : null,
  motionBoundsBuildCount: spellApi ? spellApi.motionBoundsBuildCount() : null,
  motionBoundsCacheStable: spellApi ? spellApi.motionBoundsBuildCount() === initialMotionBoundsBuildCount : null,
  sceneBounds: spellApi ? spellApi.sceneBounds() : null,
  cameraScale: spellApi ? spellApi.cameraScale() : null,
  effectiveReduceMotion: spellApi ? spellApi.effectiveReduceMotion() : null,
  idleAnimationScheduled: spellApi ? spellApi.idleAnimationScheduled() : null,
  ...(testMotionPolicy ? {motionPolicyTests} : {}),
  initialRenderMetrics, archetypes,
  worldSummaryPresent: elements.get('worldSummary').textContent.includes('WORLD SNAPSHOT'),
  canvasBackingWidth: elements.get('sceneCanvas').width, canvasBackingHeight: elements.get('sceneCanvas').height,
  ...(testVisualLab ? {visualLabTests} : {})
}));
