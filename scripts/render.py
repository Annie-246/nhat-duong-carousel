"""Render every <section class="slide"> of a carousel HTML to 1080x1080 PNG, after fitting spacing
to the measured template rhythm, and check layout.

Usage: python -I render.py <carousel.html> <out_dir>
Prints one line per slide with the real gaps; any line with 'WARN' must be fixed before delivery.

Template rhythm (measured on 12 pages of template.pdf, px @1080):
  H2 -> image == image -> text, 40 by default, allowed 27..50
  image height 400..450 ideal (>=300 minimum)
  free space under the text (above y=930) <= 120, else the slide looks empty
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SAFE_BOTTOM = 930  # avatar sits at 986; text must end >= 56px above it

FIT_JS = """
(slide) => {
  const stage = slide.querySelector('.stage');
  if (!stage || stage.classList.contains('mid')) return;
  const top = slide.getBoundingClientRect().top;
  const v = stage.querySelector(':scope > .visual');
  // 1. wrap the illustration block tightly around its images (no hidden air above/below them)
  if (v && v.querySelector('img')) {
    const contentH = c => c.tagName === 'FIGURE'
      ? [...c.children].reduce((a, k) => a + k.getBoundingClientRect().height, 0)
      : c.getBoundingClientRect().height;
    const h = Math.max(...[...v.children].map(contentH));
    if (h < v.getBoundingClientRect().height - 1) { v.style.flex = 'none'; v.style.height = h + 'px'; }
  }
  // 2. distribute leftover space equally to the two gaps (template keeps them equal), max 50
  const last = () => Math.max(...[...stage.children].map(c => c.getBoundingClientRect().bottom)) - top;
  let free = SAFE_BOTTOM - last();
  const imgH = v ? Math.max(0, ...[...v.querySelectorAll('img')].map(i => i.getBoundingClientRect().height)) : 0;
  if (imgH && imgH < 380 && !v.classList.contains('fixed')) stage.style.setProperty('--g', '30px');      // image squeezed: tighten gaps
  else if (free > 0) stage.style.setProperty('--g', Math.min(50, 40 + free / 2) + 'px');
  else if (free < 0) stage.style.setProperty('--g', Math.max(27, 40 + free / 2) + 'px');   // slightly too tall: tighten gaps first
}
""".replace("SAFE_BOTTOM", str(SAFE_BOTTOM))

CHECK_JS = """
(slide) => {
  const warn = [];
  const s = slide.getBoundingClientRect();
  const stage = slide.querySelector('.stage');
  if (!stage) return ['WARN no .stage'];
  const B = s.top + SAFE_BOTTOM, R = s.left + 1022;
  if (stage.scrollHeight > stage.clientHeight + 1) warn.push(`stage overflow ${stage.scrollHeight - stage.clientHeight}px`);
  for (const el of stage.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    if (r.bottom > B + 1) { warn.push(`<${el.tagName.toLowerCase()} class="${el.className}"> hits footer (+${Math.round(r.bottom - B)}px)`); break; }
    if (r.right > R + 1) { warn.push(`<${el.tagName.toLowerCase()}> past right margin (+${Math.round(r.right - R)}px)`); break; }
  }
  const imgs = [...stage.querySelectorAll('img')];
  for (const img of imgs) {
    if (!img.naturalWidth) { warn.push(`broken image ${img.getAttribute('src')}`); continue; }
    const up = img.getBoundingClientRect().width / img.naturalWidth;
    if (up > 1.6 && !img.src.endsWith('.svg')) warn.push(`image upscaled x${up.toFixed(1)} (blurry): ${img.getAttribute('src')}`);
  }
  for (const v of stage.querySelectorAll('.visual')) {
    const vi = [...v.querySelectorAll('img')];
    if (!vi.length || v.classList.contains('fixed')) continue;
    const vr = v.getBoundingClientRect();
    const used = vi.reduce((a, i) => { const r = i.getBoundingClientRect(); return a + r.width * r.height; }, 0);
    if (used / (vr.width * vr.height) < 0.45) warn.push(`illustration fills only ${Math.round(100 * used / (vr.width * vr.height))}% of its block: pick an image with a fitting aspect ratio or another layout`);
  }
  const missing = ['.head', '.visual', '.text'].filter(q => !stage.querySelector(q));
  if (missing.length) warn.push('missing block ' + missing.join(','));

  // real gaps between the 3 blocks
  const head = stage.querySelector('.head'), vis = stage.querySelector(':scope > .visual'), txt = stage.querySelector(':scope > .text');
  const info = [];
  if (head && vis && txt && !stage.querySelector('.text.tight')) {
    const imgTop = Math.min(...[...vis.querySelectorAll('img, table, .cols, .panel, .prompt, .bubbles, .grid2, .win, .tools, .sb')].map(e => e.getBoundingClientRect().top), vis.getBoundingClientRect().top + 9999);
    const imgBot = Math.max(...[...vis.querySelectorAll('img, .cap, table, .cols, .panel, .prompt, .bubbles, .grid2, .win, .tools, .sb')].map(e => e.getBoundingClientRect().bottom), 0);
    const a = Math.round(imgTop - head.getBoundingClientRect().bottom);
    const b = Math.round(txt.getBoundingClientRect().top + 2 - imgBot);
    info.push(`gaps ${a}/${b}`);
    if (Math.abs(a - b) > 3) warn.push(`unequal gaps head->visual ${a} vs visual->text ${b}`);
    if (a < 26 || a > 51) warn.push(`gap ${a}px outside template range 27..50`);
    const ih = Math.round(imgBot - imgTop);
    info.push(`visual h ${ih}`);
    if (vis.querySelector('img') && ih < 300) warn.push(`illustration only ${ih}px tall: cut text or split slide`);
  }
  const free = Math.round(B - Math.max(...[...stage.children].map(c => c.getBoundingClientRect().bottom)));
  info.push(`free bottom ${free}`);
  if (free > 120 && !stage.classList.contains('mid')) warn.push(`slide looks empty (${free}px unused): add content, use a taller image/2 images, or class "mid"`);
  return warn.length ? ['WARN ' + warn.join(' | '), ...info] : ['OK', ...info];
}
""".replace("SAFE_BOTTOM", str(SAFE_BOTTOM))


def main(html: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception:
            browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1200, "height": 1200}, device_scale_factor=1)
        page.goto(Path(html).resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        slides = page.query_selector_all("section.slide")
        for i, sl in enumerate(slides, 1):
            sl.evaluate(FIT_JS)
            msgs = sl.evaluate(CHECK_JS)
            print(f"slide-{i:02d} " + " | ".join(msgs))
            sl.screenshot(path=str(out / f"slide-{i:02d}.png"))
        browser.close()
    print(f"{len(slides)} slides -> {out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1], sys.argv[2])
