/* GTA 6 Italia — share readable directional codes without any tracking. */
(() => {
  "use strict";
  for (const button of document.querySelectorAll("[data-copy-sequence]")) {
    button.addEventListener("click", async () => {
      const value = button.dataset.copySequence || "";
      const feedback = button.parentElement?.querySelector("[data-cheat-feedback]");
      // Never accept arbitrary HTML or URLs from third-party source content.
      if (!/^[↑↓←→ L1R+·]+$/.test(value) || value.length > 150) {
        if (feedback) feedback.textContent = "Sequenza non disponibile.";
        return;
      }
      if (!navigator.clipboard?.writeText) {
        if (feedback) feedback.textContent = "Copia non supportata qui. Usa le frecce visualizzate sulla pagina.";
        return;
      }
      try {
        await navigator.clipboard.writeText(value);
        if (feedback) feedback.textContent = "Sequenza copiata. Inseriscila manualmente con il DualSense.";
      } catch (_) {
        if (feedback) feedback.textContent = "Il browser non consente la copia; segui le icone sopra.";
      }
    });
  }
})();
