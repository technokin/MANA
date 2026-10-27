const vscode = require('vscode');
const fs = require('fs');
const os = require('os');
const path = require('path');
const readline = require('readline');
const { spawn } = require('child_process');
const crypto = require('crypto');

const MAX_SOURCE_BYTES = 2 * 1024 * 1024;
const MAX_RECORDING_BYTES = 25 * 1024 * 1024;
const MAX_RECORDING_LINE_BYTES = 1_000_000;
const MAX_RECORDS = 100_001;
const MAX_JSON_DEPTH = 32;
const MAX_JSON_NODES = 25_000;
const MAX_CHILD_OUTPUT_BYTES = 2 * 1024 * 1024;
const RUN_TIMEOUT_MS = 5 * 60 * 1000;
const VISUAL_SETTINGS_KEY = 'manaVisualiser.visualSettings.v1';
const VISUAL_SETTINGS_SCHEMA = 1;
const VISUAL_SETTING_ENUMS = {
  palettePreset: ['elemental','arcane-spectrum','ember-brass','tidal-depths','glacial','verdant','celestial','voidborne','rose-quartz','monochrome','high-contrast','retro-terminal','solar-flare','bloodmoon','aurora','volcanic','desertglass','deep-ocean','fae-wild','neon-noir','antique-grimoire','arcane-frost','infernal-court','bioluminescent','stormglass','spectral-ink','verdigris','royal-amethyst','sunken-kingdom','mythic-gold','night-bloom','desert-mirage'],
  backgroundPreset: ['graphite','midnight','deep-space','vellum','abyss','studio','high-contrast','forest','crimson','twilight','obsidian','moonlit','copper','nebula','slate','moonstone','volcanic-glass','deep-forest'],
  spellStyle: ['classic','crystalline','rune-tech','painterly','holographic','minimal','astral','comic-ink','prismatic','pixel-art','spectral','fractured-glass','ink-wash','rune-circuit','solarized'],
  trailStyle: ['tapered','ribbon','segmented','dashed','sparks','lightning','helix','none','comet','afterimage','mist','zigzag','rune-chain'],
  glyphStyle: ['runic','geometric','alchemical','orbitals','minimal','star-mandala','knotwork','off','zodiac','fractal','lattice','triune','eldritch-grid','script'],
};
const VISUAL_SETTING_RANGES = {
  effectIntensity: [0, 1.5], glow: [0, 1.8], trailLength: [4, 60],
  particleDensity: [0, 100], spellSize: [0.5, 1.8], weatherIntensity: [0, 100], gridOpacity: [0,100],
};
const VISUAL_SETTING_BOOLEANS = ['showParticles','showImpacts','showVectors','showActorAuras','showTrajectory','showGlyphs','showSpellNames','highContrastEdges','reduceMotion'];
function normalizeVisualSettings(input) {
  const value = input && typeof input === 'object' && !Array.isArray(input) ? input : {};
  const out = { schema: VISUAL_SETTINGS_SCHEMA };
  for (const [key, choices] of Object.entries(VISUAL_SETTING_ENUMS)) {
    out[key] = choices.includes(value[key]) ? value[key] : ({palettePreset:'elemental',backgroundPreset:'graphite',spellStyle:'classic',trailStyle:'tapered',glyphStyle:'runic'})[key];
  }
  // Older preset files may still contain a quality tier; rendering is adaptive now.
  delete out.quality;
  const defaults = { effectIntensity: 1, glow: 1, trailLength: 24, particleDensity: 60, spellSize: 1, weatherIntensity: 70, gridOpacity:70 };
  for (const [key, [min, max]] of Object.entries(VISUAL_SETTING_RANGES)) {
    const n = Number(value[key]);
    out[key] = Math.max(min, Math.min(max, Number.isFinite(n) ? n : defaults[key]));
  }
  for (const key of VISUAL_SETTING_BOOLEANS) out[key] = typeof value[key] === 'boolean' ? value[key] : ({showParticles:true,showImpacts:true,showVectors:false,showActorAuras:true,showTrajectory:true,showGlyphs:true,showSpellNames:true,highContrastEdges:false,reduceMotion:false})[key];
  const colors = {};
  if (value.customColors && typeof value.customColors === 'object' && !Array.isArray(value.customColors)) {
    for (const [key, color] of Object.entries(value.customColors).slice(0, 64)) {
      if (/^[a-zA-Z][a-zA-Z0-9_-]{0,31}$/.test(key) && typeof color === 'string' && /^#[0-9a-fA-F]{6}$/.test(color)) colors[key] = color.toLowerCase();
    }
  }
  out.customColors = colors;
  const fxColors = {};
  if (value.fxColors && typeof value.fxColors === 'object' && !Array.isArray(value.fxColors)) {
    for (const channel of ['core','trail','glyph','impact','aura','accent','outline']) { const color=value.fxColors[channel]; if (typeof color === 'string' && /^#[0-9a-fA-F]{6}$/.test(color)) fxColors[channel]=color.toLowerCase(); }
  }
  out.fxColors = fxColors;
  return out;
}

function restrictedPythonEnv() {
  const allowed = process.platform === 'win32'
    ? ['PATH', 'SystemRoot', 'WINDIR', 'SystemDrive', 'ComSpec', 'TEMP', 'TMP', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA']
    : ['PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL'];
  const env = {};
  for (const key of allowed) if (process.env[key] !== undefined) env[key] = process.env[key];
  env.PYTHONUTF8 = '1';
  env.PYTHONIOENCODING = 'utf-8';
  return env;
}

function removePrivateTempDirectory(directory) {
  if (!directory) return;
  const resolved = path.resolve(directory);
  const root = path.resolve(os.tmpdir()) + path.sep;
  if (!resolved.startsWith(root) || !path.basename(resolved).startsWith('mana-visualiser-')) return;
  try { fs.rmSync(resolved, { recursive: true, force: true, maxRetries: 2, retryDelay: 100 }); } catch (_) { /* best-effort cleanup */ }
}

function assertJsonDepth(line, maxDepth = MAX_JSON_DEPTH) {
  let depth = 0, inString = false, escaped = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inString) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
      continue;
    }
    if (ch === '"') inString = true;
    else if (ch === '{' || ch === '[') {
      depth++;
      if (depth > maxDepth) throw new Error(`Record nesting exceeds the ${maxDepth}-level safety limit.`);
    } else if (ch === '}' || ch === ']') depth--;
    if (depth < 0) throw new Error('Record has unbalanced JSON delimiters.');
  }
}

function validateRecordShape(event, lineNumber) {
  if (!event || typeof event !== 'object' || Array.isArray(event) || Object.getPrototypeOf(event) !== Object.prototype) {
    throw new Error(`Record ${lineNumber} must be a JSON object.`);
  }
  if (event.schema !== 1) throw new Error(`Record ${lineNumber} uses an unsupported schema version.`);
  if (typeof event.type !== 'string' || event.type.length < 1 || event.type.length > 100) {
    throw new Error(`Record ${lineNumber} has an invalid event type.`);
  }
  if (event.time !== undefined && (typeof event.time !== 'number' || !Number.isFinite(event.time) || Math.abs(event.time) > 1e12)) {
    throw new Error(`Record ${lineNumber} has an invalid timestamp.`);
  }
  const stack = [{ value: event, depth: 0 }];
  let nodes = 0;
  while (stack.length) {
    const current = stack.pop();
    nodes++;
    if (nodes > MAX_JSON_NODES) throw new Error(`Record ${lineNumber} contains too many values.`);
    const value = current.value;
    if (current.depth > MAX_JSON_DEPTH) throw new Error(`Record ${lineNumber} is nested too deeply.`);
    if (typeof value === 'string' && value.length > 20_000) throw new Error(`Record ${lineNumber} contains an oversized text value.`);
    if (Array.isArray(value)) {
      if (value.length > 5_000) throw new Error(`Record ${lineNumber} contains an oversized array.`);
      for (const child of value) stack.push({ value: child, depth: current.depth + 1 });
    } else if (value && typeof value === 'object') {
      const entries = Object.entries(value);
      if (entries.length > MAX_JSON_NODES) throw new Error(`Record ${lineNumber} contains too many fields.`);
      for (const [key, child] of entries) {
        if (key.length > 1_000) throw new Error(`Record ${lineNumber} contains an oversized field name.`);
        stack.push({ value: child, depth: current.depth + 1 });
      }
    } else if (typeof value === 'number' && !Number.isFinite(value)) {
      throw new Error(`Record ${lineNumber} contains a non-finite number.`);
    }
  }
}

let output;
let panel;
let extensionContext;
let visualSettingsCache = null;

function activate(context) {
  extensionContext = context;
  visualSettingsCache = normalizeVisualSettings(context.globalState.get(VISUAL_SETTINGS_KEY, {}));
  output = vscode.window.createOutputChannel('MANA Visualiser');
  context.subscriptions.push(output);
  context.subscriptions.push(vscode.commands.registerCommand('manaVisualiser.runWithVisualiser', runWithVisualiser));
  context.subscriptions.push(vscode.commands.registerCommand('manaVisualiser.openRecording', openRecording));
}

function findProjectRoot(sourcePath) {
  let current = path.dirname(sourcePath);
  while (true) {
    if (fs.existsSync(path.join(current, 'mana.py'))) return current;
    const parent = path.dirname(current);
    if (parent === current) return null;
    current = parent;
  }
}

async function runWithVisualiser() {
  if (!vscode.workspace.isTrusted) {
    vscode.window.showWarningMessage('MANA execution is disabled in an untrusted workspace. Trust it only after reviewing its files.');
    return;
  }
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'mana' || editor.document.uri.scheme !== 'file'
      || !editor.document.uri.fsPath.toLowerCase().endsWith('.mana')) {
    vscode.window.showInformationMessage('Open a .mana file first.');
    return;
  }
  if (editor.document.isDirty && !(await editor.document.save())) return;
  const source = editor.document.uri.fsPath;
  let sourceStat;
  try { sourceStat = fs.statSync(source); }
  catch (error) { vscode.window.showErrorMessage(`Cannot inspect MANA source: ${error.message}`); return; }
  if (!sourceStat.isFile() || sourceStat.size > MAX_SOURCE_BYTES) {
    vscode.window.showErrorMessage(`MANA source must be a regular file no larger than ${MAX_SOURCE_BYTES / (1024 * 1024)} MB.`);
    return;
  }
  const projectRoot = findProjectRoot(source);
  if (!projectRoot) {
    vscode.window.showErrorMessage('Could not find mana.py above this file. Open a MANA project or an existing recording.');
    return;
  }

  let temporaryDirectory;
  try { temporaryDirectory = fs.mkdtempSync(path.join(os.tmpdir(), 'mana-visualiser-')); }
  catch (error) { vscode.window.showErrorMessage(`Could not create a private recording directory: ${error.message}`); return; }
  const recording = path.join(temporaryDirectory, `${crypto.randomUUID()}.jsonl`);
  const python = vscode.workspace.getConfiguration('manaVisualiser').get('pythonPath', 'python');
  output.show(true);
  output.appendLine(`Running ${path.basename(source)} with observation enabled…`);
  await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: 'Running MANA and recording magical effects…', cancellable: false }, () => new Promise(resolve => {
    let child;
    let settled = false;
    let outputBytes = 0;
    let outputTruncated = false;
    let timedOut = false;
    let timeout;
    const appendBounded = chunk => {
      const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(String(chunk));
      const remaining = Math.max(0, MAX_CHILD_OUTPUT_BYTES - outputBytes);
      const take = Math.min(remaining, buffer.length);
      if (take) output.append(buffer.subarray(0, take).toString('utf8'));
      outputBytes += take;
      if (take < buffer.length && !outputTruncated) {
        outputTruncated = true;
        output.appendLine(`\n[Process output truncated at ${MAX_CHILD_OUTPUT_BYTES.toLocaleString()} bytes; stopping the process.]`);
        if (child && !child.killed) child.kill();
      }
    };
    const finish = async code => {
      if (settled) return;
      settled = true;
      if (timeout) clearTimeout(timeout);
      output.appendLine(`MANA exited with status ${code}.`);
      if (timedOut) output.appendLine(`Execution was stopped at the ${RUN_TIMEOUT_MS / 1000}-second timeout.`);
      if (fs.existsSync(recording)) {
        await showRecording(recording, path.basename(source), temporaryDirectory);
        if (code !== 0 || timedOut || outputTruncated) {
          vscode.window.showWarningMessage('MANA ended early. Open the partial recording that was created; see MANA Visualiser output for details.');
        }
      } else {
        removePrivateTempDirectory(temporaryDirectory);
        vscode.window.showWarningMessage('MANA did not create a recording. See the MANA Visualiser output for its diagnostic.');
      }
      resolve();
    };
    child = spawn(python, ['mana.py', '--record', recording, source], {
      cwd: projectRoot, windowsHide: true, shell: false, env: restrictedPythonEnv(),
    });
    timeout = setTimeout(() => { timedOut = true; if (child && !child.killed) child.kill(); }, RUN_TIMEOUT_MS);
    if (timeout.unref) timeout.unref();
    child.stdout.on('data', appendBounded);
    child.stderr.on('data', appendBounded);
    child.on('error', error => {
      if (settled) return;
      settled = true;
      if (timeout) clearTimeout(timeout);
      output.appendLine(`Could not start MANA: ${error.message}`);
      vscode.window.showErrorMessage(`Could not start '${python}'. Check MANA Magic Visualiser: Python Path in settings.`);
      removePrivateTempDirectory(temporaryDirectory);
      resolve();
    });
    child.on('close', code => { finish(code).catch(error => { removePrivateTempDirectory(temporaryDirectory); output.appendLine(`Could not open partial recording: ${error.message}`); resolve(); }); });
  }));
}
async function openRecording() {
  const selection = await vscode.window.showOpenDialog({
    canSelectMany: false,
    openLabel: 'Open MANA recording',
    filters: { 'MANA Visualiser recording (JSON Lines)': ['jsonl'] },
  });
  if (!selection || !selection[0]) return;
  await showRecording(selection[0].fsPath, path.basename(selection[0].fsPath));
}

async function showRecording(filePath, title, temporaryDirectory = null) {
  const config = vscode.workspace.getConfiguration('manaVisualiser');
  const configuredMB = Number(config.get('maximumRecordingMB', 25));
  const maxBytes = Math.min(MAX_RECORDING_BYTES, Math.max(1, Number.isFinite(configuredMB) ? configuredMB : 25)) * 1024 * 1024;
  let stat;
  try { stat = fs.statSync(filePath); }
  catch (error) { removePrivateTempDirectory(temporaryDirectory); vscode.window.showErrorMessage(`Could not read the recording: ${error.message}`); return; }
  if (!stat.isFile() || stat.size > maxBytes) {
    removePrivateTempDirectory(temporaryDirectory);
    vscode.window.showErrorMessage(`Recording is not a regular file or exceeds the ${Math.round(maxBytes / 1024 / 1024)} MB limit.`);
    return;
  }

  if (panel) panel.dispose();
  const currentPanel = vscode.window.createWebviewPanel(
    'manaMagicVisualiser', `MANA: ${title}`, vscode.ViewColumn.Active,
    // The webview is re-created when reopened instead of keeping a large replay
    // graph alive in the background. The JSONL file is streamed back in chunks.
    { enableScripts: true, retainContextWhenHidden: false, localResourceRoots: [vscode.Uri.file(path.join(__dirname, 'media'))] }
  );
  panel = currentPanel;
  currentPanel.webview.html = getHtml(currentPanel.webview);
  let groupMaximised = false;
  let streamToken = 0;
  let disposed = false;
  let startMaximisedPending = config.get('startMaximised', true) !== false;

  const setGroupMaximised = async next => {
    if (groupMaximised === next) return;
    try {
      await vscode.commands.executeCommand('workbench.action.toggleMaximizeEditorGroup');
      groupMaximised = next;
      if (panel === currentPanel) await currentPanel.webview.postMessage({ type: 'layoutState', maximised: groupMaximised });
    } catch (error) {
      output.appendLine(`Could not ${next ? 'maximise' : 'restore'} the editor group: ${error.message}`);
    }
  };
  currentPanel.webview.onDidReceiveMessage(message => {
    if (disposed || panel !== currentPanel) return;
    if (message && message.type === 'close') { currentPanel.dispose(); return; }
    if (message && message.type === 'maximize') {
      setGroupMaximised(!groupMaximised);
      return;
    }
    if (message && message.type === 'ready') {
      currentPanel.webview.postMessage({ type: 'visualSettings', settings: normalizeVisualSettings(visualSettingsCache || extensionContext.globalState.get(VISUAL_SETTINGS_KEY, {})) });
      const stream = () => {
        // A pending maximise command can resolve after the panel has already
        // closed. Do not start I/O for a dead panel; retry temporary cleanup too.
        if (disposed || panel !== currentPanel) { removePrivateTempDirectory(temporaryDirectory); return; }
        const token = ++streamToken;
        return streamRecording(currentPanel, filePath, title, token,
          () => !disposed && panel === currentPanel && token === streamToken).catch(error => {
          if (!disposed && panel === currentPanel && token === streamToken) currentPanel.webview.postMessage({ type: 'loadError', message: error.message });
        }).finally(() => {
          // Windows may refuse to remove an open temporary recording. Retry only
          // after the streaming reader has destroyed its file handle.
          if (disposed) removePrivateTempDirectory(temporaryDirectory);
        });
      };
      if (startMaximisedPending) {
        startMaximisedPending = false;
        setGroupMaximised(true).finally(stream);
      } else {
        stream();
      }
    }
    if (message && message.type === 'saveVisualSettings') {
      const settings = normalizeVisualSettings(message.settings);
      currentPanel.webview.postMessage({ type: 'visualSettings', settings });
      currentPanel.__manaVisualSettings = settings;
      visualSettingsCache = settings;
      extensionContext.globalState.update(VISUAL_SETTINGS_KEY, settings).then(undefined, error => output.appendLine(`Could not persist Visualiser settings: ${error.message}`));
      return;
    }
    if (message && message.type === 'exportVisualSettings') {
      const settings = normalizeVisualSettings(message.settings);
      exportVisualSettings(settings).catch(error => vscode.window.showErrorMessage(`Could not export Visualiser settings: ${error.message}`));
      return;
    }
    if (message && message.type === 'importVisualSettings') {
      importVisualSettings(currentPanel).catch(error => vscode.window.showErrorMessage(`Could not import Visualiser settings: ${error.message}`));
      return;
    }
    if (message && message.type === 'jumpToSource' && typeof message.file === 'string'
        && message.file.length <= 4_096 && Number.isSafeInteger(message.line) && message.line > 0) {
      openSourceLocation(message.file, message.line).catch(error =>
        vscode.window.showWarningMessage(`Could not open source location: ${error.message}`));
    }
  }, undefined, []);
  currentPanel.onDidDispose(() => {
    disposed = true;
    streamToken++;
    if (panel === currentPanel) panel = undefined;
    if (groupMaximised) {
      groupMaximised = false;
      vscode.commands.executeCommand('workbench.action.toggleMaximizeEditorGroup').then(undefined, error =>
        output.appendLine(`Could not restore the editor layout after closing the Visualiser: ${error.message}`));
    }
    removePrivateTempDirectory(temporaryDirectory);
  }, undefined, []);
}

async function exportVisualSettings(settings) {
  const target = await vscode.window.showSaveDialog({
    saveLabel: 'Export MANA Visualiser preset',
    filters: { 'JSON preset': ['json'] },
    defaultUri: vscode.Uri.file(path.join(os.homedir(), 'mana-visualiser-preset.json')),
  });
  if (!target) return;
  await fs.promises.writeFile(target.fsPath, `${JSON.stringify({ app: 'MANA Magic Visualiser', schema: VISUAL_SETTINGS_SCHEMA, settings }, null, 2)}\n`, { encoding: 'utf8', flag: 'w' });
  vscode.window.showInformationMessage('MANA Visualiser preset exported.');
}

async function importVisualSettings(targetPanel) {
  const selections = await vscode.window.showOpenDialog({
    canSelectMany: false,
    openLabel: 'Import MANA Visualiser preset',
    filters: { 'MANA Visualiser settings': ['json'] },
  });
  if (!selections || !selections[0]) return;
  const stat = await fs.promises.stat(selections[0].fsPath);
  if (!stat.isFile() || stat.size > 128 * 1024) throw new Error('Preset must be a regular JSON file smaller than 128 KB.');
  const raw = JSON.parse(await fs.promises.readFile(selections[0].fsPath, 'utf8'));
  if (!raw || typeof raw !== 'object' || raw.schema !== VISUAL_SETTINGS_SCHEMA || raw.app !== 'MANA Magic Visualiser') throw new Error('This is not a supported MANA Visualiser preset.');
  const settings = normalizeVisualSettings(raw.settings);
  visualSettingsCache = settings;
  await extensionContext.globalState.update(VISUAL_SETTINGS_KEY, settings);
  if (targetPanel && !targetPanel._disposed) await targetPanel.webview.postMessage({ type: 'visualSettings', settings });
  vscode.window.showInformationMessage('MANA Visualiser preset imported and saved.');
}

async function streamRecording(targetPanel, filePath, title, token, isCurrent) {
  const input = fs.createReadStream(filePath, { encoding: 'utf8' });
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  let lineNumber = 0;
  let headerSeen = false;
  let recordCount = 0;
  let chunk = [];
  let chunkBytes = 0;
  try {
    for await (const line of lines) {
      if (!isCurrent()) { input.destroy(); lines.close(); return; }
      lineNumber++;
      if (!line.trim()) continue;
      if (Buffer.byteLength(line, 'utf8') > MAX_RECORDING_LINE_BYTES) throw new Error(`Record ${lineNumber} exceeds the 1 MB line limit.`);
      assertJsonDepth(line);
      const event = JSON.parse(line);
      validateRecordShape(event, lineNumber);
      recordCount++;
      if (recordCount > MAX_RECORDS) throw new Error(`Recording contains too many records (limit: ${MAX_RECORDS.toLocaleString()}, including the recording header).`);
      if (!headerSeen) {
        if (event.type !== 'recording') throw new Error('This file is not a MANA Visualiser recording.');
        headerSeen = true;
        const started = await targetPanel.webview.postMessage({
          type: 'loadStart', title,
          reduceMotion: vscode.workspace.getConfiguration('manaVisualiser').get('reduceMotion', false),
        });
        if (!started || !isCurrent()) return;
        continue;
      }
      if (event.type === 'recording') continue;
      chunk.push(event);
      chunkBytes += Buffer.byteLength(line, 'utf8');
      // Bound transient host + webview transfer allocations. The viewer keeps
      // one parsed event timeline; the extension host never keeps a second copy.
      if (chunk.length >= 200 || chunkBytes >= 256 * 1024) {
        const sent = await targetPanel.webview.postMessage({ type: 'loadChunk', events: chunk });
        chunk = [];
        chunkBytes = 0;
        if (!sent || !isCurrent()) return;
      }
    }
    if (!headerSeen) throw new Error('The recording is empty or has no recording header.');
    if (chunk.length) {
      const sent = await targetPanel.webview.postMessage({ type: 'loadChunk', events: chunk });
      if (!sent || !isCurrent()) return;
    }
    await targetPanel.webview.postMessage({ type: 'loadDone', records: recordCount - 1 });
  } catch (error) {
    if (isCurrent()) await targetPanel.webview.postMessage({ type: 'loadError', message: error.message });
    output.appendLine(`Visualiser recording load failed: ${error.message}`);
  } finally {
    lines.close();
    input.destroy();
  }
}

async function openSourceLocation(sourcePath, requestedLine) {
  if (path.extname(sourcePath).toLowerCase() !== '.mana') throw new Error('source links may only open .mana files');
  const realTarget = await fs.promises.realpath(sourcePath);
  const sourceInfo = await fs.promises.stat(realTarget);
  if (!sourceInfo.isFile() || sourceInfo.size > MAX_SOURCE_BYTES) throw new Error('source file is missing, not regular, or too large');
  let allowed = false;
  for (const folder of (vscode.workspace.workspaceFolders || [])) {
    try {
      const realRoot = await fs.promises.realpath(folder.uri.fsPath);
      const relative = path.relative(realRoot, realTarget);
      if (relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative))) {
        allowed = true;
        break;
      }
    } catch (_) { /* a removed workspace folder cannot authorise navigation */ }
  }
  if (!allowed) throw new Error('source links must point to a .mana file inside the current workspace');
  const target = vscode.Uri.file(realTarget);
  const document = await vscode.workspace.openTextDocument(target);
  const editor = await vscode.window.showTextDocument(document, vscode.ViewColumn.One);
  const line = Math.max(0, Math.min(document.lineCount - 1, requestedLine - 1));
  editor.selection = new vscode.Selection(line, 0, line, 0);
  editor.revealRange(new vscode.Range(line, 0, line, 0), vscode.TextEditorRevealType.InCenter);
}

function getHtml(webview) {
  const nonce = crypto.randomBytes(24).toString('base64');
  const script = webview.asWebviewUri(vscode.Uri.file(path.join(__dirname, 'media', 'viewer.js')));
  const style = webview.asWebviewUri(vscode.Uri.file(path.join(__dirname, 'media', 'viewer.css')));
  return `<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${webview.cspSource} data:; style-src ${webview.cspSource}; script-src 'nonce-${nonce}' ${webview.cspSource}; connect-src 'none'; font-src ${webview.cspSource};">
<link rel="stylesheet" href="${style}"><title>MANA Magic Visualiser</title></head>
<body><header class="top">
  <div class="brand"><div class="brand-mark">M</div><div><div class="eyebrow">MANA · MAGIC SCENE</div><h1 id="title">Magic scene</h1></div><span class="result" id="result">RECORDING</span></div>
  <div class="top-actions"><button id="fitScene" title="Fit scene (0)">Fit scene</button><div class="zoom-control"><button id="zoomOut" aria-label="Zoom out" title="Zoom out (−)">−</button><span id="zoomLabel">100%</span><button id="zoomIn" aria-label="Zoom in" title="Zoom in (+)">+</button></div><button id="maximizeScene" title="Maximise editor group">⛶</button><button id="closeScene" class="close" title="Close visualiser" aria-label="Close visualiser">×</button></div>
</header>
<div class="layout">
  <section id="scene" class="view active">
    <div class="scene-wrap"><canvas id="sceneCanvas" aria-label="Magical scene. Drag to pan, scroll to zoom, click an object to inspect it. Use arrow keys to move through the replay."></canvas><div id="sceneNotice" class="scene-notice">Loading recording…</div>
      <div class="scene-toolbar" role="toolbar" aria-label="Scene display controls">
        <button id="toggleGrid" class="scene-toggle is-on" type="button" aria-pressed="true" title="Show or hide the world grid (G)">Grid</button>
        <button id="toggleLabels" class="scene-toggle is-on" type="button" aria-pressed="true" title="Show or hide object names (L)">Names</button>
        <button id="toggleEffects" class="scene-toggle is-on" type="button" aria-pressed="true" title="Show or hide spell trails and impacts (E)">Magic FX</button>
        <button id="toggleWeather" class="scene-toggle is-on" type="button" aria-pressed="true" title="Show or hide atmospheric visuals (W)">Weather</button>
        <button id="toggleSpellForms" class="scene-toggle is-on" type="button" aria-pressed="true" title="Show or hide spell silhouettes and casting glyphs (S)">Spell form</button>
        <button id="openVisualSettings" class="scene-toggle customize-button" type="button" aria-expanded="false" aria-controls="visualSettings" title="Customize the spell palette, trails, glyphs and scene layers">✦ Customize</button>
        <button id="focusSelected" type="button" title="Centre the camera on the selected object (F)">Focus target</button><button id="focusMode" type="button" aria-pressed="false" title="Expand the scene and focus the selected character">Character view</button>
      </div>
      <section id="visualSettings" class="visual-settings" role="dialog" aria-label="Visualiser appearance settings" aria-modal="false" hidden>
        <div class="visual-settings-head"><div><div class="eyebrow">SPELL VISUAL LAB</div><strong>Appearance & rendering</strong><span>Changes affect this viewer, not the MANA simulation. Styles are previewed live.</span></div><button id="closeVisualSettings" type="button" aria-label="Close appearance settings">×</button></div>
        <div class="visual-settings-scroll">
          <div class="settings-section"><div class="settings-section-title">Complete looks</div><p class="settings-note">Choose a starting recipe, then fine-tune any setting below. Recipes only change presentation, never the recorded MANA simulation.</p>
            <label for="lookPreset">Apply a complete look</label><select id="lookPreset" class="filter-select"><option value="">Choose a look…</option><option value="arcane-scholar">Arcane scholar</option><option value="infernal-court">Infernal court</option><option value="glacial-cathedral">Glacial cathedral</option><option value="abyssal-leviathan">Abyssal leviathan</option><option value="fae-wild">Fae wild</option><option value="prismatic-astral">Prismatic astral</option><option value="void-necromancy">Void necromancy</option><option value="stormglass">Stormglass</option><option value="antique-grimoire">Antique grimoire</option><option value="verdigris-alchemy">Verdigris alchemy</option><option value="mythic-relic">Mythic relic</option><option value="high-clarity">High clarity / reduced motion</option></select>
          </div>
          <div class="settings-section"><div class="settings-section-title">Art direction</div>
            <label for="palettePreset">Element palette</label><select id="palettePreset" class="filter-select"><option value="elemental">Elemental classic</option><option value="arcane-spectrum">Arcane spectrum</option><option value="ember-brass">Ember &amp; brass</option><option value="tidal-depths">Tidal depths</option><option value="glacial">Glacial crystal</option><option value="verdant">Verdant alchemy</option><option value="celestial">Celestial gold</option><option value="voidborne">Voidborne</option><option value="rose-quartz">Rose quartz</option><option value="monochrome">Monochrome</option><option value="high-contrast">High contrast</option><option value="retro-terminal">Retro terminal</option><option value="solar-flare">Solar flare</option><option value="bloodmoon">Blood moon</option><option value="aurora">Aurora</option><option value="volcanic">Volcanic forge</option><option value="desertglass">Desert glass</option><option value="deep-ocean">Deep ocean</option><option value="fae-wild">Fae wild</option><option value="neon-noir">Neon noir</option><option value="antique-grimoire">Antique grimoire</option><option value="arcane-frost">Arcane frost</option><option value="infernal-court">Infernal court</option><option value="bioluminescent">Bioluminescent</option><option value="stormglass">Stormglass</option><option value="spectral-ink">Spectral ink</option><option value="verdigris">Verdigris</option><option value="royal-amethyst">Royal amethyst</option><option value="sunken-kingdom">Sunken kingdom</option><option value="mythic-gold">Mythic gold</option><option value="night-bloom">Night bloom</option><option value="desert-mirage">Desert mirage</option></select>
            <label for="backgroundPreset">Scene backdrop</label><select id="backgroundPreset" class="filter-select"><option value="graphite">Graphite grid</option><option value="midnight">Midnight blue</option><option value="deep-space">Deep space</option><option value="vellum">Vellum / parchment</option><option value="abyss">Abyssal teal</option><option value="studio">Neutral studio</option><option value="high-contrast">High contrast</option><option value="forest">Enchanted forest</option><option value="crimson">Crimson void</option><option value="twilight">Twilight ink</option><option value="obsidian">Obsidian</option><option value="moonlit">Moonlit blue</option><option value="copper">Copper atelier</option><option value="nebula">Nebula</option><option value="slate">Slate studio</option><option value="moonstone">Moonstone</option><option value="volcanic-glass">Volcanic glass</option><option value="deep-forest">Deep forest</option></select>
            <label for="spellStyle">Spell body style</label><select id="spellStyle" class="filter-select"><option value="classic">Elemental anatomy</option><option value="crystalline">Crystalline facets</option><option value="rune-tech">Runic machinery</option><option value="painterly">Painterly streaks</option><option value="holographic">Holographic</option><option value="minimal">Minimal / clean</option><option value="astral">Astral orbitals</option><option value="comic-ink">Comic ink</option><option value="prismatic">Prismatic spectrum</option><option value="pixel-art">Pixel-art blocks</option><option value="spectral">Spectral fringes</option><option value="fractured-glass">Fractured glass</option><option value="ink-wash">Ink wash</option><option value="rune-circuit">Rune circuit</option><option value="solarized">Solarized rays</option></select>
            <label for="trailStyle">Projectile trail</label><select id="trailStyle" class="filter-select"><option value="tapered">Tapered energy</option><option value="ribbon">Ribbon stream</option><option value="segmented">Segmented pulses</option><option value="dashed">Dashed trajectory</option><option value="sparks">Spark marks</option><option value="lightning">Jagged lightning</option><option value="helix">Twin helix</option><option value="none">No trail</option><option value="comet">Comet tail</option><option value="afterimage">Layered afterimage</option><option value="mist">Mist wisps</option><option value="zigzag">Zigzag arc</option><option value="rune-chain">Rune chain</option></select>
            <label for="glyphStyle">Casting glyphs</label><select id="glyphStyle" class="filter-select"><option value="runic">Runic circles</option><option value="geometric">Geometric seals</option><option value="alchemical">Alchemical rings</option><option value="orbitals">Orbiting marks</option><option value="minimal">Minimal glyph</option><option value="star-mandala">Star mandala</option><option value="knotwork">Knotwork</option><option value="off">Off</option><option value="zodiac">Zodiac wheel</option><option value="fractal">Fractal seal</option><option value="lattice">Lattice geometry</option><option value="triune">Triune circles</option><option value="eldritch-grid">Spiral grid</option><option value="script">Runic script ring</option></select>
          </div>
          <div class="settings-section"><div class="settings-section-title">Colour overrides</div><p class="settings-note">Override any element or material family. For core, trail, glyph, impact, aura, accent and outline, use the independent channels below.</p>
            <div class="color-editor"><select id="customColorTarget" class="filter-select" aria-label="Element or material to recolour"></select><input id="customColorValue" type="color" value="#9feaff" aria-label="Custom colour"><button id="applyCustomColor" type="button">Apply</button></div>
            <div id="customColorSwatches" class="custom-color-swatches" aria-label="Current custom colour overrides"></div><button id="clearCustomColors" class="settings-secondary" type="button">Clear custom colours</button>
          </div>
          <div class="settings-section"><div class="settings-section-title">Magic colour channels</div><p class="settings-note">Set the colour of a visual layer independently of its element palette. Clear overrides to return that channel to automatic colours.</p>
            <div class="color-editor"><select id="fxColorTarget" class="filter-select" aria-label="Magic visual colour channel"></select><input id="fxColorValue" type="color" value="#9feaff" aria-label="Magic channel colour"><button id="applyFxColor" type="button">Apply</button></div>
            <div id="fxColorSwatches" class="custom-color-swatches" aria-label="Magic colour channels"></div><button id="clearFxColors" class="settings-secondary" type="button">Clear channel overrides</button>
          </div>
          <div class="settings-section"><div class="settings-section-title">Rendering controls</div>
            <div class="adaptive-graphics-card" role="status" aria-live="polite"><span class="adaptive-graphics-mark" aria-hidden="true">✦</span><div><strong>Adaptive graphics</strong><p>Best-looking spell forms by default. Detail, trail work and canvas resolution adjust automatically when the scene or display becomes expensive.</p><span id="adaptiveStatus" class="adaptive-status">Balancing detail to your scene…</span></div></div>
            <div class="setting-slider"><label for="effectIntensity">Magic intensity <output id="effectIntensityOut">100%</output></label><input id="effectIntensity" type="range" min="0" max="150" value="100" step="5"></div>
            <div class="setting-slider"><label for="glow">Glow strength <output id="glowOut">100%</output></label><input id="glow" type="range" min="0" max="180" value="100" step="5"></div>
            <div class="setting-slider"><label for="trailLength">Trail length <output id="trailLengthOut">24 steps</output></label><input id="trailLength" type="range" min="4" max="60" value="24" step="2"></div>
            <div class="setting-slider"><label for="particleDensity">Particle detail <output id="particleDensityOut">60%</output></label><input id="particleDensity" type="range" min="0" max="100" value="60" step="5"></div>
            <div class="setting-slider"><label for="spellSize">Spell size <output id="spellSizeOut">100%</output></label><input id="spellSize" type="range" min="50" max="180" value="100" step="5"></div>
            <div class="setting-slider"><label for="weatherIntensity">Atmosphere <output id="weatherIntensityOut">70%</output></label><input id="weatherIntensity" type="range" min="0" max="100" value="70" step="5"></div>
            <div class="setting-slider"><label for="gridOpacity">Grid strength <output id="gridOpacityOut">70%</output></label><input id="gridOpacity" type="range" min="0" max="100" value="70" step="5"></div>
          </div>
          <div class="settings-section"><div class="settings-section-title">Scene layers</div>
            <div class="settings-toggles"><label><input id="showParticles" type="checkbox" checked> Particles</label><label><input id="showImpacts" type="checkbox" checked> Impact bursts</label><label><input id="showVectors" type="checkbox"> Velocity vectors</label><label><input id="showActorAuras" type="checkbox" checked> Being auras</label><label><input id="showTrajectory" type="checkbox" checked> Trajectory paths</label><label><input id="showGlyphs" type="checkbox" checked> Casting glyphs</label><label><input id="showSpellNames" type="checkbox" checked> Spell labels</label><label><input id="highContrastEdges" type="checkbox"> Strong outlines</label><label><input id="reduceMotion" type="checkbox"> Reduce motion</label></div>
            <p class="settings-note">Colour never carries the only meaning: spells keep distinct silhouettes and labels. System reduced-motion preferences are always respected; this toggle can reduce motion further.</p>
          </div>
        </div>
        <div class="visual-settings-actions"><button id="resetVisualSettings" type="button" class="settings-secondary">Reset</button><button id="exportVisualSettings" type="button" class="settings-secondary">Export preset</button><button id="importVisualSettings" type="button" class="settings-secondary">Import preset</button><button id="saveVisualSettings" type="button" class="settings-primary">Save defaults</button></div>
        <div id="settingsStatus" class="settings-status" role="status" aria-live="polite">Custom changes are preview-only.</div>
      </section>
      <div class="scene-help">DRAG TO MOVE <span>·</span> SCROLL TO ZOOM <span>·</span> CLICK TO INSPECT <span>·</span> G GRID <span>·</span> F FOCUS</div></div>
    <div class="playback"><div class="play-row"><button id="prev" title="Previous event (←)">◀</button><button id="play" class="primary" title="Play or pause (Space)">▶ Play</button><button id="next" title="Next event (→)">▶|</button><button id="prevImpact" title="Jump to previous recorded impact">↶ Impact</button><button id="nextImpact" title="Jump to next recorded impact">Impact ↷</button><button id="replay" title="Replay from the beginning">↺ Replay</button><label class="speed">Speed <select id="speed" aria-label="Replay speed"><option value="0.25">Slow motion · 0.25×</option><option value="0.5">Slow · 0.5×</option><option value="1" selected>Normal · 1×</option><option value="2">Fast · 2×</option><option value="4">Very fast · 4×</option></select></label><span id="positionLabel">0 / 0</span></div><input id="timeline" type="range" min="0" max="0" value="0" aria-label="Replay timeline"><div class="timeline-labels"><span id="eventLabel">Ready</span><span id="timeLabel">0.0 s</span></div></div>
  </section>
  <aside class="inspector"><div class="inspector-head"><div><div class="eyebrow">SCENE INSPECTOR</div><div id="sceneStatus">Scene ready</div></div><div class="tab-bar"><button class="tab" data-tab="objects">Objects</button><button class="tab" data-tab="activity">Activity</button><button class="tab" data-tab="spell">Spell</button><button class="tab active" data-tab="details">Inspect</button><button class="tab" data-tab="world">World</button></div></div>
    <section id="objects" class="view"><h2>Scene objects <span id="objectCount" class="count-pill">0</span></h2><p class="muted">Search recorded entities, filter by role, then select one to focus it in the scene.</p><label class="field-label" for="objectSearch">Find an object</label><input id="objectSearch" class="search-field" type="search" maxlength="100" placeholder="Name, material, element…" autocomplete="off" spellcheck="false"><label class="field-label" for="objectFilter">Show</label><select id="objectFilter" class="filter-select"><option value="all">All active objects</option><option value="living">Living / beings</option><option value="summoned">Summoned / undead</option><option value="material">Physical materials</option><option value="construct">Mana constructs</option><option value="anchored">Anchored targets</option><option value="moving">Physics-enabled</option></select><div id="objectList" class="object-list" role="list" aria-label="World objects"></div><p id="objectsEmpty" class="muted list-note" hidden>No active objects match the current filter.</p><p id="objectLimitNote" class="muted list-note" hidden></p></section>
    <section id="activity" class="view"><h2>Event timeline</h2><p class="muted">Recorded spell results, manifestations, environment changes and physics contacts.</p><div class="filter-row"><input id="activitySearch" class="search-field" type="search" maxlength="100" placeholder="Search events…" aria-label="Search activity events" autocomplete="off"><select id="activityFilter" class="filter-select" aria-label="Filter activity events"><option value="all">All events</option><option value="magic">Magic</option><option value="contact">Impacts</option><option value="world">World / weather</option><option value="errors">Failures</option></select></div><ol id="activityList" class="activity-list"></ol><p id="activityEmpty" class="muted list-note" hidden>No events match this filter.</p></section>
    <section id="spell" class="view spell-view"><h2>Spell anatomy</h2><p class="muted">A spell-first replay trace, reconstructed from what the runtime actually recorded.</p><div id="spellHero" class="spell-hero"></div><h2 id="spellName">No spell in recording</h2><p id="spellSubtitle" class="muted">Waiting for a spell lifecycle record.</p><div id="spellFacts" class="facts"></div><div class="spell-trace-head"><span>Recorded construction sequence</span><span>Click a step to seek</span></div><ol id="spellTrace" class="spell-trace"></ol><p id="spellEmpty" class="muted list-note" hidden></p><div class="inspector-note">Silhouette and runes are procedural artwork. They do not alter the simulation or claim to recover source-level details absent from the recording.</div></section>
    <section id="details" class="view active"><h2 id="detailName">Nothing selected</h2><p id="detailSubtitle" class="muted">Select a character or object in the scene.</p><div id="detailFacts" class="facts"></div><div class="inspector-note">Inspect values recorded by the runtime. Selection and camera controls never change the simulated world.</div></section>
    <section id="world" class="view"><h2>World laws</h2><p class="muted">Recorded environmental rules. The renderer never decides physical outcomes.</p><div id="worldFacts" class="facts"></div><div id="worldSummary" class="world-summary">Waiting for world-state records.</div><div class="inspector-note">This is a 2D simulation with swept-circle contacts, translational friction and simplified thermal/material rules. Spin, rolling resistance, fluid simulation and full chemistry are not simulated.</div></section>
  </aside>
</div>
<footer><span id="footerStatus">Waiting for recording</span><span>2D world simulation · 3D geometry is calculation-only · no portal or plane view</span></footer>
<script nonce="${nonce}" src="${script}"></script></body></html>`;
}

function deactivate() { if (panel) panel.dispose(); }
module.exports = { activate, deactivate };
