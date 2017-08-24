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
      '#ffffff'
    ],
    copyOnSelect: true,
    css: '',
    cursorColor: '#f81ce5',
    fontFamily: 'Menlo, "DejaVu Sans Mono", "Lucida Console", monospace',
    fontSize: 16,
    foregroundColor: '#fff',
    modifierKeys: {
      altIsMeta: true
    },
    padding: '12px 14px',
    shell: '/bin/zsh',
    summon: {
      hideDock: true
    },
    termCSS: '',
    windowSize: [1440, 900]
  },

  localPlugins: [
    'hyperterm-summon'
  ],

  plugins: [
    'hyper-snazzy',
    'hypercwd',
    "hyperlinks",
    "hyperterm-cursor"
  ]
};
