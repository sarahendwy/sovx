/**
 * Client-side shopping cart, persisted to localStorage.
 *
 * No build step, no dependencies — attaches a single global, `window.Cart`,
 * the same way the inline scripts in cart.html / product.html /
 * product_card.html already work in this project.
 *
 * A cart line represents a specific ProductBuyingOption (SKU) of a product —
 * not the bare product — since price/stock live on the buying option, and a
 * product can have several purchasable options. `id` below is the buying
 * option's id. Items snapshot display data at add-time (title/optionName/
 * amount/unit/price/thumbnail/stock) since there is no product JSON API to
 * re-fetch them by id later. Calling Cart.add() again for the same option id
 * refreshes that snapshot.
 *
 * Usage:
 *   Cart.add({
 *     id: 34,                 // ProductBuyingOption id — the cart line's key
 *     productId: 12,          // parent Product id, for linking back to it
 *     title: 'Necklace',      // product title
 *     optionName: '1 kg',     // ProductBuyingOption.name
 *     amount: 1,              // ProductBuyingOption.amount
 *     unit: 'kg',             // ProductBuyingOption.unit
 *     price: 199,             // ProductBuyingOption.price
 *     thumbnail: '/media/x.jpg',
 *     stock: 5,                // ProductBuyingOption.stock
 *   });
 *   Cart.increment(34);
 *   Cart.decrement(34);      // quantity 0 auto-removes the item
 *   Cart.setQuantity(34, 3);
 *   Cart.remove(34);
 *   Cart.getItems();         // -> array of items
 *   Cart.getCount();         // -> total quantity, e.g. for a navbar badge
 *   Cart.getSubtotal();      // -> sum of price * quantity
 *   Cart.onChange(function (summary) { ... });          // fires on every mutation
 *   window.addEventListener('cart:change', function (e) { e.detail... });
 *
 * This module only manages client-side state. It does not talk to the
 * server-side session cart (accessories/views.py, orders/views.py) — wiring
 * it into the templates and checkout flow is a separate step.
 */
(function (window) {
  'use strict';

  if (window.Cart) {
    // Script included more than once — keep the first instance.
    return;
  }

  var STORAGE_KEY = 'sovx:cart';
  // v2: cart lines key on ProductBuyingOption id and carry productId/optionName/amount/unit.
  var SCHEMA_VERSION = 2;

  /** In-memory cache of { items: [...] }. Falls back to this if localStorage is unavailable. */
  var state = null;
  var listeners = [];

  // ---- helpers ---------------------------------------------------------

  function toInt(value, fallback) {
    var n = Math.floor(Number(value));
    return Number.isFinite(n) ? n : (fallback || 0);
  }

  function normalizeId(id) {
    var n = Number(id);
    return Number.isFinite(n) ? Math.trunc(n) : null;
  }

  /** Returns a finite non-negative integer stock, or null meaning "unlimited/unknown". */
  function normalizeStock(value) {
    if (value === undefined || value === null || value === '') return null;
    var n = Number(value);
    if (!Number.isFinite(n) || n < 0) return null;
    return Math.floor(n);
  }

  /** Clamps a desired quantity to >= 0 and, when stock is known, to <= stock. */
  function clampQuantity(quantity, stock) {
    var q = toInt(quantity, 0);
    if (q < 0) q = 0;
    if (typeof stock === 'number' && Number.isFinite(stock)) {
      q = Math.min(q, stock);
    }
    return q;
  }

  function findIndex(items, id) {
    for (var i = 0; i < items.length; i++) {
      if (items[i].id === id) return i;
    }
    return -1;
  }

  function cloneItem(item) {
    return {
      id: item.id,
      productId: item.productId,
      title: item.title,
      optionName: item.optionName,
      amount: item.amount,
      unit: item.unit,
      price: item.price,
      thumbnail: item.thumbnail,
      stock: item.stock,
      quantity: item.quantity,
    };
  }

  function sanitizeStoredItem(raw) {
    if (!raw || typeof raw !== 'object') return null;
    var id = normalizeId(raw.id);
    if (id === null) return null;
    var stock = normalizeStock(raw.stock);
    var quantity = clampQuantity(raw.quantity, stock);
    if (quantity <= 0) return null;
    return {
      id: id,
      productId: raw.productId != null ? normalizeId(raw.productId) : null,
      title: raw.title != null ? String(raw.title) : '',
      optionName: raw.optionName != null ? String(raw.optionName) : '',
      amount: Number.isFinite(Number(raw.amount)) ? Number(raw.amount) : 1,
      unit: raw.unit != null ? String(raw.unit) : '',
      price: Number.isFinite(Number(raw.price)) ? Number(raw.price) : 0,
      thumbnail: raw.thumbnail != null ? String(raw.thumbnail) : '',
      stock: stock,
      quantity: quantity,
    };
  }

  // ---- persistence -------------------------------------------------------

  function defaultState() {
    return { version: SCHEMA_VERSION, items: [] };
  }

  function readState() {
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) return defaultState();

      var parsed = JSON.parse(raw);
      if (!parsed || parsed.version !== SCHEMA_VERSION || !Array.isArray(parsed.items)) {
        return defaultState();
      }

      var items = [];
      for (var i = 0; i < parsed.items.length; i++) {
        var item = sanitizeStoredItem(parsed.items[i]);
        if (item) items.push(item);
      }
      return { version: SCHEMA_VERSION, items: items };
    } catch (e) {
      // Corrupt JSON, storage disabled, etc. — start clean rather than throw.
      return defaultState();
    }
  }

  function loadState() {
    if (!state) state = readState();
    return state;
  }

  function persist() {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      // localStorage unavailable (private mode, quota, disabled) — keep
      // working against the in-memory cache for the rest of this session.
    }
    notify();
  }

  // ---- change notifications ----------------------------------------------

  function summary() {
    return { items: getItems(), count: getCount(), subtotal: getSubtotal() };
  }

  function notify() {
    var data = summary();

    listeners.forEach(function (callback) {
      try {
        callback(data);
      } catch (e) {
        if (window.console && window.console.error) {
          window.console.error('Cart.onChange listener threw:', e);
        }
      }
    });

    if (typeof window.CustomEvent === 'function') {
      window.dispatchEvent(new window.CustomEvent('cart:change', { detail: data }));
    }
  }

  // Keep other tabs/windows in sync.
  window.addEventListener('storage', function (event) {
    if (event.key !== STORAGE_KEY) return;
    state = null; // force a re-read from localStorage on next access
    notify();
  });

  // ---- public API ---------------------------------------------------------

  /**
   * Add a buying option to the cart, or increase its quantity if it's
   * already there. `item.id` must be the ProductBuyingOption id — that's
   * the cart line's key, since price/stock belong to the option, not the
   * product. Refreshes the stored snapshot (title/productId/optionName/
   * amount/unit/price/thumbnail/stock) with whatever is passed; omitted
   * fields keep their previously known value. Quantity is clamped to
   * `item.stock` when stock is a known number. Returns the resulting item,
   * or null if the id was invalid or the resulting quantity is 0 (e.g.
   * stock is 0).
   */
  function add(item, quantity) {
    if (!item || typeof item !== 'object') return null;
    var id = normalizeId(item.id);
    if (id === null) return null;

    quantity = quantity === undefined ? 1 : quantity;

    var s = loadState();
    var idx = findIndex(s.items, id);
    var existing = idx > -1 ? s.items[idx] : null;

    var incomingStock = normalizeStock(item.stock);
    var stock = incomingStock !== null ? incomingStock : (existing ? existing.stock : null);

    var baseQuantity = existing ? existing.quantity : 0;
    var nextQuantity = clampQuantity(baseQuantity + toInt(quantity, 0), stock);

    if (nextQuantity <= 0) {
      if (existing) s.items.splice(idx, 1);
      persist();
      return null;
    }

    var resultItem = {
      id: id,
      productId: item.productId != null ? normalizeId(item.productId) : (existing ? existing.productId : null),
      title: item.title != null ? String(item.title) : (existing ? existing.title : ''),
      optionName: item.optionName != null ? String(item.optionName) : (existing ? existing.optionName : ''),
      amount: Number.isFinite(Number(item.amount)) ? Number(item.amount) : (existing ? existing.amount : 1),
      unit: item.unit != null ? String(item.unit) : (existing ? existing.unit : ''),
      price: Number.isFinite(Number(item.price)) ? Number(item.price) : (existing ? existing.price : 0),
      thumbnail: item.thumbnail != null ? String(item.thumbnail) : (existing ? existing.thumbnail : ''),
      stock: stock,
      quantity: nextQuantity,
    };

    if (existing) {
      s.items[idx] = resultItem;
    } else {
      s.items.push(resultItem);
    }

    persist();
    return cloneItem(resultItem);
  }

  /** Removes an item entirely, regardless of its quantity. Returns true if something was removed. */
  function remove(id) {
    var nid = normalizeId(id);
    if (nid === null) return false;

    var s = loadState();
    var idx = findIndex(s.items, nid);
    if (idx === -1) return false;

    s.items.splice(idx, 1);
    persist();
    return true;
  }

  /** Increases an item's quantity by `step` (default 1), clamped to its known stock. */
  function increment(id, step) {
    var nid = normalizeId(id);
    if (nid === null) return null;

    var s = loadState();
    var idx = findIndex(s.items, nid);
    if (idx === -1) return null;

    var item = s.items[idx];
    var delta = step === undefined ? 1 : toInt(step, 1);
    var nextQuantity = clampQuantity(item.quantity + delta, item.stock);

    if (nextQuantity <= 0) {
      s.items.splice(idx, 1);
      persist();
      return null;
    }

    item.quantity = nextQuantity;
    persist();
    return cloneItem(item);
  }

  /** Decreases an item's quantity by `step` (default 1). Reaching 0 removes the item. */
  function decrement(id, step) {
    var delta = step === undefined ? 1 : toInt(step, 1);
    return increment(id, -Math.abs(delta));
  }

  /** Sets an exact quantity (e.g. from a typed number input). <= 0 removes the item; clamps to stock. */
  function setQuantity(id, quantity) {
    var nid = normalizeId(id);
    if (nid === null) return null;

    var s = loadState();
    var idx = findIndex(s.items, nid);
    if (idx === -1) return null;

    var item = s.items[idx];
    var nextQuantity = clampQuantity(quantity, item.stock);

    if (nextQuantity <= 0) {
      s.items.splice(idx, 1);
      persist();
      return null;
    }

    item.quantity = nextQuantity;
    persist();
    return cloneItem(item);
  }

  /** Empties the cart. */
  function clear() {
    var s = loadState();
    s.items = [];
    persist();
  }

  /** Returns a fresh array copy of the current cart items. */
  function getItems() {
    return loadState().items.map(cloneItem);
  }

  /** Returns a single item by id, or null. */
  function getItem(id) {
    var nid = normalizeId(id);
    if (nid === null) return null;
    var idx = findIndex(loadState().items, nid);
    return idx === -1 ? null : cloneItem(loadState().items[idx]);
  }

  /** Whether the given buying-option id is currently in the cart. */
  function has(id) {
    return getItem(id) !== null;
  }

  /** Total quantity across all items (e.g. for a navbar badge). */
  function getCount() {
    return loadState().items.reduce(function (sum, item) {
      return sum + item.quantity;
    }, 0);
  }

  /** Sum of price * quantity across all items. */
  function getSubtotal() {
    return loadState().items.reduce(function (sum, item) {
      return sum + item.price * item.quantity;
    }, 0);
  }

  /**
   * Subscribe to cart changes. `callback` receives { items, count, subtotal }
   * on every mutation. Returns an unsubscribe function.
   */
  function onChange(callback) {
    if (typeof callback !== 'function') return function () {};
    listeners.push(callback);
    return function unsubscribe() {
      var idx = listeners.indexOf(callback);
      if (idx > -1) listeners.splice(idx, 1);
    };
  }

  window.Cart = {
    add: add,
    remove: remove,
    increment: increment,
    decrement: decrement,
    setQuantity: setQuantity,
    clear: clear,
    getItems: getItems,
    getItem: getItem,
    has: has,
    getCount: getCount,
    getSubtotal: getSubtotal,
    onChange: onChange,
  };
})(window);
