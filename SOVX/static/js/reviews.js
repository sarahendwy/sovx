(function () {
  "use strict";

  var root = document.querySelector("[data-reviews-root]");
  var dataEl = document.getElementById("reviews-data");
  if (!root || !dataEl) return;

  var reviews;
  try {
    reviews = JSON.parse(dataEl.textContent);
  } catch (err) {
    return;
  }
  if (!reviews || !reviews.length) return;

  var track = root;
  var slots = {
    left: root.querySelector('[data-slot="left"]'),
    middle: root.querySelector('[data-slot="middle"]'),
    right: root.querySelector('[data-slot="right"]'),
  };
  var prevBtn = document.querySelector("[data-reviews-prev]");
  var nextBtn = document.querySelector("[data-reviews-next]");

  // matches the server-rendered initial markup: left=reviews[0],
  // middle=reviews[1], right=reviews[2]
  var mid = reviews.length > 1 ? 1 : 0;

  function wrap(i) {
    var n = reviews.length;
    return ((i % n) + n) % n;
  }

  function fillCard(el, review) {
    if (!el || !review) return;
    var avatar = el.querySelector('[data-field="avatar"]');
    var name = el.querySelector('[data-field="name"]');
    var dateEl = el.querySelector('[data-field="date"]');
    var text = el.querySelector('[data-field="text"]');
    if (avatar) avatar.src = review.avatar;
    if (name) name.textContent = review.name;
    if (dateEl) dateEl.textContent = review.date;
    if (text) text.textContent = review.description;
  }

  function render() {
    fillCard(slots.left, reviews[wrap(mid - 1)]);
    fillCard(slots.middle, reviews[wrap(mid)]);
    fillCard(slots.right, reviews[wrap(mid + 1)]);
  }

  var animating = false;
  function go(step) {
    if (animating) return;
    animating = true;
    mid = wrap(mid + step);
    track.classList.add("is-updating");
    window.setTimeout(function () {
      render();
      track.classList.remove("is-updating");
      animating = false;
    }, 180);
  }

  if (prevBtn) prevBtn.addEventListener("click", function () { go(-1); });
  if (nextBtn) nextBtn.addEventListener("click", function () { go(1); });

  // swipe support (mobile shows one card at a time - see reviews.css)
  var touchStartX = null;
  track.addEventListener(
    "touchstart",
    function (e) {
      touchStartX = e.changedTouches[0].clientX;
    },
    { passive: true }
  );

  track.addEventListener(
    "touchend",
    function (e) {
      if (touchStartX === null) return;
      var deltaX = e.changedTouches[0].clientX - touchStartX;
      var threshold = 40;
      if (deltaX <= -threshold) {
        go(1);
      } else if (deltaX >= threshold) {
        go(-1);
      }
      touchStartX = null;
    },
    { passive: true }
  );
})();
