/**
 * TailorCV frontend logic.
 *
 * Pure functions (setPreview, triggerDownload, getCurrentPdf) are exported
 * for unit testing. DOM wiring is handled by init(), called automatically
 * when the script loads in a browser context.
 */

let _currentPdfBase64 = null;

/**
 * Returns the most recently received PDF as a base64 string, or null.
 * @returns {string|null}
 */
export function getCurrentPdf() {
  return _currentPdfBase64;
}

/**
 * Updates the PDF preview iframe and stores the base64 for download.
 * @param {HTMLIFrameElement} iframe
 * @param {string} base64
 */
export function setPreview(iframe, base64) {
  iframe.src = 'data:application/pdf;base64,' + base64;
  _currentPdfBase64 = base64;
}

/**
 * Triggers a PDF download using the given base64 string.
 * @param {string|null} base64
 * @param {Document} doc - injected for testability
 */
export function triggerDownload(base64, doc) {
  if (!base64) return;
  const a = doc.createElement('a');
  a.href = 'data:application/pdf;base64,' + base64;
  a.download = 'curriculo.pdf';
  a.click();
}

/**
 * Sets the status message with an optional visual state.
 * @param {HTMLElement} el
 * @param {string} message
 * @param {'ok'|'err'|''} state
 */
function setStatus(el, message, state = '') {
  el.textContent = message;
  el.className = 'status' + (state ? ' ' + state : '');
}

/**
 * Toggles between dark and light theme, persisting the choice.
 */
export function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

/**
 * Wires up buttons to the API endpoints and the theme toggle.
 * Called automatically in browser context.
 */
export function init() {
  const jobDesc      = document.getElementById('job-description');
  const btnGenerate  = document.getElementById('btn-generate');
  const btnLabel     = btnGenerate.querySelector('.btn-label');
  const btnLoading   = btnGenerate.querySelector('.btn-loading');
  const texContent   = document.getElementById('tex-content');
  const btnRecompile = document.getElementById('btn-recompile');
  const btnDownload  = document.getElementById('btn-download');
  const preview      = document.getElementById('preview');
  const status       = document.getElementById('status');
  const btnTheme     = document.getElementById('btn-theme');

  btnTheme.addEventListener('click', toggleTheme);

  btnGenerate.addEventListener('click', async () => {
    const job_description = jobDesc.value.trim();
    if (!job_description) { setStatus(status, 'Cole a descrição da vaga.', 'err'); return; }

    btnGenerate.disabled = true;
    btnLabel.hidden = true;
    btnLoading.hidden = false;
    setStatus(status, 'Gerando currículo…');

    try {
      const res = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_description }),
      });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail); }
      const data = await res.json();

      texContent.value = data.tex_content;
      setPreview(preview, data.pdf_base64);
      btnRecompile.disabled = false;
      btnDownload.disabled = false;
      setStatus(status, 'Currículo gerado com sucesso.', 'ok');
    } catch (err) {
      setStatus(status, 'Erro: ' + err.message, 'err');
    } finally {
      btnGenerate.disabled = false;
      btnLabel.hidden = false;
      btnLoading.hidden = true;
    }
  });

  btnRecompile.addEventListener('click', async () => {
    btnRecompile.disabled = true;
    setStatus(status, 'Recompilando…');

    try {
      const res = await fetch('/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tex_content: texContent.value }),
      });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail); }
      const data = await res.json();

      setPreview(preview, data.pdf_base64);
      btnDownload.disabled = false;
      setStatus(status, 'Recompilado com sucesso.', 'ok');
    } catch (err) {
      setStatus(status, 'Erro: ' + err.message, 'err');
    } finally {
      btnRecompile.disabled = false;
    }
  });

  btnDownload.addEventListener('click', () => {
    triggerDownload(_currentPdfBase64, document);
  });
}

// Auto-init in browser — skipped in test environment
if (typeof document !== 'undefined' && typeof process === 'undefined') {
  init();
}
