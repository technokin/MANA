(() => {
  const vscode = acquireVsCodeApi();
  const canvas = document.getElementById('sceneCanvas');
  const ctx = canvas.getContext('2d');
  const timeline = document.getElementById('timeline');
  const playButton = document.getElementById('play');
  const speedSelect = document.getElementById('speed');
  const activityList = document.getElementById('activityList');
  const sceneNotice = document.getElementById('sceneNotice');
  const resultBadge = document.getElementById('result');
  const objectList = document.getElementById('objectList');
  const objectSearch = document.getElementById('objectSearch');
  const objectFilter = document.getElementById('objectFilter');
  const activitySearch = document.getElementById('activitySearch');
  const activityFilter = document.getElementById('activityFilter');
  // The palette is magical rather than diagnostic: elemental identity remains
  // recognizable while the aura brightens as actual engine-calculated energy rises.
  const palette = {
    fire:'#ff633f', water:'#52adf5', earth:'#a88a61', air:'#cbeaff',
    mana:'#9feaff', ice:'#77e9ff', thunder:'#fff05a', lightning:'#ffe04d',
    life:'#55d98a', death:'#a977d8', darkness:'#59466f', shadow:'#655084',
    light:'#fff3b2', holy:'#ffe8a0', void:'#8970d0', spirit:'#a4e9df', soul:'#ffb4df',
    space:'#62c5dc', time:'#d1c3ff', order:'#ebd5a9', entropy:'#d27a9c',
    metal:'#bcc9d8', nature:'#65c87b', wood:'#86bf71', mud:'#8f725b',
    rock:'#9ba1a6', stone:'#a4a6a1', bone:'#e0d5bc', flesh:'#c88f84',
    puremana:'#9feaff', compound:'#b8a9cc', thermalrelease:'#ffb977',
    being:'#9ee0c1', target:'#c6d4e2', blood:'#ad526a', leather:'#a77b55', glass:'#a9e1ec',
    crystal:'#9ce8f4', sand:'#d5b77c', acid:'#9cde54', fabric:'#b5a1cc', ceramic:'#dcc9b2',
    plastic:'#80b7b4', mineral:'#a7a9b6', magic:'#bba7f5', arcane:'#bba7f5', poison:'#a2cf54',
    steam:'#bbcbd1', smoke:'#9aa7b5', ash:'#8f8986', force:'#b6d6ff', psychic:'#eb9ed5'
  };
  const BASE_PALETTE = { ...palette };
  const PALETTE_THEMES = {
    'elemental': {},
    'arcane-spectrum': {fire:'#ff936e',water:'#55d9e9',earth:'#c7a7ff',air:'#e2d9ff',mana:'#c8a7ff',ice:'#99f2ff',thunder:'#f8f69e',lightning:'#fff18a',life:'#82ffd1',death:'#ff85c8',darkness:'#40335f',shadow:'#7d5bb6',light:'#fff0d0',holy:'#ffe6a5',void:'#9e7dff',spirit:'#8ef7f1',soul:'#ffb1e8',space:'#69dbff',time:'#dfc1ff',order:'#a8dcff',entropy:'#fb8ca9',metal:'#b9d6ea',nature:'#76e8a0',wood:'#9ce28b',mud:'#a58bca',rock:'#b5b8cc',stone:'#bec5d5',bone:'#eee1c9',flesh:'#e2a0bd',puremana:'#d2b4ff',compound:'#c8b7dd',thermalrelease:'#ffba94',being:'#a9f5d7'},
    'ember-brass': {fire:'#ff5b24',water:'#42b5c8',earth:'#a56b45',air:'#ffd08a',mana:'#ffc16b',ice:'#9eeeff',thunder:'#fff0a5',lightning:'#ffe47a',life:'#91d58d',death:'#b77c65',darkness:'#46302d',shadow:'#77443b',light:'#ffe4a3',holy:'#ffd77a',void:'#9163a2',spirit:'#e0c18f',soul:'#eda0a0',space:'#6bb4cb',time:'#d0a26e',order:'#dfc28e',entropy:'#d97958',metal:'#d6ae71',nature:'#8eac63',wood:'#af8051',mud:'#886548',rock:'#85786a',stone:'#a69a86',bone:'#dfc8a3',flesh:'#c98568',puremana:'#ffe0a2',compound:'#c0a181',thermalrelease:'#ff9b54',being:'#c9bd8a'},
    'tidal-depths': {fire:'#ff7c63',water:'#36cfe0',earth:'#668b9b',air:'#a5f3ee',mana:'#61d8ef',ice:'#a8fbff',thunder:'#c9ffff',lightning:'#c6f6ff',life:'#50d6ae',death:'#5f99c7',darkness:'#163b51',shadow:'#235a76',light:'#caffff',holy:'#9af7ea',void:'#527bbd',spirit:'#99f4e8',soul:'#9bc9e6',space:'#2bb9d6',time:'#a3d8f0',order:'#89e3d9',entropy:'#3c9db5',metal:'#8ab5c8',nature:'#43bfa3',wood:'#5da88c',mud:'#537f83',rock:'#7795a0',stone:'#94aab2',bone:'#d5e6dc',flesh:'#b5c6c9',puremana:'#91f3ff',compound:'#9abcc9',thermalrelease:'#77d4e0',being:'#72d6c3'},
    'glacial': {fire:'#ffa477',water:'#6dbfec',earth:'#9bb4c5',air:'#e4f7ff',mana:'#9cecff',ice:'#78e9ff',thunder:'#e8fdff',lightning:'#d4f7ff',life:'#90e9c5',death:'#b7b2e5',darkness:'#354b68',shadow:'#697ca9',light:'#f7ffff',holy:'#e8ffff',void:'#91a9e8',spirit:'#b4f2ee',soul:'#e2dcff',space:'#88c9f6',time:'#cedcff',order:'#b8e4f6',entropy:'#d7b1db',metal:'#b7d7e9',nature:'#8bcdbb',wood:'#9cbeaf',mud:'#8ba6b9',rock:'#a9b7c5',stone:'#bdc9d7',bone:'#f2f7ec',flesh:'#d4c9ce',puremana:'#b4f8ff',compound:'#c3d1e3',thermalrelease:'#b1dfff',being:'#b0f4e6'},
    'verdant': {fire:'#ef9d52',water:'#48c9b5',earth:'#967c50',air:'#d7eaa2',mana:'#b5e68f',ice:'#9bdfe1',thunder:'#ebef88',lightning:'#f3f58a',life:'#3fe38f',death:'#7d9f68',darkness:'#2d4833',shadow:'#486d4c',light:'#eeffb5',holy:'#f2f3ac',void:'#777ba1',spirit:'#9cf0b1',soul:'#c8e5a5',space:'#69cbb2',time:'#d0df97',order:'#c4dfa4',entropy:'#c5a477',metal:'#9eb5a1',nature:'#50ce77',wood:'#88b960',mud:'#8c8054',rock:'#929b7a',stone:'#b0b39a',bone:'#e5dfb9',flesh:'#cda58c',puremana:'#c8f3a6',compound:'#b3c5a0',thermalrelease:'#f5bc6b',being:'#82dba1'},
    'celestial': {fire:'#ffb55d',water:'#71d5ee',earth:'#d5b679',air:'#dce9ff',mana:'#f3d08a',ice:'#b4f1ff',thunder:'#fff2a1',lightning:'#fff5a0',life:'#9df0bb',death:'#b7a7e2',darkness:'#302d4f',shadow:'#5c537b',light:'#fff4c6',holy:'#ffe7a0',void:'#8c7ad4',spirit:'#c9f3e5',soul:'#f4c0e8',space:'#7cd5ff',time:'#e8d1ff',order:'#f0dba5',entropy:'#d7a0bd',metal:'#d7d2c4',nature:'#8bd9a2',wood:'#b9d49d',mud:'#ab9978',rock:'#b1b3b9',stone:'#cdccc5',bone:'#f1e7cc',flesh:'#dcada0',puremana:'#fff0bc',compound:'#d5c4e8',thermalrelease:'#ffd18b',being:'#cae9cc'},
    'voidborne': {fire:'#fa6b9f',water:'#44c7df',earth:'#786aa4',air:'#b3a9f7',mana:'#a17cff',ice:'#85eeff',thunder:'#ff77f5',lightning:'#e5a0ff',life:'#55edc4',death:'#9c6ada',darkness:'#21172e',shadow:'#4b286d',light:'#f5dcff',holy:'#d6b2ff',void:'#9f68ee',spirit:'#8dd6df',soul:'#ff85d4',space:'#597bdf',time:'#bf91ff',order:'#a5a0df',entropy:'#ef67b4',metal:'#9d9cbd',nature:'#59c4a1',wood:'#787aa1',mud:'#6a557b',rock:'#807d9b',stone:'#9b97af',bone:'#ddd2e7',flesh:'#b57eae',puremana:'#bc91ff',compound:'#aa8cce',thermalrelease:'#ff95b0',being:'#8ae0cf'},
    'rose-quartz': {fire:'#ff8299',water:'#80cce5',earth:'#c89ab4',air:'#f2d4ec',mana:'#e7a6e7',ice:'#b4f3f6',thunder:'#ffe5ba',lightning:'#ffd4e8',life:'#95dcbd',death:'#bf83b5',darkness:'#544051',shadow:'#8b6388',light:'#fff0f4',holy:'#ffdde8',void:'#b38bd4',spirit:'#a7ded8',soul:'#ffaddb',space:'#9cb9f1',time:'#e0b1e8',order:'#e4bfd2',entropy:'#e08ca8',metal:'#c3becd',nature:'#8fcba9',wood:'#c39ba1',mud:'#aa8e9a',rock:'#b5aab3',stone:'#cfc4ca',bone:'#f5e2e2',flesh:'#dfa1b2',puremana:'#f5c1ff',compound:'#d7bdd5',thermalrelease:'#ffb2b0',being:'#b4e6d2'},
    'monochrome': {fire:'#f4f4f4',water:'#ced6df',earth:'#a9a9a9',air:'#ffffff',mana:'#dedede',ice:'#e9f4ff',thunder:'#f2f2f2',lightning:'#ffffff',life:'#b7c9bc',death:'#888888',darkness:'#505050',shadow:'#777777',light:'#ffffff',holy:'#eeeeee',void:'#929292',spirit:'#dadada',soul:'#b5b5b5',space:'#bfcbd4',time:'#e0e0e0',order:'#d0d0d0',entropy:'#858585',metal:'#c9c9c9',nature:'#b9c9b9',wood:'#a7a7a7',mud:'#888888',rock:'#a0a0a0',stone:'#b0b0b0',bone:'#f0f0f0',flesh:'#c0c0c0',puremana:'#f4f4f4',compound:'#bcbcbc',thermalrelease:'#dedede',being:'#d2d2d2'},
    'high-contrast': {fire:'#ff4d00',water:'#00d9ff',earth:'#f3c400',air:'#ffffff',mana:'#ff00e5',ice:'#7fffff',thunder:'#ffff00',lightning:'#ffff00',life:'#00ff70',death:'#ff70e6',darkness:'#ffffff',shadow:'#d68cff',light:'#ffffff',holy:'#fff700',void:'#ff00d4',spirit:'#00ffff',soul:'#ff70e6',space:'#00d9ff',time:'#ffc9ff',order:'#fff700',entropy:'#ff60a0',metal:'#e0e0e0',nature:'#00ff70',wood:'#b6ff00',mud:'#e2c5a3',rock:'#d7d7d7',stone:'#ffffff',bone:'#ffffff',flesh:'#ffabb5',puremana:'#ff00e5',compound:'#e1d8ff',thermalrelease:'#ff4d00',being:'#ffffff'},
    'retro-terminal': {fire:'#ff754e',water:'#43f9c5',earth:'#a5c96a',air:'#9bffd8',mana:'#64ffaf',ice:'#a4fff1',thunder:'#dfff73',lightning:'#c4ff3d',life:'#55ff7c',death:'#bb92ff',darkness:'#17422f',shadow:'#297d53',light:'#ccffd8',holy:'#b7ffd3',void:'#8c9cff',spirit:'#a1ffcc',soul:'#ff9bde',space:'#4bffda',time:'#a6ffc0',order:'#b4ed8b',entropy:'#ed8ebd',metal:'#a7d8c1',nature:'#51ec84',wood:'#91c67d',mud:'#8c9f6a',rock:'#a1b2a8',stone:'#b5cbc0',bone:'#d9e8d8',flesh:'#c7a9a2',puremana:'#b0ffd4',compound:'#b5d3be',thermalrelease:'#ffb58b',being:'#8affbd'},
    'solar-flare': {fire:'#ff4a1c',water:'#47bde8',earth:'#c88b4a',air:'#ffe2ad',mana:'#fff08d',ice:'#9ceaff',thunder:'#fff52d',lightning:'#fff700',life:'#8ddb6b',death:'#cd72ad',darkness:'#3b2c44',shadow:'#815170',light:'#fffbd7',holy:'#fff1a8',void:'#bd78d9',spirit:'#c9edaf',soul:'#ff9cae',space:'#6dc8ff',time:'#ffd0a6',order:'#ffdf7a',entropy:'#ff7b65',metal:'#dcc19b',nature:'#a3d65f',wood:'#bf9857',mud:'#a27d50',rock:'#b6a38b',stone:'#d0c0a9',bone:'#f3e1ba',flesh:'#e2a08a',puremana:'#fff8af',compound:'#dbc1ab',thermalrelease:'#ff832f',being:'#b8e6a2'},
    'bloodmoon': {fire:'#ff4967',water:'#658bc9',earth:'#876276',air:'#e8c8d8',mana:'#ff5ca8',ice:'#bdcfff',thunder:'#ffc3d6',lightning:'#ff8bb4',life:'#b65c87',death:'#e9569a',darkness:'#1c111d',shadow:'#56213f',light:'#ffe5f1',holy:'#ffbdda',void:'#be4f9d',spirit:'#d9a4d0',soul:'#ff85c5',space:'#7351b5',time:'#dca7eb',order:'#d7a5bb',entropy:'#f24f80',metal:'#bca9c0',nature:'#ad5e83',wood:'#88526a',mud:'#6f4b5b',rock:'#817281',stone:'#a392a4',bone:'#ead6e1',flesh:'#cf8295',blood:'#d64d75',puremana:'#ffadd5',compound:'#c89abc',thermalrelease:'#ff6f6b',being:'#d09ab8'},
    'aurora': {fire:'#ff9877',water:'#48e4db',earth:'#8c91b9',air:'#d2fffa',mana:'#85f4e3',ice:'#abfff6',thunder:'#e6fff5',lightning:'#b8fff2',life:'#73f4b0',death:'#be9bdf',darkness:'#15233b',shadow:'#4d4e8d',light:'#edfff9',holy:'#c8fff4',void:'#7b86dc',spirit:'#a6ffe3',soul:'#f7bdf0',space:'#70d9ff',time:'#c8b9ff',order:'#b8f8de',entropy:'#c797e1',metal:'#9ecbd0',nature:'#63dca0',wood:'#77b6a0',mud:'#6f8c8c',rock:'#8ca3b3',stone:'#a7bbc2',bone:'#e3f2e7',flesh:'#c8b4cf',puremana:'#b5fff2',compound:'#b6d9d8',thermalrelease:'#b2ffcf',being:'#89edc9'},
    'volcanic': {fire:'#ff501b',water:'#488d9c',earth:'#81503b',air:'#f1b17e',mana:'#ff9866',ice:'#9ddde4',thunder:'#ffd47b',lightning:'#ffc04b',life:'#a5bd62',death:'#a85a4b',darkness:'#241b1b',shadow:'#5a312f',light:'#ffe1bc',holy:'#f5c883',void:'#8e5574',spirit:'#d1a16e',soul:'#df817c',space:'#6495a3',time:'#d59a7e',order:'#c9a27b',entropy:'#e05c42',metal:'#9f8d82',nature:'#8da55d',wood:'#8c6243',mud:'#684a3d',rock:'#84685b',stone:'#a28b7d',bone:'#e7d5b4',flesh:'#c78a69',puremana:'#ffb18a',compound:'#b99b87',thermalrelease:'#ff5c20',being:'#c5ae80'},
    'desertglass': {fire:'#df8152',water:'#6bb9c9',earth:'#bb9867',air:'#fff0c9',mana:'#f0d6a0',ice:'#b6e5e7',thunder:'#fff0a2',lightning:'#fff1b0',life:'#b7c77d',death:'#a78d9f',darkness:'#55493c',shadow:'#88715c',light:'#fff6df',holy:'#f8e5b3',void:'#9a89b6',spirit:'#c2d9c5',soul:'#eac7d6',space:'#78b4c2',time:'#dfc69d',order:'#d9c49c',entropy:'#ce9b84',metal:'#b6ac98',nature:'#a5bd79',wood:'#b4a06e',mud:'#9c815c',rock:'#b6a186',stone:'#c8b395',bone:'#f6e8c7',flesh:'#dbb09a',sand:'#e5c58b',glass:'#c5f2e9',crystal:'#d4f4eb',puremana:'#fff0c0',compound:'#d9ccb0',thermalrelease:'#f4a875',being:'#d9d9b1'},
    'deep-ocean': {fire:'#ff8164',water:'#18c5ed',earth:'#456d89',air:'#b9f3ff',mana:'#50deff',ice:'#a3f3ff',thunder:'#a7f7ff',lightning:'#e4fbff',life:'#40d8b5',death:'#4e83b2',darkness:'#061422',shadow:'#123b5b',light:'#d2fbff',holy:'#a5efff',void:'#4778bb',spirit:'#7de9e5',soul:'#87b6e8',space:'#2798d7',time:'#8db7eb',order:'#76d6db',entropy:'#247b9d',metal:'#7eafc8',nature:'#35b99b',wood:'#3d9188',mud:'#365d70',rock:'#507a91',stone:'#6a8da1',bone:'#cbe3e2',flesh:'#95bbc8',glass:'#79e2f0',crystal:'#9bf5ff',puremana:'#8deeff',compound:'#83b8c5',thermalrelease:'#71c7d8',being:'#70dbcd'},
    'fae-wild': {fire:'#ff9d65',water:'#71d9ea',earth:'#b0c17a',air:'#e5ffd0',mana:'#d3ef8c',ice:'#baf9f3',thunder:'#fff7a8',lightning:'#f3ff9b',life:'#58ed97',death:'#9f87c9',darkness:'#293344',shadow:'#5c4c8d',light:'#faffd2',holy:'#eaf9b0',void:'#8a79c1',spirit:'#acf7cc',soul:'#f1addc',space:'#83d9e1',time:'#d8d19c',order:'#c4e9ae',entropy:'#c995b3',metal:'#b8d0ac',nature:'#5de58a',wood:'#7bc66b',mud:'#87996a',rock:'#9fad92',stone:'#b7c7a4',bone:'#eef1cf',flesh:'#dcae9b',poison:'#a3e656',puremana:'#e0ff9e',compound:'#bfd9a7',thermalrelease:'#ffbd7f',being:'#96edaf'},
    'neon-noir': {fire:'#ff4f36',water:'#00d9ff',earth:'#d7ab37',air:'#d3e0ff',mana:'#ff3dd4',ice:'#5df8ff',thunder:'#ffff23',lightning:'#fff900',life:'#00f58c',death:'#ff31a2',darkness:'#c6c9d4',shadow:'#a35aff',light:'#ffffff',holy:'#fbff00',void:'#ff00e6',spirit:'#00ffe1',soul:'#ff75c9',space:'#00bfff',time:'#e6a7ff',order:'#eaff00',entropy:'#ff0088',metal:'#d2e4ff',nature:'#00f58c',wood:'#88ff19',mud:'#c58bff',rock:'#c6d1e8',stone:'#ffffff',bone:'#ffffff',flesh:'#ff98b7',glass:'#8effff',crystal:'#eaffff',blood:'#ff2b57',puremana:'#ff41ef',compound:'#e3d6ff',thermalrelease:'#ff5d30',being:'#f4ffff'},
    'arcane-frost': {fire:'#ff9a8f',water:'#66d9ff',earth:'#8a9eb8',air:'#f3fbff',mana:'#91bfff',ice:'#b6f6ff',thunder:'#d7f8ff',lightning:'#e7fcff',life:'#8ee9d2',death:'#9588d8',darkness:'#111c35',shadow:'#384f8d',light:'#ffffff',holy:'#d4f7ff',void:'#6d76dd',spirit:'#a4e9ff',soul:'#d8c8ff',space:'#68b8ff',time:'#b9d2ff',order:'#8bd3ee',entropy:'#a69bd8',metal:'#b4c8e8',nature:'#85d9bc',wood:'#709d9b',mud:'#607991',rock:'#899cb6',stone:'#b0c4db',bone:'#e6f3f7',flesh:'#c1b7d0',puremana:'#bcf4ff',compound:'#b1c2e4',thermalrelease:'#a7dfff',being:'#9cebdc'},
    'infernal-court': {fire:'#ff391f',water:'#5a91b8',earth:'#a55b38',air:'#ffd2ad',mana:'#ff784b',ice:'#9edce8',thunder:'#ffcb4c',lightning:'#fff08a',life:'#9fae67',death:'#d45b69',darkness:'#160e18',shadow:'#5a2037',light:'#ffe1bc',holy:'#ffc87f',void:'#853c83',spirit:'#d28b83',soul:'#e36b9d',space:'#5f7da8',time:'#ce9b83',order:'#bd8669',entropy:'#ed5545',metal:'#a88d8d',nature:'#8a9c53',wood:'#765044',mud:'#5d3c34',rock:'#8a6558',stone:'#b08c7b',bone:'#ead3be',flesh:'#d78a78',blood:'#c3273e',puremana:'#ffb08b',compound:'#b78a85',thermalrelease:'#ff592e',being:'#d29c7d'},
    'bioluminescent': {fire:'#ff8c79',water:'#2ee7df',earth:'#587b74',air:'#c2fff1',mana:'#60ffe8',ice:'#b7fff4',thunder:'#d4fff6',lightning:'#f1fff5',life:'#39ff9e',death:'#a98bff',darkness:'#071b25',shadow:'#1b5669',light:'#edfffb',holy:'#a7fff0',void:'#8c73d8',spirit:'#a1ffe0',soul:'#ff9bde',space:'#26c7df',time:'#ace7dc',order:'#9ae9d2',entropy:'#a778bd',metal:'#81c5c0',nature:'#34e7a0',wood:'#4eaa8d',mud:'#456f67',rock:'#618f8b',stone:'#8eb8b2',bone:'#d8f5e9',flesh:'#c49fae',glass:'#65fff1',crystal:'#a3fff7',puremana:'#aaffef',compound:'#95d8ce',thermalrelease:'#8efbd8',being:'#5df3bd'},
    'stormglass': {fire:'#ff8e62',water:'#49cfff',earth:'#7b8da2',air:'#e0f5ff',mana:'#7de8ff',ice:'#c7f6ff',thunder:'#e2fdff',lightning:'#ffffff',life:'#7bd9c3',death:'#9a8bd1',darkness:'#101b31',shadow:'#415879',light:'#f7fdff',holy:'#d0f4ff',void:'#758bd6',spirit:'#b5f5f0',soul:'#d2bcff',space:'#4c9deb',time:'#b5c8f1',order:'#a1d7e7',entropy:'#9b9aca',metal:'#a5bdd7',nature:'#75c5ad',wood:'#6d9b90',mud:'#657c8a',rock:'#839eb4',stone:'#b4c9d9',bone:'#d9e9ee',flesh:'#c8b2c1',glass:'#9bebff',crystal:'#c7f8ff',puremana:'#c3f5ff',compound:'#a7c4d8',thermalrelease:'#82d9f3',being:'#a7e8dc'},
    'spectral-ink': {fire:'#ff7c94',water:'#72cfff',earth:'#8f8ba9',air:'#eee6ff',mana:'#c8b6ff',ice:'#b9e9ff',thunder:'#f9e8ff',lightning:'#fff6ff',life:'#9fe3c3',death:'#a37cca',darkness:'#191626',shadow:'#59406f',light:'#fffaff',holy:'#e4d9ff',void:'#a879e2',spirit:'#bed7ff',soul:'#f5a9d6',space:'#8c9deb',time:'#d6b7f0',order:'#c4b8df',entropy:'#cf89c4',metal:'#b2b1cd',nature:'#9bcab2',wood:'#9f89ad',mud:'#81718a',rock:'#9995aa',stone:'#c5bed0',bone:'#eee5f3',flesh:'#d0a8c2',blood:'#a55a86',puremana:'#e4d7ff',compound:'#c9b5db',thermalrelease:'#edb3d0',being:'#c2d9d8'},
    'verdigris': {fire:'#ff845b',water:'#4bc8b7',earth:'#8d8870',air:'#d2e7d9',mana:'#9de0c4',ice:'#9de8e2',thunder:'#d4edb0',lightning:'#f1f5ba',life:'#6fcb82',death:'#7b8b83',darkness:'#172724',shadow:'#375d54',light:'#edf9e8',holy:'#d4e8ba',void:'#718d8c',spirit:'#a4d9bd',soul:'#caafb5',space:'#5ab7a8',time:'#b6c8a1',order:'#9db99e',entropy:'#9d8d82',metal:'#99b5a6',nature:'#67b87c',wood:'#779b78',mud:'#758575',rock:'#91a39a',stone:'#b0beb3',bone:'#e2ead9',flesh:'#c4a69a',puremana:'#bfead6',compound:'#b3c7b7',thermalrelease:'#e0b386',being:'#a1d5b4'},
    'royal-amethyst': {fire:'#ff8e78',water:'#6bbae5',earth:'#927caf',air:'#e2dcff',mana:'#be9bff',ice:'#c6efff',thunder:'#f4ddff',lightning:'#ffe7ff',life:'#78dbbd',death:'#c18bdb',darkness:'#1d1333',shadow:'#4a286f',light:'#fff4ff',holy:'#f1d8ff',void:'#9d65ee',spirit:'#bca9f7',soul:'#f39bdd',space:'#6e7fe2',time:'#dac2ff',order:'#c5b0ec',entropy:'#c178bd',metal:'#b8abd0',nature:'#84c6a8',wood:'#8a78a8',mud:'#79658d',rock:'#8e86a1',stone:'#b1a7c3',bone:'#eee2f4',flesh:'#cea2c7',puremana:'#e0c6ff',compound:'#c3add9',thermalrelease:'#e9a3bf',being:'#b3d9d7'},
    'sunken-kingdom': {fire:'#f18f73',water:'#35c6dd',earth:'#596f87',air:'#c2e7ef',mana:'#69d5e4',ice:'#a6f0f4',thunder:'#c8f8ff',lightning:'#f2ffff',life:'#63d0ad',death:'#6178ad',darkness:'#071522',shadow:'#173d55',light:'#e0f8ff',holy:'#b9eff5',void:'#526caa',spirit:'#8bdedc',soul:'#8faed8',space:'#328fb9',time:'#8cbce0',order:'#6ab8c2',entropy:'#396f8c',metal:'#7ea7b8',nature:'#4bb8a0',wood:'#3f7f7c',mud:'#395b69',rock:'#5e7d8d',stone:'#84a4ae',bone:'#cee1e4',flesh:'#98bac5',glass:'#6fe3ef',crystal:'#a9f6ff',puremana:'#91eefa',compound:'#83afc0',thermalrelease:'#6ec5d3',being:'#6ed4c9'},
    'mythic-gold': {fire:'#ff7c38',water:'#66c4da',earth:'#ad8550',air:'#fae8c4',mana:'#ffd97e',ice:'#b2e9f0',thunder:'#fff2a6',lightning:'#fff9be',life:'#a8d68d',death:'#a884b9',darkness:'#28202d',shadow:'#64506b',light:'#fff5d6',holy:'#ffe3a1',void:'#8973b6',spirit:'#d4d6b1',soul:'#e4b7d0',space:'#7bbbc7',time:'#e4c991',order:'#ddc181',entropy:'#cb8c78',metal:'#cdb78e',nature:'#a1bc78',wood:'#b79a63',mud:'#8a7158',rock:'#a3937b',stone:'#c6b59c',bone:'#f4e6c6',flesh:'#d2a38e',puremana:'#ffe8a3',compound:'#d8c8a9',thermalrelease:'#ffac63',being:'#c9d3a2'},
    'night-bloom': {fire:'#ff6d91',water:'#52c7f3',earth:'#7f7796',air:'#c4d6ff',mana:'#a68aff',ice:'#9bf5ff',thunder:'#e5cfff',lightning:'#fff1ff',life:'#4de7b5',death:'#cb66df',darkness:'#100d25',shadow:'#3a205a',light:'#f7efff',holy:'#c5baff',void:'#9554d1',spirit:'#88eee6',soul:'#ff8fda',space:'#3d7fce',time:'#b9a5ff',order:'#8dcfe0',entropy:'#d56eb9',metal:'#8a96bc',nature:'#51cfa8',wood:'#617da1',mud:'#5c5678',rock:'#7880a0',stone:'#a0a8c4',bone:'#d8def0',flesh:'#b88ebc',puremana:'#c2adff',compound:'#a6a2d7',thermalrelease:'#fa8fa5',being:'#83e3d0'},
    'desert-mirage': {fire:'#e98350',water:'#64c2c8',earth:'#bd9866',air:'#fff0d0',mana:'#edce98',ice:'#b7e8e3',thunder:'#ffe4a0',lightning:'#fff0b5',life:'#a8c27a',death:'#a68ca1',darkness:'#493a32',shadow:'#806854',light:'#fff9e8',holy:'#f7e4b4',void:'#9480ae',spirit:'#c2d8bf',soul:'#e4c4cc',space:'#83b7bd',time:'#e1c59e',order:'#d8c39d',entropy:'#c38e7f',metal:'#bdb09a',nature:'#9fb67b',wood:'#b7a273',mud:'#9e815b',rock:'#b9a184',stone:'#cdb89c',bone:'#f7ebd1',flesh:'#d8ad99',sand:'#f0d09a',glass:'#c5f1e2',crystal:'#d5f5ea',puremana:'#fff0bf',compound:'#dacdb6',thermalrelease:'#f2a777',being:'#d9d9b4'} ,
    'antique-grimoire': {fire:'#a74b2c',water:'#427f8a',earth:'#76644b',air:'#d8c8a3',mana:'#b58b5e',ice:'#96b6bd',thunder:'#e3c77b',lightning:'#e9d58a',life:'#6e8760',death:'#725575',darkness:'#29231d',shadow:'#524035',light:'#edddae',holy:'#e2cb8e',void:'#79618d',spirit:'#b3ad82',soul:'#b7869e',space:'#667e89',time:'#b9a17b',order:'#b59c73',entropy:'#a56757',metal:'#898a7c',nature:'#77865b',wood:'#89714e',mud:'#75634c',rock:'#817b6c',stone:'#b1a58b',bone:'#d8c9a5',flesh:'#b98976',blood:'#8b4140',puremana:'#dbc397',compound:'#b7a787',thermalrelease:'#c8794e',being:'#b2a77d'}
  };
  const VISUAL_DEFAULTS = Object.freeze({
    schema:1, palettePreset:'elemental', backgroundPreset:'graphite', spellStyle:'classic', trailStyle:'tapered', glyphStyle:'runic',
    effectIntensity:1, glow:1, trailLength:24, particleDensity:60, spellSize:1, weatherIntensity:70, gridOpacity:70,
    showParticles:true, showImpacts:true, showVectors:false, showActorAuras:true, showTrajectory:true, showGlyphs:true, showSpellNames:true, highContrastEdges:false, reduceMotion:false, customColors:{}, fxColors:{}
  });
  const FX_COLOR_CHANNELS = ['core','trail','glyph','impact','aura','accent','outline'];
  let visualSettings = { ...VISUAL_DEFAULTS, customColors:{}, fxColors:{} };
  let settingsSaveTimer = null;
  const SETTING_ENUMS = {
    palettePreset:Object.keys(PALETTE_THEMES), backgroundPreset:['graphite','midnight','deep-space','vellum','abyss','studio','high-contrast','forest','crimson','twilight','obsidian','moonlit','copper','nebula','slate','moonstone','volcanic-glass','deep-forest'],
    spellStyle:['classic','crystalline','rune-tech','painterly','holographic','minimal','astral','comic-ink','prismatic','pixel-art','spectral','fractured-glass','ink-wash','rune-circuit','solarized'],
    trailStyle:['tapered','ribbon','segmented','dashed','sparks','lightning','helix','none','comet','afterimage','mist','zigzag','rune-chain'], glyphStyle:['runic','geometric','alchemical','orbitals','minimal','star-mandala','knotwork','off','zodiac','fractal','lattice','triune','eldritch-grid','script'],
  };
  const SETTING_RANGES = { effectIntensity:[0,1.5],glow:[0,1.8],trailLength:[4,60],particleDensity:[0,100],spellSize:[.5,1.8],weatherIntensity:[0,100],gridOpacity:[0,100] };
  const SETTING_BOOLS = ['showParticles','showImpacts','showVectors','showActorAuras','showTrajectory','showGlyphs','showSpellNames','highContrastEdges','reduceMotion'];
  function normalizeVisualSettings(value) {
    const incoming = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
    const result = { ...VISUAL_DEFAULTS, ...incoming, schema:1, customColors:{}, fxColors:{} };
    // Graphics quality is adaptive now; silently ignore obsolete tier settings in older presets.
    delete result.quality;
    for (const [key, choices] of Object.entries(SETTING_ENUMS)) if (!choices.includes(result[key])) result[key] = VISUAL_DEFAULTS[key];
    for (const [key, range] of Object.entries(SETTING_RANGES)) { const n=Number(result[key]); result[key]=Math.max(range[0],Math.min(range[1],Number.isFinite(n)?n:VISUAL_DEFAULTS[key])); }
    for (const key of SETTING_BOOLS) result[key]=typeof incoming[key]==='boolean'?incoming[key]:VISUAL_DEFAULTS[key];
    if (incoming.customColors && typeof incoming.customColors === 'object' && !Array.isArray(incoming.customColors)) {
      for (const [key, color] of Object.entries(incoming.customColors).slice(0,64)) if (Object.prototype.hasOwnProperty.call(BASE_PALETTE,key) && typeof color==='string' && /^#[0-9a-fA-F]{6}$/.test(color)) result.customColors[key]=color.toLowerCase();
    }
    if (incoming.fxColors && typeof incoming.fxColors === 'object' && !Array.isArray(incoming.fxColors)) {
      for (const channel of FX_COLOR_CHANNELS) { const color=incoming.fxColors[channel]; if(typeof color==='string' && /^#[0-9a-fA-F]{6}$/.test(color)) result.fxColors[channel]=color.toLowerCase(); }
    }
    return result;
  }
  function applyPaletteSelection() {
    Object.assign(palette, BASE_PALETTE, PALETTE_THEMES[visualSettings.palettePreset] || {});
    Object.assign(palette, visualSettings.customColors || {});
  }
  // Independent colour channels sit above element/material identity. A palette
  // still sets the default; a channel override is an explicit art-direction choice.
  function fxColor(channel, fallback) { return visualSettings.fxColors && visualSettings.fxColors[channel] || fallback; }
  const VISUAL_LOOKS = {
    'arcane-scholar': {palettePreset:'arcane-spectrum',backgroundPreset:'deep-space',spellStyle:'rune-circuit',trailStyle:'helix',glyphStyle:'alchemical',glow:1.15,particleDensity:70,showGlyphs:true},
    'infernal-court': {palettePreset:'infernal-court',backgroundPreset:'crimson',spellStyle:'painterly',trailStyle:'comet',glyphStyle:'geometric',effectIntensity:1.2,glow:1.25},
    'glacial-cathedral': {palettePreset:'arcane-frost',backgroundPreset:'moonlit',spellStyle:'fractured-glass',trailStyle:'afterimage',glyphStyle:'star-mandala',glow:1.1,particleDensity:55},
    'abyssal-leviathan': {palettePreset:'sunken-kingdom',backgroundPreset:'abyss',spellStyle:'holographic',trailStyle:'ribbon',glyphStyle:'orbitals',glow:1.0,weatherIntensity:45},
    'fae-wild': {palettePreset:'fae-wild',backgroundPreset:'deep-forest',spellStyle:'ink-wash',trailStyle:'mist',glyphStyle:'knotwork',particleDensity:75,weatherIntensity:82},
    'prismatic-astral': {palettePreset:'spectral-ink',backgroundPreset:'nebula',spellStyle:'spectral',trailStyle:'helix',glyphStyle:'fractal',glow:1.45,particleDensity:88},
    'void-necromancy': {palettePreset:'night-bloom',backgroundPreset:'obsidian',spellStyle:'astral',trailStyle:'afterimage',glyphStyle:'eldritch-grid',glow:1.2,particleDensity:62},
    'stormglass': {palettePreset:'stormglass',backgroundPreset:'moonstone',spellStyle:'fractured-glass',trailStyle:'zigzag',glyphStyle:'lattice',glow:1.0,particleDensity:68},
    'antique-grimoire': {palettePreset:'antique-grimoire',backgroundPreset:'vellum',spellStyle:'ink-wash',trailStyle:'rune-chain',glyphStyle:'knotwork',glow:.7,particleDensity:28,gridOpacity:40},
    'verdigris-alchemy': {palettePreset:'verdigris',backgroundPreset:'deep-forest',spellStyle:'rune-circuit',trailStyle:'segmented',glyphStyle:'triune',glow:.9,particleDensity:48},
    'mythic-relic': {palettePreset:'mythic-gold',backgroundPreset:'copper',spellStyle:'solarized',trailStyle:'comet',glyphStyle:'zodiac',glow:1.2,particleDensity:60},
    'high-clarity': {palettePreset:'high-contrast',backgroundPreset:'high-contrast',spellStyle:'minimal',trailStyle:'dashed',glyphStyle:'geometric',highContrastEdges:true,reduceMotion:true,glow:.3,particleDensity:20}
  };
  // Keep the timeline compact: JSON strings retain the complete recording while
  // avoiding thousands of long-lived nested JS objects. Parse only records being
  // replayed; eventTimes keeps per-frame weather and labels fast.
  let events = [];
  let eventTimes = [];
  let index = 0;
  let playing = false;
  let raf = 0;
  let idleRaf = 0;
  let idleLastFrame = 0;
  let lastFrame = 0;
  let lastLoopFrameStamp = 0;
  let frameIntervalForRender = 16.7;
  let frameTargetMs = 16.7;
  let entities = new Map();
  let visibleEntityCache = null;
  // Preview entities are a separate, dashed overlay. A post() snapshot restores
  // the real world but must not make the hypothetical spell vanish immediately.
  let previewEntities = new Map();
  let selectedId = null;
  let previewIds = new Set();
  let contacts = [];
  let effects = [];
  let activities = [];
  let currentRecord = null;
  let displayTitle = 'Magic scene';
  let reduceMotion = false;
  let systemReduceMotion = typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let showGrid = true;
  let showLabels = true;
  let showEffects = true;
  let showWeather = true;
  let showSpellForms = true;
  let spellTrace = [];
  let motionTracks = [];
  let motionTrackById = new Map();
  // Motion-track geometry is immutable for a loaded recording. Cache its world
  // bounds once instead of walking every sampled point for every camera transform.
  let cachedMotionBounds = null;
  let motionBoundsBuilt = false;
  let motionBoundsBuildCount = 0;
  let castEvents = [];
  let lastSpellPanelKey = '';
  let lastRenderMetrics = { movingTracks: 0, visibleProjectileHeads: 0, detailedSpellBodies: 0, culledProjectileTracks: 0 };
  let renderPositions = new Map();
  const sampledMotion = new Map();
  let weatherState = null;
  let worldSettings = {
    gravity_m_s2:[0,0], air_density_kg_m3:1.225, default_restitution:0.2,
    friction_coefficient:0.35, drag_enabled:true, thermal_exchange_enabled:true,
    phase_changes_enabled:true, wetting_enabled:true,
  };
  let camera = { x: 0, y: 0, zoom: 1, baseScale: 60, initialized: false };
  let pointerDrag = null;
  let suppressNextClick = false;
  // Keep the zoom floor low enough to fit very large valid world recordings.
  // Camera zoom itself is bounded relative to the fitted base scale, so this
  // floor does not expose an unbounded user zoom range on ordinary scenes.
  const MIN_SCENE_SCALE = 1e-12;
  const MAX_SCENE_SCALE = 700;
  // A single adaptive graphics policy replaces user-facing quality tiers.
  // Bound the backing store to roughly 16 MB of RGBA pixels on any display.
  const MAX_CANVAS_PIXELS = 4_000_000;
  // Imported JSONL is untrusted; coordinates beyond this range cannot be
  // represented usefully at this canvas scale and are omitted from world drawing.
  const MAX_SCENE_COORDINATE = 1e12;
  const MAX_DETAIL_BODIES = 128;
  const MIN_DETAIL_BODIES = 32;
  const MAX_DETAIL_TRAILS = 96;
  const MIN_DETAIL_TRAILS = 24;
  const MAX_EVENT_CACHE_ENTRIES = 512;
  const MAX_EVENT_CACHE_CHARS = 1_500_000;
  const MAX_CACHEABLE_EVENT_CHARS = 32_000;
  const adaptiveGraphics = {
    bodyBudget: 96, trailBudget: 72, particleScale: 1, frameMs: 16.7, frameIntervalMs: 16.7,
    overloadedFrames: 0, fastFrames: 0, pixelCount: 0, renderCount: 0,
  };
  const eventObjectCache = new Map();
  let eventObjectCacheChars = 0;

  function text(value, max = 220) { return String(value == null ? '' : value).slice(0, max); }
  function safeNumber(value, fallback = 0) { const n = Number(value); return Number.isFinite(n) ? n : fallback; }
  function worldPosition(value) {
    if (!Array.isArray(value) || value.length < 2) return null;
    const x=value[0], y=value[1];
    return typeof x==='number' && typeof y==='number' && Number.isFinite(x) && Number.isFinite(y) &&
      Math.abs(x)<=MAX_SCENE_COORDINATE && Math.abs(y)<=MAX_SCENE_COORDINATE ? [x,y] : null;
  }
  function hexChannels(value) { const hex = String(value || '#ffffff').replace('#',''); return [0,2,4].map(i => parseInt(hex.slice(i,i+2),16) || 0); }
  function blendHex(a, b, amount) {
    const aa=hexChannels(a),bb=hexChannels(b),t=Math.max(0,Math.min(1,amount));
    return '#'+aa.map((v,i)=>Math.round(v+(bb[i]-v)*t).toString(16).padStart(2,'0')).join('');
  }
  function entityColor(entity) {
    const element = text(entity.element || '').toLowerCase();
    const material = text(entity.material || '').toLowerCase();
    const name = text(entity.name || '').toLowerCase();
    const kind = text(entity.kind || '').toLowerCase();
    const generic = new Set(['target', 'compound', 'being', 'material']);
    const candidates = [
      ...(generic.has(element) ? [] : [element]),
      ...(generic.has(material) ? [] : [material]),
      name,
      element,
      material,
      kind
    ];
    const key = candidates.find(candidate => Object.prototype.hasOwnProperty.call(palette, candidate));
    let base = (key && palette[key]) || (kind === 'being' ? palette.being : '');
    // The expanded materials catalogue contains many custom names. Give those
    // materials a family-level visual identity instead of colouring all unknowns alike.
    if (!base) {
      if (/bone|ivory|antler|shell|chitin/.test(material)) base = palette.bone;
      else if (/flesh|meat|skin|blood|muscle|leather|hide|wool|silk|cotton|linen|cloth|textile/.test(material)) base = /blood/.test(material) ? palette.blood : /leather|hide/.test(material) ? palette.leather : /cloth|textile|wool|silk|cotton|linen/.test(material) ? palette.fabric : palette.flesh;
      else if (/wood|oak|pine|bark|timber|paper|bamboo/.test(material)) base = palette.wood;
      else if (/glass|crystal|quartz|gem|ceramic|porcelain|enamel|ice/.test(material)) base = /ice/.test(material) ? palette.ice : /crystal|quartz|gem/.test(material) ? palette.crystal : /ceramic|porcelain|enamel/.test(material) ? palette.ceramic : palette.glass;
      else if (/iron|steel|metal|alloy|bronze|brass|copper|silver|gold|titanium|aluminium|aluminum|mithril|adamant/.test(material)) base = palette.metal;
      else if (/stone|rock|granite|marble|concrete|brick|clay|sand|soil|mud|obsidian/.test(material)) base = /sand/.test(material) ? palette.sand : /mud|clay|soil/.test(material) ? palette.mud : palette.rock;
      else if (/water|oil|acid|fluid|slurry|mercury|liquid/.test(material)) base = /acid/.test(material) ? palette.acid : palette.water;
      else if (/rubber|polymer|plastic|resin|foam|composite|carbon fibre|carbon fiber/.test(material)) base = palette.plastic;
      else if (/slime|ooze|gel/.test(name+' '+material)) base = palette.nature;
      else base = kind === 'being' ? palette.being : '#b7c6d1';
    }
    const energy = Math.max(0, Math.min(1, safeNumber(entity.energy_glow)));
    const charged = blendHex(base, '#91e9ff', Math.min(.68, energy * .8));
    return blendHex(charged, '#fff5cc', Math.max(0, (energy - .42) / .58) * .88);
  }
  function eventAt(i) {
    if (i < 0 || i >= events.length) return null;
    const stored = events[i];
    if (stored == null) return null;
    if (typeof stored !== 'string') return stored;
    const cached = eventObjectCache.get(i);
    if (cached) {
      // Map insertion order gives a tiny LRU; never cache large snapshots.
      eventObjectCache.delete(i); eventObjectCache.set(i, cached);
      return cached.event;
    }
    try {
      const parsed = JSON.parse(stored);
      if (stored.length <= MAX_CACHEABLE_EVENT_CHARS) {
        eventObjectCache.set(i, { event: parsed, chars: stored.length });
        eventObjectCacheChars += stored.length;
        while (eventObjectCache.size > MAX_EVENT_CACHE_ENTRIES || eventObjectCacheChars > MAX_EVENT_CACHE_CHARS) {
          const oldest = eventObjectCache.keys().next().value;
          const entry = eventObjectCache.get(oldest);
          eventObjectCacheChars -= entry ? entry.chars : 0;
          eventObjectCache.delete(oldest);
        }
      }
      return parsed;
    } catch (_) { return null; }
  }
  function clearEventObjectCache() { eventObjectCache.clear(); eventObjectCacheChars = 0; }
  function tuneAdaptiveGraphics(renderMs) {
    const cpuElapsed = Number.isFinite(renderMs) ? Math.max(0, Math.min(250, renderMs)) : 16.7;
    const intervalElapsed = Number.isFinite(frameIntervalForRender) ? Math.max(0, Math.min(250, frameIntervalForRender)) : frameTargetMs;
    // Convert missed frame budget into estimated per-frame work. Idle inspection
    // intentionally targets ~30 FPS, while active replay targets the display rate.
    const intervalCost = intervalElapsed > frameTargetMs + 8
      ? Math.min(250, intervalElapsed - frameTargetMs + 16.7) : 16.7;
    const elapsed = Math.max(cpuElapsed, intervalCost);
    adaptiveGraphics.frameIntervalMs = intervalElapsed;
    adaptiveGraphics.frameMs = adaptiveGraphics.frameMs * .82 + elapsed * .18;
    const exceededFrameBudget = intervalElapsed > frameTargetMs + 8;
    frameIntervalForRender = 16.7;
    frameTargetMs = 16.7;
    if (cpuElapsed > 24 || exceededFrameBudget || adaptiveGraphics.frameMs > 22) {
      adaptiveGraphics.overloadedFrames++;
      adaptiveGraphics.fastFrames = 0;
    } else if (cpuElapsed < 14 && !exceededFrameBudget) {
      adaptiveGraphics.fastFrames++;
      adaptiveGraphics.overloadedFrames = Math.max(0, adaptiveGraphics.overloadedFrames - 1);
    } else {
      adaptiveGraphics.overloadedFrames = Math.max(0, adaptiveGraphics.overloadedFrames - 1);
      adaptiveGraphics.fastFrames = Math.max(0, adaptiveGraphics.fastFrames - 2);
    }
    // Avoid oscillation: adjust only after repeated evidence, then hold steady.
    if (adaptiveGraphics.overloadedFrames >= 3) {
      adaptiveGraphics.bodyBudget = Math.max(MIN_DETAIL_BODIES, Math.floor(adaptiveGraphics.bodyBudget * .84));
      adaptiveGraphics.trailBudget = Math.max(MIN_DETAIL_TRAILS, Math.floor(adaptiveGraphics.trailBudget * .82));
      adaptiveGraphics.particleScale = Math.max(.25, adaptiveGraphics.particleScale * .82);
      adaptiveGraphics.overloadedFrames = 0;
    } else if (adaptiveGraphics.fastFrames >= 90) {
      adaptiveGraphics.bodyBudget = Math.min(MAX_DETAIL_BODIES, adaptiveGraphics.bodyBudget + 8);
      adaptiveGraphics.trailBudget = Math.min(MAX_DETAIL_TRAILS, adaptiveGraphics.trailBudget + 6);
      adaptiveGraphics.particleScale = Math.min(1, adaptiveGraphics.particleScale + .08);
      adaptiveGraphics.fastFrames = 0;
    }
    adaptiveGraphics.renderCount++;
    if (adaptiveGraphics.renderCount % 30 === 0) {
      const status = document.getElementById('adaptiveStatus');
      if (status) {
        const state = adaptiveGraphics.bodyBudget <= 48 ? 'simplifying decorative detail to protect frame time' : adaptiveGraphics.bodyBudget >= 120 ? 'using full available detail' : 'adjusting detail to current load';
        status.textContent = `${state} · ${adaptiveGraphics.pixelCount.toLocaleString()} backing pixels`; 
      }
    }
  }
  function eventName(e) { return text(e && e.type, 100); }
  function playbackTimeAt(position) {
    if (!events.length) return 0;
    const lowerIndex = Math.max(0, Math.min(events.length - 1, Math.floor(position)));
    const upperIndex = Math.max(0, Math.min(events.length - 1, lowerIndex + 1));
    const lower = eventAt(lowerIndex), upper = eventAt(upperIndex);
    const a = safeNumber(lower && lower.time), b = safeNumber(upper && upper.time, a);
    return a + (b - a) * Math.max(0, Math.min(1, position - lowerIndex));
  }

  function resetState() {
    entities = new Map(); previewEntities = new Map(); previewIds = new Set(); visibleEntityCache = null;
    contacts = []; effects = []; activities = []; selectedId = null; currentRecord = null; weatherState = null;
    lastSpellPanelKey = '';
    worldSettings = { gravity_m_s2:[0,0], air_density_kg_m3:1.225, default_restitution:0.2,
      friction_coefficient:0.35, drag_enabled:true, thermal_exchange_enabled:true,
      phase_changes_enabled:true, wetting_enabled:true };
  }
  function visibleEntities() {
    if (visibleEntityCache) return visibleEntityCache;
    visibleEntityCache = new Map(entities);
    for (const [id, entity] of previewEntities) visibleEntityCache.set(id, entity);
    return visibleEntityCache;
  }
  function upsert(entity, isPreview = false) {
    if (!entity || entity.id == null) return;
    const target = isPreview ? previewEntities : entities;
    const old = target.get(entity.id) || {};
    target.set(entity.id, { ...old, ...entity });
    visibleEntityCache = null;
    if (isPreview) previewIds.add(entity.id);
    else { previewIds.delete(entity.id); previewEntities.delete(entity.id); }
    if (selectedId == null && entity.active !== false && worldPosition(entity.position)) selectedId = entity.id;
  }
  function pushActivity(event, message, preview = false, eventIndex = index) {
    if (!message) return;
    activities.push({ at: safeNumber(event.time), message: text(message, 500), type: eventName(event), preview, eventIndex: Math.max(0, safeNumber(eventIndex, 0)), file: event.filename, line: event.line });
    // The panel only displays the latest 300 entries, so keep a small buffer.
    if (activities.length > 1000) activities.shift();
  }
  function drawEntityShape(shapeValue, x, y, r, color) {
    const shape = text(shapeValue || 'circle').toLowerCase();
    ctx.beginPath();
    if (shape === 'point') {
      ctx.arc(x, y, Math.max(2.5, r * .22), 0, Math.PI * 2);
    } else if (shape === 'round') {
      ctx.ellipse(x, y, r * .9, r * .82, 0, 0, Math.PI * 2);
    } else if (['wall','barrier','shield','corridor'].includes(shape)) {
      ctx.roundRect(x-r, y-r*.42, r*2, r*.84, Math.min(9,r*.3));
    } else if (shape === 'ellipse') {
      ctx.ellipse(x,y,r*1.25,r*.72,0,0,Math.PI*2);
    } else if (shape === 'ring' || shape === 'field') {
      ctx.arc(x,y,r*.82,0,Math.PI*2);
    } else if (shape === 'arc' || shape === 'dome') {
      ctx.arc(x,y,r*.85,Math.PI,Math.PI*2);
      if (shape === 'dome') { ctx.lineTo(x-r*.85,y); ctx.closePath(); }
    } else if (shape === 'line' || shape === 'ray' || shape === 'segment' || shape === 'beam') {
      ctx.moveTo(x-r,y); ctx.lineTo(x+r,y);
    } else if (shape === 'cone' || shape === 'fan') {
      ctx.moveTo(x,y); ctx.lineTo(x+r,y-r*.72); ctx.arc(x,y,r, -Math.PI*.22, Math.PI*.22); ctx.closePath();
    } else if (shape === 'polygon') {
      for (let i=0;i<6;i++) { const a=-Math.PI/2+i*Math.PI/3; const xx=x+Math.cos(a)*r, yy=y+Math.sin(a)*r; if(!i)ctx.moveTo(xx,yy);else ctx.lineTo(xx,yy); } ctx.closePath();
    } else if (shape === 'wave') {
      ctx.moveTo(x-r,y); ctx.quadraticCurveTo(x-r*.65,y-r,x-r*.3,y); ctx.quadraticCurveTo(x+r*.05,y+r,x+r*.4,y); ctx.quadraticCurveTo(x+r*.7,y-r,x+r,y);
    } else if (shape === 'spiral') {
      for(let i=0;i<=45;i++){const t=i/45*Math.PI*3.2, rr=r*.08+r*.82*i/45;const xx=x+Math.cos(t)*rr,yy=y+Math.sin(t)*rr;if(!i)ctx.moveTo(xx,yy);else ctx.lineTo(xx,yy);}
    } else if (shape === 'chain' || shape === 'tendril') {
      ctx.moveTo(x-r,y+r*.3); for(let i=1;i<=6;i++){const xx=x-r+(2*r*i/6), yy=y+Math.sin(i*1.45)*(shape==='chain'?r*.28:r*.58);ctx.lineTo(xx,yy);}
    } else if (shape === 'cage') {
      ctx.arc(x,y,r,0,Math.PI*2); ctx.moveTo(x-r,y);ctx.lineTo(x+r,y);ctx.moveTo(x,y-r);ctx.lineTo(x,y+r);ctx.moveTo(x-r*.7,y-r*.7);ctx.lineTo(x+r*.7,y+r*.7);ctx.moveTo(x-r*.7,y+r*.7);ctx.lineTo(x+r*.7,y-r*.7);
    } else if (shape === 'disc') {
      ctx.ellipse(x,y,r,r*.48,0,0,Math.PI*2);
    } else {
      ctx.arc(x,y,r,0,Math.PI*2);
    }
    if (!['line','ray','segment','beam','wave','spiral','chain','tendril','ring','arc','field'].includes(shape)) {
      ctx.fillStyle = color + '2e'; ctx.fill();
    }
    if (shape === 'point') {
      ctx.fillStyle = color; ctx.fill();
      ctx.beginPath(); ctx.arc(x, y, Math.max(5, r * .46), 0, Math.PI * 2);
      ctx.strokeStyle = color + '99'; ctx.lineWidth = 1; ctx.stroke();
    }
    ctx.strokeStyle = color; ctx.lineWidth = visualSettings.highContrastEdges ? 3 : 2; ctx.stroke();
    if (shape === 'field' || shape === 'ring') { ctx.beginPath(); ctx.arc(x,y,r*.52,0,Math.PI*2); ctx.stroke(); }
  }

  function semanticActivity(event) {
    const type = eventName(event);
    if (type === 'world.changed') return `World laws ${event.operation === 'reset' ? 'reset to defaults' : 'updated'}`;
    if (type === 'entity.created') {
      const e = event.entity || {};
      return `${text(e.name || e.element || 'Something magical')} appears`;
    }
    if (type === 'entity.changed') {
      const e = event.entity || {};
      const op = text(event.operation);
      if (op === 'heat' || op === 'object_ignited') return `${text(e.name)} glows with heat`;
      if (op === 'transform') return `${text(e.name)} changes form`;
      if (op === 'weave') return `${text(e.name || 'Mana construct')} takes shape`;
      if (op === 'move' || op === 'velocity' || op === 'accelerate') return `${text(e.name)} moves`;
      return '';
    }
    if (type === 'contact.begin') {
      const entities = Array.isArray(event.entities) ? event.entities : [];
      const names = Array.isArray(event.names) ? event.names : entities.filter(e => e && typeof e === 'object' && !Array.isArray(e)).map(e => e.name);
      return names.length >= 2 ? `${text(names[0])} touches ${text(names[1])}` : 'A magical impact flashes';
    }
    if (type === 'magic.effect') {
      if (event.effect === 'weather') return 'The weather changes around the scene';
      if (event.effect === 'burst') return 'A wave of magic bursts outward';
      if (event.effect === 'beam') return 'A beam of magic streaks across the scene';
      if (event.effect === 'construct_formed') return `${text((event.entity || {}).name || 'A magical shape')} takes form`;
      return '';
    }
    if (type === 'mana.event') {
      const name = event.name;
      const args = Array.isArray(event.args) ? event.args : [];
      if (name === 'being_summoned') {
        const being = args.find(x => typeof x === 'string') || 'A being';
        return `${text(being)} manifests in a swirl of light`;
      }
      if (name === 'being_reanimated') return 'The remains rise again';
      if (name === 'object_ignited') return 'A nearby object catches fire';
      if (name === 'mana_burst') return 'A wave of magic bursts outward';
      if (name === 'mana_emitted') return 'A beam of magic streaks across the scene';
      return '';
    }
    if (type === 'weather.changed' || type === 'environment.changed' || (type === 'magic.effect' && event.effect === 'weather')) {
      const descriptor = event.weather || event.environment || {};
      const label = text(descriptor.kind || descriptor.type || event.kind || event.weather || 'Weather', 50);
      return `The weather shifts: ${label}`;
    }
    if (type === 'spell.result') {
      const firstError = Array.isArray(event.errors) && event.errors.length ? text(event.errors[0], 180) : '';
      if (event.mode === 'post') return event.ok ? 'Spell preview completed; the world was not changed' : `Spell preview failed${firstError ? `: ${firstError}` : ''}`;
      if (event.mode === 'release') return event.ok && event.committed ? 'Spell released successfully' : `Spell failed${firstError ? `: ${firstError}` : ''}`;
      return event.ok ? 'Spell completed' : `Spell failed${firstError ? `: ${firstError}` : ''}`;
    }
    if (type === 'preview.output') return `PREVIEW · ${text(event.text, 400)}`;
    if (type === 'recording.notice') return text(event.message || 'Some visual details were omitted to keep the recording small.');
    if (type === 'activity' && /summoned-being limit|reanimate_many\(\) is limited/i.test(event.label || '')) return text(event.label);
    if (type === 'program.completed') return 'Run completed';
    return '';
  }

  function applyEvent(event, atIndex = index) {
    const type = eventName(event);
    currentRecord = event;
    if (type === 'spell.started') {
      // A new cast gets its own preview layer. Never blend one trial into another.
      previewEntities = new Map();
      previewIds = new Set();
      // Weather is world state, never inferred from the name of a spell.
    }
    if (type === 'entity.created') {
      const entity = event.entity;
      upsert(entity, event.mode === 'post');
      if (entity && Array.isArray(entity.position) &&
          (entity.kind === 'being' || entity.summoned || entity.undead)) {
        effects.push({ effect: 'manifestation', position: entity.position, spell: event.spell,
          time: safeNumber(event.time), eventIndex: atIndex, preview: event.mode === 'post' });
        if (effects.length > 50) effects.shift();
      }
    } else if (type === 'entity.changed') {
      const entity = event.entity;
      upsert(entity, event.mode === 'post');
      if (entity && Array.isArray(entity.position) && entity.undead && event.operation === 'reanimate') {
        effects.push({ effect: 'manifestation', position: entity.position, spell: event.spell,
          time: safeNumber(event.time), eventIndex: atIndex, preview: event.mode === 'post', necromancy: true });
        if (effects.length > 50) effects.shift();
      }
    } else if (type === 'world.changed') {
      if (event.settings && typeof event.settings === 'object') worldSettings = { ...worldSettings, ...event.settings };
      if (event.operation === 'magnetic_field_created' && event.field && typeof event.field === 'object') {
        effects.push({ ...event.field, effect: 'magnetic_field', time: safeNumber(event.time), eventIndex: atIndex, center_m: event.field.center_m });
        if (effects.length > 50) effects.shift();
      }
    } else if (type === 'world.effect') {
      const center = Array.isArray(event.center_m) ? event.center_m : (event.target && event.target.position);
      effects.push({ ...event, position: center, time: safeNumber(event.time), eventIndex: atIndex, target: event.target });
      if (effects.length > 50) effects.shift();
    } else if (type === 'scene.snapshot') {
      const snapshotEntities = Array.isArray(event.entities) ? event.entities : [];
      const isVisualPreview = event.mode === 'post' && event.presentation === 'visual';
      if (isVisualPreview && event.reason !== 'after_post' && event.reason !== 'after_error') {
        // Intermediate snapshots belong to the hypothetical cast, not the real world.
        previewEntities = new Map();
        previewIds = new Set();
        for (const entity of snapshotEntities) {
          if (entity && entity.id != null) { previewEntities.set(entity.id, entity); previewIds.add(entity.id); }
        }
        visibleEntityCache = null;
      } else {
        // This is the restored world (for a preview) or an ordinary committed snapshot.
        entities = new Map();
        for (const entity of snapshotEntities) {
          if (entity && entity.id != null) entities.set(entity.id, entity);
        }
        visibleEntityCache = null;
      }
      const selected = selectedId == null ? null : visibleEntities().get(selectedId);
      if (selectedId != null && (!selected || !worldPosition(selected.position))) selectedId = null;
      if (selectedId == null) {
        const firstSelectable = Array.from(visibleEntities().values()).find(entity => entity && entity.active !== false && worldPosition(entity.position));
        if (firstSelectable) selectedId = firstSelectable.id;
      }
      if (event.environment) beginWeather(event.environment, safeNumber(event.time), atIndex);
      if (event.truncated) {
        sceneNotice.textContent = `Showing ${visibleEntities().size} of ${safeNumber(event.entity_count)}${event.entity_count_exact === false ? '+' : ''} magical objects`;
        sceneNotice.hidden = false;
      } else {
        sceneNotice.hidden = true;
      }
    } else if (type === 'contact.begin') {
      const involved = Array.isArray(event.entities) ? event.entities.filter(e => e && typeof e === 'object' && !Array.isArray(e)) : [];
      involved.forEach(e => upsert(e, event.mode === 'post'));
      const names = Array.isArray(event.names) ? event.names : involved.map(e => e.name);
      contacts.push({ time: safeNumber(event.time), eventIndex: atIndex, ids: involved.map(e => e.id), names, position: worldPosition(event.position) || undefined, preview: event.mode === 'post' });
      if (contacts.length > 50) contacts.shift();
    } else if (type === 'magic.effect') {
      effects.push({ ...event, time: safeNumber(event.time), eventIndex: atIndex, preview: event.mode === 'post' });
      if (effects.length > 50) effects.shift();
      if (event.effect === 'weather') beginWeather(event.weather || event, safeNumber(event.time), atIndex);
      if (event.entity) upsert(event.entity, event.mode === 'post');
    } else if (type === 'mana.event') {
      if (event.name === 'mana_formed') {
        const args = Array.isArray(event.args) ? event.args : [];
        const ref = args.find(x => x && typeof x === 'object' && x.entity_id != null);
        if (ref) {
          const existing = visibleEntities().get(ref.entity_id);
          if (existing) upsert({ ...existing, kind: 'mana_construct' }, event.mode === 'post');
        }
      }
    } else if (type === 'weather.changed' || type === 'environment.changed') {
      beginWeather(event.weather || event.environment || event, safeNumber(event.time), atIndex);
    } else if (type === 'spell.result') {
      currentRecord = event;
    }
    const message = semanticActivity(event);
    if (message) pushActivity(event, message, event.mode === 'post' || type === 'preview.output', atIndex);
    if (type === 'spell.result') updateResult(event);
  }
  function updateResult(event) {
    if (event.mode === 'post') resultBadge.textContent = event.ok ? 'PREVIEW' : 'PREVIEW FAILED';
    else if (event.mode === 'release') resultBadge.textContent = event.ok && event.committed ? 'RELEASED' : 'FAILED';
    else if (event.type === 'program.completed') resultBadge.textContent = 'COMPLETE';
  }
  function stateAt(target) {
    resetState();
    for (let i = 0; i <= target && i < events.length; i++) { const event = eventAt(i); if (event) applyEvent(event, i); }
    index = Math.min(target, Math.max(0, events.length - 1));
    renderActivity();
    renderDetails();
    renderObjectList();
    renderWorldLaws();
    renderSpellInspector(index);
    render();
    updateControls();
  }
  function renderActivity() {
    activityList.replaceChildren();
    const query=text(activitySearch&&activitySearch.value||'',100).trim().toLowerCase();
    const filter=text(activityFilter&&activityFilter.value||'all',20);
    const matches=activities.filter(item=>{
      const type=text(item.type,100).toLowerCase(),message=text(item.message,500).toLowerCase();
      if(query&&!`${type} ${message}`.includes(query))return false;
      if(filter==='contact'&&!type.startsWith('contact.'))return false;
      if(filter==='world'&&!(/world|weather|environment/.test(type)))return false;
      if(filter==='errors'&&!(/failed|error|denied|invalid|not committed/.test(message)))return false;
      if(filter==='magic'&&!(/spell|magic|mana|entity\.(created|changed)|preview/.test(type)))return false;
      return true;
    });
    for (const item of matches.slice(-300)) {
      const li = document.createElement('li');
      if (item.preview) li.classList.add('preview');
      if (item.eventIndex === index) li.classList.add('is-current');
      li.tabIndex = 0;
      li.title = 'Jump replay to this event';
      li.setAttribute('aria-label', `Jump to ${text(item.type || 'event',40)} at ${item.at.toFixed(2)} seconds`);
      const jump = () => go(item.eventIndex);
      li.addEventListener('click', event => { if (event.target && event.target.closest && event.target.closest('.source-link')) return; jump(); });
      li.addEventListener('keydown', event => { if (event.target !== li) return; if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); jump(); } });
      const when = document.createElement('span'); when.className = 'when'; when.textContent = `${item.preview ? 'PREVIEW · ' : ''}${item.at.toFixed(2)} s`;
      const body = document.createElement('span'); body.textContent = item.message;
      li.append(when, body);
      if(item.type){const kind=document.createElement('span');kind.className='event-kind';kind.textContent=text(item.type,40);li.append(kind);}
      if (typeof item.file === 'string' && Number.isInteger(item.line) && item.line > 0) {
        const source = document.createElement('button'); source.type = 'button'; source.className = 'source-link'; source.textContent = 'View source';
        source.addEventListener('click', event => { event.stopPropagation(); vscode.postMessage({ type: 'jumpToSource', file: item.file, line: item.line }); });
        li.append(source);
      }
      activityList.append(li);
    }
    const empty=document.getElementById('activityEmpty');if(empty)empty.hidden=matches.length!==0;
  }
  function objectCategory(entity) {
    const kind=text(entity.kind||'').toLowerCase();
    if (kind==='mana_construct' || kind==='puremana' || kind==='mana') return 'construct';
    if (entity.summoned || entity.undead) return entity.undead ? 'undead' : 'summoned';
    if (kind==='being' || entity.alive===true || entity.is_living===true || ['humanoid','bird','serpent','beast','golem'].includes(text(entity.visual_form).toLowerCase())) return 'living';
    if (entity.anchored) return 'anchored';
    return 'material';
  }
  function isLivingEntity(entity) {
    const kind=text(entity.kind||'').toLowerCase();
    return entity.undead!==true && (kind==='being' || entity.alive===true || entity.is_living===true ||
      ['humanoid','bird','serpent','beast','golem'].includes(text(entity.visual_form).toLowerCase()));
  }
  function isSummonedEntity(entity) { return entity.summoned===true || entity.undead===true; }
  function renderObjectList() {
    if (!objectList) return;
    const query=text(objectSearch&&objectSearch.value||'',100).trim().toLowerCase();
    const filter=text(objectFilter&&objectFilter.value||'all',24);
    const all=[];
    for (const entity of visibleEntities().values()) {
      if (!entity || entity.active===false || !worldPosition(entity.position)) continue;
      const label=text(entity.name||entity.element||entity.material||`Object ${entity.id}`,140);
      const haystack=`${label} ${text(entity.material,80)} ${text(entity.element,80)} ${text(entity.kind,60)} ${text(entity.visual_form,60)}`.toLowerCase();
      if (query && !haystack.includes(query)) continue;
      const category=objectCategory(entity);
      // Filters are predicates, not mutually exclusive labels: a summoned griffin
      // is both living and summoned, so it should appear in either view.
      if (filter==='living' && !isLivingEntity(entity)) continue;
      if (filter==='summoned' && !isSummonedEntity(entity)) continue;
      if (filter==='material' && (category==='construct' || isSummonedEntity(entity) || isLivingEntity(entity))) continue;
      if (filter==='construct' && category!=='construct') continue;
      if (filter==='anchored' && !entity.anchored) continue;
      if (filter==='moving' && (entity.anchored || entity.collidable===false)) continue;
      all.push({entity,label,category});
    }
    all.sort((a,b)=>a.label.localeCompare(b.label));
    const count=document.getElementById('objectCount');
    if(count)count.textContent=all.length.toLocaleString();
    const note=document.getElementById('objectLimitNote');
    const display=all.slice(0,250);
    objectList.replaceChildren();
    for(const item of display){
      const e=item.entity;
      const listItem=document.createElement('div');listItem.setAttribute('role','listitem');listItem.className='object-row-wrap';
      const row=document.createElement('button');row.type='button';row.className='object-row'+(selectedId===e.id?' selected':'');row.setAttribute('aria-pressed',selectedId===e.id?'true':'false');row.setAttribute('aria-label',`${item.label}, ${text(e.material||e.element||'unknown material',60)}, ${e.anchored?'anchored':e.collidable===false?'non-colliding':'physics-enabled'}`);
      const swatch=document.createElement('span');swatch.className='object-swatch';swatch.style.color=entityColor(e);swatch.style.background=entityColor(e);
      const copy=document.createElement('span');copy.className='object-copy';
      const name=document.createElement('span');name.className='object-name';name.textContent=item.label;
      const meta=document.createElement('span');meta.className='object-meta';meta.textContent=`${text(e.material||e.element||'Unknown material',60)} · ${e.anchored?'anchored':e.collidable===false?'non-colliding':'physics-enabled'}`;
      const kind=document.createElement('span');kind.className='object-kind';kind.textContent=item.category;
      copy.append(name,meta);row.append(swatch,copy,kind);listItem.append(row);
      row.addEventListener('click',()=>{selectedId=e.id;focusEntity(e);renderDetails();renderObjectList();render();});
      objectList.append(listItem);
    }
    if(note){note.hidden=all.length<=display.length;note.textContent=all.length>display.length?`Showing ${display.length} of ${all.length.toLocaleString()} matching objects to keep the inspector responsive.`:'';}
    const empty=document.getElementById('objectsEmpty');
    if(empty)empty.hidden=all.length!==0;
  }
  function focusEntity(entity) {
    const position=entity && worldPosition(entity.position);
    if(!position)return;
    const rect=canvas.getBoundingClientRect();
    const w=rect.width||900,h=rect.height||600;
    if(!camera.initialized)transformFor(w,h);
    const scale=Math.max(MIN_SCENE_SCALE,Math.min(MAX_SCENE_SCALE,camera.baseScale*camera.zoom));
    const floorY=h*.78;
    camera.x=position[0];
    camera.y=position[1]+(h*.5-floorY)/scale;
    camera.initialized=true;
  }
  function selectedEntity() { return selectedId == null ? null : visibleEntities().get(selectedId) || null; }
  function distanceLabel(e) {
    const position=e && worldPosition(e.position);
    if (!position) return '—';
    let nearest = Infinity;
    for (const other of visibleEntities().values()) {
      if (other.id === e.id || other.active === false) continue;
      const otherPosition=worldPosition(other.position);
      if (!otherPosition) continue;
      const d = Math.hypot(otherPosition[0]-position[0], otherPosition[1]-position[1]);
      if (Number.isFinite(d)) nearest = Math.min(nearest, d);
    }
    if (!Number.isFinite(nearest)) return '—';
    const scaled = nearest >= 1000 ? `${(nearest / 1000).toFixed(nearest >= 10000 ? 0 : 1)} km` : `${nearest.toFixed(nearest >= 100 ? 0 : nearest >= 10 ? 1 : 2).replace(/\.0+$|(?<=\.[0-9])0+$/g, '')} m`;
    return scaled;
  }
  function addFact(label, value) {
    const card = document.createElement('div'); card.className = 'fact';
    const l = document.createElement('span'); l.className = 'label'; l.textContent = label;
    const v = document.createElement('span'); v.className = 'value'; v.textContent = text(value || '—');
    card.append(l, v); document.getElementById('detailFacts').append(card);
  }
  function renderWorldLaws() {
    const facts = document.getElementById('worldFacts');
    if (!facts) return;
    facts.replaceChildren();
    const gravity = Array.isArray(worldSettings.gravity_m_s2) ? worldSettings.gravity_m_s2 : [0,0];
    const fmt = (value, digits=3) => Number.isFinite(Number(value)) ? Number(value).toLocaleString(undefined,{maximumFractionDigits:digits}) : '—';
    const gx=safeNumber(gravity[0]),gy=safeNumber(gravity[1]),gMagnitude=Math.hypot(gx,gy);
    const gDirection=gMagnitude<1e-6?'none':Math.abs(gx)<1e-4?(gy<0?'downward':'upward'):Math.abs(gy)<1e-4?(gx<0?'leftward':'rightward'):'angled';
    addFactTo(facts, 'Gravity', `${fmt(gMagnitude,3)} m/s² · ${gDirection}`);
    addFactTo(facts, 'Air density', `${fmt(worldSettings.air_density_kg_m3,4)} kg/m³`);
    addFactTo(facts, 'Restitution', fmt(worldSettings.default_restitution,3));
    addFactTo(facts, 'Friction', fmt(worldSettings.friction_coefficient,3));
    addFactTo(facts, 'Wind drag', worldSettings.drag_enabled ? 'Enabled' : 'Disabled');
    addFactTo(facts, 'Thermal exchange', worldSettings.thermal_exchange_enabled ? 'Enabled' : 'Disabled');
    addFactTo(facts, 'Phase changes', worldSettings.phase_changes_enabled ? 'Enabled' : 'Disabled');
    addFactTo(facts, 'Wetting / dust', worldSettings.wetting_enabled ? 'Enabled' : 'Disabled');
    if (weatherState) {
      addFactTo(facts, 'Weather', text(weatherState.kind || 'clear'));
      addFactTo(facts, 'Precipitation', text(weatherState.precipitation || 'none'));
      addFactTo(facts, 'Wind speed', `${fmt(weatherState.windSpeedMps,2)} m/s`);
      addFactTo(facts, 'Ambient temperature', `${fmt(safeNumber(weatherState.temperature,293.15),1)} K`);
      addFactTo(facts, 'Humidity', `${Math.round(safeNumber(weatherState.humidity,.45)*100)}%`);
      addFactTo(facts, 'Cloud cover', `${Math.round(safeNumber(weatherState.clouds,0)*100)}%`);
    }
    const summary=document.getElementById('worldSummary');
    if(summary){
      let active=0,anchored=0,summoned=0,constructs=0;
      for(const entity of visibleEntities().values()){
        if(!entity||entity.active===false||!Array.isArray(entity.position))continue;
        active++;if(entity.anchored)anchored++;if(entity.summoned||entity.undead)summoned++;if(text(entity.kind||'').toLowerCase()==='mana_construct')constructs++;
      }
      summary.textContent=`WORLD SNAPSHOT\n${active.toLocaleString()} active objects · ${anchored.toLocaleString()} anchored · ${summoned.toLocaleString()} summoned/undead · ${constructs.toLocaleString()} mana constructs\n${contacts.length.toLocaleString()} recorded contacts · ${effects.length.toLocaleString()} retained effect markers\n${weatherState?`Atmosphere: ${text(weatherState.kind,24)} · ${Math.round(safeNumber(weatherState.intensity,0)*100)}% intensity`:'No active weather state recorded'}\nInspector values describe this replay position; they do not edit or simulate the world.`;
    }
  }
  function addFactTo(container, label, value) {
    const card = document.createElement('div'); card.className = 'fact';
    const l = document.createElement('span'); l.className = 'label'; l.textContent = label;
    const v = document.createElement('span'); v.className = 'value'; v.textContent = text(value || '—');
    card.append(l, v); container.append(card);
  }
  function spellStageName(stage) {
    return ({cast:'Cast',form:'Form',shape:'Shape',release:'Release',travel:'Travel',impact:'Contact',result:'Outcome'})[stage] || 'Stage';
  }
  function spellEventDescription(event) {
    const type = eventName(event), effect = text(event.effect || '', 60).toLowerCase();
    if (type === 'spell.started') return 'The named spell begins executing';
    if (type === 'entity.created') return 'A world entity was created by the runtime';
    if (type === 'entity.changed') return `Runtime operation: ${text(event.operation || 'change', 50)}`;
    if (type === 'magic.effect') return `Recorded magic operation: ${effect || 'unspecified'}`;
    if (type === 'contact.begin') return 'A recorded physical contact occurred';
    if (type === 'spell.result') return 'Execution outcome reported by the runtime';
    if (type === 'mana.event') return `Mana operation: ${text(event.name || 'event', 50)}`;
    return type.replaceAll('.', ' ');
  }
  function renderSpellInspector(playback = index) {
    const cast = [...castEvents].reverse().find(item => item.index <= playback) || castEvents[0];
    const panelKey = `${cast ? cast.index : 'none'}:${Math.floor(playback)}:${cast && cast.trace.length}`;
    if (panelKey === lastSpellPanelKey) return;
    lastSpellPanelKey = panelKey;
    const titleEl = document.getElementById('spellName');
    const subtitleEl = document.getElementById('spellSubtitle');
    const heroEl = document.getElementById('spellHero');
    const factsEl = document.getElementById('spellFacts');
    const traceEl = document.getElementById('spellTrace');
    const emptyEl = document.getElementById('spellEmpty');
    if (!titleEl || !subtitleEl || !heroEl || !factsEl || !traceEl) return;
    traceEl.replaceChildren(); factsEl.replaceChildren(); heroEl.replaceChildren();
    if (!cast) {
      titleEl.textContent = 'No spell in recording'; subtitleEl.textContent = 'Run a .mana spell with recording enabled, or open a recording that contains spell.started events.';
      if (emptyEl) { emptyEl.hidden = false; emptyEl.textContent = 'This file has no recorded spell lifecycle. Generic world and physics events remain visible in the other tabs.'; }
      return;
    }
    const trace = cast.trace || [];
    const currentTrace = [...trace].reverse().find(item => item.index <= playback);
    const recent = currentTrace || trace[0] || null;
    const stage = recent ? spellStageName(recent.stage) : 'Cast begins';
    const colour = castColour(cast);
    titleEl.textContent = cast.spell || 'Unnamed spell';
    const status = cast.result ? (cast.result.mode === 'post' ? (cast.result.ok ? 'Preview · rolled back' : 'Preview failed') : (cast.result.committed ? 'Released · committed' : cast.result.ok ? 'Completed' : 'Failed')) : 'Recorded execution';
    subtitleEl.textContent = `${status} · ${stage} · event ${cast.index + 1}`;
    const identity = [...trace].reverse().find(item => item.element)?.element || '';
    const formIdentity = `${cast.spell} ${identity} ${trace.map(item => item.type === 'magic.effect' ? item.detail : '').join(' ')}`.toLowerCase();
    const form = spellArchetype(formIdentity);
    const symbols = {orb:'◉',lance:'➤',bolt:'ϟ',wave:'≋',field:'⬡',ring:'◎',sigil:'✦'};
    const glyph = document.createElement('div'); glyph.className = `spell-glyph spell-${form}`; glyph.style.setProperty('--spell-colour', colour);
    const outer = document.createElement('span'); outer.className = 'glyph-ring';
    const inner = document.createElement('span'); inner.className = 'glyph-core'; inner.textContent = symbols[form] || '✦';
    const orbit = document.createElement('span'); orbit.className = 'glyph-orbit';
    glyph.append(outer, orbit, inner); heroEl.append(glyph);
    const heroCopy = document.createElement('div'); heroCopy.className = 'spell-hero-copy';
    const formTitle = document.createElement('strong'); formTitle.textContent = ({orb:'Contained core / orb',lance:'Directed projectile / lance',bolt:'Forked energy bolt',wave:'Continuous flow / ribbon',field:'Field boundary / shield',ring:'Ring-shaped spell',sigil:'Geometric mana form'})[form] || 'Geometric mana form';
    const formNote = document.createElement('span'); formNote.textContent = 'Procedural spell silhouette · source world remains unchanged by viewing';
    heroCopy.append(formTitle, formNote); heroEl.append(heroCopy);
    const facts = [
      ['Mode', cast.mode === 'post' ? 'POST · preview' : 'RELEASE'],
      ['Observed operations', String(trace.length)],
      ['Recorded stages', [...new Set(trace.map(item => item.stage))].map(spellStageName).join(' → ') || 'Cast only'],
      ['Resolution', cast.result ? (cast.result.committed ? 'Committed' : cast.result.ok ? 'Completed, not committed' : 'Failed') : 'No result record yet']
    ];
    for (const [labelText, valueText] of facts) { const box = document.createElement('div'); box.className = 'fact'; const label = document.createElement('span'); label.className = 'label'; label.textContent = labelText; const value = document.createElement('span'); value.className = 'value'; value.textContent = valueText; box.append(label, value); factsEl.append(box); }
    const visibleTrace = trace.slice(-28);
    for (const item of visibleTrace) {
      const row = document.createElement('li'); row.className = `spell-trace-row${item.index <= playback ? ' is-seen' : ' is-future'}${item.index === Math.floor(playback) ? ' is-current' : ''}`;
      row.tabIndex = 0; row.setAttribute('role', 'button'); row.title = `Seek to event ${item.index + 1}`;
      const when = document.createElement('span'); when.className = 'spell-trace-time'; when.textContent = `${safeNumber(item.time).toFixed(2)}s · ${spellStageName(item.stage)}`;
      const label = document.createElement('strong'); label.textContent = item.label;
      const detail = document.createElement('span'); detail.className = 'spell-trace-detail'; detail.textContent = item.detail || spellEventDescription({ type: item.type });
      row.append(when, label, detail);
      const seek = () => { go(item.index); selectTab('scene'); };
      row.addEventListener('click', seek); row.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); seek(); } });
      traceEl.append(row);
    }
    if (emptyEl) { emptyEl.hidden = trace.length > 0; emptyEl.textContent = trace.length ? '' : 'No operation detail was recorded for this cast. The spell name is available, but the recording does not expose its internal form.'; }
  }

  function renderDetails() {
    const e = selectedEntity();
    document.getElementById('detailName').textContent = e ? text(e.name || e.element) : 'Nothing selected';
    document.getElementById('detailSubtitle').textContent = e ? `${text(e.material || e.element)} · ${text(e.state || 'present')}` : 'Choose a magical object in the scene.';
    const facts = document.getElementById('detailFacts'); facts.replaceChildren();
    if (!e) return;
    addFact('Distance', distanceLabel(e));
    addFact('Form', e.visual_form ? text(e.visual_form) : e.body_form ? text(e.body_form) : e.kind === 'mana_construct' ? 'Woven mana' : e.kind === 'being' ? 'Being' : text(e.shape || 'natural form'));
    if (e.species || e.anatomy_species_id) addFact('Species / body plan', text(e.species || e.anatomy_species_id, 120));
    if (e.skeleton_type) addFact('Skeleton', text(e.skeleton_type, 80));
    addFact('Condition', e.active === false ? 'Gone' : e.undead ? 'Undead' : e.summoned ? 'Summoned' : e.state || 'Present');
    addFact('Material', text(e.material || e.element || '—'));
    if (e.element_symbol || e.atomic_number != null) {
      const atomic = `${text(e.element_symbol || 'Element')}${e.atomic_number != null ? ` · Z ${Math.round(safeNumber(e.atomic_number))}` : ''}`;
      addFact('Periodic ID', atomic);
    }
    if (e.composition && typeof e.composition === 'object') {
      const comp = e.composition;
      if (comp.kind === 'element') addFact('Composition', `${text(comp.symbol || e.element_symbol || '')} · pure element`);
      else if (Array.isArray(comp.elements) && comp.elements.length) {
        const parts=comp.elements.slice(0,8).map(part => `${text(part.symbol || part.name || '?')} ${part.mass_fraction == null ? '' : `${(safeNumber(part.mass_fraction)*100).toFixed(1)}%`}`).join(' · ');
        addFact('Composition', `${text(comp.formula || comp.name || comp.kind)}: ${parts}`);
      } else if (comp.kind === 'compound') addFact('Composition', `${text(comp.formula || comp.name || 'Compound')} · compound`);
      else addFact('Composition', text(comp.name || comp.kind || 'Mixed material'));
    }
    const fmt = (v, unit, digits=3) => v == null || !Number.isFinite(Number(v)) ? '—' : `${Number(v).toLocaleString(undefined,{maximumFractionDigits:digits})} ${unit}`;
    if (e.mass_kg != null) addFact('Mass', fmt(e.mass_kg, 'kg'));
    if (e.volume_m3 != null) addFact('Volume', fmt(e.volume_m3, 'm³'));
    if (e.density_kg_m3 != null) addFact('Density', fmt(e.density_kg_m3, 'kg/m³', 1));
    if (e.temperature_k != null) addFact('Temperature', `${fmt(e.temperature_k, 'K', 1)} (${fmt(safeNumber(e.temperature_k)-273.15, '°C', 1)})`);
    if (e.melting_point_k != null) addFact('Melting point', fmt(e.melting_point_k, 'K', 1));
    if (e.boiling_point_k != null) addFact('Boiling point', fmt(e.boiling_point_k, 'K', 1));
    if (e.estimated_material_data) addFact('Data quality', 'Estimated reference data');
    if (e.hp != null) addFact('Health', `${Math.round(safeNumber(e.hp))}${e.max_hp != null ? ` / ${Math.round(safeNumber(e.max_hp))}` : ''}`);
    addFact('Movement', e.anchored ? 'Anchored' : e.collidable === false ? 'Non-colliding' : 'Physics-enabled');
    if (e.wetness > 0.001) addFact('Surface wetness', `${Math.round(safeNumber(e.wetness)*100)}%`);
    if (e.dust_coating > 0.001) addFact('Dust coating', `${Math.round(safeNumber(e.dust_coating)*100)}%`);
    if (previewIds.has(e.id)) addFact('Status', 'Preview only');
  }
  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const deviceDpr = Math.max(.5, Math.min(2, Number(window.devicePixelRatio) || 1));
    const area = Math.max(1, rect.width * rect.height);
    const pixelBoundDpr = Math.sqrt(MAX_CANVAS_PIXELS / area);
    let width = Math.max(1, Math.round(rect.width * Math.min(deviceDpr, pixelBoundDpr)));
    let height = Math.max(1, Math.round(rect.height * Math.min(deviceDpr, pixelBoundDpr)));
    // Rounding and exceptionally skinny/wide windows can breach the estimate;
    // enforce the hard pixel limit on the actual backing dimensions as well.
    if (width * height > MAX_CANVAS_PIXELS) {
      const shrink = Math.sqrt(MAX_CANVAS_PIXELS / (width * height));
      width = Math.max(1, Math.floor(width * shrink));
      height = Math.max(1, Math.floor(height * shrink));
      // One dimension may be 1 px for extreme viewport ratios. Clamp the
      // longer axis directly; never loop through millions of single-pixel steps.
      if (width * height > MAX_CANVAS_PIXELS) {
        if (width >= height) width = Math.max(1, Math.floor(MAX_CANVAS_PIXELS / height));
        else height = Math.max(1, Math.floor(MAX_CANVAS_PIXELS / width));
      }
    }
    // Avoid resetting the backing store unless its dimensions actually changed.
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width; canvas.height = height;
    }
    adaptiveGraphics.pixelCount = width * height;
    // Independent axes preserve the viewport proportions after the hard cap.
    ctx.setTransform(width / rect.width, 0, 0, height / rect.height, 0, 0);
    ctx.imageSmoothingEnabled = true;
    render();
  }

  function rebuildMotionBounds() {
    let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
    for (const track of motionTracks) {
      for (const point of (track.points || [])) {
        if (!Number.isFinite(point.x) || !Number.isFinite(point.y)) continue;
        minX=Math.min(minX,point.x-.2);maxX=Math.max(maxX,point.x+.2);
        minY=Math.min(minY,point.y-.2);maxY=Math.max(maxY,point.y+.2);
      }
    }
    cachedMotionBounds = minX === Infinity ? null : {minX,maxX,minY,maxY};
    motionBoundsBuilt = true;
    motionBoundsBuildCount++;
  }
  function sceneBounds() {
    let minX=-.5,maxX=.5,minY=-.5,maxY=.5;
    const include=(x,y,r)=>{
      minX=Math.min(minX,x-r);maxX=Math.max(maxX,x+r);
      minY=Math.min(minY,y-r);maxY=Math.max(maxY,y+r);
    };
    include(5.5,0,.55);
    for (const e of visibleEntities().values()) {
      if (!e || e.active===false) continue;
      // Do not turn malformed [null, null] coordinates into a fake origin via
      // Number(null) == 0. Use the same strict validator as the draw pass.
      const position=worldPosition(e.position);
      if (!position) continue;
      include(position[0],position[1],Math.max(.2,Math.min(100000,safeNumber(e.radius_m,.22))));
    }
    if (!motionBoundsBuilt) rebuildMotionBounds();
    if (cachedMotionBounds) {
      minX=Math.min(minX,cachedMotionBounds.minX);maxX=Math.max(maxX,cachedMotionBounds.maxX);
      minY=Math.min(minY,cachedMotionBounds.minY);maxY=Math.max(maxY,cachedMotionBounds.maxY);
    }
    for (const effect of effects) {
      const position=worldPosition(effect.position)||worldPosition(effect.center_m)||worldPosition(effect.origin_m)||(effect.entity&&worldPosition(effect.entity.position));
      if(position) include(position[0],position[1],Math.max(0,Math.min(20,safeNumber(effect.radius_m,1))));
    }
    return {minX,maxX,minY,maxY};
  }

  function fitCamera() {
    const rect = canvas.getBoundingClientRect();
    const w = rect.width || 1000, h = rect.height || 620, b = sceneBounds();
    const spanX = Math.max(5.5,b.maxX-b.minX), spanY = Math.max(3.4,b.maxY-b.minY);
    camera.zoom = 1;
    camera.baseScale = Math.max(MIN_SCENE_SCALE,Math.min((w*.42)/spanX,(h*.52)/spanY));
    // Bias the view toward the target: the caster sits left, the target near centre.
    camera.x = b.maxX - (w*.12/camera.baseScale);
    camera.y = 0;
    camera.initialized = true;
    updateZoomLabel();
    render();
  }

  function transformFor(w,h) {
    const b = sceneBounds();
    if (!camera.initialized) {
      const spanX = Math.max(5.5,b.maxX-b.minX), spanY = Math.max(3.4,b.maxY-b.minY);
      camera.baseScale = Math.max(MIN_SCENE_SCALE,Math.min((w*.42)/spanX,(h*.52)/spanY));
      camera.x = b.maxX - (w*.12/camera.baseScale); camera.y = 0; camera.initialized = true;
    }
    const scale = Math.max(MIN_SCENE_SCALE,Math.min(MAX_SCENE_SCALE,camera.baseScale * camera.zoom));
    const floorY = h*.78;
    return {
      scale, floorY,
      px: x => w*.5 + (x-camera.x)*scale,
      py: y => floorY - (y-camera.y)*scale,
      wx: x => camera.x + (x-w*.5)/scale,
      wy: y => camera.y + (floorY-y)/scale,
      w,h,b
    };
  }

  function updateZoomLabel() {
    const label = document.getElementById('zoomLabel');
    if (label) label.textContent = `${Math.round(camera.zoom*100)}%`;
  }

  function fitScene() { fitCamera(); }
  function zoomBy(factor, anchorX, anchorY) {
    const rect = canvas.getBoundingClientRect();
    const w = rect.width, h = rect.height;
    if (!w || !h) return;
    const old = transformFor(w,h), ax = Number.isFinite(anchorX) ? anchorX : w*.5, ay = Number.isFinite(anchorY) ? anchorY : h*.5;
    const fixedX = old.wx(ax), fixedY = old.wy(ay);
    camera.zoom = Math.max(.28,Math.min(4.5,camera.zoom*factor));
    const scale = camera.baseScale*camera.zoom;
    camera.x = fixedX-(ax-w*.5)/scale;
    camera.y = fixedY-(old.floorY-ay)/scale;
    updateZoomLabel(); render();
  }

  function niceGridStep(raw) {
    const safe = Math.max(1e-6, raw);
    const power = Math.pow(10, Math.floor(Math.log10(safe)));
    const scaled = safe / power;
    return (scaled <= 1 ? 1 : scaled <= 2 ? 2 : scaled <= 5 ? 5 : 10) * power;
  }

  function drawStage(t, playback) {
    const {w,h,scale} = t;
    // Backdrop presets are purely presentational. World coordinates and physical
    // rules are unaffected by colour grading or scene art direction.
    const stageStyle = ({
      graphite:{base:'#111315',major:'rgba(151,158,166,.15)',minor:'rgba(120,127,135,.075)',axis:'rgba(170,186,198,.42)',vignette:'rgba(0,0,0,.24)'},
      midnight:{base:'#071320',major:'rgba(108,171,211,.22)',minor:'rgba(79,135,177,.10)',axis:'rgba(113,201,236,.50)',vignette:'rgba(0,0,18,.30)'},
      'deep-space':{base:'#080817',major:'rgba(135,123,202,.19)',minor:'rgba(91,81,159,.085)',axis:'rgba(188,158,255,.48)',vignette:'rgba(0,0,0,.4)'},
      vellum:{base:'#dfd0b0',major:'rgba(92,69,44,.27)',minor:'rgba(92,69,44,.12)',axis:'rgba(66,48,28,.62)',vignette:'rgba(68,46,21,.08)'},
      abyss:{base:'#071b1c',major:'rgba(77,174,163,.22)',minor:'rgba(57,127,125,.09)',axis:'rgba(111,222,203,.5)',vignette:'rgba(0,8,10,.30)'},
      studio:{base:'#202329',major:'rgba(196,204,215,.16)',minor:'rgba(162,170,181,.08)',axis:'rgba(224,229,237,.5)',vignette:'rgba(0,0,0,.18)'},
      'high-contrast':{base:'#000000',major:'rgba(255,255,255,.38)',minor:'rgba(255,255,255,.16)',axis:'rgba(255,255,255,.85)',vignette:'rgba(0,0,0,0)'},
      forest:{base:'#07140e',major:'rgba(101,185,139,.20)',minor:'rgba(66,137,101,.085)',axis:'rgba(135,229,173,.46)',vignette:'rgba(0,0,0,.34)'},
      crimson:{base:'#190d1a',major:'rgba(220,107,145,.20)',minor:'rgba(137,64,103,.085)',axis:'rgba(255,153,189,.48)',vignette:'rgba(0,0,0,.34)'},
      twilight:{base:'#17172a',major:'rgba(156,145,214,.22)',minor:'rgba(102,96,161,.09)',axis:'rgba(205,183,255,.53)',vignette:'rgba(0,0,0,.32)'},
      obsidian:{base:'#090b10',major:'rgba(132,146,165,.20)',minor:'rgba(84,96,113,.09)',axis:'rgba(181,198,220,.48)',vignette:'rgba(0,0,0,.45)'},
      moonlit:{base:'#101d30',major:'rgba(124,174,224,.22)',minor:'rgba(68,113,164,.09)',axis:'rgba(194,225,255,.53)',vignette:'rgba(0,0,8,.32)'},
      copper:{base:'#201a18',major:'rgba(204,143,98,.22)',minor:'rgba(124,82,58,.10)',axis:'rgba(245,190,142,.52)',vignette:'rgba(0,0,0,.32)'},
      nebula:{base:'#100d24',major:'rgba(165,119,218,.22)',minor:'rgba(97,67,153,.09)',axis:'rgba(219,178,255,.52)',vignette:'rgba(0,0,0,.38)'},
      slate:{base:'#171d24',major:'rgba(157,174,193,.20)',minor:'rgba(93,111,132,.09)',axis:'rgba(208,221,236,.5)',vignette:'rgba(0,0,0,.28)'},
      moonstone:{base:'#18212c',major:'rgba(135,198,210,.2)',minor:'rgba(79,128,146,.085)',axis:'rgba(204,246,252,.50)',vignette:'rgba(0,0,0,.28)'},
      'volcanic-glass':{base:'#190f13',major:'rgba(203,79,65,.23)',minor:'rgba(107,48,50,.095)',axis:'rgba(255,150,107,.5)',vignette:'rgba(0,0,0,.42)'},
      'deep-forest':{base:'#091710',major:'rgba(92,155,117,.21)',minor:'rgba(45,92,66,.085)',axis:'rgba(151,214,167,.48)',vignette:'rgba(0,0,0,.38)'}
    })[visualSettings.backgroundPreset] || {base:'#111315',major:'rgba(151,158,166,.15)',minor:'rgba(120,127,135,.075)',axis:'rgba(170,186,198,.42)',vignette:'rgba(0,0,0,.24)'};
    ctx.fillStyle = stageStyle.base;
    ctx.fillRect(0,0,w,h);
    if(['deep-space','nebula','moonstone'].includes(visualSettings.backgroundPreset) && visualSettings.particleDensity>0){
      ctx.save();ctx.globalAlpha=.18+visualSettings.particleDensity/620;ctx.fillStyle=visualSettings.backgroundPreset==='moonstone'?'#d3faff':visualSettings.backgroundPreset==='nebula'?'#dfc4ff':'#d6d0ff';
      const count=Math.min(80,Math.round(visualSettings.particleDensity*adaptiveGraphics.particleScale*.8));
      for(let i=0;i<count;i++){const sx=stableNoise(i,11)*w,sy=stableNoise(i,12)*h*.85,rr=.45+stableNoise(i,13)*1.1;ctx.beginPath();ctx.arc(sx,sy,rr,0,Math.PI*2);ctx.fill();}
      ctx.restore();
    }
    const major = niceGridStep(56 / Math.max(MIN_SCENE_SCALE, scale));
    const minor = major / 4;
    const left=t.wx(0),right=t.wx(w),top=t.wy(0),bottom=t.wy(h);
    const minX=Math.floor(left/minor),maxX=Math.ceil(right/minor);
    const minY=Math.floor(bottom/minor),maxY=Math.ceil(top/minor);
    ctx.save();
    if(showGrid){
      ctx.save();ctx.globalAlpha=Math.max(0,Math.min(1,visualSettings.gridOpacity/100));
      ctx.lineWidth=1;
      for(let i=minX;i<=maxX && i-minX<320;i++){
        const worldX=i*minor, sx=Math.round(t.px(worldX))+.5;
        const isMajor=Math.abs(worldX/major-Math.round(worldX/major))<1e-5;
        ctx.strokeStyle=isMajor?stageStyle.major:stageStyle.minor;
        ctx.beginPath();ctx.moveTo(sx,0);ctx.lineTo(sx,h);ctx.stroke();
      }
      for(let i=minY;i<=maxY && i-minY<320;i++){
        const worldY=i*minor, sy=Math.round(t.py(worldY))+.5;
        const isMajor=Math.abs(worldY/major-Math.round(worldY/major))<1e-5;
        ctx.strokeStyle=isMajor?stageStyle.major:stageStyle.minor;
        ctx.beginPath();ctx.moveTo(0,sy);ctx.lineTo(w,sy);ctx.stroke();
      }
      ctx.restore();
    }
    // A faint inset vignette gives depth while keeping the grid readable.
    const vignette=ctx.createRadialGradient(w*.5,h*.46,Math.min(w,h)*.12,w*.5,h*.46,Math.max(w,h)*.76);
    vignette.addColorStop(0,'rgba(0,0,0,0)');vignette.addColorStop(1,stageStyle.vignette);
    ctx.fillStyle=vignette;ctx.fillRect(0,0,w,h);
    if(showGrid){
      ctx.save();ctx.globalAlpha=Math.max(0,Math.min(1,visualSettings.gridOpacity/100));
      ctx.strokeStyle=stageStyle.axis;ctx.lineWidth=1.4;ctx.beginPath();ctx.moveTo(0,Math.round(t.py(0))+.5);ctx.lineTo(w,Math.round(t.py(0))+.5);ctx.stroke();
      ctx.beginPath();ctx.moveTo(Math.round(t.px(0))+.5,0);ctx.lineTo(Math.round(t.px(0))+.5,h);ctx.stroke();
      const barWorld=niceGridStep(96/Math.max(MIN_SCENE_SCALE,scale)),barPixels=Math.max(24,Math.min(110,barWorld*scale));
      ctx.globalAlpha=.8;ctx.strokeStyle=stageStyle.axis;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(w-24-barPixels,h-24);ctx.lineTo(w-24,h-24);ctx.moveTo(w-24-barPixels,h-28);ctx.lineTo(w-24-barPixels,h-20);ctx.moveTo(w-24,h-28);ctx.lineTo(w-24,h-20);ctx.stroke();
      ctx.font='10px var(--vscode-font-family, sans-serif)';ctx.textAlign='right';ctx.fillStyle=visualSettings.backgroundPreset==='vellum'?'#3e3020':'#c2d0db';ctx.fillText(`${Number(barWorld.toPrecision(3))}`,w-24,h-31);
      ctx.restore();
    }
    ctx.restore();
  }

  function drawWizard(x, y, height, dir, now, active = false, casting = false) {
    const h = height;
    const bob = reduceMotion ? 0 : Math.sin(now / 480) * 2;
    const castPulse = casting && !reduceMotion ? Math.sin(now / 58) * h * .018 : 0;
    ctx.save(); ctx.translate(x, y + bob); ctx.scale(dir, 1); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    if (casting) ctx.rotate(-.035);
    ctx.fillStyle = 'rgba(0,0,0,.42)'; ctx.beginPath(); ctx.ellipse(0, 0, h * .31, h * .055, 0, 0, Math.PI * 2); ctx.fill();
    // Robe, stitched seams and a moving hem.
    const robe = ctx.createLinearGradient(-h * .25, -h * .55, h * .24, 0);
    robe.addColorStop(0, '#252447'); robe.addColorStop(.42, '#5556a0'); robe.addColorStop(1, '#202238');
    ctx.fillStyle = robe; ctx.strokeStyle = '#171a34'; ctx.lineWidth = 1.5; ctx.beginPath();
    ctx.moveTo(-h * .1, -h * .57); ctx.quadraticCurveTo(-h * .27, -h * .48, -h * .25, -h * .25);
    ctx.lineTo(-h * .34, -.025 * h); ctx.quadraticCurveTo(0, h * .035, h * .34, -h * .025);
    ctx.lineTo(h * .23, -h * .31); ctx.quadraticCurveTo(h * .2, -h * .49, h * .1, -h * .57); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.strokeStyle = '#d9b76e'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(-h * .23, -h * .08);
    ctx.quadraticCurveTo(0, -h * .02, h * .23, -h * .08); ctx.moveTo(-h * .075, -h * .53); ctx.lineTo(-h * .02, -h * .12); ctx.stroke();
    // Shoes and belt.
    ctx.fillStyle = '#1a1b2e'; ctx.fillRect(-h * .22, -h * .055, h * .17, h * .065); ctx.fillRect(h * .04, -h * .055, h * .17, h * .065);
    ctx.strokeStyle = '#8f754b'; ctx.lineWidth = h * .018; ctx.beginPath(); ctx.moveTo(-h * .13, -h * .32); ctx.lineTo(h * .13, -h * .32); ctx.stroke();
    // Casting arm reaches forward; at rest it hangs closer to the robe.
    ctx.strokeStyle = '#4b4f8a'; ctx.lineWidth = h * .075; ctx.beginPath(); ctx.moveTo(h * .1, -h * .5);
    if (casting) { ctx.lineTo(h * .25, -h * .46 + castPulse); ctx.lineTo(h * .39, -h * .57 + castPulse); }
    else { ctx.lineTo(h * .24, -h * .39); ctx.lineTo(h * .29, -h * .55); }
    ctx.stroke();
    const handX = casting ? h * .39 : h * .29, handY = casting ? -h * .57 + castPulse : -h * .55;
    ctx.fillStyle = '#e1b18c'; ctx.beginPath(); ctx.arc(handX, handY, h * .035, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#9b7047'; ctx.lineWidth = h * .022; ctx.beginPath(); ctx.moveTo(handX, handY);
    ctx.lineTo(casting ? h * .62 : h * .48, casting ? -h * .69 + castPulse : -h * .76); ctx.stroke();
    if (active || casting) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.shadowColor = casting ? '#fff1b5' : '#9edfff';
      ctx.shadowBlur = casting ? 25 : 13; ctx.fillStyle = casting ? '#fff6d9' : '#d9f8ff'; ctx.beginPath();
      ctx.arc(casting ? h * .63 : h * .49, casting ? -h * .70 + castPulse : -h * .77, h * (casting ? .045 : .028), 0, Math.PI * 2); ctx.fill(); ctx.restore();
    }
    // Face, hair and pointed hat.
    ctx.fillStyle = '#d6a782'; ctx.fillRect(-h * .045, -h * .62, h * .09, h * .095);
    ctx.fillStyle = '#e4bd99'; ctx.beginPath(); ctx.ellipse(0, -h * .68, h * .105, h * .125, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#241b27'; ctx.beginPath(); ctx.arc(-h * .015, -h * .7, h * .012, 0, Math.PI * 2); ctx.arc(h * .055, -h * .7, h * .012, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#2a1d37'; ctx.beginPath(); ctx.moveTo(-h * .14, -h * .74); ctx.quadraticCurveTo(-h * .15, -h * .93, -h * .02, -h * 1.02); ctx.lineTo(h * .025, -h * .82); ctx.quadraticCurveTo(h * .12, -h * .87, h * .14, -h * .74); ctx.closePath(); ctx.fill();
    ctx.fillStyle = '#38315f'; ctx.beginPath(); ctx.moveTo(-h * .19, -h * .76); ctx.lineTo(h * .03, -h * 1.22); ctx.lineTo(h * .2, -h * .76); ctx.quadraticCurveTo(0, -h * .81, -h * .19, -h * .76); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = '#d3b36f'; ctx.lineWidth = h * .018; ctx.beginPath(); ctx.moveTo(-h * .19, -h * .76); ctx.quadraticCurveTo(0, -h * .8, h * .2, -h * .76); ctx.stroke();
    ctx.restore();
  }

  function magicIdentityColor(identity, fallback='#bba7f5') {
    const name=text(identity,'240').toLowerCase();
    const keys=Object.keys(palette).filter(key=>!['target','compound','being','material','puremana','thermalrelease'].includes(key));
    const direct=keys.sort((a,b)=>b.length-a.length).find(key=>new RegExp(`(^|[^a-z])${key.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}([^a-z]|$)`).test(name)||name.includes(key));
    return direct?palette[direct]:fallback;
  }
  function castColour(cast) {
    const name = text(cast && cast.spell || '').toLowerCase();
    return magicIdentityColor(name,'#bba7f5');
  }

  function drawCastingWeave(x, y, height, now, cast) {
    if (!cast || !showSpellForms) return;
    const handX = x + height * .63;
    const handY = y - height * .70;
    const color = castColour(cast);
    const radius = Math.max(15, Math.min(30, height * .19));
    if(visualSettings.showGlyphs)drawSpellSigil(handX, handY, radius, color, now, spellArchetype(text(cast.spell, 100).toLowerCase()), .96);
    drawSpellLabel(handX, handY - radius - 8, cast.spell, color);
    ctx.save(); ctx.translate(handX, handY); ctx.globalCompositeOperation = 'lighter';
    ctx.strokeStyle = color; ctx.globalAlpha = .72; ctx.lineWidth = 1.1;
    const p = reduceMotion ? 0 : now / 700;
    for (let i = 0; i < 3; i++) {
      const a = p + i * Math.PI * 2 / 3, rr = radius * (1.17 + .13 * Math.sin(p * .8 + i));
      ctx.beginPath(); ctx.arc(Math.cos(a) * rr * .74, Math.sin(a) * rr * .74, Math.max(2.2, radius * .11), 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); ctx.lineTo(Math.cos(a + .16) * rr * .78, Math.sin(a + .16) * rr * .78); ctx.stroke();
    }
    ctx.restore();
  }

  function drawHumanoid(x, y, height, now, selected = false, color = '#6d8f9b', motion = null) {
    const h = height, moving = Boolean(motion && motion.moving && !reduceMotion);
    const gait = moving ? Math.sin(now / 82) * h * .055 : 0;
    const breathe = reduceMotion ? 0 : Math.sin(now / 620) * 1.1;
    ctx.save(); ctx.translate(x, y + breathe); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    if (moving) ctx.rotate(-Math.max(-.06, Math.min(.06, safeNumber(motion.dx) * .012)));
    ctx.fillStyle = 'rgba(0,0,0,.40)'; ctx.beginPath(); ctx.ellipse(0, 0, h * .27, h * .045, 0, 0, Math.PI * 2); ctx.fill();
    // Knees and feet alternate in opposition, making movement legible at scene zoom.
    ctx.strokeStyle = '#343a40'; ctx.lineWidth = h * .075; ctx.beginPath();
    ctx.moveTo(-h * .075, -h * .25); ctx.lineTo(-h * .10 + gait * .48, -h * .14);
    ctx.lineTo(-h * .10 + gait, -h * .035); ctx.moveTo(h * .075, -h * .25);
    ctx.lineTo(h * .10 - gait * .48, -h * .14); ctx.lineTo(h * .10 - gait, -h * .035); ctx.stroke();
    ctx.strokeStyle = '#20262b'; ctx.lineWidth = h * .065; ctx.beginPath();
    ctx.moveTo(-h * .10 + gait, -h * .035); ctx.lineTo(-h * .20 + gait, -h * .015);
    ctx.moveTo(h * .10 - gait, -h * .035); ctx.lineTo(h * .20 - gait, -h * .015); ctx.stroke();
    const shirt = ctx.createLinearGradient(-h * .17, 0, h * .17, 0);
    shirt.addColorStop(0, blendHex(color, '#171c22', .45)); shirt.addColorStop(.5, color); shirt.addColorStop(1, blendHex(color, '#e5f1f4', .25));
    ctx.fillStyle = shirt; ctx.strokeStyle = blendHex(color, '#111820', .55); ctx.lineWidth = 1.3; ctx.beginPath();
    ctx.moveTo(-h * .11, -h * .59); ctx.lineTo(h * .11, -h * .59); ctx.lineTo(h * .16, -h * .29);
    ctx.lineTo(h * .10, -h * .23); ctx.lineTo(-h * .10, -h * .23); ctx.lineTo(-h * .16, -h * .29); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.strokeStyle = blendHex(color, '#1c2228', .28); ctx.lineWidth = h * .065; ctx.beginPath();
    ctx.moveTo(-h * .12, -h * .53); ctx.lineTo(-h * .22 - gait * .55, -h * .35); ctx.lineTo(-h * .19 - gait, -h * .24);
    ctx.moveTo(h * .12, -h * .53); ctx.lineTo(h * .21 + gait * .55, -h * .37); ctx.lineTo(h * .18 + gait, -h * .25); ctx.stroke();
    ctx.fillStyle = '#b98d70'; ctx.fillRect(-h * .035, -h * .65, h * .07, h * .09);
    ctx.fillStyle = '#d6aa89'; ctx.beginPath(); ctx.ellipse(0, -h * .70, h * .095, h * .115, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#24252a'; ctx.beginPath(); ctx.arc(-h * .032, -h * .715, h * .009, 0, Math.PI * 2); ctx.arc(h * .032, -h * .715, h * .009, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#342820'; ctx.beginPath(); ctx.arc(0, -h * .755, h * .095, Math.PI, Math.PI * 2); ctx.lineTo(h * .085, -h * .69); ctx.lineTo(-h * .085, -h * .69); ctx.closePath(); ctx.fill();
    if (selected) { ctx.strokeStyle = 'rgba(236,220,176,.88)'; ctx.lineWidth = 1.6; ctx.setLineDash([5, 4]); ctx.beginPath(); ctx.ellipse(0, -h * .40, h * .31, h * .51, 0, 0, Math.PI * 2); ctx.stroke(); ctx.setLineDash([]); }
    ctx.restore();
  }

  function drawDragon(x,y,r,color,now) {
    const beat=reduceMotion?0:Math.sin(now/190)*r*.10;ctx.save();ctx.translate(x,y);ctx.lineJoin='round';ctx.lineCap='round';ctx.fillStyle=color+'45';ctx.strokeStyle=color;ctx.lineWidth=Math.max(1.5,r*.07);
    ctx.beginPath();ctx.ellipse(-r*.08,-r*.05,r*.62,r*.34,-.08,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(-r*.12,-r*.18);ctx.quadraticCurveTo(-r*.78,-r*.82+beat,-r*.92,-r*.44+beat);ctx.lineTo(-r*.36,-r*.03);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(r*.02,-r*.18);ctx.quadraticCurveTo(r*.38,-r*.94-beat,r*.72,-r*.52-beat);ctx.lineTo(r*.36,-r*.02);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(r*.35,-r*.14);ctx.lineTo(r*.72,-r*.30);ctx.lineTo(r*.88,-r*.22);ctx.lineTo(r*.72,-r*.06);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(-r*.48,r*.02);ctx.quadraticCurveTo(-r*.92,r*.42,-r*1.12,r*.15);ctx.stroke();
    ctx.fillStyle='#f3d77c';ctx.beginPath();ctx.arc(r*.72,-r*.25,Math.max(1.8,r*.045),0,Math.PI*2);ctx.fill();ctx.restore();
  }

  function drawEasternDragon(x,y,r,color,now) {
    const undulate=reduceMotion?0:Math.sin(now/240)*r*.06;
    ctx.save();ctx.translate(x,y);ctx.lineCap='round';ctx.lineJoin='round';
    ctx.strokeStyle=color;ctx.fillStyle=color+'45';ctx.lineWidth=Math.max(1.5,r*.075);
    // Long serpentine body, whiskers, antlers and small cloud-like limbs.
    ctx.beginPath();ctx.moveTo(-r*.95,r*.15);ctx.bezierCurveTo(-r*.7,-r*.42+undulate,-r*.15,r*.38-undulate,r*.08,-r*.04);ctx.bezierCurveTo(r*.32,-r*.42+undulate,r*.52,-r*.36,r*.56,-r*.12);ctx.stroke();
    ctx.beginPath();ctx.ellipse(r*.54,-r*.15,r*.24,r*.18,-.2,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(r*.65,-r*.25);ctx.lineTo(r*.85,-r*.33);ctx.lineTo(r*.98,-r*.24);ctx.lineTo(r*.82,-r*.16);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(r*.45,-r*.28);ctx.quadraticCurveTo(r*.35,-r*.52,r*.23,-r*.46);ctx.moveTo(r*.58,-r*.3);ctx.quadraticCurveTo(r*.66,-r*.52,r*.75,-r*.44);ctx.stroke();
    ctx.beginPath();ctx.moveTo(r*.73,-r*.12);ctx.quadraticCurveTo(r*.93,-r*.06,r*.99,r*.04);ctx.moveTo(r*.72,-r*.1);ctx.quadraticCurveTo(r*.9,-r*.12,r*.97,-r*.19);ctx.stroke();
    for(const side of [-1,1]){ctx.beginPath();ctx.moveTo(-r*.08,side*r*.05);ctx.lineTo(-r*.18,side*r*.27);ctx.lineTo(-r*.04,side*r*.29);ctx.stroke();}
    ctx.fillStyle='#f5df91';ctx.beginPath();ctx.arc(r*.63,-r*.19,Math.max(1.5,r*.04),0,Math.PI*2);ctx.fill();ctx.restore();
  }

  function drawMinotaur(x,y,height,now,selected=false,color='#82705b',motion=null) {
    const h=height,moving=Boolean(motion&&motion.moving&&!reduceMotion),gait=moving?Math.sin(now/85)*h*.045:0,breathe=reduceMotion?0:Math.sin(now/580)*h*.006;
    ctx.save();ctx.translate(x,y+breathe);ctx.lineCap='round';ctx.lineJoin='round';
    ctx.fillStyle='rgba(0,0,0,.42)';ctx.beginPath();ctx.ellipse(0,0,h*.34,h*.05,0,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle='#453a31';ctx.lineWidth=h*.105;ctx.beginPath();ctx.moveTo(-h*.11,-h*.25);ctx.lineTo(-h*.13+gait,-h*.04);ctx.moveTo(h*.11,-h*.25);ctx.lineTo(h*.14-gait,-h*.04);ctx.stroke();
    ctx.strokeStyle='#4a3b31';ctx.lineWidth=h*.095;ctx.beginPath();ctx.moveTo(-h*.11,-h*.48);ctx.lineTo(-h*.25,-h*.32);ctx.moveTo(h*.11,-h*.48);ctx.lineTo(h*.24,-h*.33);ctx.stroke();
    const fur=ctx.createLinearGradient(-h*.2,-h*.5,h*.2,-h*.22);fur.addColorStop(0,blendHex(color,'#24201d',.35));fur.addColorStop(.5,color);fur.addColorStop(1,blendHex(color,'#d0b18b',.25));
    ctx.fillStyle=fur;ctx.strokeStyle='#392e27';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(-h*.17,-h*.59);ctx.lineTo(h*.17,-h*.59);ctx.lineTo(h*.21,-h*.28);ctx.lineTo(h*.11,-h*.22);ctx.lineTo(-h*.11,-h*.22);ctx.lineTo(-h*.21,-h*.28);ctx.closePath();ctx.fill();ctx.stroke();
    // Bull-shaped head with muzzle, ears and sweeping horns.
    ctx.fillStyle='#b98d70';ctx.beginPath();ctx.ellipse(0,-h*.69,h*.12,h*.13,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle=fur;ctx.beginPath();ctx.ellipse(0,-h*.67,h*.12,h*.13,0,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(-h*.07,-h*.75);ctx.quadraticCurveTo(-h*.25,-h*.87,-h*.30,-h*.73);ctx.quadraticCurveTo(-h*.19,-h*.76,-h*.12,-h*.65);ctx.moveTo(h*.07,-h*.75);ctx.quadraticCurveTo(h*.25,-h*.87,h*.30,-h*.73);ctx.quadraticCurveTo(h*.19,-h*.76,h*.12,-h*.65);ctx.stroke();
    ctx.fillStyle='#d9c7a7';ctx.beginPath();ctx.moveTo(-h*.08,-h*.76);ctx.quadraticCurveTo(-h*.2,-h*.92,-h*.24,-h*.98);ctx.moveTo(h*.08,-h*.76);ctx.quadraticCurveTo(h*.2,-h*.92,h*.24,-h*.98);ctx.stroke();
    ctx.fillStyle='#302722';ctx.beginPath();ctx.arc(-h*.045,-h*.7,h*.012,0,Math.PI*2);ctx.arc(h*.045,-h*.7,h*.012,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#d0a58b';ctx.beginPath();ctx.ellipse(0,-h*.62,h*.065,h*.045,0,0,Math.PI*2);ctx.fill();
    if(selected){ctx.strokeStyle='rgba(236,220,176,.9)';ctx.lineWidth=1.6;ctx.setLineDash([5,4]);ctx.beginPath();ctx.ellipse(0,-h*.43,h*.35,h*.53,0,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);}
    ctx.restore();
  }

  function drawDinosaur(x,y,r,color,now,speciesName="",motion=null) {
    const moving=Boolean(motion&&motion.moving&&!reduceMotion),gait=moving?Math.sin(now/95)*r*.1:0,bob=reduceMotion?0:Math.sin(now/(moving?130:320))*r*.025;ctx.save();ctx.translate(x,y+bob);ctx.lineJoin='round';ctx.lineCap='round';ctx.fillStyle=color+'55';ctx.strokeStyle=color;ctx.lineWidth=Math.max(1.5,r*.065);
    ctx.beginPath();ctx.ellipse(0,-r*.12,r*.66,r*.38,-.08,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(-r*.45,-r*.13);ctx.lineTo(-r*1.0,-r*.36);ctx.lineTo(-r*1.28,-r*.27);ctx.stroke();
    ctx.beginPath();ctx.moveTo(r*.32,-r*.34);ctx.lineTo(r*.58,-r*.62);ctx.lineTo(r*.86,-r*.56);ctx.lineTo(r*.73,-r*.36);ctx.closePath();ctx.fill();ctx.stroke();
    for(let i=0;i<3;i++){const xx=-r*.15+i*r*.22;ctx.beginPath();ctx.moveTo(xx,-r*.42);ctx.lineTo(xx+r*.08,-r*.61-(i%2)*r*.08);ctx.lineTo(xx+r*.15,-r*.40);ctx.closePath();ctx.fill();ctx.stroke();}
    speciesName=String(speciesName||'').toLowerCase();
    if(/triceratops/.test(speciesName)){ctx.beginPath();ctx.moveTo(r*.55,-r*.48);ctx.lineTo(r*.67,-r*.74);ctx.moveTo(r*.68,-r*.45);ctx.lineTo(r*.83,-r*.67);ctx.stroke();ctx.beginPath();ctx.ellipse(r*.48,-r*.42,r*.18,r*.22,0,0,Math.PI*2);ctx.stroke();}
    else if(/stegosaur/.test(speciesName)){for(let i=0;i<5;i++){const xx=-r*.38+i*r*.19;ctx.beginPath();ctx.moveTo(xx,-r*.38);ctx.lineTo(xx+r*.07,-r*.68-(i%2)*r*.06);ctx.lineTo(xx+r*.16,-r*.35);ctx.closePath();ctx.fill();ctx.stroke();}}
    else if(/velociraptor|raptor/.test(speciesName)){ctx.beginPath();ctx.moveTo(r*.26,r*.12);ctx.lineTo(r*.39,r*.32);ctx.lineTo(r*.33,r*.39);ctx.moveTo(r*.01,r*.12);ctx.lineTo(r*.13,r*.31);ctx.stroke();}
    ctx.strokeStyle=blendHex(color,'#202020',.28);ctx.lineWidth=r*.09;ctx.beginPath();ctx.moveTo(-r*.3,r*.06);ctx.lineTo(-r*.34+gait,r*.38);ctx.moveTo(r*.20,r*.08);ctx.lineTo(r*.25-gait,r*.38);ctx.stroke();ctx.fillStyle='#f6df82';ctx.beginPath();ctx.arc(r*.73,-r*.51,Math.max(1.5,r*.04),0,Math.PI*2);ctx.fill();ctx.restore();
  }

  function drawAnt(x,y,r,color,now) {
    const sway=reduceMotion?0:Math.sin(now/140)*r*.05;ctx.save();ctx.translate(x,y);ctx.strokeStyle=color;ctx.fillStyle=color+'68';ctx.lineWidth=Math.max(1.4,r*.075);ctx.lineCap='round';
    for(let side of [-1,1])for(let i=0;i<3;i++){const sx=side*r*.12, sy=-r*.02+i*r*.12;ctx.beginPath();ctx.moveTo(sx,sy);ctx.lineTo(sx+side*r*(.35+i*.06),sy+r*.22+sway);ctx.lineTo(sx+side*r*(.48+i*.07),sy+r*.42);ctx.stroke();}
    ctx.beginPath();ctx.ellipse(-r*.28,0,r*.26,r*.20,-.2,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.ellipse(0,-r*.02,r*.15,r*.14,0,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.beginPath();ctx.arc(r*.27,-r*.12,r*.16,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(r*.29,-r*.25);ctx.quadraticCurveTo(r*.38,-r*.52,r*.48,-r*.44);ctx.moveTo(r*.20,-r*.25);ctx.quadraticCurveTo(r*.13,-r*.51,r*.05,-r*.44);ctx.stroke();ctx.fillStyle='#f8e5a2';ctx.beginPath();ctx.arc(r*.32,-r*.14,Math.max(1.2,r*.025),0,Math.PI*2);ctx.fill();ctx.restore();
  }

  function drawSlime(x,y,r,color,now,motion=null) {
    const moving=Boolean(motion&&motion.moving&&!reduceMotion),wobble=reduceMotion?1:1+Math.sin(now/(moving?95:210))*(moving?.13:.055);ctx.save();ctx.translate(x,y);ctx.fillStyle=color+'70';ctx.strokeStyle=color;ctx.lineWidth=Math.max(1.5,r*.065);ctx.beginPath();ctx.moveTo(-r*.78,0);ctx.quadraticCurveTo(-r*.86,-r*.7,-r*.25,-r*.68*wobble);ctx.quadraticCurveTo(r*.2,-r*.88*wobble,r*.67,-r*.50);ctx.quadraticCurveTo(r*.94,-r*.22,r*.78,0);ctx.quadraticCurveTo(r*.35,r*.11,-r*.25,r*.08);ctx.closePath();ctx.fill();ctx.stroke();ctx.fillStyle='#f5f4dd';ctx.beginPath();ctx.ellipse(-r*.20,-r*.34,r*.10,r*.13,0,0,Math.PI*2);ctx.ellipse(r*.20,-r*.34,r*.10,r*.13,0,0,Math.PI*2);ctx.fill();ctx.fillStyle='#27313b';ctx.beginPath();ctx.arc(-r*.18,-r*.33,r*.04,0,Math.PI*2);ctx.arc(r*.22,-r*.33,r*.04,0,Math.PI*2);ctx.fill();ctx.restore();
  }

  function drawKnight(x,y,height,now,selected=false,motion=null) {
    const h=height, moving=Boolean(motion&&motion.moving&&!reduceMotion), gait=moving?Math.sin(now/82)*h*.055:0, breathe=reduceMotion?0:Math.sin(now/650)*1.2;
    ctx.save();ctx.translate(x,y+breathe);ctx.lineCap='round';ctx.lineJoin='round';
    ctx.fillStyle='rgba(0,0,0,.45)';ctx.beginPath();ctx.ellipse(0,0,h*.32,h*.055,0,0,Math.PI*2);ctx.fill();
    // Legs and greaves.
    ctx.strokeStyle='#6f7c91';ctx.lineWidth=h*.09;ctx.beginPath();ctx.moveTo(-h*.1,-h*.25);ctx.lineTo(-h*.13+gait*.45,-h*.14);ctx.lineTo(-h*.13+gait,-h*.04);ctx.moveTo(h*.1,-h*.25);ctx.lineTo(h*.13-gait*.45,-h*.14);ctx.lineTo(h*.13-gait,-h*.04);ctx.stroke();
    ctx.strokeStyle='#222b3f';ctx.lineWidth=h*.08;ctx.beginPath();ctx.moveTo(-h*.13+gait,-h*.04);ctx.lineTo(-h*.23+gait,-h*.02);ctx.moveTo(h*.13-gait,-h*.04);ctx.lineTo(h*.23-gait,-h*.02);ctx.stroke();
    // Body armour, layered plates and shoulder guards.
    const metal=ctx.createLinearGradient(-h*.25,0,h*.25,0);metal.addColorStop(0,'#59677d');metal.addColorStop(.45,'#d0d8e1');metal.addColorStop(1,'#64718a');
    ctx.fillStyle=metal;ctx.strokeStyle='#30394d';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(-h*.16,-h*.58);ctx.lineTo(h*.16,-h*.58);ctx.lineTo(h*.19,-h*.27);ctx.lineTo(0,-h*.2);ctx.lineTo(-h*.19,-h*.27);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.strokeStyle='#a77d43';ctx.lineWidth=h*.025;ctx.beginPath();ctx.moveTo(0,-h*.55);ctx.lineTo(0,-h*.24);ctx.moveTo(-h*.12,-h*.42);ctx.lineTo(h*.12,-h*.42);ctx.stroke();
    for(const s of [-1,1]){ctx.fillStyle='#a5b1c2';ctx.beginPath();ctx.ellipse(s*h*.19,-h*.53,h*.095,h*.07,s*.15,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.strokeStyle='#6a7488';ctx.lineWidth=h*.06;ctx.beginPath();ctx.moveTo(s*h*.19,-h*.48);ctx.lineTo(s*h*.25,-h*.32);ctx.stroke();}
    // Helmet and narrow visor.
    ctx.fillStyle=metal;ctx.beginPath();ctx.moveTo(-h*.12,-h*.66);ctx.quadraticCurveTo(-h*.1,-h*.82,0,-h*.83);ctx.quadraticCurveTo(h*.12,-h*.82,h*.12,-h*.66);ctx.lineTo(h*.07,-h*.59);ctx.lineTo(-h*.07,-h*.59);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.fillStyle='#20283a';ctx.fillRect(-h*.065,-h*.72,h*.13,h*.025);ctx.fillStyle='#ffcf78';ctx.fillRect(-h*.035,-h*.71,h*.07,h*.012);
    // Sword, angled safely down at rest.
    ctx.strokeStyle='#8c9bb2';ctx.lineWidth=h*.025;ctx.beginPath();ctx.moveTo(h*.25,-h*.34);ctx.lineTo(h*.34,-h*.07);ctx.stroke();ctx.strokeStyle='#caa96b';ctx.lineWidth=h*.035;ctx.beginPath();ctx.moveTo(h*.2,-h*.32);ctx.lineTo(h*.3,-h*.36);ctx.stroke();
    if(selected){ctx.strokeStyle='rgba(255,222,158,.9)';ctx.lineWidth=2;ctx.setLineDash([5,5]);ctx.beginPath();ctx.ellipse(0,-h*.43,h*.4,h*.57,0,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);}
    ctx.restore();
  }

  function drawBird(x,y,r,color,now){
    const wing=reduceMotion?0:Math.sin(now/95)*r*.55;ctx.save();ctx.translate(x,y);ctx.fillStyle=color+'36';ctx.strokeStyle=color;ctx.lineWidth=Math.max(1.4,r*.075);
    ctx.beginPath();ctx.ellipse(0,0,r*.58,r*.3,-.1,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(-r*.15,-r*.05);ctx.quadraticCurveTo(-r*.7,-r*.8+wing,-r*.85,-r*.2+wing*.25);ctx.quadraticCurveTo(-r*.45,r*.05,-r*.15,r*.1);ctx.closePath();ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.moveTo(r*.25,-r*.08);ctx.lineTo(r*.62,-r*.18);ctx.lineTo(r*.39,r*.02);ctx.closePath();ctx.fillStyle='#e9be72';ctx.fill();
    ctx.beginPath();ctx.arc(r*.34,-r*.17,Math.max(1.3,r*.055),0,Math.PI*2);ctx.fillStyle='#f7f4e8';ctx.fill();ctx.beginPath();ctx.arc(r*.36,-r*.17,Math.max(.8,r*.03),0,Math.PI*2);ctx.fillStyle='#142033';ctx.fill();ctx.restore();
  }
  function drawSerpent(x,y,r,color,now){
    ctx.save();ctx.lineCap='round';ctx.lineJoin='round';ctx.strokeStyle=color;ctx.lineWidth=Math.max(5,r*.5);ctx.beginPath();
    for(let i=0;i<=16;i++){const u=i/16,px=x-r+u*r*2,py=y+Math.sin(u*Math.PI*2.5+now/460)*r*.42;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.stroke();
    ctx.strokeStyle=blendHex(color,'#ffffff',.45);ctx.lineWidth=Math.max(1,r*.11);ctx.beginPath();for(let i=0;i<=16;i++){const u=i/16,px=x-r+u*r*2,py=y+Math.sin(u*Math.PI*2.5+now/460)*r*.42-r*.08;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.stroke();
    ctx.fillStyle=color;ctx.beginPath();ctx.ellipse(x+r*.88,y+Math.sin(2.5*Math.PI+now/460)*r*.42,r*.25,r*.18,0,0,Math.PI*2);ctx.fill();ctx.fillStyle='#f4dc75';ctx.beginPath();ctx.arc(x+r*.98,y-r*.06,r*.045,0,Math.PI*2);ctx.fill();ctx.restore();
  }
  function drawBeast(x,y,r,color,now,golem){
    const bob=reduceMotion?0:Math.sin(now/340)*r*.035;ctx.save();ctx.translate(x,y+bob);ctx.fillStyle=color+'38';ctx.strokeStyle=color;ctx.lineWidth=Math.max(1.5,r*.07);ctx.lineJoin='round';
    ctx.beginPath();ctx.ellipse(0,-r*.05,r*.75,r*.48,0,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.beginPath();ctx.ellipse(r*.47,-r*.38,r*.37,r*.33,-.25,0,Math.PI*2);ctx.fill();ctx.stroke();
    if(golem){for(let i=0;i<4;i++){const px=-r*.42+i*r*.28;ctx.beginPath();ctx.moveTo(px,-r*.35);ctx.lineTo(px+r*.13,-r*.68-(i%2)*r*.1);ctx.lineTo(px+r*.27,-r*.37);ctx.closePath();ctx.fill();ctx.stroke();}}else{ctx.beginPath();ctx.moveTo(r*.3,-r*.6);ctx.lineTo(r*.24,-r*.93);ctx.lineTo(r*.48,-r*.65);ctx.moveTo(r*.56,-r*.6);ctx.lineTo(r*.69,-r*.89);ctx.lineTo(r*.76,-r*.54);ctx.stroke();}
    for(let i=0;i<4;i++){const lx=-r*.48+i*r*.3;ctx.beginPath();ctx.moveTo(lx,-r*.02);ctx.lineTo(lx-r*.03,r*.28);ctx.stroke();}
    ctx.fillStyle=golem?'#ffb75d':'#f4e3ae';ctx.beginPath();ctx.arc(r*.57,-r*.42,Math.max(1.8,r*.055),0,Math.PI*2);ctx.fill();ctx.restore();
  }

  function drawFacing(x, y, motion, draw) {
    if (!motion || (!motion.moving || motion.dx >= 0) && !(motion.impact > 0)) { draw(); return; }
    ctx.save();
    // A recorded collision briefly rocks a character away from the contact.
    // This is presentation only: the runtime's collision result stays unchanged.
    if (motion.impact > 0) {
      const lean = (motion.impactSign || 1) * Math.min(.12, motion.impact * .105);
      ctx.translate(x, y); ctx.rotate(-lean); ctx.translate(-x, -y);
    }
    // Mirror about the character's feet/centre without changing its world position.
    if (motion.moving && motion.dx < 0) { ctx.translate(x * 2, 0); ctx.scale(-1, 1); }
    draw(); ctx.restore();
  }

  function drawWorldObject(e, x, y, r, color, now, motion = null) {
    const kind = text(e.kind || '').toLowerCase(), name = text(e.name || '').toLowerCase();
    const material = text(e.material || e.element || '').toLowerCase(), form = text(e.visual_form || '').toLowerCase();
    const visualScale = Math.max(.05, Math.min(20, safeNumber(e.visual_scale, 1)));
    const actorHeight = Math.max(64, Math.min(300, (canvas.clientHeight || 600) * .34 * visualScale));
    const creature = `${form} ${name} ${text(e.species || e.species_name || e.anatomy_species_id || e.body_form || e.body_plan || '')}`.toLowerCase();
    const actorLike=kind==='being'||Boolean(e.summoned||e.undead||e.living)||/dragon|drake|wyvern|dinosaur|raptor|minotaur|ant_worker|ant_soldier|ant_queen|slime|ooze|serpent|humanoid|knight|bird|beast|golem/.test(creature);
    if(visualSettings.showActorAuras&&actorLike){
      const auraColor=fxColor('aura',color);
      const auraR=Math.max(r*2.05,Math.min(140,actorHeight*.43)),aura=ctx.createRadialGradient(x,y-auraR*.48,1,x,y-auraR*.48,auraR);
      aura.addColorStop(0,auraColor+Math.round(Math.min(.19,.10+visualSettings.glow*.035)*255).toString(16).padStart(2,'0'));aura.addColorStop(.54,auraColor+'18');aura.addColorStop(1,auraColor+'00');
      ctx.save();ctx.globalAlpha=Math.min(.9,visualSettings.glow*.48);ctx.fillStyle=aura;ctx.beginPath();ctx.ellipse(x,y-auraR*.45,auraR*.68,auraR,0,0,Math.PI*2);ctx.fill();
      if(visualSettings.glow>.3){ctx.strokeStyle=auraColor;ctx.globalAlpha*=.45;ctx.lineWidth=visualSettings.highContrastEdges?2.4:1.2;ctx.beginPath();ctx.ellipse(x,y-auraR*.45,auraR*.58,auraR*.85,0,Math.PI*.08,Math.PI*1.92);ctx.stroke();}ctx.restore();
    }
    if (/eastern dragon|oriental dragon|long dragon|shenlong|lung dragon/.test(creature)) { drawFacing(x,y,motion,()=>drawEasternDragon(x,y,r*1.18,color,now)); return; }
    if (/dragon|drake|wyvern|western dragon/.test(creature)) { drawFacing(x,y,motion,()=>drawDragon(x,y,r*1.18,color,now)); return; }
    if (/tyrannosaur|t-rex|triceratops|velociraptor|stegosaur|dinosaur|raptor/.test(creature)) { drawFacing(x,y,motion,()=>drawDinosaur(x,y,r*1.18,color,now,creature)); return; }
    if (/ant_worker|ant_soldier|ant_queen|\bant\b/.test(creature)) { drawFacing(x,y,motion,()=>drawAnt(x,y,r*1.2,color,now)); return; }
    if (/slime|ooze/.test(creature)) { drawSlime(x,y,r*1.15,color,now,motion); return; }
    if (/minotaur|bull-headed/.test(creature)) { drawFacing(x,y,motion,()=>drawMinotaur(x,y,actorHeight*.94,now,selectedId===e.id,color,motion)); return; }
    if (form==='humanoid') { drawFacing(x,y,motion,()=>drawHumanoid(x,y,actorHeight,now,selectedId===e.id,color,motion)); return; }
    if (form==='knight') { drawFacing(x,y,motion,()=>drawKnight(x,y,actorHeight,now,selectedId===e.id,motion)); return; }
    if (form==='bird') { drawFacing(x,y,motion,()=>drawBird(x,y,r,color,now)); return; }
    if (form==='serpent') { drawFacing(x,y,motion,()=>drawSerpent(x,y,r,color,now)); return; }
    if (form==='beast'||form==='golem') { drawFacing(x,y,motion,()=>drawBeast(x,y,r,color,now,form==='golem')); return; }
    const personLike = kind==='target' && (material==='target' || /knight|npc|dummy|guard|enemy|training|wizard|person/.test(name));
    if (personLike) { drawFacing(x,y,motion,()=>drawHumanoid(x,y,Math.max(82,Math.min(180,(canvas.clientHeight||600)*.30)),now,selectedId===e.id,color,motion)); return; }
    if (kind==='being'||e.summoned||e.undead) { drawFacing(x,y,motion,()=>drawHumanoid(x,y,actorHeight,now,selectedId===e.id,color,motion)); return; }
    const energy = Math.max(0, Math.min(1, safeNumber(e.energy_glow)));
    const pulse = reduceMotion ? 1 : .92 + .08 * Math.sin(now/400 + (safeNumber(e.id)%9));
    const glow = ctx.createRadialGradient(x,y,1,x,y,r*(1.8+energy)); glow.addColorStop(0,color+(energy>.2?'aa':'66')); glow.addColorStop(.45,color+'30'); glow.addColorStop(1,color+'00');
    ctx.fillStyle=glow;ctx.beginPath();ctx.arc(x,y,r*(1.8+energy),0,Math.PI*2);ctx.fill();
    ctx.save();if(previewIds.has(e.id))ctx.setLineDash([6,5]);drawEntityShape(e.shape,x,y,r*pulse,color);ctx.restore();
    if(/steel|iron|metal|gold|silver|copper|bronze|brass|aluminium|aluminum/.test(material)){
      ctx.save();ctx.globalAlpha=.7;ctx.strokeStyle=blendHex(color,'#ffffff',.65);ctx.lineWidth=Math.max(1,r*.08);ctx.beginPath();ctx.moveTo(x-r*.45,y-r*.35);ctx.lineTo(x+r*.32,y-r*.45);ctx.moveTo(x-r*.22,y+r*.22);ctx.lineTo(x+r*.44,y+r*.12);ctx.stroke();ctx.restore();
    }else if(/wood|oak|pine|bark/.test(material)){
      ctx.save();ctx.strokeStyle=blendHex(color,'#42301e',.42);ctx.lineWidth=Math.max(1,r*.07);for(let i=-1;i<=1;i++){ctx.beginPath();ctx.moveTo(x-r*.4,y+i*r*.23);ctx.quadraticCurveTo(x,y+i*r*.12,x+r*.4,y+i*r*.23);ctx.stroke();}ctx.restore();
    }else if(/glass|crystal|ice/.test(material)){
      ctx.save();ctx.strokeStyle='rgba(240,251,255,.86)';ctx.lineWidth=Math.max(1,r*.06);ctx.beginPath();ctx.moveTo(x-r*.45,y-r*.32);ctx.lineTo(x-r*.08,y-r*.56);ctx.lineTo(x+r*.25,y-r*.2);ctx.stroke();ctx.restore();
    }
    if(energy>.1){ctx.save();ctx.globalAlpha=.5;ctx.strokeStyle=blendHex(color,'#ffffff',energy);ctx.lineWidth=1.3;ctx.beginPath();ctx.arc(x,y,r*1.25,now/900,now/900+Math.PI*(.65+energy));ctx.stroke();ctx.restore();}
  }

  function trackProgress(track, position) {
    const points = track && Array.isArray(track.points) ? track.points : [];
    if (points.length < 2 || position < points[0].index || position > track.endIndex) return null;
    return Math.max(0, Math.min(1, (position - points[0].index) / Math.max(1, track.endIndex - points[0].index)));
  }

  // Sample the actual positions recorded by the runtime. Do not draw a line from
  // spawn to final position: forces, steering, gravity and collisions can all turn it.
  function sampleMotionTrack(track, playback) {
    const points = track && Array.isArray(track.points) ? track.points : [];
    if (points.length < 2 || playback < points[0].index || playback > track.endIndex) return null;
    // Binary-search the sample interval: long steering records must not turn
    // each frame into a full scan for every moving projectile.
    let low=1,high=points.length;
    while(low<high){const mid=(low+high)>>1;if(points[mid].index<playback)low=mid+1;else high=mid;}
    const rightIndex=Math.min(points.length-1,low);
    const leftIndex=Math.max(0,rightIndex-1);
    const left=points[leftIndex],right=points[rightIndex];
    const span = Math.max(1e-6, right.index - left.index);
    const indexFraction = Math.max(0, Math.min(1, (playback - left.index) / span));
    const elapsed = right.time - left.time;
    // Log entries are not evenly spaced in simulated time. When timestamps
    // differ, use them for the interpolation; use the log index only for
    // same-time records so instantaneous state changes stay deterministic.
    const currentTime = playbackTimeAt(playback);
    const f = elapsed > 1e-6
      ? Math.max(0, Math.min(1, (currentTime - left.time) / elapsed))
      : indexFraction;
    const x = left.x + (right.x - left.x) * f;
    const y = left.y + (right.y - left.y) * f;
    let dx = right.x - left.x, dy = right.y - left.y;
    let distance = Math.hypot(dx, dy);
    if (distance < 1e-8 && left !== points[0]) {
      const prev = points[Math.max(0, leftIndex - 1)];
      dx = right.x - prev.x; dy = right.y - prev.y; distance = Math.hypot(dx, dy);
    }
    const speed = distance / (elapsed > 1e-6 ? elapsed : span * .02);
    const sampledTime = left.time + (right.time - left.time) * f;
    return { x, y, dx, dy, angle: Math.atan2(-dy, dx), speed, moving: distance > .002,
      fraction: f, time: sampledTime, segmentStart: left, segmentEnd: right, distance };
  }

  function drawTrajectoryTrail(track, sample, playback, t, color, radius, simplified = false) {
    if (!sample || visualSettings.trailStyle === 'none' || !visualSettings.showTrajectory || !track.points || track.points.length < 2 || visualSettings.effectIntensity <= 0) return;
    const trailSteps=Math.max(4,Math.min(60,visualSettings.trailLength));
    const startIndex=Math.max(track.points[0].index,playback-trailSteps);
    const points=track.points;
    // Binary search avoids scanning every retained point for every projectile.
    let lo=0,hi=points.length;
    while(lo<hi){const mid=(lo+hi)>>1;if(points[mid].index<startIndex)lo=mid+1;else hi=mid;}
    const first=Math.max(0,lo-1),visible=[];
    for(let i=first;i<points.length&&points[i].index<playback;i++)visible.push(points[i]);
    const last=visible[visible.length-1];
    if(!last||last.index<playback)visible.push({index:playback,x:sample.x,y:sample.y});
    if(visible.length<2)return;
    ctx.save();ctx.lineCap='round';ctx.lineJoin='round';
    const strength=Math.max(0,Math.min(1.5,visualSettings.effectIntensity));
    if (simplified) {
      // Low-cost fallback preserves the path for every visible spell when a
      // dense scene exhausts the budget for elaborate trail treatments.
      const pointLimit = 14;
      const stride = Math.max(1, Math.ceil(visible.length / pointLimit));
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = .5 * strength;
      ctx.strokeStyle = color;
      ctx.lineWidth = Math.max(1.15, radius * .085);
      ctx.beginPath();
      for (let i = 0; i < visible.length; i += stride) {
        const point = visible[i], x = t.px(point.x), y = t.py(point.y);
        i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
      }
      const end = visible[visible.length - 1];
      ctx.lineTo(t.px(end.x), t.py(end.y));
      ctx.stroke();
      ctx.globalAlpha = .18 * strength;
      ctx.lineWidth = Math.max(2.2, radius * .19);
      ctx.stroke();
      ctx.restore();
      return;
    }
    if(visualSettings.trailStyle==='dashed'){
      ctx.setLineDash([7,5]);ctx.strokeStyle=color;ctx.globalAlpha=.65*strength;ctx.lineWidth=Math.max(1,radius*.12);ctx.beginPath();
      visible.forEach((point,i)=>{const x=t.px(point.x),y=t.py(point.y);i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();ctx.setLineDash([]);
    } else if(visualSettings.trailStyle==='lightning'){
      const screen=visible.map(point=>({x:t.px(point.x),y:t.py(point.y)}));
      ctx.globalCompositeOperation='lighter';ctx.strokeStyle=color;ctx.shadowColor=color;ctx.shadowBlur=Math.min(10,visualSettings.glow*4);ctx.globalAlpha=.83*strength;ctx.lineWidth=Math.max(1.5,radius*.16);ctx.beginPath();ctx.moveTo(screen[0].x,screen[0].y);
      for(let i=1;i<screen.length;i++){const a=screen[i-1],b=screen[i],dx=b.x-a.x,dy=b.y-a.y,len=Math.max(1,Math.hypot(dx,dy)),jitter=(stableNoise(i,track.startIndex||0)-.5)*Math.min(12,radius*.75);ctx.lineTo((a.x+b.x)/2-dy/len*jitter,(a.y+b.y)/2+dx/len*jitter);ctx.lineTo(b.x,b.y);}ctx.stroke();
      ctx.shadowBlur=0;ctx.strokeStyle='#f5fbff';ctx.globalAlpha=.62*strength;ctx.lineWidth=Math.max(.8,radius*.055);ctx.stroke();
    } else if(visualSettings.trailStyle==='helix'){
      const screen=visible.map(point=>({x:t.px(point.x),y:t.py(point.y)}));
      for(const lane of [-1,1]){ctx.strokeStyle=lane<0?color:blendHex(color,'#ffffff',.62);ctx.globalAlpha=(lane<0?.48:.72)*strength;ctx.lineWidth=Math.max(1,radius*.09);ctx.beginPath();
        screen.forEach((point,i)=>{const prev=screen[Math.max(0,i-1)],next=screen[Math.min(screen.length-1,i+1)],dx=next.x-prev.x,dy=next.y-prev.y,len=Math.max(1,Math.hypot(dx,dy)),phase=(reduceMotion?0:playback*.42)+i*.78,lift=Math.sin(phase+lane*Math.PI/2)*Math.min(7,radius*.55);const x=point.x-dy/len*lift,y=point.y+dx/len*lift;i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();}
    } else if(visualSettings.trailStyle==='comet' || visualSettings.trailStyle==='afterimage'){
      const screen=visible.map(point=>({x:t.px(point.x),y:t.py(point.y)}));
      const copies=visualSettings.trailStyle==='afterimage'?3:1;
      for(let copy=copies-1;copy>=0;copy--){const shift=copy*radius*.09;for(let i=1;i<screen.length;i++){const a=screen[i-1],b=screen[i],fresh=i/(screen.length-1),width=Math.max(.8,radius*(visualSettings.trailStyle==='comet'?.03+fresh*.23:.045+fresh*.09));ctx.strokeStyle=copy?blendHex(color,'#ffffff',.28*copy):color;ctx.globalAlpha=(visualSettings.trailStyle==='comet'?.10+fresh*.78:.15+fresh*.42)*strength/(copy+1);ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(a.x-shift,a.y+shift*.4);ctx.lineTo(b.x-shift,b.y+shift*.4);ctx.stroke();}}
    } else if(visualSettings.trailStyle==='zigzag'){
      const screen=visible.map(point=>({x:t.px(point.x),y:t.py(point.y)}));ctx.strokeStyle=color;ctx.globalCompositeOperation='lighter';ctx.globalAlpha=.8*strength;ctx.lineWidth=Math.max(1.3,radius*.11);ctx.beginPath();ctx.moveTo(screen[0].x,screen[0].y);for(let i=1;i<screen.length;i++){const a=screen[i-1],b=screen[i],dx=b.x-a.x,dy=b.y-a.y,len=Math.max(1,Math.hypot(dx,dy)),side=(i%2?1:-1)*Math.min(radius*.42,len*.24);ctx.lineTo((a.x+b.x)/2-dy/len*side,(a.y+b.y)/2+dx/len*side);ctx.lineTo(b.x,b.y);}ctx.stroke();
    } else if(visualSettings.trailStyle==='mist'){
      const hop=Math.max(1,Math.floor(visible.length/Math.max(5,Math.round(visualSettings.particleDensity*adaptiveGraphics.particleScale/8))));ctx.fillStyle=color;for(let i=1;i<visible.length;i+=hop){const point=visible[i],age=(playback-point.index)/Math.max(1,playback-startIndex),rr=radius*(.12+(.7-age)*.16);ctx.globalAlpha=.06+(1-age)*.15;ctx.beginPath();ctx.ellipse(t.px(point.x),t.py(point.y),rr*1.4,rr,.45,0,Math.PI*2);ctx.fill();}
    } else if(visualSettings.trailStyle==='rune-chain'){
      const screen=visible.map(point=>({x:t.px(point.x),y:t.py(point.y)}));ctx.globalCompositeOperation='lighter';for(let i=0;i<screen.length;i+=Math.max(1,Math.round(7-(visualSettings.particleDensity*adaptiveGraphics.particleScale)/20))){const p=screen[i];ctx.globalAlpha=.18+(i/screen.length)*.58;ctx.strokeStyle=color;ctx.lineWidth=Math.max(1,radius*.055);ctx.save();ctx.translate(p.x,p.y);ctx.rotate((reduceMotion?0:playback*.05)+i*.3);const rr=Math.max(2,radius*.16);ctx.strokeRect(-rr,-rr,rr*2,rr*2);ctx.restore();}
    } else {
      for(let i=1;i<visible.length;i++){
        const a=visible[i-1],b=visible[i],age=(playback-b.index)/Math.max(1,playback-startIndex),fresh=1-age;
        if(visualSettings.trailStyle==='segmented' && i%2===0)continue;
        const xx=t.px(a.x),yy=t.py(a.y),bx=t.px(b.x),by=t.py(b.y);
        const taper=visualSettings.trailStyle==='ribbon'?1.65:visualSettings.trailStyle==='sparks'?.8:1;
        ctx.globalAlpha=(.08+fresh*(visualSettings.trailStyle==='ribbon'?.42:.34))*strength;
        ctx.strokeStyle=color;ctx.lineWidth=Math.max(1,radius*(.10+fresh*.20)*taper);
        if(visualSettings.trailStyle==='ribbon'){
          ctx.shadowColor=color;ctx.shadowBlur=Math.min(8,visualSettings.glow*3);
        }
        ctx.beginPath();ctx.moveTo(xx,yy);ctx.lineTo(bx,by);ctx.stroke();ctx.shadowBlur=0;
        if(visualSettings.trailStyle==='sparks'&&visualSettings.showParticles&&visualSettings.particleDensity>0&&i%Math.max(1,Math.round(9-(visualSettings.particleDensity*adaptiveGraphics.particleScale)/15))===0){
          const r=Math.max(1.1,radius*.08)*(0.7+fresh*.6);ctx.globalAlpha=.65*strength*visualSettings.particleDensity/100;ctx.fillStyle=blendHex(color,'#ffffff',.45);ctx.beginPath();ctx.moveTo(bx,by-r);ctx.lineTo(bx+r,by);ctx.lineTo(bx,by+r);ctx.lineTo(bx-r,by);ctx.closePath();ctx.fill();
        }
      }
    }
    ctx.restore();
  }

  function drawArcaneGlyphs(radius, color, now, count = 8) {
    ctx.save();
    ctx.strokeStyle = color; ctx.lineWidth = Math.max(1, radius * .018); ctx.globalAlpha = .86;
    ctx.beginPath(); ctx.arc(0, 0, radius, 0, Math.PI * 2); ctx.stroke();
    ctx.globalAlpha = .5; ctx.setLineDash([Math.max(2, radius * .08), Math.max(3, radius * .12)]);
    ctx.beginPath(); ctx.arc(0, 0, radius * .78, -now / 1700, Math.PI * 2 - now / 1700); ctx.stroke(); ctx.setLineDash([]);
    for (let i = 0; i < count; i++) {
      const a = Math.PI * 2 * i / count + now / 2200;
      const cs = Math.cos(a), sn = Math.sin(a);
      ctx.beginPath(); ctx.moveTo(cs * radius * .82, sn * radius * .82);
      ctx.lineTo(cs * radius * 1.08, sn * radius * 1.08);
      ctx.lineTo(Math.cos(a + .13) * radius * .94, Math.sin(a + .13) * radius * .94);
      ctx.closePath(); ctx.stroke();
    }
    ctx.restore();
  }

  // The spell has a silhouette and internal structure of its own. This is not
  // a generic impact flare: it is the moving spell body, drawn around the actual
  // recorded entity position and oriented to its sampled direction of travel.
  function spellArchetype(identity, explicitShape = '') {
    // Prefer explicit recorded geometry, then the spell's intended form, and
    // only then its element. This prevents names such as "ice shield" or
    // "fire beam" from being mistaken for a generic ice shard or fire orb.
    const shape = text(explicitShape, 40).toLowerCase().replace(/[ _-]/g, '');
    if (['orb','sphere','ball','fireball','wisp','seed'].includes(shape)) return 'orb';
    if (['lance','spear','arrow','dart','needle','missile'].includes(shape)) return 'lance';
    if (['bolt'].includes(shape)) return 'bolt';
    if (['wave','surge','stream','ribbon'].includes(shape)) return 'wave';
    if (['shield','barrier','dome','field'].includes(shape)) return 'field';
    if (['ring','disc','disk','halo'].includes(shape)) return 'ring';
    if (['construct','sigil','glyph','rune'].includes(shape)) return 'sigil';
    const name = text(identity, 240).toLowerCase();
    if (/shield|barrier|ward|dome|\bfield\b/.test(name)) return 'field';
    if (/\bring\b|\bdisc\b|\bdisk\b|\bhalo\b|\bnova\b/.test(name)) return 'ring';
    if (/beam|ray|laser|lance|spear|arrow|dart|needle|bolt|missile|projectile/.test(name)) return /bolt|lightning|thunder|electric|volt|storm/.test(name) ? 'bolt' : 'lance';
    if (/construct|sigil|seal|rune|glyph|summon|reanimat|reviv|transform|transfigur|manifestation/.test(name)) return 'sigil';
    if (/wave|surge|stream|ribbon|tide|torrent|current/.test(name)) return 'wave';
    if (/orb|sphere|fireball|sunball|emberball|wisp|seed|plasma ball/.test(name)) return 'orb';
    if (/lightning|thunder|electric|volt|storm/.test(name)) return 'bolt';
    if (/ice|frost|crystal|glacier/.test(name)) return 'lance';
    if (/water|aqua|wind|air|gale/.test(name)) return 'wave';
    if (/fire|flame|ember|thermal|plasma|lava/.test(name)) return 'orb';
    if (/death|necrom|shadow|void|soul|bone|dark/.test(name)) return 'sigil';
    if (/life|nature|wood|vine|plant|healing/.test(name)) return 'orb';
    if (/earth|rock|stone|sand|boulder|mud|metal|steel|iron/.test(name)) return 'lance';
    return 'sigil';
  }

  function drawSimpleSpellBody(radius, identity, color, explicitShape = '') {
    const r = Math.max(5, Math.min(36, radius));
    const form = spellArchetype(identity, explicitShape);
    ctx.save();
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha *= Math.min(1.2, visualSettings.effectIntensity);
    ctx.fillStyle = color + '55';
    ctx.strokeStyle = fxColor('outline', visualSettings.highContrastEdges ? '#ffffff' : color);
    ctx.lineWidth = visualSettings.highContrastEdges ? 1.8 : 1.25;
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.beginPath();
    if (form === 'orb') {
      ctx.arc(0, 0, r * .9, 0, Math.PI * 2);
    } else if (form === 'lance') {
      ctx.moveTo(r * 1.6, 0); ctx.lineTo(r * .45, -r * .48); ctx.lineTo(-r, -r * .25);
      ctx.lineTo(-r * .48, 0); ctx.lineTo(-r, r * .25); ctx.lineTo(r * .45, r * .48); ctx.closePath();
    } else if (form === 'bolt') {
      ctx.moveTo(-r, -r * .12); ctx.lineTo(-r * .28, -r * .36); ctx.lineTo(r * .05, r * .02);
      ctx.lineTo(r * .8, -r * .15); ctx.lineTo(r * .34, r * .28); ctx.lineTo(r * .08, r * .55); ctx.lineTo(-r * .12, r * .14); ctx.closePath();
    } else if (form === 'ring') {
      ctx.ellipse(0, 0, r, r * .56, 0, 0, Math.PI * 2);
    } else if (form === 'field') {
      for (let i = 0; i < 8; i++) { const a = -Math.PI / 8 + i * Math.PI / 4, px = Math.cos(a) * r, py = Math.sin(a) * r * .8; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
      ctx.closePath();
    } else if (form === 'wave') {
      ctx.moveTo(-r * 1.3, -r * .28); ctx.quadraticCurveTo(0, -r * .8, r * 1.35, 0);
      ctx.quadraticCurveTo(0, r * .8, -r * 1.3, r * .28); ctx.closePath();
    } else {
      ctx.moveTo(0, -r); ctx.lineTo(r * .8, 0); ctx.lineTo(0, r); ctx.lineTo(-r * .8, 0); ctx.closePath();
    }
    ctx.fill(); ctx.stroke();
    ctx.globalAlpha *= .9;
    ctx.fillStyle = '#ffffff';
    ctx.beginPath(); ctx.arc(0, 0, Math.max(1.4, r * .12), 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  function drawSpellBody(radius, identity, color, now, explicitShape = '') {
    const r = Math.max(7, Math.min(40, radius));
    const form = spellArchetype(identity, explicitShape);
    const pulse = reduceMotion ? 0 : Math.sin(now / 92) * .055;
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.globalAlpha *= .94*Math.min(1.5,visualSettings.effectIntensity);
    ctx.shadowColor=color;ctx.shadowBlur=Math.min(9,visualSettings.glow*4);

    if (form === 'orb') {
      // A contained core with longitudinal/latitudinal bands reads as a solid
      // magical projectile rather than a collection of particles.
      const shell = ctx.createRadialGradient(-r * .22, -r * .2, 1, 0, 0, r * 1.23);
      shell.addColorStop(0, '#ffffff'); shell.addColorStop(.22, color); shell.addColorStop(.72, color + 'aa'); shell.addColorStop(1, color + '00');
      ctx.fillStyle = shell; ctx.beginPath(); ctx.arc(0, 0, r * (1.08 + pulse), 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#f7ffff'; ctx.globalAlpha *= .84; ctx.lineWidth = Math.max(1.1, r * .075);
      ctx.beginPath(); ctx.ellipse(0, 0, r * .92, r * .48, 0, -.04, Math.PI * 1.96); ctx.stroke();
      ctx.beginPath(); ctx.ellipse(0, 0, r * .42, r * .96, 0, -.08, Math.PI * 1.93); ctx.stroke();
      ctx.globalAlpha *= .75; ctx.strokeStyle = color; ctx.lineWidth = Math.max(1, r * .05);
      ctx.beginPath(); ctx.ellipse(0, 0, r * 1.43, r * .55, reduceMotion ? -.34 : now / 720, Math.PI * 1.05, Math.PI * 2.82); ctx.stroke();
      ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(-r * .22, -r * .24, Math.max(1.4, r * .13), 0, Math.PI * 2); ctx.fill();
    } else if (form === 'lance') {
      // The head has a clear forward point, a solid shaft and inset spine.
      ctx.fillStyle = color + '66'; ctx.strokeStyle = color; ctx.lineWidth = Math.max(1.3, r * .075);
      ctx.beginPath(); ctx.moveTo(r * 1.95, 0); ctx.lineTo(r * .48, -r * .54); ctx.lineTo(-r * .98, -r * .30);
      ctx.lineTo(-r * .48, 0); ctx.lineTo(-r * .98, r * .30); ctx.lineTo(r * .48, r * .54); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.strokeStyle = '#f5ffff'; ctx.lineWidth = Math.max(1, r * .055); ctx.beginPath(); ctx.moveTo(r * 1.52, 0); ctx.lineTo(-r * .62, 0); ctx.stroke();
      ctx.globalAlpha *= .78; ctx.strokeStyle = color; ctx.lineWidth = Math.max(1, r * .04);
      for (let i = 0; i < 3; i++) { const xx = -r * (.25 + i * .44); ctx.beginPath(); ctx.moveTo(xx, -r * .24); ctx.lineTo(xx - r * .16, 0); ctx.lineTo(xx, r * .24); ctx.stroke(); }
    } else if (form === 'bolt') {
      // A branching lightning body is an angular, forked shape with a bright core.
      const pts = [[-1.45,-.10],[-.68,-.27],[-.26,-.76],[.02,-.24],[.58,-.58],[.30,-.08],[1.43,0],[.43,.20],[.12,.71],[-.12,.23],[-.67,.43],[-.40,.08]];
      ctx.fillStyle = color + '77'; ctx.strokeStyle = color; ctx.lineWidth = Math.max(1.2, r * .06); ctx.beginPath();
      pts.forEach(([px,py],i)=>{const xx=px*r,yy=py*r;i?ctx.lineTo(xx,yy):ctx.moveTo(xx,yy);});ctx.closePath();ctx.fill();ctx.stroke();
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = Math.max(1.2, r * .07); ctx.beginPath(); ctx.moveTo(-r * .95, 0); ctx.lineTo(-r * .25, -r * .13); ctx.lineTo(r * .08, r * .12); ctx.lineTo(r * .65, -.02 * r); ctx.stroke();
    } else if (form === 'wave') {
      // Parallel ribbon bands retain a continuous body even when the camera zooms out.
      for (let lane = 0; lane < 3; lane++) {
        const f = lane - 1, phase = reduceMotion ? 0 : Math.sin(now / 105 + lane * 2) * r * .09;
        ctx.strokeStyle = lane === 1 ? '#f5ffff' : color; ctx.globalAlpha *= lane === 1 ? .95 : .7;
        ctx.lineWidth = Math.max(1.5, r * (lane === 1 ? .11 : .16)); ctx.beginPath();
        ctx.moveTo(-r * 1.8, f * r * .18); ctx.bezierCurveTo(-r * .9, -f * r * .7 + phase, r * .12, f * r * .78 - phase, r * 1.55, 0); ctx.stroke();
      }
      ctx.globalAlpha *= .9; ctx.fillStyle = color; ctx.beginPath(); ctx.moveTo(r * 1.85, 0); ctx.lineTo(r * .85, -r * .34); ctx.lineTo(r * 1.05, 0); ctx.lineTo(r * .85, r * .34); ctx.closePath(); ctx.fill();
    } else if (form === 'field') {
      // This is the traveling/held spell boundary itself, not a bloom at impact.
      ctx.strokeStyle = color; ctx.lineWidth = Math.max(1.4, r * .075); ctx.globalAlpha *= .9;
      ctx.beginPath();
      for (let i = 0; i < 8; i++) { const a = -Math.PI / 8 + i * Math.PI / 4, xx = Math.cos(a) * r * 1.12, yy = Math.sin(a) * r * .9; i ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
      ctx.closePath(); ctx.stroke();
      ctx.globalAlpha *= .7; ctx.beginPath(); ctx.ellipse(0, 0, r * .72, r * .35, 0, 0, Math.PI * 2); ctx.stroke();
      for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + (reduceMotion ? 0 : now / 1600); ctx.beginPath(); ctx.arc(Math.cos(a) * r * .77, Math.sin(a) * r * .56, Math.max(1.5, r * .09), 0, Math.PI * 2); ctx.stroke(); }
    } else if (form === 'ring') {
      ctx.strokeStyle = color; ctx.lineWidth = Math.max(1.5, r * .09); ctx.beginPath(); ctx.ellipse(0, 0, r * 1.18, r * .66, 0, 0, Math.PI * 2); ctx.stroke();
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = Math.max(1, r * .04); ctx.beginPath(); ctx.ellipse(0, 0, r * .75, r * .4, 0, 0, Math.PI * 2); ctx.stroke();
      for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; ctx.beginPath(); ctx.moveTo(Math.cos(a) * r * .8, Math.sin(a) * r * .45); ctx.lineTo(Math.cos(a) * r * 1.24, Math.sin(a) * r * .7); ctx.stroke(); }
    } else {
      ctx.strokeStyle = color; ctx.lineWidth = Math.max(1.2, r * .06); ctx.beginPath();
      for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 + Math.PI / 8, rr = i % 2 ? r * .68 : r * 1.18; const xx = Math.cos(a) * rr, yy = Math.sin(a) * rr; i ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
      ctx.closePath(); ctx.stroke();
      ctx.strokeStyle = '#f7ffff'; ctx.globalAlpha *= .85; ctx.lineWidth = Math.max(1, r * .04); ctx.beginPath(); ctx.moveTo(-r * .45, 0); ctx.lineTo(0, -r * .45); ctx.lineTo(r * .45, 0); ctx.lineTo(0, r * .45); ctx.closePath(); ctx.stroke();
      ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(0, 0, Math.max(1.4, r * .12), 0, Math.PI * 2); ctx.fill();
    }
    // Accent and outline are distinct controls from the spell-core hue. The
    // procedural contour is bounded to the current body form and adds no world entities.
    ctx.shadowBlur=0;
    const accent = fxColor('accent', blendHex(color,'#ffffff',.66));
    ctx.save(); ctx.globalCompositeOperation='source-over'; ctx.globalAlpha=.74; ctx.strokeStyle=accent; ctx.lineWidth=Math.max(1,r*.028); ctx.setLineDash(visualSettings.spellStyle==='minimal'?[]:[Math.max(2,r*.09),Math.max(2,r*.07)]);
    if(form==='orb'){ctx.beginPath();ctx.ellipse(0,0,r*.82,r*.38,reduceMotion?0:now/1200,0,Math.PI*2);ctx.stroke();}
    else if(form==='lance'){ctx.beginPath();ctx.moveTo(-r*.7,0);ctx.lineTo(r*1.6,0);ctx.stroke();}
    else if(form==='bolt'){ctx.beginPath();ctx.moveTo(-r*1.1,r*.1);ctx.lineTo(-r*.42,-r*.08);ctx.lineTo(-r*.06,r*.17);ctx.lineTo(r*.38,-r*.04);ctx.lineTo(r*1.04,0);ctx.stroke();}
    else if(form==='wave'){ctx.beginPath();ctx.moveTo(-r*1.55,0);ctx.bezierCurveTo(-r*.8,-r*.3,r*.45,r*.3,r*1.5,0);ctx.stroke();}
    else if(form==='field'){ctx.beginPath();for(let i=0;i<8;i++){const a=-Math.PI/8+i*Math.PI/4,px=Math.cos(a)*r*1.03,py=Math.sin(a)*r*.82;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.closePath();ctx.stroke();}
    else if(form==='ring'){ctx.beginPath();ctx.ellipse(0,0,r*1.03,r*.57,0,0,Math.PI*2);ctx.stroke();}
    else {ctx.beginPath();ctx.moveTo(0,-r*.9);ctx.lineTo(r*.9,0);ctx.lineTo(0,r*.9);ctx.lineTo(-r*.9,0);ctx.closePath();ctx.stroke();}
    ctx.setLineDash([]); ctx.restore();
    if(visualSettings.fxColors.outline || visualSettings.highContrastEdges){
      ctx.save();ctx.globalCompositeOperation='source-over';ctx.globalAlpha=.95;ctx.strokeStyle=fxColor('outline','#11131a');ctx.lineWidth=Math.max(1.5,r*(visualSettings.highContrastEdges?.105:.065));
      if(form==='orb'){ctx.beginPath();ctx.arc(0,0,r*1.08,0,Math.PI*2);ctx.stroke();}
      else if(form==='lance'){ctx.beginPath();ctx.moveTo(r*1.95,0);ctx.lineTo(r*.48,-r*.54);ctx.lineTo(-r*.98,-r*.3);ctx.lineTo(-r*.48,0);ctx.lineTo(-r*.98,r*.3);ctx.lineTo(r*.48,r*.54);ctx.closePath();ctx.stroke();}
      else if(form==='ring'){ctx.beginPath();ctx.ellipse(0,0,r*1.18,r*.66,0,0,Math.PI*2);ctx.stroke();}
      else if(form==='field'){ctx.beginPath();for(let i=0;i<8;i++){const a=-Math.PI/8+i*Math.PI/4,px=Math.cos(a)*r*1.12,py=Math.sin(a)*r*.9;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.closePath();ctx.stroke();}
      else {ctx.beginPath();ctx.moveTo(-r*1.05,0);ctx.lineTo(-r*.4,-r*.45);ctx.lineTo(r*.35,-r*.45);ctx.lineTo(r*1.05,0);ctx.lineTo(r*.35,r*.45);ctx.lineTo(-r*.4,r*.45);ctx.closePath();ctx.stroke();}
      ctx.restore();
    }
    // Optional art-direction overlays stay attached to the spell body; they do
    // not change trajectory, mass, energy, contacts or spell outcomes.
    if(visualSettings.spellStyle==='crystalline'){
      ctx.globalAlpha*=.8;ctx.strokeStyle=blendHex(color,'#ffffff',.65);ctx.lineWidth=Math.max(1,r*.035);
      ctx.beginPath();ctx.moveTo(-r*.62,-r*.12);ctx.lineTo(-r*.08,-r*.72);ctx.lineTo(r*.25,-r*.18);ctx.lineTo(r*.72,r*.12);ctx.moveTo(-r*.08,-r*.72);ctx.lineTo(r*.05,r*.42);ctx.lineTo(-r*.45,r*.55);ctx.moveTo(r*.25,-r*.18);ctx.lineTo(r*.05,r*.42);ctx.stroke();
    }else if(visualSettings.spellStyle==='rune-tech'){
      ctx.globalAlpha*=.8;ctx.strokeStyle=color;ctx.lineWidth=Math.max(1,r*.035);ctx.setLineDash([r*.12,r*.1]);ctx.beginPath();ctx.ellipse(0,0,r*1.7,r*.64,reduceMotion?0:now/1800,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
      if(visualSettings.showParticles&&visualSettings.particleDensity*adaptiveGraphics.particleScale>20){for(let i=0;i<Math.max(1,Math.round(4*adaptiveGraphics.particleScale));i++){const a=i*Math.PI/2+(reduceMotion?0:now/950),d=r*1.64;ctx.fillStyle=blendHex(color,'#ffffff',.5);ctx.fillRect(Math.cos(a)*d-1.5,Math.sin(a)*d-1.5,3,3);}}
    }else if(visualSettings.spellStyle==='painterly'){
      ctx.globalAlpha*=.62;ctx.strokeStyle=blendHex(color,'#ffffff',.35);ctx.lineWidth=Math.max(1,r*.055);for(let i=0;i<3;i++){ctx.beginPath();ctx.moveTo(-r*(1.55-i*.22),r*(i-1)*.18);ctx.quadraticCurveTo(-r*.35,r*(i-1)*.32,r*(.6+i*.12),r*(i-1)*.1);ctx.stroke();}
    }else if(visualSettings.spellStyle==='holographic'){
      ctx.globalAlpha*=.72;ctx.strokeStyle='#dbfbff';ctx.lineWidth=Math.max(1,r*.025);ctx.setLineDash([r*.15,r*.08]);ctx.beginPath();ctx.ellipse(0,0,r*1.58,r*.84,0,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
    }else if(visualSettings.spellStyle==='astral'){
      ctx.globalAlpha*=.88;ctx.strokeStyle=blendHex(color,'#fff1ba',.35);ctx.lineWidth=Math.max(1,r*.03);ctx.beginPath();ctx.ellipse(0,0,r*1.7,r*.54,reduceMotion?0:now/900,0,Math.PI*2);ctx.ellipse(0,0,r*1.7,r*.54,reduceMotion?Math.PI/3:now/900+Math.PI/3,0,Math.PI*2);ctx.stroke();
      if(visualSettings.showParticles&&visualSettings.particleDensity*adaptiveGraphics.particleScale>10){for(let i=0;i<Math.max(1,Math.round(3*adaptiveGraphics.particleScale));i++){const a=now/780+i*Math.PI*2/3,d=r*1.7;ctx.fillStyle=blendHex(color,'#ffffff',.68);ctx.beginPath();ctx.arc(Math.cos(a)*d,Math.sin(a)*d,Math.max(1.4,r*.07),0,Math.PI*2);ctx.fill();}}
    }else if(visualSettings.spellStyle==='spectral'){
      ctx.globalAlpha*=.58;ctx.lineWidth=Math.max(1,r*.055);for(let i=0;i<4;i++){const off=(i-1.5)*r*.13;ctx.strokeStyle=blendHex(color,['#f7a5ff','#8deaff','#a7ffd7','#fff1ad'][i],.35);ctx.beginPath();ctx.ellipse(off,0,r*(form==='lance'?1.38:1.12),r*(form==='field'?.82:.52),off/r,0,Math.PI*2);ctx.stroke();}
    }else if(visualSettings.spellStyle==='fractured-glass'){
      ctx.globalAlpha*=.88;ctx.strokeStyle=fxColor('accent',blendHex(color,'#ffffff',.7));ctx.lineWidth=Math.max(1,r*.035);for(let i=0;i<6;i++){const a=i*Math.PI/3,rr=r*(.28+(i%2)*.18);ctx.beginPath();ctx.moveTo(Math.cos(a)*r*.1,Math.sin(a)*r*.1);ctx.lineTo(Math.cos(a+.6)*rr,Math.sin(a+.6)*rr);ctx.lineTo(Math.cos(a+1.7)*r*.74,Math.sin(a+1.7)*r*.74);ctx.stroke();}
    }else if(visualSettings.spellStyle==='ink-wash'){
      ctx.globalCompositeOperation='source-over';ctx.globalAlpha*=.24;ctx.strokeStyle=blendHex(color,'#10121a',.45);ctx.lineWidth=Math.max(2,r*.16);for(let i=0;i<3;i++){ctx.beginPath();ctx.ellipse((i-1)*r*.11,0,r*(1.28+i*.08),r*(.52+i*.07),i*.16,0,Math.PI*2);ctx.stroke();}
      ctx.globalAlpha=.82;ctx.strokeStyle=fxColor('accent',blendHex(color,'#fff2d5',.3));ctx.lineWidth=Math.max(1,r*.035);ctx.beginPath();ctx.moveTo(-r*1.15,r*.12);ctx.quadraticCurveTo(-r*.25,-r*.42,r*1.25,r*.04);ctx.stroke();
    }else if(visualSettings.spellStyle==='rune-circuit'){
      ctx.globalAlpha*=.9;ctx.strokeStyle=fxColor('accent',blendHex(color,'#b8fff2',.42));ctx.lineWidth=Math.max(1,r*.035);for(let i=0;i<4;i++){const yy=(i-1.5)*r*.21;ctx.beginPath();ctx.moveTo(-r*.8,yy);ctx.lineTo(-r*.45,yy);ctx.lineTo(-r*.3,yy-r*.13);ctx.lineTo(r*.18,yy-r*.13);ctx.lineTo(r*.36,yy);ctx.lineTo(r*.82,yy);ctx.stroke();ctx.beginPath();ctx.arc(-r*.3,yy-r*.13,Math.max(1.1,r*.045),0,Math.PI*2);ctx.arc(r*.36,yy,Math.max(1.1,r*.045),0,Math.PI*2);ctx.stroke();}
    }else if(visualSettings.spellStyle==='solarized'){
      ctx.globalAlpha*=.9;ctx.strokeStyle=fxColor('accent',blendHex(color,'#ffffff',.55));ctx.lineWidth=Math.max(1,r*.045);const spokes=12;for(let i=0;i<spokes;i++){const a=i*Math.PI*2/spokes,inner=r*.38,outer=r*(i%3===0?1.55:1.12);ctx.beginPath();ctx.moveTo(Math.cos(a)*inner,Math.sin(a)*inner);ctx.lineTo(Math.cos(a)*outer,Math.sin(a)*outer);ctx.stroke();}ctx.setLineDash([Math.max(2,r*.12),Math.max(2,r*.09)]);ctx.beginPath();ctx.ellipse(0,0,r*1.34,r*.77,0,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
    }
    if(visualSettings.spellStyle==='comic-ink'){
      ctx.globalAlpha=.96;ctx.globalCompositeOperation='source-over';ctx.strokeStyle='#15121b';ctx.lineWidth=Math.max(2.2,r*.12);ctx.stroke();
      ctx.strokeStyle=blendHex(color,'#ffffff',.35);ctx.lineWidth=Math.max(1.1,r*.045);ctx.beginPath();for(let i=0;i<5;i++){const yy=(i-2)*r*.19;ctx.moveTo(-r*.75,yy);ctx.lineTo(-r*.4,yy-r*.08);ctx.lineTo(-r*.05,yy);}ctx.stroke();
    }else if(visualSettings.spellStyle==='prismatic'){
      ctx.globalCompositeOperation='lighter';ctx.globalAlpha=.62;ctx.lineWidth=Math.max(1,r*.055);
      for(const [offset,shade] of [[-.1,'#ff6dbe'],[0,'#f9ffff'],[.1,'#65f3ff']]){ctx.strokeStyle=shade;ctx.beginPath();ctx.ellipse(offset*r,0,r*(form==='lance'?1.55:1.12),r*(form==='field'?.82:.48),offset,0,Math.PI*2);ctx.stroke();}
    }else if(visualSettings.spellStyle==='pixel-art'){
      ctx.globalCompositeOperation='source-over';ctx.globalAlpha=.94;ctx.shadowBlur=0;const unit=Math.max(2,Math.round(r*.11));ctx.fillStyle=blendHex(color,'#ffffff',.48);
      for(let i=-3;i<=3;i++){const width=(4-Math.abs(i))*unit;ctx.fillRect(Math.round(i*unit),Math.round(-width/2),unit,width);}
      ctx.strokeStyle='#10131a';ctx.lineWidth=Math.max(1.4,r*.06);ctx.strokeRect(-r*.64,-r*.64,r*1.28,r*1.28);
    }
    if(visualSettings.spellStyle!=='minimal'&&visualSettings.particleDensity>0){
      ctx.globalAlpha=.82*visualSettings.effectIntensity;ctx.strokeStyle=color;ctx.lineWidth=Math.max(1,r*.045);
      const anchors=visualSettings.showParticles?Math.max(2,Math.round(2+(visualSettings.particleDensity*adaptiveGraphics.particleScale)/35)):2;
      for(let i=0;i<anchors;i++){const a=Math.PI*2*i/anchors+(reduceMotion?0:now/1450),d=r*(visualSettings.spellStyle==='astral'?1.8:1.48);ctx.beginPath();ctx.arc(Math.cos(a)*d,Math.sin(a)*d,Math.max(1.2,r*.055),0,Math.PI*2);ctx.stroke();}
    }
    ctx.restore();
  }

  function drawSpellSigil(x, y, radius, color, now, archetype = 'sigil', opacity = 1) {
    color = fxColor('glyph', color);
    if(!visualSettings.showGlyphs||visualSettings.glyphStyle==='off'||visualSettings.effectIntensity<=0)return;
    const r = Math.max(12, Math.min(34, radius));
    ctx.save(); ctx.translate(x, y); ctx.globalAlpha *= opacity*Math.min(1.5,visualSettings.effectIntensity); ctx.globalCompositeOperation = 'lighter';
    const spin = reduceMotion ? 0 : now / 1900;
    ctx.strokeStyle = color; ctx.lineWidth = visualSettings.highContrastEdges?1.9:1.25;
    if(visualSettings.glyphStyle==='runic'){
      ctx.setLineDash([Math.max(2,r*.09),Math.max(3,r*.11)]);ctx.beginPath();ctx.arc(0,0,r*.92,spin,Math.PI*2+spin);ctx.stroke();ctx.setLineDash([]);
    }else if(visualSettings.glyphStyle==='geometric'){
      ctx.beginPath();for(let i=0;i<8;i++){const a=i*Math.PI/4-spin*.18,rr=r*(i%2?.82:1.02);i?ctx.lineTo(Math.cos(a)*rr,Math.sin(a)*rr):ctx.moveTo(Math.cos(a)*rr,Math.sin(a)*rr);}ctx.closePath();ctx.stroke();
    }else if(visualSettings.glyphStyle==='alchemical'){
      for(let i=0;i<3;i++){ctx.beginPath();ctx.arc(0,0,r*(.48+i*.2),spin*(i%2?-1:1),Math.PI*2+spin*(i%2?-1:1));ctx.stroke();}
    }else if(visualSettings.glyphStyle==='orbitals'){
      ctx.beginPath();ctx.ellipse(0,0,r*.98,r*.42,spin*.25,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.ellipse(0,0,r*.42,r*.98,-spin*.2,0,Math.PI*2);ctx.stroke();
    }else if(visualSettings.glyphStyle==='star-mandala'){
      ctx.beginPath();for(let i=0;i<24;i++){const a=i*Math.PI/12+spin*.12,rr=r*(i%2?.66:1.04);i?ctx.lineTo(Math.cos(a)*rr,Math.sin(a)*rr):ctx.moveTo(Math.cos(a)*rr,Math.sin(a)*rr);}ctx.closePath();ctx.stroke();
      for(let i=0;i<8;i++){const a=i*Math.PI/4-spin*.25;ctx.beginPath();ctx.arc(Math.cos(a)*r*.57,Math.sin(a)*r*.57,r*.22,0,Math.PI*2);ctx.stroke();}
    }else if(visualSettings.glyphStyle==='knotwork'){
      ctx.setLineDash([Math.max(2,r*.08),Math.max(2,r*.05)]);for(let i=0;i<3;i++){const a=i*Math.PI/3;ctx.beginPath();ctx.ellipse(0,0,r*.78,r*.42,a,0,Math.PI*2);ctx.stroke();}ctx.setLineDash([]);
    }else if(visualSettings.glyphStyle==='zodiac'){
      ctx.beginPath();ctx.arc(0,0,r*.94,0,Math.PI*2);ctx.stroke();for(let i=0;i<12;i++){const a=i*Math.PI/6-spin*.1,inner=r*.68,outer=r*(i%3===0?1.04:.9);ctx.beginPath();ctx.moveTo(Math.cos(a)*inner,Math.sin(a)*inner);ctx.lineTo(Math.cos(a)*outer,Math.sin(a)*outer);ctx.stroke();const nx=Math.cos(a)*r*.8,ny=Math.sin(a)*r*.8;ctx.beginPath();ctx.arc(nx,ny,Math.max(1.3,r*.06),0,Math.PI*2);ctx.stroke();}
    }else if(visualSettings.glyphStyle==='fractal'){
      for(let level=0;level<3;level++){const rr=r*(.92-level*.22),phase=spin*(level%2?-1:1)+level*.3;ctx.beginPath();for(let i=0;i<6;i++){const a=i*Math.PI/3+phase,px=Math.cos(a)*rr,py=Math.sin(a)*rr;i?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.closePath();ctx.stroke();}
    }else if(visualSettings.glyphStyle==='lattice'){
      for(let i=0;i<4;i++){const rr=r*(.38+i*.18),a=(i%2?1:-1)*Math.PI/4+spin*.08;ctx.save();ctx.rotate(a);ctx.strokeRect(-rr,-rr,rr*2,rr*2);ctx.restore();}ctx.beginPath();ctx.moveTo(-r*.75,0);ctx.lineTo(r*.75,0);ctx.moveTo(0,-r*.75);ctx.lineTo(0,r*.75);ctx.stroke();
    }else if(visualSettings.glyphStyle==='triune'){
      for(let i=0;i<3;i++){const a=i*Math.PI*2/3-spin*.1,px=Math.cos(a)*r*.34,py=Math.sin(a)*r*.34;ctx.beginPath();ctx.arc(px,py,r*.35,0,Math.PI*2);ctx.stroke();}ctx.beginPath();ctx.moveTo(0,-r*.9);ctx.lineTo(r*.78,r*.46);ctx.lineTo(-r*.78,r*.46);ctx.closePath();ctx.stroke();
    }else if(visualSettings.glyphStyle==='eldritch-grid'){
      for(let i=0;i<3;i++){const rr=r*(.3+i*.23);ctx.beginPath();for(let j=0;j<=32;j++){const a=j*Math.PI/8+spin*(i%2?-1:1),rad=rr*(.7+.3*j/32);const px=Math.cos(a)*rad,py=Math.sin(a)*rad;j?ctx.lineTo(px,py):ctx.moveTo(px,py);}ctx.stroke();}
    }else if(visualSettings.glyphStyle==='script'){
      ctx.beginPath();ctx.arc(0,0,r*.96,0,Math.PI*2);ctx.stroke();for(let i=0;i<10;i++){const a=i*Math.PI/5,inner=r*.69,outer=r*(i%2?.84:1.02),xx=Math.cos(a),yy=Math.sin(a);ctx.beginPath();ctx.moveTo(xx*inner,yy*inner);ctx.lineTo(xx*outer,yy*outer);ctx.lineTo(Math.cos(a+.08)*r*.86,Math.sin(a+.08)*r*.86);ctx.stroke();}
    }else {ctx.beginPath();ctx.arc(0,0,r*.86,0,Math.PI*2);ctx.stroke();}
    if(visualSettings.glyphStyle!=='minimal'){
      ctx.strokeStyle = fxColor('accent',visualSettings.spellStyle==='holographic'?'#d5faff':'#f5fbff');ctx.globalAlpha *= .86;ctx.lineWidth=1.05;
      ctx.beginPath();
      const sides=visualSettings.glyphStyle==='alchemical'?5:6;
      for(let i=0;i<sides;i++){const a=spin*.6+i*Math.PI*2/sides,rr=r*(i%2?.38:.67),xx=Math.cos(a)*rr,yy=Math.sin(a)*rr;i?ctx.lineTo(xx,yy):ctx.moveTo(xx,yy);}ctx.closePath();ctx.stroke();
      const markCount=archetype==='beam'?8:visualSettings.glyphStyle==='geometric'?8:6;
      for(let i=0;i<markCount;i++){const a=i*Math.PI*2/markCount-spin,inner=r*.76,outer=r*(i%2?1.02:.9);ctx.beginPath();ctx.moveTo(Math.cos(a)*inner,Math.sin(a)*inner);ctx.lineTo(Math.cos(a+.04)*outer,Math.sin(a+.04)*outer);ctx.stroke();}
    }
    ctx.fillStyle=fxColor('accent','#ffffff');ctx.globalAlpha*=.88;ctx.beginPath();ctx.arc(0,0,Math.max(1.5,r*.08),0,Math.PI*2);ctx.fill();ctx.restore();
  }

  function drawSpellLabel(x, baselineY, value, color, opacity = .96) {
    if (!showSpellForms || !showLabels || !value) return;
    const raw = text(value, 64).replaceAll('_', ' ').replaceAll('-', ' ');
    const label = raw.length > 30 ? `${raw.slice(0, 27)}…` : raw;
    if (!label) return;
    ctx.save(); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = Math.max(0, Math.min(1, opacity));
    ctx.font = '600 10px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    const width = Math.min(184, Math.max(48, ctx.measureText(label).width + 12));
    ctx.fillStyle = 'rgba(12, 15, 24, .9)'; ctx.strokeStyle = `${color}cc`; ctx.lineWidth = 1;
    ctx.beginPath();
    if (typeof ctx.roundRect === 'function') ctx.roundRect(x - width / 2, baselineY - 15, width, 18, 5);
    else ctx.rect(x - width / 2, baselineY - 15, width, 18);
    ctx.fill(); ctx.stroke(); ctx.fillStyle = '#f1f6ff'; ctx.fillText(label, x, baselineY - 2, 172); ctx.restore();
  }

  function drawProjectile(track, sample, t, now, playback, drawTrail = true, renderSpellForm = true, drawHead = true, simplifiedTrail = false) {
    if (!sample) return;
    const x = t.px(sample.x), y = t.py(sample.y), entity = track.entity || {};
    const element = text(entity.element || entity.material || 'mana').toLowerCase();
    const name = text(entity.name || entity.element || 'spell').toLowerCase();
    const identity = `${text(track.spellName || entity.spell_name || '', 100)} ${element} ${name} ${text(entity.material || '')}`;
    const color = fxColor('core', magicIdentityColor(identity,entityColor(entity)));
    const trailColor = fxColor('trail', color);
    const r = Math.max(7, Math.min(28, (5 + safeNumber(entity.radius_m, .22) * t.scale * .12)*visualSettings.spellSize));
    const angle = sample.angle;
    if (drawTrail) drawTrajectoryTrail(track, sample, playback, t, trailColor, r, simplifiedTrail);
    if (!drawHead) return;
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.globalAlpha*=Math.min(1.5,visualSettings.effectIntensity);
    const movingPulse = reduceMotion ? 0 : Math.sin(now / 55) * .12;
    if (/fire|flame|ember|thermal|plasma|lava/.test(identity)) {
      // A forward-driving flame, layered with tongues that stream backwards.
      ctx.globalCompositeOperation = 'lighter';
      const tongues=showEffects?(visualSettings.showParticles?Math.max(1,Math.round(1+(visualSettings.particleDensity*adaptiveGraphics.particleScale)/18)):2):0;
      for (let i = 0; i < tongues; i++) {
        const back = .3 + i * .22, spread = Math.sin((reduceMotion?0:now/53) + i * 2.1) * r * .18;
        ctx.fillStyle = i % 2 ? blendHex(color,palette.fire,.42) : blendHex(color,blendHex(palette.fire,'#fff3ce',.46),.35); ctx.globalAlpha = (.82 - i * .1)*Math.min(1.5,visualSettings.effectIntensity);
        ctx.beginPath(); ctx.moveTo(r * (.72 - back * .45), 0);
        ctx.quadraticCurveTo(-r * back, -r * (.25 + i * .05) + spread, -r * (back + .75), spread * 1.2);
        ctx.quadraticCurveTo(-r * back, r * (.24 + i * .05) + spread, r * (.72 - back * .45), 0);
        ctx.fill();
      }
      ctx.globalAlpha = Math.min(1,visualSettings.effectIntensity); ctx.fillStyle = blendHex(color,'#fff3ce',.2); ctx.beginPath();
      ctx.moveTo(r * 1.18, 0); ctx.quadraticCurveTo(r * .25, -r * .42, -r * .45, 0);
      ctx.quadraticCurveTo(r * .25, r * .42, r * 1.18, 0); ctx.fill();
      ctx.strokeStyle = '#fff7df'; ctx.lineWidth = Math.max(1.5, r * .09); ctx.beginPath(); ctx.moveTo(-r * 1.3, 0); ctx.lineTo(-r * 2.9, 0); ctx.stroke();
    } else if (/water|aqua|rain|liquid|icewater/.test(identity)) {
      // A water lance has a continuous ribbon and a pressure tip, not a bead of dust.
      ctx.globalCompositeOperation = 'lighter';
      for (let lane = 0; lane < 3; lane++) {
        const phase = now / 95 + lane * Math.PI * 2 / 3;
        ctx.strokeStyle = lane === 1 ? '#e4fbff' : '#48b8ff'; ctx.globalAlpha = lane === 1 ? .95 : .62;
        ctx.lineWidth = r * (lane === 1 ? .19 : .31); ctx.beginPath(); ctx.moveTo(-r * 2.6, 0);
        ctx.bezierCurveTo(-r * 1.8, Math.sin(phase) * r * .45, -r * .9, Math.cos(phase) * r * .42, r * .9, 0); ctx.stroke();
      }
      ctx.globalAlpha = 1; ctx.fillStyle = '#ddfaff'; ctx.beginPath(); ctx.moveTo(r * 1.45, 0); ctx.quadraticCurveTo(r * .15, -r * .52, -r * .42, 0); ctx.quadraticCurveTo(r * .15, r * .52, r * 1.45, 0); ctx.fill();
      for (let i = 0; i < 4; i++) { const d = (now / 110 + i * .57) % 1; ctx.globalAlpha = 1 - d; ctx.fillStyle = '#9fe8ff'; ctx.beginPath(); ctx.ellipse(-r * (1.2 + d * 2.5), Math.sin(now / 90 + i * 2) * r * .38, r * .09, r * .16, .4, 0, Math.PI * 2); ctx.fill(); }
    } else if (/ice|frost|snow|glacier|crystal/.test(identity)) {
      ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = '#8ceeff'; ctx.strokeStyle = '#ecfdff'; ctx.lineWidth = Math.max(1, r * .08);
      ctx.beginPath(); ctx.moveTo(r * 1.5, 0); ctx.lineTo(r * .15, -r * .42); ctx.lineTo(-r * .35, -r * .82);
      ctx.lineTo(-r * .72, -r * .23); ctx.lineTo(-r * 1.02, 0); ctx.lineTo(-r * .72, r * .23);
      ctx.lineTo(-r * .35, r * .82); ctx.lineTo(r * .15, r * .42); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.globalAlpha = .9; ctx.beginPath(); ctx.moveTo(r * .15, -r * .4); ctx.lineTo(-r * .48, 0); ctx.lineTo(r * .15, r * .4); ctx.stroke();
      ctx.globalAlpha = .55; for (let i = 0; i < 3; i++) { const xx = -r * (1.2 + i * .7); ctx.beginPath(); ctx.moveTo(xx, -r * .5); ctx.lineTo(xx - r * .2, 0); ctx.lineTo(xx, r * .5); ctx.stroke(); }
    } else if (/thunder|lightning|storm|volt|electric/.test(identity)) {
      ctx.globalCompositeOperation = 'lighter'; ctx.strokeStyle = '#fff7bb'; ctx.lineWidth = Math.max(2, r * .14); ctx.beginPath();
      ctx.moveTo(-r * 2.9, Math.sin(now / 38) * r * .3); ctx.lineTo(-r * 1.9, -r * .4); ctx.lineTo(-r * 1.2, r * .35); ctx.lineTo(-r * .48, -r * .22); ctx.lineTo(r * .08, r * .22); ctx.lineTo(r * .75, -r * .18); ctx.lineTo(r * 1.4, 0); ctx.stroke();
      ctx.strokeStyle = color; ctx.lineWidth = Math.max(1, r * .045); ctx.stroke();
      for (let branch = 0; branch < 3; branch++) { const bx = -r * (1.3 - branch * .65); ctx.beginPath(); ctx.moveTo(bx, 0); ctx.lineTo(bx - r * .18, r * (branch % 2 ? -.55 : .55)); ctx.lineTo(bx + r * .02, r * (branch % 2 ? -.82 : .82)); ctx.stroke(); }
    } else if (/earth|rock|stone|sand|boulder|mud|metal|steel|iron|crystal/.test(identity)) {
      // Solid payloads have a readable body and a directional highlight.
      const metal = /metal|steel|iron/.test(identity);
      ctx.globalCompositeOperation = 'source-over'; ctx.rotate(reduceMotion ? 0 : now / (metal ? 210 : 320));
      ctx.fillStyle = metal ? '#8597a8' : '#88765e'; ctx.strokeStyle = metal ? '#e5f1fb' : '#d2bd97'; ctx.lineWidth = Math.max(1.2, r * .09);
      ctx.beginPath(); const sides = metal ? 5 : 7;
      for (let i = 0; i < sides; i++) { const a = i * Math.PI * 2 / sides - Math.PI / 2, rr = r * (.78 + (i % 3) * .12); i ? ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : ctx.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); }
      ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.strokeStyle = metal ? '#ffffff' : '#5f503e'; ctx.lineWidth = Math.max(1, r * .07); ctx.beginPath(); ctx.moveTo(-r * .2, -r * .35); ctx.lineTo(r * .16, r * .03); ctx.lineTo(-r * .12, r * .33); ctx.stroke();
      if (!metal) { ctx.strokeStyle = '#d7c19b'; ctx.globalAlpha = .7; ctx.beginPath(); ctx.moveTo(-r * 1.25, -r * .2); ctx.lineTo(-r * 2.2, -r * .48); ctx.moveTo(-r * 1.35, r * .18); ctx.lineTo(-r * 2.15, r * .39); ctx.stroke(); }
    } else if (/air|wind|gale|vacuum/.test(identity)) {
      ctx.globalCompositeOperation = 'lighter';
      for (let lane = 0; lane < 4; lane++) {
        const f = lane / 3, wave = Math.sin(now / 90 + lane * 1.8);
        ctx.strokeStyle = lane % 2 ? '#83dfff' : '#effbff'; ctx.globalAlpha = .85 - f * .13;
        ctx.lineWidth = Math.max(1.5, r * (.09 + f * .05)); ctx.beginPath(); ctx.moveTo(-r * (2.7 - f * .25), wave * r * .65);
        ctx.bezierCurveTo(-r * 1.8, -wave * r, -r * .8, wave * r * .8, r * 1.2, 0); ctx.stroke();
      }
      ctx.globalAlpha = .7; ctx.strokeStyle = '#d7f5ff'; ctx.beginPath(); ctx.arc(0, 0, r * (.55 + movingPulse), -.85, .85); ctx.stroke();
    } else if (/life|nature|wood|vine|plant|healing/.test(identity)) {
      ctx.globalCompositeOperation = 'lighter'; ctx.strokeStyle = blendHex(color,palette.life,.55); ctx.lineWidth = Math.max(1.5, r * .11); ctx.beginPath(); ctx.moveTo(-r * 2.5, 0);
      ctx.bezierCurveTo(-r * 1.5, -r * .42, -r * .7, r * .42, r * 1.2, 0); ctx.stroke();
      for (let i = 0; i < 4; i++) { const xx = -r * 1.6 + i * r * .75, side = i % 2 ? 1 : -1; ctx.fillStyle = i % 2 ? blendHex(color,'#8af7a6',.55) : blendHex(color,palette.life,.35); ctx.beginPath(); ctx.ellipse(xx, side * r * .32, r * .3, r * .12, side * -.55, 0, Math.PI * 2); ctx.fill(); }
      ctx.fillStyle = '#d5ffd8'; ctx.beginPath(); ctx.arc(r * .25, 0, r * .27, 0, Math.PI * 2); ctx.fill();
    } else if (/death|necrom|bone|dark|shadow|void|soul/.test(identity)) {
      ctx.globalCompositeOperation = 'lighter'; ctx.strokeStyle = /death|necrom|bone/.test(identity) ? blendHex(color,palette.death,.4) : blendHex(color,palette.void,.45); ctx.lineWidth = Math.max(1.5, r * .1);
      for (let tendril = 0; tendril < 3; tendril++) { const side = tendril - 1; ctx.beginPath(); ctx.moveTo(-r * 2.5, side * r * .25); ctx.bezierCurveTo(-r * 1.3, side * r, -r * .7, -side * r * .72, r * .95, 0); ctx.stroke(); }
      ctx.fillStyle = '#11101a'; ctx.strokeStyle = color; ctx.lineWidth = Math.max(1.5, r * .09); ctx.beginPath(); ctx.moveTo(r * 1.1, 0); ctx.lineTo(r * .25, -r * .66); ctx.lineTo(-r * .7, -r * .32); ctx.lineTo(-r * .45, r * .34); ctx.lineTo(r * .25, r * .66); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.fillStyle = blendHex(color,'#f3f5ff',.62); ctx.beginPath(); ctx.arc(r * .12, 0, r * .19, 0, Math.PI * 2); ctx.fill();
    } else if (/light|holy|sun|radiant/.test(identity)) {
      ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = blendHex(color,'#fff4bc',.5); ctx.strokeStyle = blendHex(color,'#ffffff',.65); ctx.lineWidth = Math.max(1.2, r * .06); ctx.beginPath();
      for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, rr = i % 2 ? r * .36 : r * 1.15; i ? ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : ctx.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); }
      ctx.closePath(); ctx.fill(); ctx.stroke();
    } else {
      // Pure mana/arcane bolts are geometric: a contained core, orbiting seal and marks.
      ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = '#d4fcff'; ctx.strokeStyle = color; ctx.lineWidth = Math.max(1.2, r * .08);
      ctx.beginPath(); ctx.moveTo(r * 1.1, 0); ctx.lineTo(r * .12, -r * .55); ctx.lineTo(-r * .42, 0); ctx.lineTo(r * .12, r * .55); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.save(); ctx.rotate(-now / 170); ctx.strokeStyle = color; ctx.lineWidth = Math.max(1.1, r * .07); ctx.beginPath(); ctx.ellipse(0, 0, r * 1.1, r * .58, 0, -.95, .95); ctx.stroke(); ctx.restore();
      ctx.globalAlpha = .8; for (let i = 0; i < 3; i++) { const xx = -r * (1 + i * .7); ctx.beginPath(); ctx.moveTo(xx, -r * .35); ctx.lineTo(xx - r * .18, 0); ctx.lineTo(xx, r * .35); ctx.stroke(); }
    }
    if(showEffects&&visualSettings.showParticles&&visualSettings.particleDensity>0&&visualSettings.spellStyle!=='minimal'){
      const motes=Math.min(8,Math.max(1,Math.round(visualSettings.particleDensity/14*adaptiveGraphics.particleScale)));
      ctx.globalCompositeOperation='lighter';ctx.fillStyle=blendHex(color,'#ffffff',.48);ctx.globalAlpha=.55*visualSettings.effectIntensity;
      for(let i=0;i<motes;i++){const phase=stableNoise(i,track.startIndex||0)*Math.PI*2+(reduceMotion?0:now/360),d=r*(1.35+stableNoise(i,5)*.82),rr=Math.max(.8,r*(.025+stableNoise(i,7)*.035));ctx.beginPath();ctx.arc(Math.cos(phase)*d,Math.sin(phase)*d,rr,0,Math.PI*2);ctx.fill();}
    }
    if (showSpellForms) {
      const explicit = entity.spell_shape || entity.projectile_form || entity.visual_form || entity.shape || '';
      // Every visible spell keeps a recognizable silhouette. Heavy scenes use
      // a compact shape-only path for secondary spells instead of hiding bodies.
      if (renderSpellForm) drawSpellBody(r * 1.62, identity, color, now, explicit);
      else drawSimpleSpellBody(r * 1.28, identity, color, explicit);
    }
    if(showSpellForms&&visualSettings.showSpellNames){
      const spellLabel=track.spellName||entity.spell_name||entity.name||entity.element||'spell';
      ctx.save();ctx.rotate(-angle);drawSpellLabel(0,-r*2.15-8,spellLabel,color);ctx.restore();
    }
    ctx.restore();
  }

  function drawRadialShock(x, y, radius, color, phase, now, spikes = 12) {
    color = fxColor('impact', color);
    const r = Math.max(1, radius * phase);
    ctx.save(); ctx.translate(x, y); ctx.globalCompositeOperation = 'lighter';
    ctx.globalAlpha = Math.max(0, 1 - phase * .9);
    ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke();
    ctx.globalAlpha *= .7; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.arc(0, 0, r * .72, 0, Math.PI * 2); ctx.stroke();
    ctx.globalAlpha = Math.max(0, 1 - phase); ctx.lineWidth = 1.5;
    for (let i = 0; i < spikes; i++) {
      const a = i * Math.PI * 2 / spikes + now / 2300, inner = r * (.22 + (i % 3) * .07), outer = r * (.78 + (i % 4) * .07);
      ctx.beginPath(); ctx.moveTo(Math.cos(a) * inner, Math.sin(a) * inner);
      ctx.lineTo(Math.cos(a + .035) * (outer * .62), Math.sin(a + .035) * (outer * .62));
      ctx.lineTo(Math.cos(a) * outer, Math.sin(a) * outer); ctx.stroke();
    }
    ctx.restore();
  }

  function drawEffect(effect, t, now, playback) {
    const entity = effect.entity && typeof effect.entity === 'object' ? effect.entity : {};
    const rawPos = Array.isArray(effect.position) ? effect.position : (Array.isArray(effect.center_m) ? effect.center_m : (Array.isArray(effect.origin_m) ? effect.origin_m : entity.position));
    const worldPos = worldPosition(rawPos);
    if (!worldPos) return;
    const x = t.px(worldPos[0]), y = t.py(worldPos[1]);
    const ageInEvents = Math.max(0, playback - safeNumber(effect.eventIndex, playback));
    const kind = text(effect.effect || 'magic', 60).toLowerCase();
    if(!visualSettings.showImpacts&&/(burst|projectile_payload|impact|flare|explosion|shockwave|shatter|collision|detonation|crack)/.test(kind))return;
    if(visualSettings.effectIntensity<=0)return;
    const currentSimTime = playbackTimeAt(playback), effectTime = safeNumber(effect.time);
    const simAge = currentSimTime - effectTime;
    const duration = Math.max(.1, safeNumber(effect.duration_s, kind === 'burst' || kind === 'projectile_payload' ? 1.1 : kind === 'beam' ? .75 : 1.4));
    const useSimTime = simAge > .001 && currentSimTime > effectTime;
    const age = useSimTime ? simAge : ageInEvents;
    const life = useSimTime ? duration : (kind === 'burst' || kind === 'projectile_payload' ? 8 : kind === 'beam' ? 5 : 10);
    if (age > life) return;
    const phase = Math.max(0, Math.min(1, age / life));
    const fade = Math.max(0, 1 - phase);
    const effectElement = text(effect.element || (effect.payload && typeof effect.payload === 'object' ? effect.payload.element : '') || entity.element || '', 60).toLowerCase();
    const effectIdentity=`${text(effect.spell||'')} ${effectElement} ${text(effect.material||entity.material||'')} ${text(entity.name||'')}`;
    const paletteColor=magicIdentityColor(effectIdentity,'');
    const rawEffectColor = effect.preview ? '#d6b0ff' : (paletteColor || effect.color || (entity.element || effectElement ? entityColor({ element: effectElement || entity.element, material: effect.material || entity.material, kind: entity.kind }) : palette.mana));
    const color = fxColor(/burst|projectile_payload|impact|explosion|shockwave|shatter|detonation|collision/.test(kind) ? 'impact' : 'core', rawEffectColor);
    const radiusM = Math.max(.1, safeNumber(effect.radius_m, safeNumber(entity.radius_m, .8)));
    const radius = Math.max(18, Math.min(260, radiusM * t.scale));
    ctx.save(); ctx.globalAlpha = fade*Math.min(1.5,visualSettings.effectIntensity); ctx.globalCompositeOperation = 'lighter';
    ctx.shadowColor=color;ctx.shadowBlur=Math.min(12,visualSettings.glow*5);

    if (kind === 'beam') {
      if (!Array.isArray(effect.direction)) { ctx.restore(); return; }
      const dx = safeNumber(effect.direction[0]), dy = safeNumber(effect.direction[1]);
      const length = Math.min(Math.max(0, t.w * .7), safeNumber(effect.range_m, 8) * t.scale);
      const endX = x + dx * length, endY = y - dy * length;
      const pulse = reduceMotion ? .5 : .82 + .18 * Math.sin(now / 45);
      ctx.lineCap = 'round';
      const glow = ctx.createLinearGradient(x, y, endX, endY); glow.addColorStop(0, '#ffffff'); glow.addColorStop(.18, color); glow.addColorStop(1, color + '00');
      ctx.strokeStyle = glow; ctx.lineWidth = Math.max(10, Math.min(44, safeNumber(effect.radius_m, .25) * t.scale * 2.2)); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(endX, endY); ctx.stroke();
      const nx = -dy, ny = dx;
      const beamWidth = Math.max(5, Math.min(24, safeNumber(effect.radius_m, .25) * t.scale * .9));
      // A tapered, filled spell body gives the beam a readable silhouette. The
      // white spine is the energy channel, not the whole spell by itself.
      ctx.globalAlpha *= .7; ctx.fillStyle = color;
      ctx.beginPath(); ctx.moveTo(x + nx * beamWidth, y - ny * beamWidth);
      ctx.lineTo(endX - dx * beamWidth * .8 + nx * beamWidth * .22, endY + dy * beamWidth * .8 - ny * beamWidth * .22);
      ctx.lineTo(endX, endY);
      ctx.lineTo(endX - dx * beamWidth * .8 - nx * beamWidth * .22, endY + dy * beamWidth * .8 + ny * beamWidth * .22);
      ctx.lineTo(x - nx * beamWidth, y + ny * beamWidth); ctx.closePath(); ctx.fill();
      ctx.globalAlpha *= .9; ctx.strokeStyle = '#f5ffff'; ctx.lineWidth = Math.max(2, Math.min(8, safeNumber(effect.radius_m, .25) * t.scale * .42)) * pulse;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(endX, endY); ctx.stroke();
      // Nested flowing filaments and glyph collars turn a generic ray into a
      // constructed directed spell. Every mark is tied to the recorded vector.
      ctx.globalAlpha *= .72; ctx.strokeStyle = color; ctx.lineWidth = 1.35;
      for (let i = 1; i <= 7; i++) {
        const f = i / 8, bx = x + dx * length * f, by = y - dy * length * f;
        const rr = Math.max(3, Math.min(10, safeNumber(effect.radius_m, .25) * t.scale * .22));
        ctx.beginPath(); ctx.moveTo(bx - dy * rr, by - dx * rr); ctx.lineTo(bx + dy * rr, by + dx * rr); ctx.stroke();
        if (i % 2 === 0) { ctx.beginPath(); ctx.moveTo(bx - dx * rr * .35 + nx * rr * .5, by + dy * rr * .35 - ny * rr * .5); ctx.lineTo(bx + dx * rr * .35, by - dy * rr * .35); ctx.lineTo(bx - dx * rr * .35 - nx * rr * .5, by + dy * rr * .35 + ny * rr * .5); ctx.stroke(); }
      }
      if (!reduceMotion) {
        ctx.globalAlpha = .52 * fade; ctx.strokeStyle = '#f7ffff'; ctx.lineWidth = Math.max(1, beamWidth * .16);
        for (let lane = -1; lane <= 1; lane += 2) { ctx.beginPath(); ctx.moveTo(x + nx * beamWidth * .5 * lane, y - ny * beamWidth * .5 * lane);
          ctx.bezierCurveTo(x + dx * length * .32 + nx * beamWidth * lane, y - dy * length * .32 - ny * beamWidth * lane,
            x + dx * length * .68 - nx * beamWidth * lane, y - dy * length * .68 + ny * beamWidth * lane, endX, endY); ctx.stroke(); }
      }
      if(visualSettings.showGlyphs){drawSpellSigil(x, y, Math.max(14, Math.min(29, beamWidth * 1.3)), color, now, 'beam', .92 * fade);drawSpellSigil(endX, endY, Math.max(12, Math.min(25, beamWidth)), color, now, 'sigil', .78 * fade);}
      ctx.fillStyle = '#f8ffff'; ctx.globalAlpha *= .9; ctx.beginPath();
      ctx.moveTo(endX + dx * beamWidth * 1.5, endY - dy * beamWidth * 1.5);
      ctx.lineTo(endX - dx * beamWidth * .6 + nx * beamWidth * .7, endY + dy * beamWidth * .6 - ny * beamWidth * .7);
      ctx.lineTo(endX - dx * beamWidth * .6 - nx * beamWidth * .7, endY + dy * beamWidth * .6 + ny * beamWidth * .7); ctx.closePath(); ctx.fill();
    } else if (kind === 'burst' || kind === 'projectile_payload' || kind === 'impact') {
      const blast = radius * (.2 + phase * .8);
      drawRadialShock(x, y, blast, color, Math.max(.08, phase), now, /fire|thermal/.test(text(effect.element || entity.element)) ? 9 : 14);
      const coreR = Math.max(4, radius * (.26 * (1 - phase)));
      const core = ctx.createRadialGradient(x - coreR * .2, y - coreR * .2, 0, x, y, coreR * 2.1); core.addColorStop(0, '#ffffff'); core.addColorStop(.28, color); core.addColorStop(1, color + '00');
      ctx.fillStyle = core; ctx.beginPath(); ctx.arc(x, y, coreR * 2.1, 0, Math.PI * 2); ctx.fill();
      // Outer spell-shell: a segmented, collapsing form around the payload. Its
      // geometry is deliberately different from the simple impact shock ring.
      ctx.globalAlpha *= .72; ctx.strokeStyle = color; ctx.lineWidth = Math.max(1.2, radius * .018);
      const shellR = radius * (.24 + phase * .58);
      for (let ring = 0; ring < 2; ring++) { const rr = shellR * (ring ? .76 : 1), start = (reduceMotion ? 0 : now / (ring ? -850 : 1100)) + ring * .7;
        for (let segment = 0; segment < 6; segment++) { const a = start + segment * Math.PI / 3; ctx.beginPath(); ctx.arc(x, y, rr, a + .1, a + Math.PI / 3 - .1); ctx.stroke(); } }
      ctx.globalAlpha *= .85; ctx.fillStyle = color + 'bb'; ctx.beginPath();
      for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6 + (reduceMotion ? 0 : now / 1600), rr = i % 2 ? shellR * .72 : shellR * (1.05 + .08 * Math.sin(now / 120 + i)); const xx = x + Math.cos(a) * rr, yy = y + Math.sin(a) * rr; i ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
      ctx.closePath(); ctx.stroke();
      const identity = `${text(effect.element || entity.element)} ${text(effect.material || entity.material)} ${text(entity.name)}`.toLowerCase();
      for (let i = 0; i < 7; i++) {
        const a = i * Math.PI * 2 / 7 + now / 2500, inner = radius * (.24 + phase * .25), outer = radius * (.6 + ((i * 7) % 4) * .07);
        ctx.globalAlpha *= .97; ctx.strokeStyle = /fire|flame/.test(identity) ? (i % 2 ? '#ff6c38' : '#ffd18c') : /ice|frost/.test(identity) ? '#bbf6ff' : color;
        ctx.lineWidth = Math.max(1.5, radius * .015); ctx.beginPath(); ctx.moveTo(x + Math.cos(a) * inner, y + Math.sin(a) * inner);
        ctx.lineTo(x + Math.cos(a + .07) * outer, y + Math.sin(a + .07) * outer); ctx.stroke();
      }
    } else if (kind === 'manifestation' || kind === 'revival' || kind === 'being_reanimated' || kind === 'lich_reconstitution') {
      const necro = effect.necromancy || /death|lich|reanimat/.test(kind);
      const seal = radius * (.72 + phase * .18);
      ctx.save(); ctx.translate(x, y); ctx.rotate(reduceMotion ? 0 : (necro ? -1 : 1) * now / 850);
      drawArcaneGlyphs(seal, necro ? '#78efbd' : color, now, 10);
      ctx.globalAlpha *= .9; ctx.strokeStyle = necro ? '#65e6ab' : '#e7d9ff'; ctx.lineWidth = 2;
      for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; ctx.beginPath(); ctx.moveTo(Math.cos(a) * seal * .18, Math.sin(a) * seal * .18); ctx.lineTo(Math.cos(a) * seal * .92, Math.sin(a) * seal * .92); ctx.stroke(); }
      ctx.restore();
      const column = ctx.createLinearGradient(x, y - radius * 1.5, x, y + radius * .2);
      column.addColorStop(0, color + '00'); column.addColorStop(.55, necro ? '#65efb055' : color + '77'); column.addColorStop(1, color + '00');
      ctx.fillStyle = column; ctx.beginPath(); ctx.moveTo(x - radius * .3, y); ctx.lineTo(x - radius * .09, y - radius * 1.25); ctx.lineTo(x + radius * .09, y - radius * 1.25); ctx.lineTo(x + radius * .3, y); ctx.closePath(); ctx.fill();
    } else if (kind === 'construct_formed') {
      const entityRadius = Math.max(radius * .5, Math.min(150, safeNumber(entity.radius_m, radiusM) * t.scale));
      ctx.save(); ctx.translate(x, y); ctx.rotate(reduceMotion ? 0 : now / 1200);
      drawArcaneGlyphs(entityRadius, color, now, 6);
      const shape = text(effect.shape || entity.shape || 'circle').toLowerCase();
      ctx.globalAlpha *= .65; ctx.strokeStyle = '#ecfbff'; ctx.lineWidth = 1.5;
      if (['wall','barrier','shield','corridor'].includes(shape)) { ctx.strokeRect(-entityRadius * 1.25, -entityRadius * .24, entityRadius * 2.5, entityRadius * .48); }
      else if (shape === 'beam' || shape === 'ray' || shape === 'line') { ctx.beginPath(); ctx.moveTo(-entityRadius * 1.4, 0); ctx.lineTo(entityRadius * 1.4, 0); ctx.stroke(); }
      else if (shape === 'spiral') { ctx.beginPath(); for (let i = 0; i <= 60; i++) { const a = i * .18, rr = entityRadius * .02 + entityRadius * .9 * i / 60; i ? ctx.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : ctx.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); } ctx.stroke(); }
      else { ctx.beginPath(); ctx.arc(0, 0, entityRadius * (.45 + phase * .35), 0, Math.PI * 2); ctx.stroke(); }
      ctx.restore();
    } else if (kind === 'transformation' || kind === 'life_state_changed' || kind === 'body_enhancement' || kind === 'body_temperature_changed' || kind === 'body_toxicity_changed' || kind === 'blood_manipulation' || kind === 'metal_manipulation' || kind === 'magnetic_field' || kind === 'lichification') {
      const label = kind === 'transformation' ? 'transform' : kind.replaceAll('_', ' ');
      ctx.save(); ctx.translate(x, y);
      const spins = reduceMotion ? 0 : now / 260 * (kind === 'blood_manipulation' ? -1 : 1);
      ctx.rotate(spins);
      const c = kind === 'body_temperature_changed' ? (safeNumber(effect.temperature_k, 293) > 310 ? '#ff8b50' : '#83deff') :
        kind === 'life_state_changed' || kind === 'body_enhancement' ? '#78eea4' :
        kind === 'blood_manipulation' ? '#dc6079' :
        kind === 'metal_manipulation' || kind === 'magnetic_field' ? '#a9c9df' :
        kind === 'lichification' ? '#7becb5' : color;
      ctx.strokeStyle = c; ctx.lineWidth = 1.8; ctx.globalAlpha *= .9;
      for (let ring = 0; ring < 3; ring++) { ctx.beginPath(); ctx.ellipse(0, 0, radius * (.38 + ring * .21), radius * (.2 + ring * .15), ring * .35, now / 700 + ring, now / 700 + ring + Math.PI * 1.5); ctx.stroke(); }
      ctx.globalAlpha *= .8;
      for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, r1 = radius * .35, r2 = radius * (.72 + .08 * Math.sin(now / 120 + i)); ctx.beginPath(); ctx.moveTo(Math.cos(a) * r1, Math.sin(a) * r1); ctx.lineTo(Math.cos(a + .06) * r2, Math.sin(a + .06) * r2); ctx.stroke(); }
      ctx.restore();
      if (label === 'transform' || kind === 'life_state_changed') {
        ctx.globalAlpha = fade * .42; ctx.strokeStyle = color; ctx.lineWidth = Math.max(2, radius * .04); ctx.beginPath(); ctx.arc(x, y, radius * (.3 + phase * .6), 0, Math.PI * 2); ctx.stroke();
      }
    } else if (kind === 'smoke') {
      // Smoke blooms upward in overlapping soft masses; it is visibly different
      // from a mana flash and remains bounded to its recorded lifetime.
      const rise = phase * radius * .9;
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha *= .38 * fade;
      for (let i = 0; i < 8; i++) {
        const drift = Math.sin(now / 700 + i * 1.7) * radius * .12;
        const puffX = x + drift + Math.cos(i * 2.4) * radius * .24;
        const puffY = y - rise * (i / 7) - radius * (.08 + (i % 3) * .07);
        const puffR = radius * (.12 + (i % 4) * .035) * (.8 + phase * .3);
        const cloud = ctx.createRadialGradient(puffX, puffY, 1, puffX, puffY, puffR);
        cloud.addColorStop(0, 'rgba(132,142,154,.75)'); cloud.addColorStop(1, 'rgba(55,62,73,0)');
        ctx.fillStyle = cloud; ctx.beginPath(); ctx.arc(puffX, puffY, puffR, 0, Math.PI * 2); ctx.fill();
      }
    } else if (kind === 'flare') {
      const flareR = radius * (.22 + phase * .7);
      const flare = ctx.createRadialGradient(x, y, 0, x, y, flareR);
      flare.addColorStop(0, '#fff9d4'); flare.addColorStop(.16, '#ffcb73'); flare.addColorStop(1, '#ff8d3b00');
      ctx.fillStyle = flare; ctx.beginPath(); ctx.arc(x, y, flareR, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#ffe6a6'; ctx.lineWidth = 1.5;
      for (let i = 0; i < 10; i++) { const a = i * Math.PI / 5 + now / 2700; ctx.beginPath(); ctx.moveTo(x + Math.cos(a) * flareR * .2, y + Math.sin(a) * flareR * .2); ctx.lineTo(x + Math.cos(a) * flareR * (.75 + (i % 3) * .08), y + Math.sin(a) * flareR * (.75 + (i % 3) * .08)); ctx.stroke(); }
    } else if (kind === 'weather') {
      // The weather renderer owns the ongoing motion; mark the change as a wave
      // travelling through the world instead of a generic sparkle.
      const wave = radius * (.2 + phase * .8); ctx.globalAlpha *= .8; ctx.strokeStyle = color; ctx.lineWidth = 2.2;
      for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.ellipse(x, y, wave * (1 - i * .18), wave * (.34 + i * .07), 0, 0, Math.PI * 2); ctx.stroke(); }
    } else {
      // Unknown effect types still get a restrained sigil, never a cloud of random dust.
      ctx.save(); ctx.translate(x, y); drawArcaneGlyphs(radius * (.35 + phase * .25), color, now, 6); ctx.restore();
    }
    if (effect.spell) drawSpellLabel(x, y - Math.min(radius, 54) - 11, effect.spell, color, fade);
    ctx.restore();
  }

  function stableNoise(i,seed=0) { const v=Math.sin(i*127.1+seed*311.7)*43758.5453; return v-Math.floor(v); }
  function beginWeather(payload,time,indexAt) {
    let raw=typeof payload==='string'?{kind:payload}:(payload&&typeof payload==='object'?payload:{});
    if(raw.weather && typeof raw.weather==='object' && !Array.isArray(raw.weather)) raw=raw.weather;
    else if(raw.environment && typeof raw.environment==='object' && !Array.isArray(raw.environment)) raw=raw.environment;
    const kind=text(raw.kind||raw.type||'clear',32).toLowerCase();
    const allowed=['rain','snow','storm','heatwave','sandstorm','fog','wind','ashfall','aurora','clear','custom','blizzard'];
    const safeKind=allowed.includes(kind)?kind:'custom';
    const number=(key,def,min=0,max=1)=>{const v=raw[key];return Number.isFinite(Number(v))?Math.max(min,Math.min(max,Number(v))):def;};
    const startsAt=Number.isFinite(Number(raw.started_at))?Number(raw.started_at):safeNumber(time);
    const hasSourceDuration=Object.prototype.hasOwnProperty.call(raw,'started_at') && raw.duration == null;
    const indefinite=raw.indefinite===true || hasSourceDuration;
    weatherState={
      kind:safeKind,
      precipitation:text(raw.precipitation||({rain:'rain',storm:'rain',snow:'snow',blizzard:'snow',sandstorm:'dust',ashfall:'ash'}[safeKind]||'none'),16).toLowerCase(),
      intensity:number('intensity',safeKind==='clear'?0:.8),
      clouds:number('clouds',({rain:.8,snow:.94,blizzard:1,storm:1,heatwave:.08,sandstorm:.7,fog:.45,wind:.2,ashfall:.6,aurora:.3,clear:0,custom:0}[safeKind] ?? 0)),
      wind:number('wind',({rain:.25,snow:.7,blizzard:.9,storm:.8,heatwave:.12,sandstorm:1,fog:.05,wind:1,ashfall:.4,aurora:.12,clear:0,custom:0}[safeKind] ?? 0)),
      fog:number('fog',({rain:.1,snow:.22,blizzard:.35,storm:.15,heatwave:.05,sandstorm:.35,fog:1,wind:0,ashfall:.12,aurora:.05,clear:0,custom:0}[safeKind] ?? 0)),
      lightning:number('lightning',safeKind==='storm'?.85:0),
      heat:number('heat',0,-1,1),
      windDirection:number('wind_direction',1,-1,1),
      windX:Number.isFinite(Number(raw.wind_x_mps)) && Math.abs(safeNumber(raw.wind_speed_mps))>1e-9?Math.max(-1,Math.min(1,safeNumber(raw.wind_x_mps)/Math.abs(safeNumber(raw.wind_speed_mps)))):number('wind_direction',1,-1,1),
      windY:Number.isFinite(Number(raw.wind_y_mps)) && Math.abs(safeNumber(raw.wind_speed_mps))>1e-9?Math.max(-1,Math.min(1,safeNumber(raw.wind_y_mps)/Math.abs(safeNumber(raw.wind_speed_mps)))):0,
      windSpeedMps:Math.max(0,Number.isFinite(Number(raw.wind_speed_mps))?Number(raw.wind_speed_mps):Math.hypot(safeNumber(raw.wind_x_mps),safeNumber(raw.wind_y_mps))),
      temperature:number('temperature_k',293.15,0,10000),
      humidity:number('humidity',.45),
      startedAt:startsAt, startIndex:safeNumber(indexAt),
      duration:indefinite?null:Math.max(1,Math.min(86400,number('duration',15,1,86400))),
      indefinite,
    };
  }

  function drawWeather(t,now,playback) {
    const w=weatherState;if(!w)return;
    const simTime=eventTimes.length?eventTimes[Math.max(0,Math.min(eventTimes.length-1,Math.floor(playback)))]||0:0;
    if(w.kind==='clear'){weatherState=null;return;}
    if(!w.indefinite && w.duration!=null && simTime>w.startedAt+w.duration){weatherState=null;return;}
    const progress=Math.max(0,Math.min(1,(simTime-w.startedAt)/.8)),left=w.indefinite||w.duration==null?1:Math.max(0,Math.min(1,(w.startedAt+w.duration-simTime)/1.2));
    const weatherStrength=Math.max(w.intensity,Math.max(0,w.humidity-.65)*.5,Math.abs(w.heat)*.55);
    const alpha=Math.min(1,progress,left)*weatherStrength*Math.max(0,Math.min(1.5,visualSettings.weatherIntensity/70));if(alpha<=0)return;
    ctx.save();ctx.globalAlpha=alpha;
    if(w.clouds>.04){
      const cloud=ctx.createLinearGradient(0,0,0,t.floorY);cloud.addColorStop(0,`rgba(15,22,42,${w.clouds*.64})`);cloud.addColorStop(.72,`rgba(24,31,49,${w.clouds*.28})`);cloud.addColorStop(1,'rgba(15,22,42,0)');ctx.fillStyle=cloud;ctx.fillRect(0,0,t.w,t.floorY);
      for(let i=0;i<8;i++){const x=((stableNoise(i,3)*t.w+now*w.windX*(.006+w.wind*.012))%(t.w+180))-90,y=30+stableNoise(i,8)*t.h*.28+now*w.windY*.006,r=50+stableNoise(i,11)*100;ctx.fillStyle=`rgba(34,42,64,${w.clouds*.18})`;ctx.beginPath();ctx.ellipse(x,y,r,r*.22,0,0,Math.PI*2);ctx.fill();}
    }
    if(w.precipitation!=='none'){
      const count=Math.round(Math.min(140,120*w.intensity)*(visualSettings.particleDensity*adaptiveGraphics.particleScale/60)),wind=w.windDirection*w.wind;
      for(let i=0;i<count;i++){
        const speed=w.precipitation==='rain'?1.0: w.precipitation==='snow'?.32:.6;
        const x=(stableNoise(i,4)*t.w+now*w.windX*(w.precipitation==='rain'?.16:.075)*speed+t.w*2)%(t.w+20)-10;
        const y=(stableNoise(i,9)*t.floorY+now*((w.precipitation==='rain'?.52:.16)*speed+w.windY*.012))%(t.floorY+10);
        if(w.precipitation==='rain'){
          ctx.strokeStyle=`rgba(160,211,255,${.22+stableNoise(i,2)*.38})`;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x-3-wind*8,y+10+stableNoise(i,7)*8);ctx.stroke();
        }else if(w.precipitation==='snow'){
          ctx.fillStyle=`rgba(235,247,255,${.45+stableNoise(i,2)*.48})`;ctx.beginPath();ctx.arc(x+Math.sin(now/600+i)*5,y,1+stableNoise(i,3)*2.1,0,Math.PI*2);ctx.fill();
        }else{
          ctx.fillStyle=w.precipitation==='ash'?'rgba(255,173,103,.62)':'rgba(202,170,119,.52)';ctx.beginPath();ctx.arc(x+Math.sin(now/280+i)*6,y,1+stableNoise(i,3)*2.2,0,Math.PI*2);ctx.fill();
        }
      }
    }
    if(w.fog>.04){const fog=ctx.createLinearGradient(0,t.floorY*.35,0,t.floorY);fog.addColorStop(0,'rgba(167,184,214,0)');fog.addColorStop(.65,`rgba(167,184,214,${w.fog*.11})`);fog.addColorStop(1,`rgba(185,195,215,${w.fog*.32})`);ctx.fillStyle=fog;ctx.fillRect(0,0,t.w,t.floorY);for(let i=0;i<5;i++){const x=((stableNoise(i,44)*t.w+now*(.01+w.wind*.08))%(t.w+240))-120;ctx.fillStyle=`rgba(190,202,223,${w.fog*.055})`;ctx.beginPath();ctx.ellipse(x,t.floorY*.73+stableNoise(i,45)*50,90+stableNoise(i,7)*100,18,0,0,Math.PI*2);ctx.fill();}}
    if(w.heat>.1){const g=ctx.createRadialGradient(t.w*.5,t.floorY,10,t.w*.5,t.floorY,t.w*.65);g.addColorStop(0,`rgba(255,110,45,${w.heat*.16})`);g.addColorStop(1,'rgba(255,80,20,0)');ctx.fillStyle=g;ctx.fillRect(0,t.floorY*.45,t.w,t.h-t.floorY*.45);if(!reduceMotion){ctx.strokeStyle=`rgba(255,195,126,${w.heat*.13})`;for(let i=0;i<18;i++){const x=stableNoise(i,55)*t.w,y=t.floorY-10-stableNoise(i,33)*75;ctx.beginPath();ctx.moveTo(x,y);ctx.quadraticCurveTo(x+Math.sin(now/200+i)*4,y-8,x,y-17);ctx.stroke();}}}
    if(w.heat<-.1){const cold=Math.abs(w.heat);const frost=ctx.createLinearGradient(0,t.floorY*.2,0,t.floorY);frost.addColorStop(0,'rgba(139,213,255,0)');frost.addColorStop(.7,`rgba(139,213,255,${cold*.035})`);frost.addColorStop(1,`rgba(171,230,255,${cold*.15})`);ctx.fillStyle=frost;ctx.fillRect(0,0,t.w,t.floorY);if(!reduceMotion){ctx.fillStyle='rgba(225,248,255,.65)';for(let i=0;i<22;i++){const x=(stableNoise(i,72)*t.w+now*w.windX*.015*t.w+t.w*2)%(t.w+8)-4,y=(stableNoise(i,73)*t.floorY+now*(.008+w.wind*.01)*t.floorY)%(t.floorY+4);ctx.beginPath();ctx.arc(x,y,.8+stableNoise(i,74)*1.6,0,Math.PI*2);ctx.fill();}}}
    if(w.humidity>.65 && w.fog<.15){const moisture=(w.humidity-.65)*.08;const haze=ctx.createLinearGradient(0,0,0,t.floorY);haze.addColorStop(0,`rgba(155,199,231,${moisture*.3})`);haze.addColorStop(1,`rgba(170,208,232,${moisture})`);ctx.fillStyle=haze;ctx.fillRect(0,0,t.w,t.floorY);}
    if(Math.abs(w.windX)+Math.abs(w.windY)>.08 && w.precipitation==='none' && w.clouds<.55 && !reduceMotion){ctx.save();ctx.strokeStyle=`rgba(199,225,255,${alpha*.09})`;ctx.lineWidth=1;for(let i=0;i<10;i++){const x=(stableNoise(i,80)*t.w+now*w.windX*2+t.w*3)%(t.w+30)-15,y=stableNoise(i,81)*t.floorY+now*w.windY*.12;ctx.beginPath();ctx.moveTo(x,y);ctx.quadraticCurveTo(x+18*w.windX,y-3*w.windY,x+36*w.windX,y-6*w.windY);ctx.stroke();}ctx.restore();}
    if(w.lightning>.1 && (Math.floor(now/1600)%4===1)){ctx.globalAlpha*=w.lightning*.35;ctx.fillStyle='#d9e7ff';ctx.fillRect(0,0,t.w,t.floorY);ctx.globalAlpha=alpha;ctx.strokeStyle='rgba(240,248,255,.85)';ctx.lineWidth=2;let x=t.w*(.2+stableNoise(Math.floor(now/1600),6)*.6),y=0;ctx.beginPath();ctx.moveTo(x,y);for(let i=1;i<9;i++){x+=(stableNoise(i+Math.floor(now/1600),8)-.5)*t.w*.12;y=t.floorY*i/9;ctx.lineTo(x,y);}ctx.stroke();}
    if(w.kind==='aurora'){
      ctx.globalCompositeOperation='lighter';for(let band=0;band<4;band++){ctx.strokeStyle=`rgba(${65+band*12},${205-band*8},${161+band*15},${.1+w.intensity*.08})`;ctx.lineWidth=14+band*3;ctx.beginPath();for(let x=0;x<=t.w;x+=24){const y=t.h*.18+band*17+Math.sin(x*.008+now/800+band)*17;x?ctx.lineTo(x,y):ctx.moveTo(x,y);}ctx.stroke();}
    }
    ctx.restore();
    ctx.save();const tag=`${w.kind.toUpperCase()} · ${Math.max(0,Math.ceil(w.startedAt+w.duration-simTime))}s`;ctx.font='700 10px var(--vscode-font-family, sans-serif)';const measured=ctx.measureText?ctx.measureText(tag):null;const tw=measured&&Number.isFinite(measured.width)?measured.width:80;ctx.fillStyle='rgba(10,14,27,.78)';ctx.fillRect(18,18,tw+24,28);ctx.strokeStyle='rgba(160,180,222,.28)';ctx.strokeRect(18,18,tw+24,28);ctx.fillStyle='#dce7ff';ctx.fillText(tag,30,36);ctx.restore();
  }

  function drawVelocityVector(sample,t,color) {
    if(!visualSettings.showVectors||!sample||!sample.moving||!Number.isFinite(sample.angle))return;
    const x=t.px(sample.x),y=t.py(sample.y),length=Math.max(14,Math.min(66,14+Math.log1p(Math.max(0,sample.speed))*8));
    const endX=x+Math.cos(sample.angle)*length,endY=y-Math.sin(sample.angle)*length;
    ctx.save();ctx.globalAlpha=.82;ctx.strokeStyle=visualSettings.highContrastEdges?'#ffffff':color;ctx.fillStyle=ctx.strokeStyle;ctx.lineWidth=visualSettings.highContrastEdges?2.2:1.35;
    ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(endX,endY);ctx.stroke();ctx.beginPath();ctx.moveTo(endX,endY);ctx.lineTo(endX-Math.cos(sample.angle-.5)*7,endY+Math.sin(sample.angle-.5)*7);ctx.lineTo(endX-Math.cos(sample.angle+.5)*7,endY+Math.sin(sample.angle+.5)*7);ctx.closePath();ctx.fill();
    if(camera.zoom>.55){ctx.font='9px var(--vscode-font-family, sans-serif)';ctx.textAlign='left';ctx.fillText(`${Number(sample.speed.toPrecision(2))}`,endX+5,endY-4);}ctx.restore();
  }
  function render() {
    const rect=canvas.getBoundingClientRect(),w=rect.width,h=rect.height;if(!w||!h)return;
    const playback=playing?index+Math.max(0,Math.min(1,(window.performance.now()-lastFrame)/Math.max(35,180/(Number(speedSelect.value)||1)))):index;
    const t=transformFor(w,h),now=window.performance.now();
    // During replay, movement and spell animation follow the recording's world
    // clock; while paused, keep a calm idle animation for character inspection.
    const animationNow = playing && !reduceMotion ? playbackTimeAt(playback) * 1000 : now;
    drawStage(t,playback);
    // Interpolate every moving object along the sampled path. Non-character
    // projectiles get a material-specific head/trail; characters use the same
    // sampled tangent for their facing and gait. Runtime physics is never changed.
    renderPositions.clear();
    sampledMotion.clear();
    // Dense recordings can contain hundreds of moving entities. Keep world
    // interpolation accurate for all tracks, but spend high-detail spell-body
    // drawing only on visible heads and cap that expensive layer per frame.
    let detailedSpellBodies = 0, visibleProjectileHeads = 0, culledProjectileTracks = 0;
    const maxDetailedSpellBodies = adaptiveGraphics.bodyBudget;
    const maxDetailedTrails = adaptiveGraphics.trailBudget;
    let detailedTrails=0;
    for (const track of motionTracks) {
      const sample = sampleMotionTrack(track, playback);
      if (!sample) continue;
      sampledMotion.set(track.id, sample);
      renderPositions.set(track.id, [sample.x, sample.y]);
      if (track.isActor) continue;
      const screenX = t.px(sample.x), screenY = t.py(sample.y);
      const headVisible = screenX >= -72 && screenX <= w + 72 && screenY >= -72 && screenY <= h + 72;
      let trailVisible = headVisible;
      if (!trailVisible) {
        // Check recent recorded points only. This keeps off-screen culling
        // proportional to recent motion rather than the full recording length.
        for (let j = track.points.length - 1; j >= 0; j--) {
          const point = track.points[j];
          if (point.index < playback - 32) break;
          const px = t.px(point.x), py = t.py(point.y);
          if (px >= -72 && px <= w + 72 && py >= -72 && py <= h + 72) { trailVisible = true; break; }
        }
      }
      if (!trailVisible) { culledProjectileTracks++; continue; }
      if (headVisible) {
        visibleProjectileHeads++;
        const detailed = showSpellForms && detailedSpellBodies < maxDetailedSpellBodies;
        if (detailed) detailedSpellBodies++;
        if(visualSettings.showVectors)drawVelocityVector(sample,t,magicIdentityColor(`${track.spellName||''} ${text(track.entity&&track.entity.element||'')}`,entityColor(track.entity||{})));
        const wantTrail = showEffects && visualSettings.showTrajectory;
        const richTrail = wantTrail && detailedTrails < maxDetailedTrails;
        if (richTrail) detailedTrails++;
        drawProjectile(track, sample, t, animationNow, playback, wantTrail, detailed, true, wantTrail && !richTrail);
      } else if (showEffects && visualSettings.showTrajectory) {
        const richTrail = detailedTrails < maxDetailedTrails;
        if (richTrail) detailedTrails++;
        drawProjectile(track, sample, t, animationNow, playback, true, false, false, !richTrail);
      }
    }
    // Give beings and targets a brief, restrained stagger at an actual recorded
    // contact. Never invent a hit merely because a spell passed nearby.
    const impactById = new Map();
    for (const contact of contacts) {
      const age = playback - safeNumber(contact.eventIndex, playback);
      if (age < 0 || age > 8 || !Array.isArray(contact.ids)) continue;
      const intensity = Math.max(0, 1 - age / 8);
      for (const id of contact.ids) {
        const entity = visibleEntities().get(id);
        if (!entity) continue;
        const isActor = text(entity.kind || '').toLowerCase() === 'being' || text(entity.kind || '').toLowerCase() === 'target' ||
          entity.summoned || entity.undead || entity.living || Boolean(entity.visual_form) ||
          /npc|person|knight|guard|wizard|dragon|dinosaur|ant|slime|minotaur|serpent|beast/i.test(text(entity.name || '') + ' ' + text(entity.species || ''));
        if (!isActor) continue;
        const old = impactById.get(id);
        if (!old || intensity > old.impact) {
          const entityPosition=worldPosition(entity.position);
          const contactPosition=worldPosition(contact.position) || entityPosition;
          if (!contactPosition || !entityPosition) continue;
          const contactX=contactPosition[0], entityX=entityPosition[0];
          impactById.set(id, { impact: intensity, impactSign: entityX < contactX ? -1 : 1 });
        }
      }
    }
    if (showEffects) {
      for (const effect of effects) drawEffect(effect, t, animationNow, playback);
    }
    const list=[];let targetCount=0;
    for(const e of visibleEntities().values()){if(e.active===false||!worldPosition(e.position))continue;list.push(e);if(text(e.kind||'').toLowerCase()==='target')targetCount++;}
    // The caster is a scene actor, not a simulated object. The runtime remains authoritative for every contact.
    const sourceX=0,sourceY=0;
    const mageX=t.px(sourceX)-t.scale*.25,mageY=t.py(sourceY);
    const activeCast = [...castEvents].reverse().find(cast => playback >= cast.index - .5 && playback <= Math.max(cast.index + 1, safeNumber(cast.endIndex, cast.index + 12)));
    const casterCasting = Boolean(activeCast);
    const casterHeight = Math.max(86,Math.min(150,h*.26));
    drawWizard(mageX,mageY,casterHeight,1,animationNow,casterCasting,casterCasting);
    if (activeCast) drawCastingWeave(mageX, mageY, casterHeight, animationNow, activeCast);
    let hasHumanTarget=false;
    for(const e of list){
      const track=motionTrackById.get(e.id);
      const sampled=sampledMotion.get(e.id), impact=impactById.get(e.id);
      const motion = impact ? { ...(sampled || { dx: 0, dy: 0, angle: 0, speed: 0, moving: false }), ...impact } : sampled;
      const position=sampled ? [sampled.x,sampled.y] : e.position;
      const x=t.px(safeNumber(position[0])), y=t.py(safeNumber(position[1]));
      const radius=Math.max(7,Math.min(46,Math.max(.18,safeNumber(e.radius_m,.22))*t.scale*.32));
      if(track && motion && !track.isActor)continue;
      if(e.visual_form){
        if(['humanoid','knight','bird','serpent','beast','golem'].includes(text(e.visual_form).toLowerCase())) hasHumanTarget=true;
        drawWorldObject(e,x,y,radius,entityColor(e),animationNow,motion);
      }else if(text(e.kind||'').toLowerCase()==='target'){
        const material=text(e.material||'').toLowerCase(),name=text(e.name||'').toLowerCase();
        const personLike=material==='target'||/knight|npc|dummy|guard|enemy|training|wizard|person/.test(name);
        if(personLike){hasHumanTarget=true;drawKnight(x,y,Math.max(92,Math.min(158,h*.28)),now,selectedId===e.id,motion);}
        else drawWorldObject(e,x,y,radius,entityColor(e),animationNow,motion);
      }else drawWorldObject(e,x,y,radius,entityColor(e),animationNow,motion);
      if(selectedId===e.id){ctx.strokeStyle='#fff0c6';ctx.lineWidth=1.6;ctx.setLineDash([4,4]);ctx.beginPath();ctx.ellipse(x,y-Math.max(30,radius*1.5),Math.max(24,radius*1.2),Math.max(42,radius*2.3),0,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);}
      if(showLabels){ctx.font='600 12px var(--vscode-font-family, sans-serif)';ctx.textAlign='center';ctx.fillStyle='#f1f3ff';ctx.shadowColor='#0a0c16';ctx.shadowBlur=5;ctx.fillText(text(e.name||e.element,44),x,y-Math.max(48,radius*2)-10);ctx.shadowBlur=0;}
    }
    if(!hasHumanTarget){
      const virtualX=5.2,virtualY=0;
      const targetIsSomewhere=targetCount>0;
      if(!targetIsSomewhere)drawKnight(t.px(virtualX),t.py(virtualY),Math.max(92,Math.min(158,h*.28)),now,false);
    }
    // Actual physics contact only: the animation stops here and the impact blooms at the recorded point.
    if(showEffects)for(let contactIndex=Math.max(0,contacts.length-8);contactIndex<contacts.length;contactIndex++){
      const contact=contacts[contactIndex];
      const age=Math.abs(playback-safeNumber(contact.eventIndex,playback));if(age>7)continue;
      const entries=(contact.ids||[]).map(id=>visibleEntities().get(id)).filter(Boolean);
      const worldPos=Array.isArray(contact.position)?contact.position:(entries[0]&&entries[0].position);
      if(!Array.isArray(worldPos))continue;
      const x=t.px(safeNumber(worldPos[0])),y=t.py(safeNumber(worldPos[1])),phase=Math.min(1,age/7),radius=Math.max(20,Math.min(150,18+age*10));
      const impactColor=contact.preview?'#d5adff':(entries.length?entityColor(entries[0]):'#ffe2a2');
      drawRadialShock(x,y,radius,impactColor,Math.max(.06,phase),now,12);
      ctx.save();ctx.globalAlpha=Math.max(0,1-age/4);ctx.globalCompositeOperation='lighter';
      const flash=ctx.createRadialGradient(x,y,0,x,y,radius*.45);flash.addColorStop(0,'#ffffff');flash.addColorStop(.35,impactColor);flash.addColorStop(1,impactColor+'00');ctx.fillStyle=flash;ctx.beginPath();ctx.arc(x,y,radius*.45,0,Math.PI*2);ctx.fill();
      if(!reduceMotion){ctx.strokeStyle='#ffffff';ctx.lineWidth=1.6;for(let k=0;k<8;k++){const a=k*Math.PI/4+now/1800,inner=radius*.26,outer=radius*(.76+(k%3)*.09);ctx.beginPath();ctx.moveTo(x+Math.cos(a)*inner,y+Math.sin(a)*inner);ctx.lineTo(x+Math.cos(a+.04)*outer,y+Math.sin(a+.04)*outer);ctx.stroke();}}
      ctx.restore();
    }
    if(showWeather)drawWeather(t,animationNow,playback);
    const picked=selectedEntity();
    const label=document.getElementById('sceneStatus');
    if(label){
      if(weatherState)label.textContent=`Weather · ${weatherState.kind}`;
      else if(picked)label.textContent=`Selected · ${text(picked.name||picked.element,42)}`;
      else label.textContent='Scene ready';
    }
    if(!list.length){ctx.save();ctx.fillStyle='rgba(12,15,28,.7)';ctx.fillRect(w*.34,h*.18,w*.32,36);ctx.fillStyle='#d7def1';ctx.font='500 12px var(--vscode-font-family, sans-serif)';ctx.textAlign='center';ctx.fillText('Ready for a spell recording',w*.5,h*.18+23);ctx.restore();}
    const renderMs = Math.max(0, window.performance.now() - now);
    tuneAdaptiveGraphics(renderMs);
    lastRenderMetrics = {
      movingTracks: motionTracks.length, visibleProjectileHeads, detailedSpellBodies,
      detailedTrails, culledProjectileTracks, frameMs: renderMs,
      adaptiveBodyBudget: adaptiveGraphics.bodyBudget, adaptiveTrailBudget: adaptiveGraphics.trailBudget,
      particleScale: adaptiveGraphics.particleScale, canvasPixels: adaptiveGraphics.pixelCount,
      estimatedCanvasBytes: adaptiveGraphics.pixelCount * 4, cachedEventObjects: eventObjectCache.size, cachedEventChars: eventObjectCacheChars,
      visibleSpellSilhouettes: showSpellForms ? visibleProjectileHeads : 0,
    };
  }

  function buildMotionTracks(sourceEvents) {
    const first = new Map(), pointsById = new Map(), contactsAt = new Map(), spellByEntityId = new Map();
    const maxTracks = 600, maxSamplesPerTrack = 256;
    castEvents = []; spellTrace = []; lastSpellPanelKey = '';
    let activeCast = null;
    const appendSpellTrace = (event, i, cast) => {
      if (!cast || !event) return;
      const type = eventName(event), effect = text(event.effect || '', 60).toLowerCase();
      let label = '', detail = '', stage = 'shape';
      if (type === 'spell.started') { label = 'Casting begins'; detail = `${text(event.mode || 'release').toUpperCase()} · ${text(event.presentation || 'visual')} presentation`; stage = 'cast'; }
      else if (type === 'entity.created') { const e = event.entity || {}; label = `${text(e.name || e.element || e.material || 'Spell form')} manifests`; detail = [e.kind, e.material || e.element, e.shape || e.visual_form].filter(Boolean).map(x => text(x, 36)).join(' · ') || 'Created entity recorded by runtime'; stage = 'form'; }
      else if (type === 'entity.changed') { const op = text(event.operation || 'change', 50); if (!/move|velocity|accelerate|weave|transform|heat|reanimate|ignite|force|shape/i.test(op)) return; label = ({velocity:'Motion begins',move:'Position changes',accelerate:'Acceleration applied',weave:'Mana construct shaped',transform:'Target transforms',reanimate:'Remains reanimate',heat:'Thermal state changes'})[op] || `${op.replaceAll('_',' ')} applied`; detail = text((event.entity || {}).name || (event.entity || {}).element || 'Observed entity operation', 90); stage = /velocity|move|accelerate/.test(op) ? 'travel' : 'shape'; }
      else if (type === 'magic.effect') { if (!/beam|burst|projectile_payload|construct_formed|manifestation|transformation|revival|reanimation|lich|magnetic_field|body_|life_state|blood_|metal_/.test(effect)) return; label = ({beam:'Directed spell body released',burst:'Spell payload expands',projectile_payload:'Payload resolves at contact',construct_formed:'Construct takes shape',manifestation:'Summoning form manifests',transformation:'Transformation pattern engages',revival:'Life returns',magnetic_field:'Magnetic field establishes'})[effect] || `${effect.replaceAll('_',' ')} observed`; detail = [event.element, event.shape, event.operation, event.material].filter(Boolean).map(x => text(x, 36)).join(' · ') || 'Runtime-recorded magic operation'; stage = /beam/.test(effect) ? 'release' : /burst|payload/.test(effect) ? 'impact' : 'form'; }
      else if (type === 'world.effect') { if (!/smoke|flare|magnetic|thermal|electric|field|construct/i.test(effect)) return; label = `World interaction · ${effect.replaceAll('_',' ')}`; detail = text(event.operation || event.material || 'Observed world effect', 90); stage = 'impact'; }
      else if (type === 'contact.begin') { const names = Array.isArray(event.names) ? event.names : []; label = 'Physical contact recorded'; detail = names.slice(0, 3).map(x => text(x, 36)).join(' ↔ ') || 'Recorded collision/contact point'; stage = 'impact'; }
      else if (type === 'mana.event') { const n = text(event.name || 'mana operation', 60); if (!/summon|reanim|mana_burst|mana_emitted|mana_formed|transform|reviv|soul/i.test(n)) return; label = n.replaceAll('_',' '); detail = (Array.isArray(event.args) ? event.args : []).filter(v => typeof v === 'string' || typeof v === 'number').slice(0, 3).map(v => text(v, 36)).join(' · ') || 'Recorded mana operation'; stage = /burst|emitted/.test(n) ? 'release' : 'form'; }
      else if (type === 'spell.result') { label = event.mode === 'post' ? (event.ok ? 'Preview complete — world restored' : 'Preview failed') : (event.ok && event.committed ? 'Spell committed' : event.ok ? 'Spell completed' : 'Spell failed'); detail = Array.isArray(event.errors) && event.errors.length ? text(event.errors[0], 120) : (event.committed ? 'Runtime reports a committed release' : 'Result reported by runtime'); stage = 'result'; cast.result = { ok: Boolean(event.ok), committed: Boolean(event.committed), mode: text(event.mode || ''), detail }; }
      else if (type === 'preview.output') { label = 'Preview output'; detail = text(event.text || '', 120); stage = 'result'; }
      else return;
      cast.trace.push({ index: i, time: safeNumber(event.time), type, label, detail, stage, mode: text(event.mode || ''), element: text(event.element || (event.entity && event.entity.element) || '', 40) });
      if (cast.trace.length > 120) cast.trace.splice(0, cast.trace.length - 120);
      spellTrace.push({ castIndex: cast.index, ...cast.trace[cast.trace.length - 1] });
      if (spellTrace.length > 1200) spellTrace.splice(0, spellTrace.length - 1200);
    };
    const numberPosition = entity => worldPosition(entity && entity.position);
    const addPoint = (id, entity, i, time, position) => {
      if (!position || !Number.isFinite(Number(position[0])) || !Number.isFinite(Number(position[1])) ||
          Math.abs(Number(position[0])) > MAX_SCENE_COORDINATE || Math.abs(Number(position[1])) > MAX_SCENE_COORDINATE ||
          contactsAt.has(id) && i > contactsAt.get(id).index) return;
      let points = pointsById.get(id);
      if (!points) { points = []; pointsById.set(id, points); }
      const last = points[points.length - 1];
      const point = { index: i, time: safeNumber(time), x: position[0], y: position[1] };
      if (!last) { points.push(point); return; }
      const distance = Math.hypot(point.x - last.x, point.y - last.y);
      // Keep every meaningful bend; occasionally retain an unchanged point so a
      // genuine pause does not turn into a teleport when the object starts again.
      if (distance >= .0015 || (i - last.index >= 8 && point.time - last.time >= .15)) {
        if (i === last.index) points[points.length - 1] = point;
        else points.push(point);
      }
      // A very long recording cannot create an unbounded per-object path index.
      // Keep the first and newest samples while thinning older points gradually.
      if (points.length > maxSamplesPerTrack) {
        // Preserve the newest half-resolution window in full. Older points are
        // thinned, but sharp turns are always retained so long steering paths do
        // not silently become straight-looking when replayed.
        const recentCount = 128;
        const cutoff = Math.max(2, points.length - recentCount);
        const compact = [points[0]];
        for (let j = 1; j < cutoff - 1; j++) {
          const previous = points[j - 1], point = points[j], next = points[j + 1];
          const a = Math.atan2(point.y - previous.y, point.x - previous.x);
          const b = Math.atan2(next.y - point.y, next.x - point.x);
          const turn = Math.abs(Math.atan2(Math.sin(b - a), Math.cos(b - a)));
          if (j % 2 === 0 || turn >= .12) compact.push(point);
        }
        const boundary = points[cutoff - 1];
        if (compact[compact.length - 1] !== boundary) compact.push(boundary);
        compact.push(...points.slice(cutoff));
        pointsById.set(id, compact);
      }
    };
    const remember = (entity, i, isFirst, time) => {
      if (!entity || entity.id == null || entity.active === false) return;
      if (isFirst && !first.has(entity.id) && first.size < maxTracks) first.set(entity.id, entity);
      if (!first.has(entity.id)) return;
      addPoint(entity.id, entity, i, time, numberPosition(entity));
    };

    for (let i = 0; i < sourceEvents.length; i++) {
      let event = sourceEvents[i];
      if (typeof event === 'string') { try { event = JSON.parse(event); } catch (_) { continue; } }
      if (!event || typeof event !== 'object') continue;
      const type = eventName(event), time = safeNumber(event.time);
      if (type === 'spell.started') {
        if (activeCast) activeCast.endIndex = i - 1;
        activeCast = { index: i, time, spell: text(event.spell || 'spell', 100), mode: text(event.mode || 'release'), presentation: text(event.presentation || 'visual'), endIndex: i + 12, trace: [], result: null };
        castEvents.push(activeCast);
        appendSpellTrace(event, i, activeCast);
        if (castEvents.length > 1000) castEvents.shift();
      } else if (type === 'spell.result' && activeCast) {
        appendSpellTrace(event, i, activeCast); activeCast.endIndex = i; activeCast = null;
      } else if (activeCast) appendSpellTrace(event, i, activeCast);
      if (type === 'entity.created' || type === 'entity.changed') {
        if (event.entity && event.entity.id != null && event.spell) spellByEntityId.set(event.entity.id, text(event.spell, 100));
        remember(event.entity, i, type === 'entity.created', time);
      } else if (type === 'scene.snapshot') {
        for (const entity of (Array.isArray(event.entities) ? event.entities : [])) remember(entity, i, false, time);
      } else if (type === 'contact.begin') {
        const involved = Array.isArray(event.entities) ? event.entities : [];
        for (const entity of involved) {
          remember(entity, i, false, time);
          if (entity && entity.id != null && first.has(entity.id)) {
            const position = numberPosition(entity) || worldPosition(event.position);
            if (position) {
              addPoint(entity.id, entity, i, time, [Number(position[0]), Number(position[1])]);
              contactsAt.set(entity.id, { index: i, time, position: [Number(position[0]), Number(position[1])] });
            }
          }
        }
      }
    }

    const out = [];
    for (const [id, initial] of first) {
      const samples = pointsById.get(id) || [];
      const contact = contactsAt.get(id);
      if (contact) {
        while (samples.length && samples[samples.length - 1].index > contact.index) samples.pop();
        const last = samples[samples.length - 1];
        if (!last || Math.hypot(last.x - contact.position[0], last.y - contact.position[1]) > .0015) {
          samples.push({ index: contact.index, time: contact.time, x: contact.position[0], y: contact.position[1] });
        }
      }
      if (samples.length < 2) continue;
      const pathLength = samples.reduce((sum, point, i) => i ? sum + Math.hypot(point.x - samples[i-1].x, point.y - samples[i-1].y) : 0, 0);
      if (pathLength < .025 || samples[samples.length - 1].index <= samples[0].index) continue;
      const kind = text(initial.kind || '').toLowerCase();
      const isActor = kind === 'being' || kind === 'target' || initial.summoned === true || initial.undead === true || initial.living === true ||
        Boolean(initial.visual_form) || /npc|person|knight|guard|wizard|dragon|dinosaur|ant|slime|minotaur|serpent|beast/i.test(text(initial.name || '') + ' ' + text(initial.species || ''));
      out.push({
        id, points: samples, startIndex: samples[0].index, endIndex: contact ? contact.index : samples[samples.length - 1].index,
        start: [samples[0].x, samples[0].y], end: [samples[samples.length - 1].x, samples[samples.length - 1].y],
        entity: initial, spellName: spellByEntityId.get(id) || text(initial.spell_name || '', 100),
        element: text(initial.element || '').toLowerCase(), isActor, hit: Boolean(contact), pathLength,
      });
    }
    motionTracks = out.slice(0, maxTracks);
    motionTrackById = new Map(motionTracks.map(track => [track.id, track]));
    cachedMotionBounds = null; motionBoundsBuilt = false;
  }

  function hitEntityAt(x,y,t) {
    let best=null,dist=Infinity;
    for(const e of visibleEntities().values()){
      if(e.active===false)continue;
      const renderPosition = renderPositions.get(e.id) || e.position;
      if(!worldPosition(renderPosition))continue;
      const ex=t.px(safeNumber(renderPosition[0])),ey=t.py(safeNumber(renderPosition[1]));
      const isActor=text(e.kind||'').toLowerCase()==='being'||e.summoned||e.undead||e.living||/npc|person|knight|guard|wizard|dragon|dinosaur|ant|slime|minotaur/i.test(text(e.name||'')+' '+text(e.species||e.body_form||''));
      const actorHitRadius=isActor?Math.min(92,Math.max(28,(canvas.clientHeight||600)*.15)):0;
      const radius=Math.max(actorHitRadius,20,Math.min(72,Math.max(.22,safeNumber(e.radius_m,.22))*t.scale*.35));
      const d=(ex-x)**2+(ey-y)**2;if(d<dist&&d<radius*radius){best=e;dist=d;}
    }
    return best;
  }

  function showCurrentState(options = {}) {
    renderActivity();
    renderDetails();
    renderObjectList();
    renderWorldLaws();
    renderSpellInspector(index);
    if (options.renderScene !== false) render();
    updateControls();
  }
  function go(next) {
    playing = false;
    cancelAnimationFrame(raf); raf = 0;
    playButton.textContent = '▶ Play';
    const target = Math.max(0, Math.min(events.length - 1, next));
    if (target > index) {
      for(let step=index+1;step<=target&&step<events.length;step++){const event=eventAt(step);if(event)applyEvent(event,step);}
      index=target;showCurrentState();startIdleAnimation();return;
    }
    if(target===index){showCurrentState();startIdleAnimation();return;}
    stateAt(target); startIdleAnimation();
  }
  function updateControls() {
    timeline.max=Math.max(0,events.length-1);timeline.value=String(index);document.getElementById('positionLabel').textContent=`${events.length?index+1:0} / ${events.length}`;
    const current=eventAt(index);document.getElementById('eventLabel').textContent=current?friendlyLabel(current):'Ready';document.getElementById('timeLabel').textContent=`${safeNumber(current&&current.time).toFixed(2)} s`;
    document.getElementById('footerStatus').textContent=events.length?`${events.length.toLocaleString()} events · ${visibleEntities().size.toLocaleString()} objects · ${contacts.length.toLocaleString()} contacts`:'No events';
  }
  function friendlyLabel(event) {
    const type=eventName(event);const msg=semanticActivity(event);
    if(msg)return msg;
    if(type==='scene.snapshot')return 'Scene updated';if(type==='program.started')return 'The spellbook opens';if(type==='spell.started')return `${text(event.spell)} begins`;
    if(type==='activity')return text(event.label || 'Activity');
    return '';
  }
  function stopIdleAnimation() {
    if (idleRaf) cancelAnimationFrame(idleRaf);
    idleRaf = 0;
  }
  function startIdleAnimation() {
    if (playing || reduceMotion || idleRaf) return;
    const idleFrame = stamp => {
      idleRaf = 0;
      if (playing || reduceMotion) return;
      if (stamp - idleLastFrame >= 33) { frameIntervalForRender = idleLastFrame ? stamp - idleLastFrame : 33.3; frameTargetMs = 33.3; idleLastFrame = stamp; render(); }
      idleRaf = requestAnimationFrame(idleFrame);
    };
    idleRaf = requestAnimationFrame(idleFrame);
  }
  function tick(stamp) {
    if(!playing)return;
    frameIntervalForRender = lastLoopFrameStamp ? stamp - lastLoopFrameStamp : 16.7;
    frameTargetMs = 16.7;
    lastLoopFrameStamp = stamp;
    if(!lastFrame)lastFrame=stamp;
    const pace=Number(speedSelect.value)||1;
    if(stamp-lastFrame>Math.max(35,180/pace)){lastFrame=stamp;if(index<events.length-1){index++;const event=eventAt(index);if(event)applyEvent(event,index);showCurrentState({renderScene:false});}else{playing=false;playButton.textContent='↺ Replay';}}
    if(playing){render();raf=requestAnimationFrame(tick);}else startIdleAnimation();
  }
  function togglePlay(){if(!events.length)return;if(playing){playing=false;cancelAnimationFrame(raf);raf=0;playButton.textContent='▶ Play';startIdleAnimation();}else{stopIdleAnimation();if(index>=events.length-1)go(0);playing=true;lastFrame=0;lastLoopFrameStamp=0;playButton.textContent='Ⅱ Pause';raf=requestAnimationFrame(tick);}}
  function jumpImpact(direction) {
    if(!events.length)return;
    let found=-1;
    for(let i=index+direction;i>=0&&i<events.length;i+=direction){
      const event=eventAt(i),type=eventName(event);
      if(type==='contact.begin'||(type==='magic.effect'&&['burst','impact','beam'].includes(text(event.effect,30)))){found=i;break;}
    }
    if(found>=0)go(found);
  }
  function setToggle(id,value) {
    const el=document.getElementById(id);if(!el)return;
    el.classList.toggle('is-on',value);el.setAttribute('aria-pressed',value?'true':'false');
  }
  function toggleFlag(name,id) {
    if(name==='grid')showGrid=!showGrid;
    else if(name==='labels')showLabels=!showLabels;
    else if(name==='effects')showEffects=!showEffects;
    else if(name==='weather')showWeather=!showWeather;
    else if(name==='spellForms')showSpellForms=!showSpellForms;
    setToggle(id,({grid:showGrid,labels:showLabels,effects:showEffects,weather:showWeather,spellForms:showSpellForms})[name]);render();
  }
  function formatSettingNumber(key,value) {
    if(key==='trailLength') return `${Math.round(value)} steps`;
    if(key==='effectIntensity'||key==='glow'||key==='spellSize') return `${Math.round(value*100)}%`;
    return `${Math.round(value)}%`;
  }
  function renderCustomColorSwatches() {
    const holder=document.getElementById('customColorSwatches'); if(!holder)return;
    holder.replaceChildren();
    const entries=Object.entries(visualSettings.customColors||{});
    if(!entries.length){const note=document.createElement('span');note.className='settings-note';note.textContent='No overrides — preset palette is active.';holder.append(note);return;}
    for(const [key,value] of entries){
      const chip=document.createElement('button');chip.type='button';chip.className='custom-color-chip';chip.title=`Edit ${key} override`;chip.setAttribute('aria-label',`Edit custom ${key} colour`);
      const dot=document.createElement('span');dot.style.backgroundColor=value;const label=document.createElement('span');label.textContent=key;chip.append(dot,label);
      chip.addEventListener('click',()=>{const target=document.getElementById('customColorTarget'),picker=document.getElementById('customColorValue');if(target)target.value=key;if(picker)picker.value=value;});
      holder.append(chip);
    }
  }
  function renderFxColorSwatches() {
    const holder=document.getElementById('fxColorSwatches'); if(!holder)return;
    holder.replaceChildren();
    const defaults={core:palette.mana,trail:palette.mana,glyph:palette.mana,impact:palette.fire,aura:palette.being,accent:'#f5fbff',outline:'#11131a'};
    for(const channel of FX_COLOR_CHANNELS){
      const value=visualSettings.fxColors[channel]||defaults[channel];
      const chip=document.createElement('button');chip.type='button';chip.className='custom-color-chip';chip.title=`Edit ${channel} colour`;chip.setAttribute('aria-label',`Edit ${channel} visual colour`);
      const dot=document.createElement('span');dot.style.backgroundColor=value;const label=document.createElement('span');label.textContent=channel;chip.append(dot,label);
      chip.addEventListener('click',()=>{const target=document.getElementById('fxColorTarget'),picker=document.getElementById('fxColorValue');if(target)target.value=channel;if(picker)picker.value=value;});holder.append(chip);
    }
  }
  function syncVisualSettingsControls() {
    const controls={palettePreset:'palettePreset',backgroundPreset:'backgroundPreset',spellStyle:'spellStyle',trailStyle:'trailStyle',glyphStyle:'glyphStyle'};
    for(const [key,id] of Object.entries(controls)){const el=document.getElementById(id);if(el)el.value=visualSettings[key];}
    const numeric={effectIntensity:['effectIntensity',100],glow:['glow',100],trailLength:['trailLength',1],particleDensity:['particleDensity',1],spellSize:['spellSize',100],weatherIntensity:['weatherIntensity',1],gridOpacity:['gridOpacity',1]};
    for(const [key,[id,multiplier]] of Object.entries(numeric)){const el=document.getElementById(id);if(el)el.value=String(Math.round(visualSettings[key]*multiplier));const out=document.getElementById(`${id}Out`);if(out)out.textContent=formatSettingNumber(key,visualSettings[key]);}
    for(const key of SETTING_BOOLS){const el=document.getElementById(key);if(el)el.checked=Boolean(visualSettings[key]);}
    const target=document.getElementById('customColorTarget'),picker=document.getElementById('customColorValue');
    if(target&&target.options&&target.options.length){const selected=target.value||'fire';if(picker)picker.value=visualSettings.customColors[selected]||palette[selected]||'#bba7f5';}
    const fxTarget=document.getElementById('fxColorTarget'),fxPicker=document.getElementById('fxColorValue');
    if(fxTarget&&fxPicker){const channel=fxTarget.value||'core';fxPicker.value=visualSettings.fxColors[channel]||({core:palette.mana,trail:palette.mana,glyph:palette.mana,impact:palette.fire,aura:palette.being,accent:'#f5fbff',outline:'#11131a'})[channel]||'#bba7f5';}
    renderCustomColorSwatches(); renderFxColorSwatches();
  }
  function scheduleVisualSettingsSave() {
    if(settingsSaveTimer)clearTimeout(settingsSaveTimer);
    settingsSaveTimer=setTimeout(()=>{settingsSaveTimer=null;vscode.setState({visualSettings, title:displayTitle, lastIndex:index});},240);
    const status=document.getElementById('settingsStatus');if(status)status.textContent='Live preview active · appearance changes never alter spell physics. Save defaults to keep them across new sessions.';
  }
  function applyVisualSettings(incoming, options={}) {
    visualSettings=normalizeVisualSettings(incoming);
    applyPaletteSelection();
    document.body.dataset.backdrop=visualSettings.backgroundPreset;
    document.body.dataset.contrast=visualSettings.highContrastEdges||visualSettings.palettePreset==='high-contrast'?'high':'normal';
    reduceMotion=systemReduceMotion||visualSettings.reduceMotion;
    if (reduceMotion) stopIdleAnimation();
    else if (!playing && !document.hidden) startIdleAnimation();
    const accent=palette.mana||'#bba7f5';
    document.documentElement.style.setProperty('--accent',accent);
    document.documentElement.style.setProperty('--magic-accent',accent);
    syncVisualSettingsControls();
    if(options.persist!==false)scheduleVisualSettingsSave();
    render();
  }
  function initVisualSettingsControls() {
    const target=document.getElementById('customColorTarget');
    if(target){target.replaceChildren();for(const key of Object.keys(BASE_PALETTE)){const option=document.createElement('option');option.value=key;option.textContent=key.replaceAll(/([a-z])([A-Z])/g,'$1 $2').replaceAll('_',' ');target.append(option);}target.value='fire';}
    const fxTarget=document.getElementById('fxColorTarget');
    if(fxTarget){fxTarget.replaceChildren();const labels={core:'Spell core',trail:'Travel trail',glyph:'Glyphs / seals',impact:'Impact burst',aura:'Being aura',accent:'Internal accent',outline:'Spell outline'};for(const channel of FX_COLOR_CHANNELS){const option=document.createElement('option');option.value=channel;option.textContent=labels[channel];fxTarget.append(option);}fxTarget.value='core';}
    const open=document.getElementById('openVisualSettings'),close=document.getElementById('closeVisualSettings'),panel=document.getElementById('visualSettings');
    const setOpen=enabled=>{if(!panel||!open)return;panel.hidden=!enabled;open.setAttribute('aria-expanded',enabled?'true':'false');open.classList.toggle('is-on',enabled);if(enabled){const first=document.getElementById('palettePreset');if(first)first.focus();}};
    if(open)open.addEventListener('click',()=>setOpen(panel.hidden));
    if(close)close.addEventListener('click',()=>{setOpen(false);open.focus();});
    const selectKeys=['palettePreset','backgroundPreset','spellStyle','trailStyle','glyphStyle'];
    for(const key of selectKeys){const el=document.getElementById(key);if(el)el.addEventListener('change',()=>applyVisualSettings({...visualSettings,[key]:el.value}));}
    const numeric={effectIntensity:['effectIntensity',100],glow:['glow',100],trailLength:['trailLength',1],particleDensity:['particleDensity',1],spellSize:['spellSize',100],weatherIntensity:['weatherIntensity',1],gridOpacity:['gridOpacity',1]};
    for(const [key,[id,divisor]] of Object.entries(numeric)){const el=document.getElementById(id);if(el)el.addEventListener('input',()=>{const value=Number(el.value)/divisor;visualSettings={...visualSettings,[key]:value};const out=document.getElementById(`${id}Out`);if(out)out.textContent=formatSettingNumber(key,value);applyVisualSettings(visualSettings);});}
    for(const key of SETTING_BOOLS){const el=document.getElementById(key);if(el)el.addEventListener('change',()=>applyVisualSettings({...visualSettings,[key]:el.checked}));}
    const lookSelect=document.getElementById('lookPreset');
    if(lookSelect)lookSelect.addEventListener('change',()=>{const recipe=VISUAL_LOOKS[lookSelect.value];if(recipe)applyVisualSettings({...visualSettings,...recipe,customColors:visualSettings.customColors,fxColors:visualSettings.fxColors});lookSelect.value='';});
    const applyFx=document.getElementById('applyFxColor'),clearFx=document.getElementById('clearFxColors'),fxColorTarget=document.getElementById('fxColorTarget'),fxColorValue=document.getElementById('fxColorValue');
    if(applyFx)applyFx.addEventListener('click',()=>{if(!fxColorTarget||!fxColorValue||!/^#[0-9a-fA-F]{6}$/.test(fxColorValue.value)||!FX_COLOR_CHANNELS.includes(fxColorTarget.value))return;applyVisualSettings({...visualSettings,fxColors:{...visualSettings.fxColors,[fxColorTarget.value]:fxColorValue.value.toLowerCase()}});});
    if(fxColorTarget)fxColorTarget.addEventListener('change',()=>{if(fxColorValue){const channel=fxColorTarget.value;fxColorValue.value=visualSettings.fxColors[channel]||({core:palette.mana,trail:palette.mana,glyph:palette.mana,impact:palette.fire,aura:palette.being,accent:'#f5fbff',outline:'#11131a'})[channel]||'#bba7f5';}});
    if(clearFx)clearFx.addEventListener('click',()=>applyVisualSettings({...visualSettings,fxColors:{}}));
    const applyColor=document.getElementById('applyCustomColor'),clearColors=document.getElementById('clearCustomColors'),colorTarget=document.getElementById('customColorTarget'),colorValue=document.getElementById('customColorValue');
    if(applyColor)applyColor.addEventListener('click',()=>{if(!colorTarget||!colorValue||!/^#[0-9a-fA-F]{6}$/.test(colorValue.value))return;applyVisualSettings({...visualSettings,customColors:{...visualSettings.customColors,[colorTarget.value]:colorValue.value.toLowerCase()}});});
    if(colorTarget)colorTarget.addEventListener('change',()=>{if(colorValue)colorValue.value=visualSettings.customColors[colorTarget.value]||palette[colorTarget.value]||'#bba7f5';});
    if(clearColors)clearColors.addEventListener('click',()=>applyVisualSettings({...visualSettings,customColors:{}}));
    const reset=document.getElementById('resetVisualSettings');if(reset)reset.addEventListener('click',()=>applyVisualSettings(VISUAL_DEFAULTS));
    const save=document.getElementById('saveVisualSettings');if(save)save.addEventListener('click',()=>{if(settingsSaveTimer){clearTimeout(settingsSaveTimer);settingsSaveTimer=null;}vscode.setState({visualSettings,title:displayTitle,lastIndex:index});vscode.postMessage({type:'saveVisualSettings',settings:visualSettings});const status=document.getElementById('settingsStatus');if(status)status.textContent='Saved as your default Visualiser appearance.';});
    const exportButton=document.getElementById('exportVisualSettings');if(exportButton)exportButton.addEventListener('click',()=>vscode.postMessage({type:'exportVisualSettings',settings:visualSettings}));
    const importButton=document.getElementById('importVisualSettings');if(importButton)importButton.addEventListener('click',()=>vscode.postMessage({type:'importVisualSettings'}));
  }
  function selectTab(id){document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===id));document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.id==='scene'||v.id===id));if(id==='scene')resizeCanvas();if(id==='world')renderWorldLaws();if(id==='objects')renderObjectList();if(id==='activity')renderActivity();if(id==='spell')renderSpellInspector(index);}

  let loading = false;
  window.addEventListener('message', message => {
    const data=message.data;
    if (!data || !data.type) return;
    if(data.type==='visualSettings'){
      applyVisualSettings(data.settings,{persist:false});
      const status=document.getElementById('settingsStatus');if(status)status.textContent='Loaded saved appearance settings.';
      return;
    }
    if(data.type==='layoutState'){
      const button=document.getElementById('maximizeScene');
      if(button){button.setAttribute('aria-pressed',data.maximised?'true':'false');button.title=data.maximised?'Restore editor layout':'Maximise editor group';}
      return;
    }
    if(data.type==='loadStart'){
      displayTitle=text(data.title||'Magic scene');document.getElementById('title').textContent=displayTitle;
      stopIdleAnimation();clearEventObjectCache();adaptiveGraphics.bodyBudget=96;adaptiveGraphics.trailBudget=72;adaptiveGraphics.particleScale=1;adaptiveGraphics.overloadedFrames=0;adaptiveGraphics.fastFrames=0;systemReduceMotion=typeof window.matchMedia==='function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;reduceMotion=Boolean(data.reduceMotion) || Boolean(visualSettings.reduceMotion) || systemReduceMotion;events=[];eventTimes=[];resetState();renderWorldLaws();renderObjectList();renderActivity();index=0;motionTracks=[];motionTrackById=new Map();cachedMotionBounds=null;motionBoundsBuilt=false;motionBoundsBuildCount=0;castEvents=[];spellTrace=[];lastSpellPanelKey='';renderPositions.clear();sampledMotion.clear();
      loading=true;playing=false;cancelAnimationFrame(raf);playButton.textContent='▶ Play';
      timeline.min='0';timeline.max='0';timeline.value='0';sceneNotice.hidden=false;sceneNotice.textContent='Reading recording in low-memory chunks…';
      document.getElementById('footerStatus').textContent='Loading recording';updateControls();return;
    }
    if(data.type==='loadChunk'){
      if(!loading||!Array.isArray(data.events))return;
      // The host streams bounded chunks; do not retain a second raw-event array.
      for(const event of data.events){if(event&&eventName(event)!=='recording'){events.push(JSON.stringify(event));eventTimes.push(safeNumber(event.time));}}
      sceneNotice.textContent=`Loading scene records… ${events.length.toLocaleString()} events`;
      document.getElementById('footerStatus').textContent=`Loaded ${events.length.toLocaleString()} events`;return;
    }
    if(data.type==='loadError'){
      loading=false;events=[];eventTimes=[];clearEventObjectCache();resetState();renderWorldLaws();sceneNotice.hidden=false;sceneNotice.textContent=`Could not load recording: ${text(data.message,240)}`;
      document.getElementById('footerStatus').textContent='Recording load failed';updateControls();render();startIdleAnimation();return;
    }
    if(data.type==='loadDone'){
      if(!loading)return;loading=false;resetState();index=-1;buildMotionTracks(events);camera.initialized=false;
      sceneNotice.hidden=false;sceneNotice.textContent=events.length?'Drag to pan · scroll to zoom · click a target to inspect it':'Ready. Run a spell to fill the scene with recorded magic.';
      timeline.min='0';timeline.max=String(Math.max(0,events.length-1));timeline.value='0';
      if(events.length)go(0);else{updateControls();render();}fitCamera();renderObjectList();renderSpellInspector(index);
      document.getElementById('footerStatus').textContent=`Ready · ${events.length.toLocaleString()} events`;
      vscode.setState({ title:displayTitle, lastIndex:index });startIdleAnimation();return;
    }
  });
  document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>selectTab(b.dataset.tab)));
  document.getElementById('prev').addEventListener('click',()=>go(index-1));
  document.getElementById('next').addEventListener('click',()=>go(index+1));
  document.getElementById('prevImpact').addEventListener('click',()=>jumpImpact(-1));
  document.getElementById('nextImpact').addEventListener('click',()=>jumpImpact(1));
  playButton.addEventListener('click',togglePlay);
  document.getElementById('replay').addEventListener('click',()=>{stopIdleAnimation();go(0);playing=true;lastFrame=0;lastLoopFrameStamp=0;playButton.textContent='Ⅱ Pause';raf=requestAnimationFrame(tick);});
  timeline.addEventListener('input',()=>go(Number(timeline.value)));
  if(objectSearch)objectSearch.addEventListener('input',renderObjectList);
  if(objectFilter)objectFilter.addEventListener('change',renderObjectList);
  if(activitySearch)activitySearch.addEventListener('input',renderActivity);
  if(activityFilter)activityFilter.addEventListener('change',renderActivity);
  canvas.addEventListener('dblclick',event=>{const rect=canvas.getBoundingClientRect(),x=event.clientX-rect.left,y=event.clientY-rect.top,t=transformFor(rect.width,rect.height),best=hitEntityAt(x,y,t);if(best){selectedId=best.id;focusEntity(best);renderDetails();renderObjectList();render();}});
  canvas.addEventListener('click',event=>{
    if(suppressNextClick){suppressNextClick=false;return;}
    if(pointerDrag && pointerDrag.moved)return;
    const rect=canvas.getBoundingClientRect(),x=event.clientX-rect.left,y=event.clientY-rect.top;
    const t=transformFor(rect.width,rect.height),best=hitEntityAt(x,y,t);
    if(best){selectedId=best.id;if(document.body.classList.contains('character-view'))focusEntity(best);renderDetails();renderObjectList();render();}
  });
  canvas.addEventListener('pointerdown',event=>{
    if(event.button!==0 || event.isPrimary===false)return;
    pointerDrag={x:event.clientX,y:event.clientY,cameraX:camera.x,cameraY:camera.y,moved:false,pointerId:event.pointerId};
    if(typeof canvas.setPointerCapture==='function' && event.pointerId!=null){try{canvas.setPointerCapture(event.pointerId);}catch(_){}}
    canvas.style.cursor='grabbing';
  });
  window.addEventListener('pointermove',event=>{
    if(pointerDrag){
      if(pointerDrag.pointerId!=null&&event.pointerId!=null&&pointerDrag.pointerId!==event.pointerId)return;
      const rect=canvas.getBoundingClientRect(),dx=event.clientX-pointerDrag.x,dy=event.clientY-pointerDrag.y;
      if(Math.abs(dx)+Math.abs(dy)>3)pointerDrag.moved=true;
      const t=transformFor(rect.width,rect.height);camera.x=pointerDrag.cameraX-dx/t.scale;camera.y=pointerDrag.cameraY+dy/t.scale;render();return;
    }
  });
  const finishPointerDrag=event=>{if(pointerDrag){if(event&&pointerDrag.pointerId!=null&&event.pointerId!=null&&pointerDrag.pointerId!==event.pointerId)return;const moved=pointerDrag.moved;pointerDrag=null;suppressNextClick=moved;canvas.style.cursor='grab';}};
  window.addEventListener('pointerup',finishPointerDrag);
  window.addEventListener('pointercancel',finishPointerDrag);
  canvas.addEventListener('wheel',event=>{
    if(event.preventDefault)event.preventDefault();
    const rect=canvas.getBoundingClientRect();zoomBy(event.deltaY<0?1.13:.885,event.clientX-rect.left,event.clientY-rect.top);
  });
  canvas.addEventListener('mousemove',event=>{
    const rect=canvas.getBoundingClientRect(),x=event.clientX-rect.left,y=event.clientY-rect.top,t=transformFor(rect.width,rect.height);
    const best=hitEntityAt(x,y,t);
    let bestEffect=null,effectDist=Infinity;
    for(const effect of effects){
      const position=worldPosition(effect.position);
      if(!position)continue;
      const age=Math.abs(index-safeNumber(effect.eventIndex,index));if(age>(effect.effect==='burst'?7:5))continue;
      const ex=t.px(position[0]),ey=t.py(position[1]);
      const d=Math.abs(Math.hypot(x-ex,y-ey)-Math.max(18,Math.min(220,safeNumber(effect.radius_m,.6)*t.scale))*.8);
      if(d<effectDist&&d<26){bestEffect=effect;effectDist=d;}
    }
    const effectNames={burst:'Magical blast',beam:'Magical beam',construct_formed:'Woven mana',manifestation:'Summoning effect',weather:'Weather shift'};
    if(bestEffect&&(!best||effectDist<28)){const cause=text(bestEffect.spell||'Magic',100);canvas.title=`${cause} · ${effectNames[bestEffect.effect]||'Magical effect'}`;}
    else if(best){canvas.title=`${text(best.name||best.element,100)}${best.summoned?' · summoned':best.undead?' · reanimated':best.anchored?' · stationary target':''}`;}
    else canvas.title='Drag to pan · scroll to zoom · hover over a spell effect to identify it';
    if(!pointerDrag)canvas.style.cursor=best||bestEffect?'pointer':'grab';
  });
  canvas.tabIndex=0;
  canvas.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();go(index+1);}else if(e.key==='ArrowLeft'){e.preventDefault();go(index-1);}else if(e.key===' '){e.preventDefault();togglePlay();}else if(e.key==='Enter'){e.preventDefault();selectTab('details');}else if(e.key==='+'||e.key==='='){e.preventDefault();zoomBy(1.15);}else if(e.key==='-'){e.preventDefault();zoomBy(.87);}else if(e.key==='0'){e.preventDefault();fitScene();}else if(e.key.toLowerCase()==='g'){toggleFlag('grid','toggleGrid');}else if(e.key.toLowerCase()==='l'){toggleFlag('labels','toggleLabels');}else if(e.key.toLowerCase()==='e'){toggleFlag('effects','toggleEffects');}else if(e.key.toLowerCase()==='w'){toggleFlag('weather','toggleWeather');}else if(e.key.toLowerCase()==='s'){toggleFlag('spellForms','toggleSpellForms');}else if(e.key.toLowerCase()==='f'){const entity=selectedEntity();if(entity){focusEntity(entity);render();}}else if(e.key.toLowerCase()==='i'){toggleCharacterView();}});
  if (window.__MANA_VISUALISER_TEST__ === true) {
    window.__MANA_VISUALISER_TEST_API__ = {
      tracks: () => Array.from(motionTrackById.values()).map(track => ({
        id: track.id, isActor: track.isActor, startIndex: track.startIndex, endIndex: track.endIndex,
        spellName: track.spellName || '', entityName: text(track.entity && track.entity.name || ''),
        points: track.points.map(point => ({ index: point.index, time: point.time, x: point.x, y: point.y })),
        at: position => { const sample = sampleMotionTrack(track, position); return sample && { x: sample.x, y: sample.y, angle: sample.angle, moving: sample.moving }; },
      })),
      spellTrace: () => spellTrace.map(item => ({ ...item })),
      casts: () => castEvents.map(cast => ({ index: cast.index, spell: cast.spell, mode: cast.mode, endIndex: cast.endIndex, traceCount: cast.trace.length })),
      renderMetrics: () => ({ ...lastRenderMetrics }),
      adaptiveGraphics: () => ({ ...adaptiveGraphics, cacheEntries:eventObjectCache.size, cacheChars:eventObjectCacheChars }),
      motionBoundsBuildCount: () => motionBoundsBuildCount,
      sceneBounds: () => ({ ...sceneBounds() }),
      cameraScale: () => Math.max(MIN_SCENE_SCALE,Math.min(MAX_SCENE_SCALE,camera.baseScale*camera.zoom)),
      effectiveReduceMotion: () => reduceMotion,
      idleAnimationScheduled: () => idleRaf !== 0,
      archetype: (identity, shape = '') => spellArchetype(identity, shape),
      settings: () => JSON.parse(JSON.stringify(visualSettings)),
      palette: () => ({...palette}),
      settingEnums: () => JSON.parse(JSON.stringify(SETTING_ENUMS)),
      fxColor: (channel,fallback='#ffffff') => fxColor(channel,fallback),
      lookNames: () => Object.keys(VISUAL_LOOKS),
    };
  }
  const fitButton=document.getElementById('fitScene');if(fitButton)fitButton.addEventListener('click',fitScene);
  const focusButton=document.getElementById('focusSelected');if(focusButton)focusButton.addEventListener('click',()=>{const entity=selectedEntity();if(entity){focusEntity(entity);render();selectTab('scene');}});
  function toggleCharacterView(force){const enabled=typeof force==='boolean'?force:!document.body.classList.contains('character-view');document.body.classList.toggle('character-view',enabled);const button=document.getElementById('focusMode');if(button){button.setAttribute('aria-pressed',enabled?'true':'false');button.textContent=enabled?'Exit character view':'Character view';button.title=enabled?'Return to the full scene (I)':'Expand the scene and focus the selected character (I)';}if(enabled){const entity=selectedEntity();if(entity)focusEntity(entity);}requestAnimationFrame(()=>{resizeCanvas();render();});}
  const characterViewButton=document.getElementById('focusMode');if(characterViewButton)characterViewButton.addEventListener('click',()=>toggleCharacterView());
  [['toggleGrid','grid'],['toggleLabels','labels'],['toggleEffects','effects'],['toggleWeather','weather'],['toggleSpellForms','spellForms']].forEach(([id,name])=>{const el=document.getElementById(id);if(el)el.addEventListener('click',()=>toggleFlag(name,id));});
  const zoomIn=document.getElementById('zoomIn');if(zoomIn)zoomIn.addEventListener('click',()=>zoomBy(1.2));
  const zoomOut=document.getElementById('zoomOut');if(zoomOut)zoomOut.addEventListener('click',()=>zoomBy(.833333));
  const closeButton=document.getElementById('closeScene');if(closeButton)closeButton.addEventListener('click',()=>vscode.postMessage({type:'close'}));
  const maxButton=document.getElementById('maximizeScene');if(maxButton)maxButton.addEventListener('click',()=>vscode.postMessage({type:'maximize'}));
  initVisualSettingsControls();
  applyVisualSettings(VISUAL_DEFAULTS,{persist:false});
  if (typeof window.matchMedia === 'function') {
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handleReducedMotionChange = event => {
      systemReduceMotion = Boolean(event && event.matches);
      const next = systemReduceMotion || visualSettings.reduceMotion;
      if (next === reduceMotion) return;
      reduceMotion = next;
      if (reduceMotion) stopIdleAnimation();
      else if (!playing && !document.hidden) startIdleAnimation();
      render();
    };
    if (reducedMotionQuery && typeof reducedMotionQuery.addEventListener === 'function') reducedMotionQuery.addEventListener('change', handleReducedMotionChange);
    else if (reducedMotionQuery && typeof reducedMotionQuery.addListener === 'function') reducedMotionQuery.addListener(handleReducedMotionChange);
  }
  window.addEventListener('resize',resizeCanvas);
  if (typeof ResizeObserver === 'function') {
    const sceneResizeObserver = new ResizeObserver(() => resizeCanvas());
    sceneResizeObserver.observe(canvas);
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      if (raf) cancelAnimationFrame(raf);
      raf = 0; stopIdleAnimation(); lastFrame = 0; lastLoopFrameStamp = 0; idleLastFrame = 0;
    } else if (playing) {
      lastFrame = 0; lastLoopFrameStamp = 0; raf = requestAnimationFrame(tick);
    } else startIdleAnimation();
  });
  resizeCanvas();
  vscode.postMessage({type:'ready'});
})();
