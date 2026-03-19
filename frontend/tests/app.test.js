/**
 * Tests for frontend/app.js pure functions.
 *
 * app.js exports: setPreview(iframe, base64), triggerDownload(base64, doc)
 * The DOM wiring (event listeners) is handled by init() and is not unit-tested here.
 */

import { setPreview, triggerDownload, getCurrentPdf, toggleTheme } from '../app.js';

describe('setPreview', () => {
  it('sets iframe src to a PDF data URI', () => {
    const iframe = { src: '' };
    setPreview(iframe, 'ABC123');
    expect(iframe.src).toBe('data:application/pdf;base64,ABC123');
  });

  it('stores the current base64 for later retrieval', () => {
    const iframe = { src: '' };
    setPreview(iframe, 'XYZ789');
    expect(getCurrentPdf()).toBe('XYZ789');
  });
});

describe('triggerDownload', () => {
  it('does nothing when base64 is null', () => {
    // Should not throw
    expect(() => triggerDownload(null, document)).not.toThrow();
  });

  it('creates an anchor with the correct href and download attribute', () => {
    const clicks = [];
    const fakeDoc = {
      createElement: () => ({
        href: '',
        download: '',
        click() { clicks.push(this); },
      }),
    };

    triggerDownload('MYPDF64', fakeDoc);

    expect(clicks).toHaveLength(1);
    expect(clicks[0].href).toBe('data:application/pdf;base64,MYPDF64');
    expect(clicks[0].download).toBe('curriculo.pdf');
  });
});

describe('toggleTheme', () => {
  it('switches from dark to light', () => {
    document.documentElement.setAttribute('data-theme', 'dark');
    toggleTheme();
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });

  it('switches from light to dark', () => {
    document.documentElement.setAttribute('data-theme', 'light');
    toggleTheme();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });
});
