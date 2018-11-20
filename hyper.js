module.exports = {
  config: {
    backgroundColor: '#000',
    borderColor: '#333',
    colors: [
      '#000000',
      '#ff0000',
      '#33ff00',
      '#ffff00',
      '#0066ff',
      '#cc00ff',
      '#00ffff',
      '#d0d0d0',
      '#808080',
      '#ff0000',
      '#33ff00',
      '#ffff00',
      '#0066ff',
      '#cc00ff',
      '#00ffff',
      '#ffffff',
    ],
    copyOnSelect: true,
    cursorColor: '#f81ce5',
    css: `
      .tabs_title.tabs_title { display: block !important; } /* Snazzy: Disable hide single tab */
    `,
    fontFamily:
      '"Operator Mono SSm", Menlo, "DejaVu Sans Mono", "Lucida Console", monospace',
    fontSize: 12,
    foregroundColor: '#fff',
    hypercwd: {},
    hyperTabs: {
      activityColor: 'salmon',
      tabIconsColored: true,
      trafficButtons: true,
    },
    modifierKeys: {
      altIsMeta: true,
    },
    padding: '12px 14px',
    shell: '/bin/zsh',
    summon: {
      hotkey: 'Ctrl+;',
      hideDock: true,
      hideOnBlur: true,
    },
    termCSS: '',
    updateChannel: 'canary',
    windowSize: [1440, 900],
  },
  plugins: [
    'hyper-search',
    'hyperlinks',
    'hyperterm-paste',
    'hyperterm-summon',
    'hypercwd',
    'hyper-snazzy',
  ]
};
