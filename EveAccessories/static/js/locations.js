/**
 * Governorate/city lookups, shared by every governorate+city select pair in
 * the site (checkout, sell-with-us, the shipping fees dashboard form) and by
 * shipping fee calculation.
 *
 * No build step, no dependencies - attaches a single global, `window.Locations`,
 * the same way static/js/cart.js does.
 *
 * Usage:
 *   Locations.getCities(governorateId).then(cities => ...);         // [{id, name_ar, name_en}, ...]
 *   Locations.calculateShippingFee(governorateId, cityId).then(fee => ...); // number, or null if unavailable
 *
 * Cascading selects wire themselves up automatically: any `<select>` with a
 * `data-governorate-select` attribute paired with a `data-city-select`
 * `<select>` in the same `<form>` (set by dashboard/forms.py's
 * GovernorateCityFormMixin) gets its city options repopulated whenever the
 * governorate changes. The page's initial render already has the correct
 * options/selection from the server, so this only has to do anything once
 * the user changes the governorate - call Locations.initAll() again if you
 * inject a new form pair after page load.
 */
(function (window) {
  'use strict';

  if (window.Locations) {
    // Script included more than once - keep the first instance.
    return;
  }

  var CITIES_URL = '/dashboard/api/cities/';
  var SHIPPING_FEE_URL = '/dashboard/api/shipping-fee/';

  /** governorateId -> Promise<cities[]>, so repeated selects don't re-fetch. */
  var citiesCache = {};

  function toPositiveInt(value) {
    var n = parseInt(value, 10);
    return Number.isFinite(n) && n > 0 ? n : null;
  }

  /** Cities belonging to a governorate. Always resolves (never rejects); returns [] on error. */
  function getCities(governorateId) {
    var id = toPositiveInt(governorateId);
    if (id === null) return Promise.resolve([]);

    if (!citiesCache[id]) {
      citiesCache[id] = fetch(CITIES_URL + '?governorate=' + id)
        .then(function (response) {
          if (!response.ok) throw new Error('Request failed with status ' + response.status);
          return response.json();
        })
        .then(function (data) {
          return data.cities || [];
        })
        .catch(function (error) {
          delete citiesCache[id]; // don't cache failures - allow a retry later
          if (window.console) window.console.error('Locations.getCities failed:', error);
          return [];
        });
    }

    return citiesCache[id];
  }

  /**
   * Shipping cost for a governorate (and optional city), resolved server-side
   * from the ShippingFee table (city-specific fee first, then the
   * governorate-wide fallback). Resolves to a number, or null if unavailable
   * (no governorate, no configured fee, or a network error).
   */
  function calculateShippingFee(governorateId, cityId) {
    var govId = toPositiveInt(governorateId);
    if (govId === null) return Promise.resolve(null);

    var url = SHIPPING_FEE_URL + '?governorate=' + govId;
    var cid = toPositiveInt(cityId);
    if (cid !== null) url += '&city=' + cid;

    return fetch(url)
      .then(function (response) {
        if (!response.ok) throw new Error('Request failed with status ' + response.status);
        return response.json();
      })
      .then(function (data) {
        return typeof data.fee === 'number' ? data.fee : null;
      })
      .catch(function (error) {
        if (window.console) window.console.error('Locations.calculateShippingFee failed:', error);
        return null;
      });
  }

  /** Rebuilds citySelect's <option>s from `cities`, keeping its blank/placeholder option as-is. */
  function populateCitySelect(citySelect, cities, selectedValue) {
    var blankOption = citySelect.querySelector('option[value=""]');
    var blankHTML = blankOption ? blankOption.outerHTML : '<option value=""></option>';
    var current = selectedValue != null ? String(selectedValue) : citySelect.value;

    citySelect.innerHTML = blankHTML;
    cities.forEach(function (city) {
      var option = document.createElement('option');
      option.value = city.id;
      option.textContent = city.name_en;
      if (String(city.id) === current) option.selected = true;
      citySelect.appendChild(option);
    });

    citySelect.disabled = cities.length === 0;
  }

  /** Wires one governorate select to its dependent city select. */
  function bindGovernorateCity(governorateSelect, citySelect) {
    if (!governorateSelect || !citySelect) return;

    governorateSelect.addEventListener('change', function () {
      // The previously selected city (if any) belongs to the old
      // governorate, so it's never valid here - always reset to blank.
      var governorateId = governorateSelect.value;
      if (!governorateId) {
        populateCitySelect(citySelect, [], '');
        return;
      }
      getCities(governorateId).then(function (cities) {
        populateCitySelect(citySelect, cities, '');
      });
    });
  }

  /** Auto-wires every governorate/city select pair found in `root` (default: whole document). */
  function initAll(root) {
    root = root || document;
    root.querySelectorAll('[data-governorate-select]').forEach(function (governorateSelect) {
      var scope = governorateSelect.closest('form') || root;
      var citySelect = scope.querySelector('[data-city-select]');
      bindGovernorateCity(governorateSelect, citySelect);
    });
  }

  window.Locations = {
    getCities: getCities,
    calculateShippingFee: calculateShippingFee,
    bindGovernorateCity: bindGovernorateCity,
    initAll: initAll,
  };

  document.addEventListener('DOMContentLoaded', function () {
    initAll();
  });
})(window);
