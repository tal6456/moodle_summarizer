"""Helpers for logging into BGU Moodle and extracting lecture video links."""

from __future__ import annotations

from urllib.parse import urljoin

from playwright.async_api import Page


MOODLE_LOGIN_URL = "https://moodle2.bgu.ac.il/moodle/login/index.php"
VIDEO_HOST_MARKERS = ("panopto", "kaltura")
VIDEO_PATH_MARKERS = ("video", "videoplayer", "watch", "stream")
VIDEO_FILE_EXTENSIONS = (".mp4", ".m3u8", ".webm")
MAX_LOGIN_VERIFICATION_ATTEMPTS = 15
LOGIN_POLL_INTERVAL_MS = 1000


async def login_to_moodle(page: Page, username: str, password: str) -> None:
    """Log into BGU Moodle using the provided Playwright page."""
    await page.goto(MOODLE_LOGIN_URL, wait_until="networkidle")
    await page.wait_for_selector('input[name="username"]')
    await page.wait_for_selector('input[name="password"]')
    await page.fill('input[name="username"]', username)
    await page.fill('input[name="password"]', password)
    await page.click('button[type="submit"], input[type="submit"]')
    await page.wait_for_load_state("domcontentloaded")

    for _ in range(MAX_LOGIN_VERIFICATION_ATTEMPTS):
        login_state = await page.evaluate(
            """() => {
                const success = Boolean(
                    document.querySelector('[data-user-id], .usermenu, a[href*="logout"]')
                ) || !Boolean(document.querySelector('input[name="username"]'));
                const error = Boolean(
                    document.querySelector('.loginerrors, .alert-danger, [data-rel="error"]')
                );
                return { success, error };
            }"""
        )
        if login_state["success"]:
            return
        if login_state["error"]:
            raise RuntimeError("Moodle login failed: invalid credentials or login error displayed.")
        await page.wait_for_timeout(LOGIN_POLL_INTERVAL_MS)

    raise RuntimeError("Moodle login status could not be confirmed after submission.")


async def get_lecture_links(page: Page, course_url: str) -> list[str]:
    """Return unique video-like lecture links found on a Moodle course page."""
    await page.goto(course_url, wait_until="domcontentloaded")
    await page.wait_for_load_state("networkidle")

    candidates: list[str] = await page.evaluate(
        """() => {
            const links = [];
            for (const a of document.querySelectorAll("a[href]")) {
                links.push(a.href);
            }
            for (const frame of document.querySelectorAll("iframe[src], video[src], source[src]")) {
                links.push(frame.src);
            }
            for (const video of document.querySelectorAll("video")) {
                if (video.currentSrc) {
                    links.push(video.currentSrc);
                }
            }
            return links.filter(Boolean);
        }"""
    )

    lecture_links: list[str] = []
    seen: set[str] = set()
    for raw in candidates:
        full_url = urljoin(course_url, raw).strip()
        lowered = full_url.lower()
        is_video_link = (
            any(marker in lowered for marker in VIDEO_HOST_MARKERS)
            or lowered.endswith(VIDEO_FILE_EXTENSIONS)
            or any(marker in lowered for marker in VIDEO_PATH_MARKERS)
        )
        if is_video_link and full_url not in seen:
            seen.add(full_url)
            lecture_links.append(full_url)

    return lecture_links
