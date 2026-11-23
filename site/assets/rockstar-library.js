(() => {
  const filters = document.querySelector('#library-filters');
  if (!filters) return;
  const search = document.querySelector('#library-search');
  const category = document.querySelector('#library-category');
  const cards = [...document.querySelectorAll('[data-library-card]')];
  filters.hidden = false;
  function update() {
    const terms = search.value.trim().toLocaleLowerCase('it').split(/\s+/).filter(Boolean);
    let count = 0;
    for (const card of cards) {
      const visible = (!category.value || category.value === card.dataset.category)
        && terms.every(term => card.dataset.search.includes(term));
      card.hidden = !visible;
      if (visible) count++;
    }
    document.querySelector('#library-count').textContent = `${count} immagini su ${cards.length}`;
  }
  search.addEventListener('input', update);
  category.addEventListener('change', update);
})();
