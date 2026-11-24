const assert = require('node:assert/strict');
const { createHeroDeck } = require('./site/assets/hero-slideshow.js');

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
