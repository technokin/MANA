const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const MAX_SOURCE_BYTES = 2 * 1024 * 1024;
const MAX_OUTPUT_BYTES = 2 * 1024 * 1024;
const RUN_TIMEOUT_MS = 5 * 60 * 1000;

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

let output;
let activeProcess;

// Keep the editor extension deliberately small: run files, colour the language,
// and offer ordinary in-editor completions. The companion visualiser contributes
// the second editor-title action when installed.
const WORDS = [
  ['def', 'Define a reusable calculation function.'],
  ['spell', 'Declare a native MANA spell with an indented block; appraise it or cast it by name.'],
  ['spldef', 'Legacy spelling for a spell declaration; existing projects remain compatible.'],
  ['incant', 'Return a value from a definition and end it.'],
  ['tgset', 'Define or select a target profile. Targets are anchored by default.'],
  ['weave', 'Shape ambient mana into a mana construct.'],
  ['appraise', 'Run a non-committing spell trial and record its appraisal.'],
  ['cast', 'Execute a spell and commit its successful world changes.'],
  ['post', 'Legacy parenthesised form for appraising a spell.'],
  ['release', 'Legacy parenthesised form for casting a spell.'],
  ['load', 'Load a built-in or project library.'],
  ['skip', 'Intentionally empty statement for an empty block.'],
  ['span', 'MANA sequence function, similar in purpose to Python range().'],
  ['length', 'Length of a supported sequence or string.'],
  ['when', 'Register a world event handler.'],
  ['simul', 'Run validated statements in deterministic source order.'],
  ['create', 'Create an elemental manifestation. Use conjure() for ordinary matter.'],
  ['conjure', 'Manifest physical matter with mass, shape, state, temperature, velocity, and contact properties.'],
  ['summon', 'Bring a defined being through its recorded home-plane route.'],
  ['transmute', 'Change a material while preserving its world identity.'],
  ['transfigure', 'Change the form of a living being or matter created by conjure(); use shape() for geometry.'],
  ['world', 'World-engine laws: gravity, air density, restitution, drag, phase changes and wetting.'],
  ['periodic', 'Periodic-table data for all 118 chemical elements.'],
  ['shape', 'Change primitive geometry without turning an object into a living form.'],
  ['weather', 'Native climate statement: weather rain, radius=80 m, duration=30 s; area zones affect only objects inside the radius.'],
  ['advance_time', 'Advance the deterministic world simulation.'],
  ['combine', 'Apply the elemental interaction rules for two objects.'],
  ['mana', 'Built-in pure-mana effects and universal object control.'],
  ['geometry2d', 'Optional two-dimensional geometry helpers.'],
  ['vector3d', 'Optional three-dimensional vector calculations; world physics remains 2D.'],
];

const WORD_DETAILS = new Map(WORDS);
const BUILTINS = 'shape move heat cool accelerate decelerate velocity detect bind combine separate transform transmute transfigure conjure summon compress expand momentum kinetic_energy force pressure has_domain matter_to_mana mana_to_matter mana_to_energy energy_to_mana advance_time emit show active_objects rotate scale push pull reflect split anchor unanchor dispel last_collisions sqrt span length release post'.split(' ');
const KEYWORDS = 'if elif else while for in def spell spldef incant tgset weave post release appraise cast load skip when simul true false null'.split(' ');
const ELEMENTS = 'Fire Water Earth Air Ice Thunder Lightning Life Death Light Darkness Holy Shadow Void Metal Nature Mud Wood Order Entropy Spirit Soul Space Time Compound EarthLifeCompound ThermalRelease Mana'.split(' ');
const SHAPES = 'point line ray segment circle round arc ellipse ring polygon beam wave disc spiral fan wall field dome cage chain tendril cone corridor sphere ball projectile barrier shield'.split(' ');
const PLANES = ['Mortal Plane','Wild Realm','Fae Paradise','Atlantis','Elemental Planes','Heaven','Hell','Lineage Halls'];
const BEINGS = ['Griffin','Werewolf','Vampire','Chimera','Giant','Orc','Phoenix','Dragon','Merfolk','Nymph','Salamander','Sylph','Golem'];
const LIBRARIES = 'geometry2d vector3d planes mana weather world periodic materials metals anatomy physiology armory drafter summoning necromancy arcana planar_registry'.split(' ');
const CHEMICAL_ELEMENTS = [
  ['Hydrogen','H'],['Helium','He'],['Lithium','Li'],['Beryllium','Be'],['Boron','B'],['Carbon','C'],['Nitrogen','N'],['Oxygen','O'],['Fluorine','F'],['Neon','Ne'],['Sodium','Na'],['Magnesium','Mg'],['Aluminium','Al'],['Silicon','Si'],['Phosphorus','P'],['Sulfur','S'],['Chlorine','Cl'],['Argon','Ar'],['Potassium','K'],['Calcium','Ca'],['Scandium','Sc'],['Titanium','Ti'],['Vanadium','V'],['Chromium','Cr'],['Manganese','Mn'],['Iron','Fe'],['Cobalt','Co'],['Nickel','Ni'],['Copper','Cu'],['Zinc','Zn'],['Gallium','Ga'],['Germanium','Ge'],['Arsenic','As'],['Selenium','Se'],['Bromine','Br'],['Krypton','Kr'],['Rubidium','Rb'],['Strontium','Sr'],['Yttrium','Y'],['Zirconium','Zr'],['Niobium','Nb'],['Molybdenum','Mo'],['Technetium','Tc'],['Ruthenium','Ru'],['Rhodium','Rh'],['Palladium','Pd'],['Silver','Ag'],['Cadmium','Cd'],['Indium','In'],['Tin','Sn'],['Antimony','Sb'],['Tellurium','Te'],['Iodine','I'],['Xenon','Xe'],['Caesium','Cs'],['Barium','Ba'],['Lanthanum','La'],['Cerium','Ce'],['Praseodymium','Pr'],['Neodymium','Nd'],['Promethium','Pm'],['Samarium','Sm'],['Europium','Eu'],['Gadolinium','Gd'],['Terbium','Tb'],['Dysprosium','Dy'],['Holmium','Ho'],['Erbium','Er'],['Thulium','Tm'],['Ytterbium','Yb'],['Lutetium','Lu'],['Hafnium','Hf'],['Tantalum','Ta'],['Tungsten','W'],['Rhenium','Re'],['Osmium','Os'],['Iridium','Ir'],['Platinum','Pt'],['Gold','Au'],['Mercury','Hg'],['Thallium','Tl'],['Lead','Pb'],['Bismuth','Bi'],['Polonium','Po'],['Astatine','At'],['Radon','Rn'],['Francium','Fr'],['Radium','Ra'],['Actinium','Ac'],['Thorium','Th'],['Protactinium','Pa'],['Uranium','U'],['Neptunium','Np'],['Plutonium','Pu'],['Americium','Am'],['Curium','Cm'],['Berkelium','Bk'],['Californium','Cf'],['Einsteinium','Es'],['Fermium','Fm'],['Mendelevium','Md'],['Nobelium','No'],['Lawrencium','Lr'],['Rutherfordium','Rf'],['Dubnium','Db'],['Seaborgium','Sg'],['Bohrium','Bh'],['Hassium','Hs'],['Meitnerium','Mt'],['Darmstadtium','Ds'],['Roentgenium','Rg'],['Copernicium','Cn'],['Nihonium','Nh'],['Flerovium','Fl'],['Moscovium','Mc'],['Livermorium','Lv'],['Tennessine','Ts'],['Oganesson','Og']
];
const UNITS = ['kg','g','m','cm','mm','km','s','ms','K','C','m2','m^2','m3','m^3','m/s','m/s2','m/s^2','kg/m3','kg/m^3','N','J','Pa','W','kg*m/s','mana','mana/s'];
const NAMESPACE_CONSTANTS = {
  vector3d: ['C', 'PLANCK_TEMPERATURE_K'],
};

const NAMESPACES = {
  weather: 'set configure clear current areas wind precipitation temperature humidity fog clouds heat lightning'.split(' '),
  world: 'current laws configure reset set_gravity set_air_density set_restitution set_friction'.split(' '),
  periodic: 'lookup by_number all search density melting_point boiling_point symbol name count'.split(' '),
  mana: 'form burst emit toward away lift hold levitate stop release_control collect'.split(' '),
  planes: 'identify exists all_planes regions_of parent_of category_of planes_in same_category open_path close_path is_open paths_of neighbors find_route reachable send_energy open_channel close_channel energy_sent invoke revoke has_permission plane_of'.split(' '),
  summoning: 'bring tame send_back call find_being'.split(' '),
  necromancy: 'reanimate reanimate_many is_undead'.split(' '),
  geometry2d: 'point direction coordinates angle angle_between rotate rotate_vector scale distance project reflect_vector normalize perpendicular dot cross midpoint lerp polar to_radians to_degrees circle_area circle_circumference polygon_area closest_point_on_segment point_in_circle circles_intersect line_intersection segment_intersection point_in_polygon aim'.split(' '),
  vector3d: 'vector position velocity_vector acceleration_vector magnitude direction normalize rotate lerp midpoint dot cross distance angle_between project reflect scale components is_zero planar is_planar object_vector clamp_speed enforce_speed displacement kinetic_energy momentum force pressure'.split(' '),
  drafter: 'begin add_region add_being set_being create properties_of get_value beings_of'.split(' '),
  materials: 'lookup search all by_category define categories density melting_point boiling_point specific_heat thermal_conductivity'.split(' '),
  metals: 'lookup all search'.split(' '),
  anatomy: 'species define_species template structures systems structure body_parts has_structure structure_of count structures_of'.split(' '),
  physiology: 'define_form form systems organs get_value set_value condition function'.split(' '),
  armory: 'lookup search all define_item blueprint properties_of'.split(' '),
  arcana: 'lookup interactions combine'.split(' '),
  planar_registry: 'identify exists all_planes regions_of parent_of category_of'.split(' '),
};

const SNIPPETS = {
  def: ['Function definition', 'def ${1:function_name}(${2:value}):\n    incant ${3:value}'],
  spell: ['Native spell declaration', 'spell ${1:fire_bolt}():\n    bolt = conjure iron, mass=1 kg, shape=sphere\n    shape bolt into circle\n    incant bolt'],
  spldef: ['Legacy spell declaration', 'spldef ${1:fire_bolt}():\n    bolt = create Fire\n    shape(bolt, circle)\n    velocity(bolt, 25 m/s)\n    incant bolt'],
  'tgset:': ['Stationary target profile', '${1:training_target} = tgset:\n    hp = ${2:100}\n    max_hp = ${3:100}\n    defence = ${4:0}\n    collision_radius = ${5:0.4 m}'],
  'weave mana': ['Shape ambient mana', '${1:orb} = weave mana:\n    shape = ${2|sphere,disc,barrier,beam,ring,spiral|}\n    radius = ${3:0.5 m}\n    position = geometry2d.point(${4:3 m}, ${5:0 m})'],
  conjure: ['Conjure physical matter', '${1:ore} = conjure ${2:steel}, mass=${3:5 kg}, shape=${4|sphere,disc,wall,barrier,ring|}, anchored=${5:false}'],
  summon: ['Summon a defined being through a plane route', '${1:guardian} = summon "${2:Griffin}" from "${3:Wild Realm}"'],
  transmute: ['Change material composition', 'transmute ${1:object} into ${2:silver}'],
  transfigure: ['Change a living or conjured form', 'transfigure ${1:conjured_object} into ${2|humanoid,knight,bird,serpent,beast,golem|}'],
  shape: ['Change primitive geometry', 'shape ${1:object} into ${2|sphere,circle,round,polygon,wall,shield,beam|}'],
  transform: ['Change a material phase', 'transform ${1:object} into ${2|solid,liquid,gas,plasma,powder|}'],
  appraise: ['Preview and appraise a spell without committing changes', 'appraise ${1:spell_name}'],
  cast: ['Cast and commit a spell', 'cast ${1:spell_name}'],
  'world.configure': ['Configure physical world laws', 'world.configure(gravity=geometry2d.direction(0, -1) * 9.81 m/s2, air_density=1.225 kg/m3, restitution=0.2, friction=0.35, drag=true, thermal_exchange=true, phase_changes=true, wetting=true)'],
  'periodic.lookup': ['Look up an element', 'periodic.lookup("${1:Fe}")'],
  weather: ['Create local weather with native syntax', 'weather ${1|rain,storm,snow,blizzard,heatwave,sandstorm,fog,wind,ashfall,aurora,clear|}, intensity=${2:0.8}, wind_speed=${3:12 m/s}, wind_direction=${4|east,west,north,south,northeast,northwest,southeast,southwest|}, duration=${5:30 s}, radius=${6:80 m}'],
  'weather.configure': ['Configure global or area weather', 'weather.configure("${1:custom}", precipitation="${2:rain}", intensity=${3:0.7}, wind_speed=${4:8 m/s}, wind_direction="${5:north}", duration=${6:30 s}, radius=${7:80 m})'],
  'weather.wind': ['Set wind without a named spell', 'weather.wind(${1:12 m/s}, "${2:northwest}", intensity=${3:0.8})'],
  'weather.precipitation': ['Set the precipitation type', 'weather.precipitation("${1|rain,snow,dust,ash,hail,none|}", intensity=${2:0.7})'],
  'weather.temperature': ['Set ambient temperature', 'weather.temperature(${1:280 K})'],
};

function activate(context) {
  output = vscode.window.createOutputChannel('MANA');
  context.subscriptions.push(output);
  context.subscriptions.push(vscode.commands.registerCommand('mana.runFile', runFile));
  // Auto suggestions behave like normal editor completions; no separate palette button.
  const triggerCharacters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'.split('').concat('.');
  context.subscriptions.push(vscode.languages.registerCompletionItemProvider(
    { language: 'mana' }, { provideCompletionItems }, ...triggerCharacters,
  ));
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

async function runFile() {
  if (activeProcess) {
    output.appendLine('\nStopping the current MANA run…');
    activeProcess.kill();
    return;
  }
  if (!vscode.workspace.isTrusted) {
    vscode.window.showWarningMessage('MANA execution is disabled in an untrusted workspace. Trust the workspace only after reviewing its files.');
    return;
  }
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.document.languageId !== 'mana' || editor.document.uri.scheme !== 'file') {
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
  const root = findProjectRoot(source);
  if (!root) {
    vscode.window.showErrorMessage('Could not find mana.py in the project folder or its parents.');
    return;
  }
  const python = vscode.workspace.getConfiguration('mana').get('pythonPath', 'python');
  output.clear();
  output.show(true);
  output.appendLine(`MANA · Run\nFile: ${source}\n`);
  await new Promise(resolve => {
    let child;
    let settled = false;
    let outputBytes = 0;
    let outputTruncated = false;
    let timedOut = false;
    let timeout;
    const appendBounded = chunk => {
      if (settled) return;
      const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(String(chunk));
      const remaining = Math.max(0, MAX_OUTPUT_BYTES - outputBytes);
      const take = Math.min(remaining, buffer.length);
      if (take) output.append(buffer.subarray(0, take).toString('utf8'));
      outputBytes += take;
      if (take < buffer.length && !outputTruncated) {
        outputTruncated = true;
        output.appendLine(`\n[Output truncated at ${MAX_OUTPUT_BYTES.toLocaleString()} bytes; process stopped.]`);
        if (child && !child.killed) child.kill();
      }
    };
    const finish = code => {
      if (settled) return;
      settled = true;
      if (timeout) clearTimeout(timeout);
      if (activeProcess === child) activeProcess = undefined;
      if (timedOut) output.appendLine(`\nMANA stopped after the ${RUN_TIMEOUT_MS / 1000}-second execution timeout.`);
      if (code === 0 && !timedOut && !outputTruncated) vscode.window.setStatusBarMessage('MANA run completed', 2500);
      else output.appendLine(`\nMANA finished with exit code ${code == null ? 'unknown' : code}.`);
      resolve();
    };
    child = spawn(python, [path.join(root, 'mana.py'), source], {
      cwd: root, windowsHide: true, shell: false, env: restrictedPythonEnv(),
    });
    activeProcess = child;
    timeout = setTimeout(() => {
      timedOut = true;
      if (child && !child.killed) child.kill();
    }, RUN_TIMEOUT_MS);
    if (timeout.unref) timeout.unref();
    child.stdout.on('data', appendBounded);
    child.stderr.on('data', appendBounded);
    child.on('error', error => {
      output.appendLine(`Could not start MANA: ${error.message}`);
      vscode.window.showErrorMessage(`Could not start '${python}'. Check MANA: Python Path in Settings.`);
      finish(1);
    });
    child.on('close', code => finish(code));
  });
}

function item(label, kind, detail, insertText) {
  const completion = new vscode.CompletionItem(label, kind);
  completion.detail = detail || 'MANA';
  completion.sortText = label.toLowerCase();
  if (insertText !== undefined) completion.insertText = new vscode.SnippetString(insertText);
  return completion;
}

function provideCompletionItems(document, position) {
  const line = document.lineAt(position.line).text.slice(0, position.character);
  const member = line.match(/\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)?$/);
  if (member && NAMESPACES[member[1]]) {
    const namespace = member[1];
    const functions = NAMESPACES[namespace].map(name => {
      const key = `${namespace}.${name}`;
      const snippet = SNIPPETS[key];
      return item(name, vscode.CompletionItemKind.Function, snippet ? snippet[0] : `${namespace} function`, snippet ? snippet[1] : undefined);
    });
    const constants = (NAMESPACE_CONSTANTS[namespace] || []).map(name =>
      item(name, vscode.CompletionItemKind.Constant, `${namespace} constant`));
    return functions.concat(constants);
  }
  const summonSourceContext = line.match(/\bsummon\s+(?:"[^"]*"|'[^']*'|\([^)]*\)|[A-Za-z_]\w*)\s+from\s+["']?([A-Za-z ]*)$/);
  if (summonSourceContext) {
    const prefix = summonSourceContext[1].toLowerCase();
    return PLANES.filter(name => name.toLowerCase().startsWith(prefix)).map(name =>
      item(name, vscode.CompletionItemKind.Module, 'Known MANA plane'));
  }
  const summonBeingContext = line.match(/\bsummon\s+["']?([A-Za-z]*)$/);
  if (summonBeingContext) {
    const prefix = summonBeingContext[1].toLowerCase();
    return BEINGS.filter(name => name.toLowerCase().startsWith(prefix)).map(name =>
      item(name, vscode.CompletionItemKind.EnumMember, 'Known being catalogue entry'));
  }
  const trimmed = line.trimStart();
  if (/^load\s+[^\s]*$/.test(trimmed)) {
    return LIBRARIES.map(name => item(name, vscode.CompletionItemKind.Module, 'Built-in library'));
  }
  const transformContext = line.match(/\b(transfigure|shape|transform)\s+[A-Za-z_]\w*\s+into\s+([A-Za-z]*)$/);
  if (transformContext) {
    const kind = transformContext[1];
    const prefix = transformContext[2].toLowerCase();
    const choices = kind === 'transfigure' ? ['humanoid', 'knight', 'bird', 'serpent', 'beast', 'golem'] : kind === 'shape' ? SHAPES : ['solid', 'liquid', 'gas', 'plasma', 'powder'];
    return choices.filter(value => value.toLowerCase().startsWith(prefix)).map(value => item(value, vscode.CompletionItemKind.EnumMember, `${kind} destination`));
  }
  const materialContext = line.match(/\bconjure(?:\(\s*["']?|\s+["']?)([A-Za-z]*)$/) || line.match(/\btransmute(?:\(\s*[A-Za-z_]\w*\s*,\s*["']?|\s+[A-Za-z_]\w*\s+into\s+)([A-Za-z]*)$/);
  if (materialContext) {
    const prefix = (materialContext.length > 2 ? materialContext[2] : materialContext[1]).toLowerCase();
    const names = CHEMICAL_ELEMENTS.filter(([name, symbol]) => name.toLowerCase().startsWith(prefix) || symbol.toLowerCase().startsWith(prefix));
    const materials = ['metal','steel','stainless steel','bronze','brass','mithril','adamant','stone','granite','marble','wood','oak','pine','glass','crystal','sand','clay','bone','ice','water','coal','obsidian','ceramic','rubber','leather','cloth','paper','brick'];
    const suggestions = [];
    for (const [name, symbol] of names) {
      suggestions.push(item(name, vscode.CompletionItemKind.Value, `Periodic table · ${symbol}`));
      suggestions.push(item(symbol, vscode.CompletionItemKind.Value, `Chemical symbol for ${name}`));
    }
    for (const name of materials) if (name.toLowerCase().startsWith(prefix)) suggestions.push(item(name, vscode.CompletionItemKind.Value, 'MANA material catalogue'));
    return suggestions;
  }

  const spellContext = line.match(/\b(appraise|cast)\s+([A-Za-z_]\w*)?$/);
  if (spellContext) {
    const prefix = (spellContext[2] || '').toLowerCase();
    const source = document.getText();
    const names = new Set();
    const declaration = /^\s*(?:spell|spldef)\s+([A-Za-z_]\w*)\s*\(/gm;
    let match;
    while ((match = declaration.exec(source)) !== null) names.add(match[1]);
    return [...names].filter(name => name.toLowerCase().startsWith(prefix)).map(name =>
      item(name, vscode.CompletionItemKind.Reference, 'MANA spell declaration'));
  }

  const entries = [];
  for (const word of KEYWORDS) {
    const snippet = SNIPPETS[word];
    entries.push(item(word, snippet ? vscode.CompletionItemKind.Snippet : vscode.CompletionItemKind.Keyword,
      snippet ? snippet[0] : (WORD_DETAILS.get(word) || 'MANA keyword'), snippet ? snippet[1] : undefined));
  }
  for (const word of BUILTINS) {
    const snippet = SNIPPETS[word];
    entries.push(item(word, snippet ? vscode.CompletionItemKind.Snippet : vscode.CompletionItemKind.Function,
      snippet ? snippet[0] : 'MANA built-in', snippet ? snippet[1] : undefined));
  }
  for (const word of LIBRARIES) entries.push(item(word, vscode.CompletionItemKind.Module, 'Built-in library namespace'));
  for (const word of ELEMENTS) entries.push(item(word, vscode.CompletionItemKind.EnumMember, 'Element or material type'));
  for (const word of SHAPES) entries.push(item(word, vscode.CompletionItemKind.EnumMember, 'Shape'));
  for (const word of UNITS) entries.push(item(word, vscode.CompletionItemKind.Unit, 'Unit'));
  for (const [label, data] of Object.entries(SNIPPETS)) {
    if (label.includes('.')) continue;
    if (BUILTINS.includes(label) || KEYWORDS.includes(label)) continue;
    entries.push(item(label, vscode.CompletionItemKind.Snippet, data[0], data[1]));
  }
  return entries;
}

function deactivate() {
  if (activeProcess) activeProcess.kill();
  if (output) output.dispose();
}

module.exports = { activate, deactivate };
