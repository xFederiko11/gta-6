const assert = require('node:assert/strict');
const { createHeroDeck } = require('./site/assets/hero-slideshow.js');
const fs = require('node:fs');

// New editorial UX requirement: 1.75-second rotation, centered photo on desktop.
const script = fs.readFileSync('./site/assets/hero-slideshow.js', 'utf8');
const style = fs.readFileSync('./site/assets/hero-slideshow.css', 'utf8');
assert.match(script, /const interval = 1750;/, 'Hero photos must rotate after 1.75 seconds');
assert.match(style, /transition:opacity \.4s ease/);
assert.match(fs.readFileSync('./cloux_preview_v1.py','utf8'), /slide\(1\)\},1750\);/);
assert.match(style, /@media\(min-width:1001px\)\s*\{[\s\S]*?object-position:center center;/,
             'Desktop photo must be centered regardless of source focal point');
assert.match(style, /transform:none;/, 'Desktop hero must not be displaced');


// Check user-visible behavior over complete and consecutive shuffled passes.
for (let run = 0; run < 50; run++) {
  const next = createHeroDeck(20);
  let previous;
  for (let cycle = 0; cycle < 10; cycle++) {
    const pass = [];
    for (let i = 0; i < 20; i++) {
      const value = next();
      assert.ok(Number.isInteger(value) && value >= 0 && value < 20);
      assert.notEqual(value, previous, 'An image repeated immediately');
      pass.push(value);
      previous = value;
    }
    assert.equal(new Set(pass).size, 20, 'A complete pass must show every photograph once');
  }
}
console.log('Verified 20-image shuffle, complete passes and no immediate repeats.');
