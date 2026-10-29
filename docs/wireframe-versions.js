/* Review versions are separate pages; v0 retains its original supporting assets. */
(function () {
  'use strict';
  const selector = document.getElementById('wireframe-version');
  selector.addEventListener('change', () => {
    const destination = selector.value;
    if (destination === 'wireframe.html' || destination === 'wireframe-v0.html') {
      window.location.assign(new URL(destination, window.location.href).href);
    }
  });
  // Browsers can restore form values on Back; always identify the page being viewed.
  window.addEventListener('pageshow', () => {
    selector.value = window.location.pathname.endsWith('/wireframe-v0.html') ? 'wireframe-v0.html' : 'wireframe.html';
  });
})();
