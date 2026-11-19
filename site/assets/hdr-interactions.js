/* GTA VI Italia: copy only the visible three HDR values; no analytics or external calls. */
(() => {
  "use strict";
  for (const button of document.querySelectorAll("button[data-hdr-copy]")) {
    button.addEventListener("click", async () => {
      const values = (button.dataset.hdrCopy || "").split(" · ");
      const status = button.parentElement?.querySelector("[data-hdr-feedback]");
      if (values.length !== 3 || values.some(x => !/^\d{1,5}$/.test(x))) {
        if (status) status.textContent = "Valori non validi: consulta la scheda originale.";
        return;
      }
      const output = "GTA VI — HDR Calibration\n" +
        "Max Brightness: " + values[0] + "\n" +
        "Black Levels: " + values[1] + "\n" +
        "Paper White: " + values[2] + "\n" +
        "Nota: sono valori di partenza o testimonianze community, non calibrazioni certificate.";
      if (!navigator.clipboard?.writeText) {
        if (status) status.textContent = "La copia non è disponibile in questo browser: usa i tre valori mostrati.";
        return;
      }
      try {
        await navigator.clipboard.writeText(output);
        if (status) status.textContent = "Valori copiati con avviso sulla loro affidabilità.";
      } catch (_) {
        if (status) status.textContent = "Copia non consentita nel browser: consulta i valori sopra.";
      }
    });
  }
})();
