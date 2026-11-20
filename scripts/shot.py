"""Screenshot a real web page to use as a carousel illustration.

Usage: python -I shot.py <url> <out.png> [--w 1440] [--h 900] [--scroll 0] [--mobile]
  --scroll N : scroll N px down before the shot (to reach a specific section)
  --mobile   : 430x932 phone viewport (for portrait/split layouts)
"""
import argparse
import sys
from playwright.sync_api import sync_playwright

BLOCK_MARKERS = ["verify you are human", "xác minh bạn là con người", "thực hiện xác minh bảo mật",
                 "just a moment", "checking your browser", "access denied", "enable javascript and cookies",
                 "captcha", "attention required"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out")
    ap.add_argument("--w", type=int, default=1440)
    ap.add_argument("--h", type=int, default=900)
    ap.add_argument("--scroll", type=int, default=0)
    ap.add_argument("--mobile", action="store_true")
    a = ap.parse_args()
    w, h = (430, 932) if a.mobile else (a.w, a.h)
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception:
            browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=2,
                                locale="vi-VN")
        page.goto(a.url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        if a.scroll:
            page.mouse.wheel(0, a.scroll)
        page.wait_for_timeout(2500)  # let hero animations / lazy images settle
        body = page.inner_text("body")[:3000].lower()
        blocked = [m for m in BLOCK_MARKERS if m in body]
        if blocked:
            browser.close()
            sys.exit(f"BLOCKED: bot-check / login page ({blocked[0]!r}). Do NOT use this shot; "
                     "take an official screenshot from the tool's docs/blog/press kit instead.")
        page.screenshot(path=a.out)
        browser.close()
    print(f"saved {a.out} ({w}x{h} @2x)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
