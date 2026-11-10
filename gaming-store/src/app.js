/* Neon Forge — catalog, cart (idempotent), checkout. Storefront logic. */
'use strict';

const GAMES = [
  { id:'ashfall-harbor', title:'Ashfall Harbor', genre:'rpg', platform:['PC','PS5'], price:39.99, rating:4.8, stock:'ok', icon:'🌫️', blurb:'A rain port that holds the storm together — until it doesn’t.' },
  { id:'emberline-tactics', title:'Emberline Tactics', genre:'tactics', platform:['PC','Switch'], price:29.99, rating:4.6, stock:'ok', icon:'♟️', blurb:'Turn-based wildfires over a dying valley.' },
  { id:'cinderpatch', title:'Cinderpatch', genre:'roguelike', platform:['PC'], price:19.99, rating:4.9, stock:'ok', icon:'🕳️', blurb:'Descend a burning foundry of living slag. 60 fps, no mercy.' },
  { id:'saltwake', title:'Saltwake', genre:'action', platform:['PS5'], price:49.99, rating:4.4, stock:'ok', icon:'🌊', blurb:'Melee on a razor-ridged reef at low tide.' },
  { id:'kettlestep', title:'Kettlestep', genre:'puzzle', platform:['PC','Switch'], price:14.99, rating:4.7, stock:'ok', icon:'🫖', blurb:'A kettle that walks. Sort the tea, save the village.' },
  { id:'furnace-district', title:'Furnace District', genre:'sim', platform:['PC'], price:24.99, rating:4.2, stock:'warn', icon:'🏭', blurb:'Run a coal district’s budget, air quality, and strikes.' },
  { id:'parrot-circuit', title:'Parrot Circuit', genre:'racing', platform:['Switch','PS5'], price:34.99, rating:4.1, stock:'ok', icon:'🦜', blurb:'Feather-light arcade racing on hanging cages.' },
  { id:'blackloom', title:'Blackloom', genre:'roguelike', platform:['PC','PS5'], price:21.99, rating:4.5, stock:'ok', icon:'🪡', blurb:'Weave plots of death for noble families.' },
  { id:'thicket-run', title:'Thicket Run', genre:'action', platform:['PC'], price:16.99, rating:3.9, stock:'warn', icon:'🌿', blurb:'Free-run a grown-over express line.' },
  { id:'ledger-of-ink', title:'Ledger of Ink', genre:'rpg', platform:['Switch'], price:27.99, rating:4.6, stock:'ok', icon:'🖋️', blurb:'An inkwell magistrate must acquit the forest itself.' },
  { id:'kiln-ward', title:'Kiln Ward', genre:'sim', platform:['PC'], price:22.99, rating:4.3, stock:'ok', icon:'🏺', blurb:'Tend a kiln under a mountain — crack lore vs crack clay.' },
  { id:'paper-lantern', title:'Paper Lantern', genre:'puzzle', platform:['PC','Switch','PS5'], price:12.99, rating:4.8, stock:'ok', icon:'🏮', blurb:'Realign light sources so the foxes can cross the dark.' },
];

const LS_KEY = 'neonforge.cart.v1';
const IDEMPOTENCY_KEY = () => crypto.randomUUID ? crypto.randomUUID() : `idem-${Date.now()}-${Math.random().toString(36).slice(2)}`;

const state = {
  platform: 'all',
  genre: 'all',
  sort: 'featured',
  query: '',
  cart: new Map(), // id -> qty
  idempotency: null,
};

function loadCart() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (raw) new Map(Object.entries(JSON.parse(raw))).forEach((v, k) => state.cart.set(k, v));
  } catch { /* corrupt store → start fresh, truthfully empty */ }
}
function saveCart() {
  localStorage.setItem(LS_KEY, JSON.stringify(Object.fromEntries(state.cart)));
}
const money = n => `$${n.toFixed(2)}`;
const byId = id => GAMES.find(g => g.id === id);
const cartCount = () => [...state.cart.values()].reduce((a, b) => a + b, 0);
const cartSubtotal = () => [...state.cart.entries()].reduce((sum, [id, qty]) => sum + byId(id).price * qty, 0);

function filteredGames() {
  let list = GAMES.filter(g =>
    (state.platform === 'all' || g.platform.includes(state.platform)) &&
    (state.genre === 'all' || g.genre === state.genre) &&
    (!state.query || (`${g.title} ${g.genre} ${g.blurb}`.toLowerCase().includes(state.query)))
  );
  switch (state.sort) {
    case 'price-asc': list.sort((a,b) => a.price - b.price); break;
    case 'price-desc': list.sort((a,b) => b.price - a.price); break;
    case 'rating': list.sort((a,b) => b.rating - a.rating); break;
    case 'name': list.sort((a,b) => a.title.localeCompare(b.title)); break;
    default: break; // featured: catalog order as authored
  }
  return list;
}

function renderGrid() {
  const grid = document.getElementById('game-grid');
  const list = filteredGames();
  document.getElementById('result-count').textContent = `${list.length} title${list.length === 1 ? '' : 's'}`;
  document.getElementById('empty-state').hidden = list.length !== 0;
  grid.innerHTML = list.map(g => `
    <li class="card" data-game="${g.id}">
      <div class="card__art" aria-hidden="true">${ART[g.id] ? `<img class="card__img" src="${ART[g.id]}" alt="${escapeHtml(g.title)} cover art" loading="lazy" onerror="this.remove();this.parentElement.textContent='${g.icon}'">` : g.icon}</div>
      <div class="card__body">
        <h3 class="card__title">${escapeHtml(g.title)}</h3>
        <div class="card__meta">
          <span class="badge ${g.stock === 'ok' ? 'badge--ok' : 'badge--warn'}">${g.stock === 'ok' ? 'In stock' : 'Low stock'}</span>
          <span>${g.platform.join(' · ')}</span>
          <span>${g.genre}</span>
        </div>
        <p class="card__desc">${escapeHtml(g.blurb)}</p>
        <div class="card__foot">
          <div><div class="price">${money(g.price)}</div><div class="rating" aria-label="Rated ${g.rating} out of 5">★ ${g.rating}</div></div>
          <button class="card__add" data-add="${g.id}" aria-label="Add ${escapeHtml(g.title)} to cart">Add →</button>
        </div>
      </div>
    </li>`).join('');
}
function escapeHtml(s) { return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
const ART = {
  'ashfall-harbor':'assets/ashfall-harbor.jpg','emberline-tactics':'assets/emberline-tactics.jpg',
  'cinderpatch':'assets/cinderpatch.jpg','saltwake':'assets/saltwake.jpg','kettlestep':'assets/kettlestep.jpg',
  'furnace-district':'assets/furnace-district.jpg','parrot-circuit':'assets/parrot-circuit.jpg',
  'blackloom':'assets/blackloom.jpg','thicket-run':'assets/thicket-run.jpg','ledger-of-ink':'assets/ledger-of-ink.jpg',
  'kiln-ward':'assets/kiln-ward.jpg','paper-lantern':'assets/paper-lantern.webp',
};

function bumpCartCount() {
  const el = document.getElementById('cart-count');
  el.classList.remove('bump'); void el.offsetWidth; el.classList.add('bump');
}
function renderCart() {
  bumpCartCount();
  const list = document.getElementById('cart-list');
  if (state.cart.size === 0) {
    list.innerHTML = '<li class="cart-empty">Empty for now.<br/><span style="font-size:.85em">Your drilled keys will wait for you.</span></li>';
  } else {
    list.innerHTML = [...state.cart.entries()].map(([id, qty]) => {
      const g = byId(id);
      return `<li class="cart-item">
        <div class="cart-item__art" aria-hidden="true">${g.icon}</div>
        <div><div class="cart-item__name">${escapeHtml(g.title)}</div><div class="cart-item__price">${money(g.price)} × ${qty}</div></div>
        <div class="qty" aria-label="Quantity of ${escapeHtml(g.title)}">
          <button data-dec="${id}" aria-label="Decrease quantity">−</button>
          <span aria-live="polite">${qty}</span>
          <button data-inc="${id}" aria-label="Increase quantity">+</button>
        </div>
      </li>`;
    }).join('');
  }
  document.getElementById('cart-count').textContent = cartCount();
  document.getElementById('cart-subtotal').textContent = money(cartSubtotal());
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.hidden = false;
  setTimeout(() => { t.hidden = true; }, 2600);
}

function openCart() { document.getElementById('cart-drawer').hidden = false; document.getElementById('scrim').hidden = false; renderCart(); document.getElementById('close-cart').focus(); }
function closeCart() { document.getElementById('cart-drawer').hidden = true; document.getElementById('scrim').hidden = true; document.getElementById('open-cart').focus(); }
function openCheckout() { hideCheckout(true); document.getElementById('checkout-modal').hidden = false; document.getElementById('scrim').hidden = false; if (state.idempotency === null) state.idempotency = IDEMPOTENCY_KEY(); document.getElementById('checkout-email').focus(); }
function hideCheckout(keepScrim) { document.getElementById('checkout-modal').hidden = true; if (!keepScrim) document.getElementById('scrim').hidden = true; }

document.addEventListener('click', e => {
  const add = e.target.closest('[data-add]');
  if (add) { const id = add.dataset.add; state.cart.set(id, (state.cart.get(id) || 0) + 1); saveCart(); renderCart(); showToast(`${byId(id).title} → your cart`); return; }
  const inc = e.target.closest('[data-inc]');
  if (inc) { const id = inc.dataset.inc; state.cart.set(id, (state.cart.get(id) || 0) + 1); saveCart(); renderCart(); return; }
  const dec = e.target.closest('[data-dec]');
  if (dec) { const id = dec.dataset.dec; const q = (state.cart.get(id) || 0) - 1; if (q <= 0) state.cart.delete(id); else state.cart.set(id, q); saveCart(); renderCart(); return; }
  if (e.target.id === 'open-cart') openCart();
  else if (e.target.id === 'close-cart' || e.target.id === 'scrim' || e.target.id === 'checkout-close') { closeCart(); hideCheckout(); }
  else if (e.target.id === 'checkout-btn') openCheckout();
  else if (e.target.id === 'clear-cart') { state.cart.clear(); saveCart(); renderCart(); showToast('Cart emptied'); }
});

document.getElementById('genre-select').addEventListener('change', e => { state.genre = e.target.value; renderGrid(); });
document.getElementById('sort-select').addEventListener('change', e => { state.sort = e.target.value; renderGrid(); });
document.getElementById('search-form').addEventListener('submit', e => { e.preventDefault(); state.query = document.getElementById('search-input').value.trim().toLowerCase(); renderGrid(); });
document.getElementById('platform-chips').addEventListener('click', e => { const chip = e.target.closest('.chip'); if (!chip) return; state.platform = chip.dataset.platform; document.querySelectorAll('.chip').forEach(c => c.classList.toggle('is-on', c === chip)); renderGrid(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeCart(); hideCheckout(); } });

document.getElementById('checkout-form').addEventListener('submit', e => {
  e.preventDefault();
  const email = document.getElementById('checkout-email').value.trim();
  const note = document.getElementById('checkout-note').value.trim();
  if (state.idempotency === null) state.idempotency = IDEMPOTENCY_KEY();
  const order = { email, note, idempotency: state.idempotency, lines: [...state.cart.entries()].map(([id, qty]) => ({ id, qty, price: byId(id).price })), total: cartSubtotal(), ts: new Date().toISOString() };
  try { localStorage.setItem('neonforge.orders.v1', JSON.stringify([...JSON.parse(localStorage.getItem('neonforge.orders.v1') || '[]'), order])); } catch { /* storage full: cart stays intact, report honestly */ }
  document.getElementById('checkout-status').textContent = `Drilled key → ${email} · ref ${state.idempotency.slice(0, 8)} · $${order.total.toFixed(2)}`;
  state.cart.clear(); saveCart(); renderCart();
  state.idempotency = null; // next checkout gets a fresh idempotency key
});
document.getElementById('newsletter-form').addEventListener('submit', e => {
  e.preventDefault();
  const email = document.getElementById('newsletter-email').value.trim();
  document.getElementById('newsletter-status').textContent = `Subscribed: ${email} — see you Friday.`;
  document.getElementById('newsletter-email').value = '';
});

loadCart();
renderGrid();
renderCart();
