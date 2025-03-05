module.exports = {
  presets: [
    ['@babel/preset-env', { targets: { node: 'current' } }],
    ['@babel/preset-react', { runtime: 'automatic' }]
  ],
  plugins: [
    ['@babel/plugin-transform-runtime', { regenerator: true }],
    '@babel/plugin-proposal-class-properties'
  ]
};