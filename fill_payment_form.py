#!/usr/bin/env python3
"""SignalWire payment form automation with cookie-based session restore."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.async_api import Browser, BrowserContext, Frame, Locator, Page, async_playwright


ROOT = Path(__file__).resolve().parent
COOKIES_PATH = ROOT / "cookies.json"
COOKIES_TEMPLATE_PATH = ROOT / "cookies.template.json"
CONFIG_PATH = ROOT / "config.json"
CONFIG_TEMPLATE_PATH = ROOT / "config.json.example"

PLACEHOLDER_MARKERS = (
    "HOT HNA",
    "PASTE",
    "REPLACE_WITH",
    "paste value",
    "paste cookies",
    "YOUR_EMAIL",
    "YOUR_PASSWORD",
    "email@example.com",
    "your_password",
    "ton_email",
    "ton_password",
)


def setup_logging(log_file: str) -> logging.Logger:
    log_path = ROOT / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("signalwire_automation")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def load_json(path: Path, label: str) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def ensure_cookies_file() -> None:
    """Create cookies.json from template so the user has a clear place to paste cookies."""
    if COOKIES_PATH.exists():
        return

    if COOKIES_TEMPLATE_PATH.exists():
        COOKIES_PATH.write_text(COOKIES_TEMPLATE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        return

    # Fallback minimal template
    template = """[
  {
    "name": "_signalwire_session",
    "value": "HOT HNA COOKIES DYALEK — paste value dyal session hna",
    "domain": ".signalwire.com",
    "path": "/",
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  }
]
"""
    COOKIES_PATH.write_text(template, encoding="utf-8")


def cookies_still_placeholder(raw_cookies: list[dict[str, Any]]) -> bool:
    for cookie in raw_cookies:
        if not isinstance(cookie, dict):
            continue
        value = str(cookie.get("value", ""))
        if any(marker.lower() in value.lower() for marker in PLACEHOLDER_MARKERS):
            return True
    return False


def ensure_config_file() -> None:
    """Create config.json from example so the user can edit email/password."""
    if CONFIG_PATH.exists():
        return
    if CONFIG_TEMPLATE_PATH.exists():
        CONFIG_PATH.write_text(CONFIG_TEMPLATE_PATH.read_text(encoding="utf-8"), encoding="utf-8")


def is_placeholder(value: str) -> bool:
    cleaned = value.strip()
    if not cleaned:
        return True
    return any(marker.lower() in cleaned.lower() for marker in PLACEHOLDER_MARKERS)


def account_credentials_ready(config: dict[str, Any]) -> bool:
    account = config.get("account", {})
    email = str(account.get("email", "")).strip()
    password = str(account.get("password", "")).strip()
    return bool(email and password and not is_placeholder(email) and not is_placeholder(password))


def print_account_instructions() -> None:
    print("\n" + "=" * 60)
    print("3MER ACCOUNT DYALEK F config.json:")
    print(f"  -> {CONFIG_PATH}")
    print("\n\"account\": {")
    print('    "email": "email dyalek hna",')
    print('    "password": "password dyalek hna"')
    print("}")
    print("\nMen ba3d: double-click run.bat")
    print("=" * 60 + "\n")


def print_cookies_instructions() -> None:
    print("\n" + "=" * 60)
    print("FIN THOT COOKIES DYAL ACCOUNT DYALEK:")
    print(f"  -> {COOKIES_PATH}")
    print("\n1) Connecté f SignalWire f Chrome")
    print("2) F12 -> Application -> Cookies -> signalwire.com")
    print("3) Copier name + value dial cookies")
    print(f"4) Paste f file: {COOKIES_PATH}")
    print("5) 3awed run: python fill_payment_form.py")
    print("\nTalimt kamla: COOKIES_HNA.md")
    print("=" * 60 + "\n")


def normalize_cookies(raw_cookies: list[dict[str, Any]], base_url: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for cookie in raw_cookies:
        item = {key: value for key, value in cookie.items() if not str(key).startswith("_")}
        if "name" not in item or "value" not in item:
            continue
        if "url" not in item and ("domain" not in item or "path" not in item):
            item.setdefault("url", base_url)
        normalized.append(item)
    return normalized


async def save_error_screenshot(page: Page | None, screenshot_dir: Path, name: str, logger: logging.Logger) -> None:
    if page is None or page.is_closed():
        return
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = screenshot_dir / f"{name}_{timestamp}.png"
    try:
        await page.screenshot(path=str(path), full_page=True)
        logger.error("Screenshot saved: %s", path)
    except Exception as exc:
        logger.error("Failed to save screenshot: %s", exc)


async def is_visible(locator: Locator, timeout: int = 1500) -> bool:
    try:
        await locator.first.wait_for(state="visible", timeout=timeout)
        return True
    except Exception:
        return False


async def save_context_cookies(context: BrowserContext, base_url: str, logger: logging.Logger) -> None:
    cookies = await context.cookies()
    if not cookies:
        return
    serializable = []
    for cookie in cookies:
        item = {key: cookie[key] for key in cookie if key in {
            "name", "value", "domain", "path", "expires", "httpOnly", "secure", "sameSite"
        }}
        serializable.append(item)
    COOKIES_PATH.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    logger.info("Saved %s cookie(s) to %s for next run", len(serializable), COOKIES_PATH)


async def login_with_credentials(page: Page, config: dict[str, Any], logger: logging.Logger) -> bool:
    account = config.get("account", {})
    email = str(account.get("email", "")).strip()
    password = str(account.get("password", "")).strip()
    base_url = config.get("base_url", "https://us11111111.signalwire.com")

    login_urls = config.get("login_urls") or [
        config.get("login_url"),
        f"{base_url}/users/sign_in",
        f"{base_url}/login",
        f"{base_url}/accounts/sign_in",
        "https://signalwire.com/accounts/sign_in",
    ]
    login_urls = [url for url in login_urls if url]

    email_selectors = config.get("login_email_selectors", [
        "input[type='email']",
        "input[name*='email' i]",
        "input[id*='email' i]",
        "input[autocomplete='username']",
        "input[name='user[email]']",
    ])
    password_selectors = config.get("login_password_selectors", [
        "input[type='password']",
        "input[name*='password' i]",
        "input[id*='password' i]",
        "input[name='user[password]']",
    ])
    submit_selectors = config.get("login_submit_selectors", [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Sign in')",
        "button:has-text('Log in')",
        "button:has-text('Login')",
    ])

    for login_url in login_urls:
        logger.info("Trying login page: %s", login_url)
        try:
            await page.goto(login_url, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_load_state("networkidle", timeout=30000)
        except Exception as exc:
            logger.warning("Could not open %s: %s", login_url, exc)
            continue

        email_field = await find_first_visible(page, email_selectors)
        password_field = await find_first_visible(page, password_selectors)
        if email_field is None or password_field is None:
            logger.warning("Login form not found on %s", login_url)
            continue

        logger.info("Filling login credentials")
        await email_field.fill(email)
        await password_field.fill(password)

        submit = await find_first_visible(page, submit_selectors)
        if submit is not None:
            await submit.click()
        else:
            await password_field.press("Enter")

        try:
            await page.wait_for_load_state("networkidle", timeout=45000)
        except Exception:
            pass

        await page.wait_for_timeout(2000)

        if await verify_session(page, config, logger):
            logger.info("Login successful")
            return True

        logger.warning("Login attempt on %s did not produce a valid session", login_url)

    return False


async def authenticate(
    page: Page,
    context: BrowserContext,
    config: dict[str, Any],
    logger: logging.Logger,
) -> bool:
    base_url = config.get("base_url", "https://us11111111.signalwire.com")
    auth_mode = str(config.get("auth_mode", "auto")).lower()

    use_login = auth_mode in {"auto", "login", "credentials"} and account_credentials_ready(config)
    use_cookies = auth_mode in {"auto", "cookies"}

    if use_login:
        logger.info("Authentication mode: login with email/password")
        if await login_with_credentials(page, config, logger):
            await save_context_cookies(context, base_url, logger)
            return True
        logger.warning("Login failed, trying cookies fallback...")
        await context.clear_cookies()

    if use_cookies and COOKIES_PATH.exists():
        try:
            raw_cookies = load_json(COOKIES_PATH, "cookies.json")
            if not cookies_still_placeholder(raw_cookies):
                cookies = normalize_cookies(raw_cookies, base_url)
                logger.info("Importing %s cookie(s) from %s", len(cookies), COOKIES_PATH)
                await context.add_cookies(cookies)
                if await verify_session(page, config, logger):
                    logger.info("Cookie session restored successfully")
                    return True
                logger.error("Cookies imported but session is invalid")
        except Exception as exc:
            logger.error("Cookie auth failed: %s", exc)

    return False


async def verify_session(page: Page, config: dict[str, Any], logger: logging.Logger) -> bool:
    check_url = config.get("session_check_url") or config.get("base_url")
    logger.info("Verifying authenticated session at %s", check_url)

    response = await page.goto(check_url, wait_until="domcontentloaded")
    await page.wait_for_load_state("networkidle", timeout=30000)

    if response and response.status >= 400:
        logger.error("Session check failed with HTTP status %s", response.status)
        return False

    for selector in config.get("login_indicators", []):
        if await is_visible(page.locator(selector)):
            logger.error("Login indicator detected (%s) — session is invalid", selector)
            return False

    valid_selectors = config.get("session_valid_selectors", [])
    if valid_selectors:
        for selector in valid_selectors:
            if await is_visible(page.locator(selector)):
                logger.info("Session valid — found authenticated marker: %s", selector)
                return True
        logger.warning("No explicit authenticated marker found; continuing with URL-based check")

    current_url = page.url.lower()
    if any(token in current_url for token in ("sign_in", "login", "auth")):
        logger.error("Redirected to login page — session is invalid")
        return False

    logger.info("Session appears valid (no login redirect detected)")
    return True


async def find_first_visible(page_or_frame: Page | Frame, selectors: list[str]) -> Locator | None:
    for selector in selectors:
        locator = page_or_frame.locator(selector)
        if await is_visible(locator):
            return locator.first
    return None


async def fill_text_field(
    page_or_frame: Page | Frame,
    selectors: list[str],
    value: str,
    field_name: str,
    logger: logging.Logger,
) -> bool:
    locator = await find_first_visible(page_or_frame, selectors)
    if locator is None:
        logger.warning("Field not found: %s", field_name)
        return False

    await locator.click()
    await locator.fill(value)
    actual = await locator.input_value()
    if actual.strip() != value.strip():
        logger.error("Verification failed for %s (expected=%r, actual=%r)", field_name, value, actual)
        return False

    logger.info("Filled and verified field: %s", field_name)
    return True


async def fill_select_field(
    page: Page,
    selectors: list[str],
    value: str,
    field_name: str,
    logger: logging.Logger,
) -> bool:
    locator = await find_first_visible(page, selectors)
    if locator is None:
        logger.warning("Select field not found: %s", field_name)
        return False

    tag_name = await locator.evaluate("el => el.tagName.toLowerCase()")
    if tag_name == "select":
        try:
            await locator.select_option(label=value)
        except Exception:
            await locator.select_option(value=value)
    else:
        await locator.fill(value)

    logger.info("Filled and verified field: %s", field_name)
    return True


async def discover_form_fields(page: Page, logger: logging.Logger) -> list[dict[str, str]]:
    fields = await page.evaluate(
        """() => {
            const result = [];
            const nodes = document.querySelectorAll('input, select, textarea');
            for (const node of nodes) {
                const style = window.getComputedStyle(node);
                if (style.display === 'none' || style.visibility === 'hidden') continue;
                result.push({
                    tag: node.tagName.toLowerCase(),
                    type: node.getAttribute('type') || '',
                    name: node.getAttribute('name') || '',
                    id: node.id || '',
                    placeholder: node.getAttribute('placeholder') || '',
                    autocomplete: node.getAttribute('autocomplete') || ''
                });
            }
            return result;
        }"""
    )
    logger.info("Detected %s visible form fields on main page", len(fields))
    for field in fields:
        logger.info(
            "Field: tag=%s type=%s name=%s id=%s placeholder=%s autocomplete=%s",
            field.get("tag"),
            field.get("type"),
            field.get("name"),
            field.get("id"),
            field.get("placeholder"),
            field.get("autocomplete"),
        )
    return fields


async def fill_payment_iframes(
    page: Page,
    config: dict[str, Any],
    payment_data: dict[str, str],
    logger: logging.Logger,
) -> dict[str, bool]:
    results: dict[str, bool] = {key: False for key in payment_data}
    iframe_patterns = config.get("payment_iframe_patterns", [])
    payment_patterns = config.get("payment_field_patterns", {})

    frames = page.frames
    logger.info("Scanning %s frames for payment fields", len(frames))

    candidate_frames: list[Frame] = []
    for frame in frames:
        if frame == page.main_frame:
            continue
        frame_name = (frame.name or "").lower()
        frame_url = (frame.url or "").lower()
        if any(token in frame_name or token in frame_url for token in ("stripe", "card", "payment", "secure")):
            candidate_frames.append(frame)

    if not candidate_frames:
        for pattern in iframe_patterns:
            iframe_locator = page.locator(pattern)
            count = await iframe_locator.count()
            for index in range(count):
                handle = await iframe_locator.nth(index).element_handle()
                if handle is None:
                    continue
                frame = await handle.content_frame()
                if frame is not None:
                    candidate_frames.append(frame)

    candidate_frames = list(dict.fromkeys(candidate_frames))
    logger.info("Found %s candidate payment iframe(s)", len(candidate_frames))

    for frame in candidate_frames:
        logger.info("Inspecting iframe: name=%s url=%s", frame.name, frame.url)
        for field_key, selectors in payment_patterns.items():
            if results.get(field_key):
                continue
            value = payment_data.get(field_key, "")
            if not value:
                continue
            success = await fill_text_field(frame, selectors, value, f"payment.{field_key}", logger)
            results[field_key] = success

    return results


async def fill_main_form(page: Page, config: dict[str, Any], logger: logging.Logger) -> dict[str, bool]:
    form_data = config.get("form", {})
    mappings = config.get("field_mappings", {})
    results: dict[str, bool] = {}

    await discover_form_fields(page, logger)

    for field_name in ("name", "billing_address", "city", "country", "state", "postal_code"):
        value = form_data.get(field_name, "")
        selectors = mappings.get(field_name, [])
        if not value or not selectors:
            continue

        if field_name == "country":
            results[field_name] = await fill_select_field(page, selectors, value, field_name, logger)
        else:
            results[field_name] = await fill_text_field(page, selectors, value, field_name, logger)

    payment_data = form_data.get("payment", {})
    if payment_data:
        payment_results = await fill_payment_iframes(page, config, payment_data, logger)
        for key, ok in payment_results.items():
            results[f"payment.{key}"] = ok

        for field_key, selectors in config.get("payment_field_patterns", {}).items():
            if payment_results.get(field_key):
                continue
            value = payment_data.get(field_key, "")
            if not value:
                continue
            success = await fill_text_field(page, selectors, value, f"payment.{field_key}", logger)
            results[f"payment.{field_key}"] = success

    return results


async def run() -> int:
    ensure_config_file()

    if not CONFIG_PATH.exists():
        print_account_instructions()
        print(f"ERROR: config.json not found at {CONFIG_PATH}", file=sys.stderr)
        return 1

    config = load_json(CONFIG_PATH, "config.json")
    logger = setup_logging(config.get("log_file", "automation.log"))
    screenshot_dir = ROOT / config.get("screenshot_dir", "screenshots")

    base_url = config.get("base_url", "https://us11111111.signalwire.com")
    target_url = config.get("target_url", f"{base_url}/payment_methods/new")

    logger.info("Starting SignalWire payment form automation")
    logger.info("Loading config from %s", CONFIG_PATH)

    if not account_credentials_ready(config):
        ensure_cookies_file()
        if COOKIES_PATH.exists():
            try:
                raw = load_json(COOKIES_PATH, "cookies.json")
                if cookies_still_placeholder(raw):
                    print_account_instructions()
                    print_cookies_instructions()
                    print(
                        f"ERROR: 3mer account f {CONFIG_PATH} wla cookies f {COOKIES_PATH}",
                        file=sys.stderr,
                    )
                    return 1
            except Exception:
                print_account_instructions()
                return 1
        else:
            print_account_instructions()
            return 1

    browser: Browser | None = None
    context: BrowserContext | None = None
    page: Page | None = None

    try:
        async with async_playwright() as playwright:
            logger.info("Launching Chromium browser (tab ghadi ytftah)")
            browser = await playwright.chromium.launch(
                headless=config.get("headless", False),
                slow_mo=config.get("slow_mo", 100),
            )

            context = await browser.new_context()
            page = await context.new_page()

            if not await authenticate(page, context, config, logger):
                await save_error_screenshot(page, screenshot_dir, "auth_failed", logger)
                print("ERROR: Ma qdrnach ndkhlou l account. Chouf email/password f config.json", file=sys.stderr)
                logger.error("Authentication failed")
                return 1

            logger.info("Navigating to billing page: %s", target_url)
            response = await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=45000)
            logger.info("Billing page loaded (status=%s)", response.status if response else "unknown")

            fill_results = await fill_main_form(page, config, logger)

            logger.info("Field fill summary:")
            for field_name, ok in fill_results.items():
                status = "OK" if ok else "FAILED"
                logger.info("  - %s: %s", field_name, status)

            failed = [name for name, ok in fill_results.items() if not ok]
            if failed:
                await save_error_screenshot(page, screenshot_dir, "field_fill_errors", logger)
                logger.warning("Some fields could not be filled: %s", ", ".join(failed))

            print("\n" + "=" * 60)
            print("Browser ma7loul — review form dial billing.")
            print("Press ENTER bash tsed browser (ma tsubmitich ila ma bghitich).")
            print("=" * 60)
            await asyncio.to_thread(input, "Press ENTER to close browser... ")

            return 0

    except Exception as exc:
        logging.getLogger("signalwire_automation").exception("Unhandled error: %s", exc)
        await save_error_screenshot(page, screenshot_dir, "unhandled_error", logger)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    finally:
        if context is not None:
            await context.close()
        if browser is not None:
            await browser.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
