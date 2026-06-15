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
)

SAMESITE_MAP = {
    "strict": "Strict",
    "lax": "Lax",
    "none": "None",
    "no_restriction": "None",
    "unspecified": "Lax",
    "default": "Lax",
}

DEFAULT_FIXED_BILLING = {
    "name": "david alaba",
    "billing_address": "New York",
    "city": "New York",
    "country": "United States",
    "state": "NY",
    "postal_code": "10080",
}


def setup_logging(log_file: str) -> logging.Logger:
    logger = logging.getLogger("signalwire_automation")
    if logger.handlers:
        return logger

    log_path = ROOT / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.setLevel(logging.INFO)
    logger.propagate = False

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
    """Create config.json from example (URLs + form — ma khassk tbeddlha)."""
    if CONFIG_PATH.exists():
        return
    if CONFIG_TEMPLATE_PATH.exists():
        CONFIG_PATH.write_text(CONFIG_TEMPLATE_PATH.read_text(encoding="utf-8"), encoding="utf-8")


def load_config() -> dict[str, Any]:
    ensure_config_file()
    if CONFIG_PATH.exists():
        return load_json(CONFIG_PATH, "config.json")
    if CONFIG_TEMPLATE_PATH.exists():
        return load_json(CONFIG_TEMPLATE_PATH, "config.json.example")
    return {
        "base_url": "https://us11111111.signalwire.com",
        "cookie_start_url": "https://signalwire.com",
        "target_url": "https://us11111111.signalwire.com/payment_methods/new",
        "session_check_url": "https://us11111111.signalwire.com/payment_methods/new",
        "headless": False,
        "slow_mo": 0,
        "screenshot_dir": "screenshots",
        "log_file": "automation.log",
    }


def print_cookies_instructions() -> None:
    print("\n" + "=" * 60)
    print("FIN THOT COOKIES DYAL ACCOUNT DYALEK:")
    print(f"  -> {COOKIES_PATH}")
    print("\n1) Connecté f SignalWire f Chrome")
    print("2) F12 -> Application -> Cookies")
    print("   -> id.signalwire.com  (IMPORTANT)")
    print("   -> us11111111.signalwire.com")
    print("   -> .signalwire.com")
    print("3) Copier name + value dial cookies")
    print(f"4) Paste f file: {COOKIES_PATH}")
    print("5) 3awed double-click run.bat")
    print("=" * 60 + "\n")


def normalize_samesite(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text in ("Strict", "Lax", "None"):
        return text
    return SAMESITE_MAP.get(text.lower())


def normalize_cookies(raw_cookies: list[dict[str, Any]], base_url: str) -> list[dict[str, Any]]:
    allowed_keys = {"name", "value", "domain", "path", "expires", "httpOnly", "secure", "sameSite", "url"}
    normalized: list[dict[str, Any]] = []

    for cookie in raw_cookies:
        if not isinstance(cookie, dict):
            continue

        item = {key: value for key, value in cookie.items() if not str(key).startswith("_")}
        if "name" not in item or "value" not in item:
            continue

        if "expirationDate" in item and "expires" not in item:
            item["expires"] = int(float(item["expirationDate"]))
        item.pop("expirationDate", None)
        item.pop("hostOnly", None)
        item.pop("session", None)
        item.pop("storeId", None)
        item.pop("partitionKey", None)

        if "sameSite" in item:
            fixed = normalize_samesite(item["sameSite"])
            if fixed:
                item["sameSite"] = fixed
            else:
                item.pop("sameSite")

        if "expires" in item:
            try:
                item["expires"] = int(float(item["expires"]))
            except (TypeError, ValueError):
                item.pop("expires")

        item = {key: value for key, value in item.items() if key in allowed_keys}

        if "url" not in item and ("domain" not in item or "path" not in item):
            item.setdefault("url", base_url)
        if "path" not in item:
            item["path"] = "/"

        normalized.append(item)

    return normalized


def get_fixed_billing(config: dict[str, Any]) -> dict[str, str]:
    billing = dict(DEFAULT_FIXED_BILLING)
    billing.update(config.get("fixed_billing", {}))
    return billing


def build_payment_data(card: str, month: str, year: str, cvc: str, cardholder_name: str) -> dict[str, str]:
    month_int = int(month)
    year_text = str(year).strip()
    year_short = year_text[-2:] if len(year_text) >= 2 else year_text
    expiry = f"{month_int:02d}/{year_short}"
    return {
        "card_number": card.strip().replace(" ", ""),
        "expiry": expiry,
        "cvc": cvc.strip(),
        "cardholder_name": cardholder_name,
    }


def merge_form_with_card(config: dict[str, Any], payment_data: dict[str, str]) -> dict[str, Any]:
    merged = json.loads(json.dumps(config))
    billing = get_fixed_billing(config)
    merged.setdefault("form", {})
    merged["form"].update(billing)
    merged["form"]["payment"] = payment_data
    return merged


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


async def is_visible(locator: Locator, timeout: int = 800) -> bool:
    try:
        await locator.first.wait_for(state="visible", timeout=timeout)
        return True
    except Exception:
        return False


async def quick_wait(page: Page, ms: int = 80) -> None:
    await page.wait_for_timeout(ms)


async def goto_fast(page: Page, url: str, *, wait: str = "commit") -> None:
    await page.goto(url, wait_until=wait, timeout=20000)


async def goto_payment_form(page: Page, config: dict[str, Any], logger: logging.Logger, *, reload: bool = False) -> None:
    url = config.get("target_url", f"{config.get('base_url')}/payment_methods/new")
    logger.info("Go payment page: %s", url)
    await goto_fast(page, url, wait="domcontentloaded")
    await quick_wait(page, 80)


async def authenticate_with_cookies(
    page: Page,
    context: BrowserContext,
    config: dict[str, Any],
    logger: logging.Logger,
) -> bool:
    """signalwire.com → import cookies → payment_methods/new"""
    base_url = config.get("base_url", "https://us11111111.signalwire.com")
    target_url = config.get("target_url", f"{base_url}/payment_methods/new")
    start_url = config.get("cookie_start_url", "https://signalwire.com")

    if not COOKIES_PATH.exists():
        logger.error("cookies.json not found")
        return False

    try:
        raw_cookies = load_json(COOKIES_PATH, "cookies.json")
    except Exception as exc:
        logger.error("Failed to read cookies.json: %s", exc)
        return False

    if cookies_still_placeholder(raw_cookies):
        logger.error("cookies.json still has placeholder values")
        return False

    cookies = normalize_cookies(raw_cookies, base_url)
    if not cookies:
        logger.error("No valid cookies found in cookies.json")
        return False

    logger.info("Step 1: Open tab %s", start_url)
    await goto_fast(page, start_url, wait="commit")
    await quick_wait(page, 100)

    logger.info("Step 2: Import %s cookie(s)", len(cookies))
    await context.add_cookies(cookies)

    logger.info("Step 3: Redirect %s", target_url)
    await goto_fast(page, target_url, wait="domcontentloaded")
    await quick_wait(page, 120)

    if await verify_session(page, config, logger):
        logger.info("Payment page ready")
        return True

    logger.error("Session invalid (url=%s)", page.url)
    return False


async def navigate_to_targets(page: Page, config: dict[str, Any], logger: logging.Logger) -> None:
    """Already on payment page after auth — skip extra redirects."""
    target = config.get("target_url", "")
    if target and "payment_methods/new" in page.url:
        logger.info("Already on payment page — skip redirect")
        return
    await goto_payment_form(page, config, logger)


async def verify_session(page: Page, config: dict[str, Any], logger: logging.Logger) -> bool:
    current_url = page.url.lower()
    if any(token in current_url for token in ("sign_in", "login", "session/new")):
        logger.error("Login redirect (url=%s)", page.url)
        return False

    if "payment_methods" in current_url:
        return True

    add_card = page.locator("input[type='submit'][name='commit'][value='Add Card']")
    if await is_visible(add_card, timeout=2000):
        return True

    return "login" not in current_url and "id.signalwire.com" not in current_url


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

    await locator.fill(value, timeout=3000)
    try:
        actual = await locator.input_value()
        if actual.strip() != value.strip():
            logger.warning("Verify skip %s (expected=%r got=%r)", field_name, value, actual)
    except Exception:
        pass

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

    if not config.get("fast_mode", True):
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


async def click_add_card(page: Page, config: dict[str, Any], logger: logging.Logger) -> bool:
    submit_selectors = config.get("submit_selectors", [
        "input[type='submit'][name='commit'][value='Add Card']",
        "input.btn.btn-confirm[value='Add Card']",
        "input[data-disable-with='Processing...'][value='Add Card']",
        "input[type='submit'][name='commit']",
        "input[type='submit'].btn-confirm",
        "input[type='submit']",
        "button[type='submit']",
    ])

    for selector in submit_selectors:
        locator = page.locator(selector).first
        try:
            await locator.wait_for(state="visible", timeout=3000)
            await locator.scroll_into_view_if_needed()
            await locator.click(timeout=5000)
            logger.info("Clicked Add Card: %s", selector)
            return True
        except Exception:
            continue

    try:
        await page.locator("input[value='Add Card']").first.click(force=True, timeout=3000)
        logger.info("Clicked Add Card (force)")
        return True
    except Exception as exc:
        logger.error("Add Card button not clickable: %s", exc)
        return False


async def submit_and_check_card(page: Page, config: dict[str, Any], logger: logging.Logger) -> dict[str, Any]:
    success_selectors = config.get("success_selectors", [
        ".alert-success",
        "text=successfully",
        "text=added",
    ])
    error_selectors = config.get("error_selectors", [
        ".alert-danger",
        "text=declined",
        "text=The payment was declined",
        "text=invalid",
        "text=failed",
    ])

    if not await click_add_card(page, config, logger):
        return {"submitted": False, "added": False, "message": "Add Card button not found"}

    await quick_wait(page, 1500)

    for selector in error_selectors:
        if await is_visible(page.locator(selector), timeout=2000):
            text = (await page.locator(selector).first.inner_text()).strip()
            logger.error("Card error detected: %s", text)
            return {"submitted": True, "added": False, "message": text or "Card not added (error on page)"}

    for selector in success_selectors:
        if await is_visible(page.locator(selector), timeout=2000):
            text = (await page.locator(selector).first.inner_text()).strip()
            logger.info("Card success detected: %s", text)
            return {"submitted": True, "added": True, "message": text or "Card added successfully"}

    current_url = page.url.lower()
    if "/payment_methods/new" not in current_url:
        logger.info("Redirected after submit — treating as success: %s", page.url)
        return {"submitted": True, "added": True, "message": "Card likely added (redirected after submit)"}

    body_text = (await page.locator("body").inner_text()).lower()
    if any(word in body_text for word in ("declined", "invalid card", "failed", "error")):
        return {"submitted": True, "added": False, "message": "Card not added (error text on page)"}

    return {"submitted": True, "added": False, "message": "Submitted but could not confirm if card was added"}


class PersistentBrowserSession:
    """Tab wa7da — browser kaybqa ma7loul, /chk kayredirect ghir l payment form."""

    def __init__(self) -> None:
        self._playwright: Any = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._ready = False
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        await safe_close(self._browser, self._context)
        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception:
                pass
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._ready = False

    async def _ensure_browser(self, config: dict[str, Any], logger: logging.Logger) -> Page:
        if self._page is not None and not self._page.is_closed():
            return self._page

        await self.close()
        logger.info("Opening browser tab")
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=False,
            slow_mo=0,
        )
        self._context = await self._browser.new_context(no_viewport=True)
        self._page = await self._context.new_page()
        await self._page.bring_to_front()
        self._ready = False
        return self._page

    async def run_card(
        self,
        card_number: str,
        month: str,
        year: str,
        cvc: str,
    ) -> dict[str, Any]:
        async with self._lock:
            config = load_config()
            logger = setup_logging(config.get("log_file", "automation.log"))
            screenshot_dir = ROOT / config.get("screenshot_dir", "screenshots")

            result: dict[str, Any] = {
                "success": False,
                "card_added": False,
                "message": "",
                "fill_results": {},
                "screenshot": None,
                "reused_tab": self._ready,
            }

            billing = get_fixed_billing(config)
            payment = build_payment_data(card_number, month, year, cvc, billing["name"])
            config = merge_form_with_card(config, payment)

            try:
                page = await self._ensure_browser(config, logger)

                if not self._ready:
                    if not await authenticate_with_cookies(page, self._context, config, logger):
                        await save_error_screenshot(page, screenshot_dir, "invalid_cookies", logger)
                        result["message"] = "Cookies invalid — tab ma7loul, jib cookies jdad"
                        return result
                    self._ready = True
                    logger.info("Tab ready — payment page")
                else:
                    logger.info("Nfs tab — redirect payment page")
                    await goto_payment_form(page, config, logger)

                fill_results = await fill_main_form(page, config, logger)
                result["fill_results"] = fill_results

                check = await submit_and_check_card(page, config, logger)
                result["card_added"] = bool(check.get("added"))
                result["success"] = result["card_added"]
                result["message"] = str(check.get("message", ""))

                if not result["card_added"]:
                    await save_error_screenshot(page, screenshot_dir, "card_not_added", logger)
                    shots = sorted(screenshot_dir.glob("card_not_added_*.png"))
                    if shots:
                        result["screenshot"] = str(shots[-1])

                return result

            except Exception as exc:
                logger.exception("Session error: %s", exc)
                await save_error_screenshot(self._page, screenshot_dir, "session_error", logger)
                result["message"] = str(exc)
                await self.close()
                return result


_persistent_session: PersistentBrowserSession | None = None


def get_persistent_session() -> PersistentBrowserSession:
    global _persistent_session
    if _persistent_session is None:
        _persistent_session = PersistentBrowserSession()
    return _persistent_session


async def safe_close(browser: Browser | None, context: BrowserContext | None) -> None:
    try:
        if context is not None:
            await context.close()
    except Exception:
        pass
    try:
        if browser is not None:
            await browser.close()
    except Exception:
        pass


async def run_automation(
    card_number: str | None = None,
    month: str | None = None,
    year: str | None = None,
    cvc: str | None = None,
    *,
    interactive: bool = True,
    submit_card: bool = False,
    reuse_session: bool = False,
) -> dict[str, Any]:
    if card_number and month and year and cvc and reuse_session:
        return await get_persistent_session().run_card(card_number, month, year, cvc)

    ensure_cookies_file()
    config = load_config()
    logger = setup_logging(config.get("log_file", "automation.log"))
    screenshot_dir = ROOT / config.get("screenshot_dir", "screenshots")

    result: dict[str, Any] = {
        "success": False,
        "card_added": False,
        "message": "",
        "fill_results": {},
        "screenshot": None,
    }

    if not COOKIES_PATH.exists():
        result["message"] = f"cookies.json not found at {COOKIES_PATH}"
        return result

    try:
        raw_cookies = load_json(COOKIES_PATH, "cookies.json")
    except Exception as exc:
        result["message"] = str(exc)
        return result

    if cookies_still_placeholder(raw_cookies):
        result["message"] = "cookies.json still has placeholder values — paste real cookies"
        return result

    if card_number and month and year and cvc:
        billing = get_fixed_billing(config)
        payment = build_payment_data(card_number, month, year, cvc, billing["name"])
        config = merge_form_with_card(config, payment)
        submit_card = True

    browser: Browser | None = None
    context: BrowserContext | None = None
    page: Page | None = None

    try:
        async with async_playwright() as playwright:
            logger.info("Launching Chromium browser")
            browser = await playwright.chromium.launch(
                headless=config.get("headless", False),
                slow_mo=config.get("slow_mo", 0),
            )
            context = await browser.new_context()
            page = await context.new_page()

            if not await authenticate_with_cookies(page, context, config, logger):
                await save_error_screenshot(page, screenshot_dir, "invalid_cookies", logger)
                result["message"] = "Cookies invalid or expired"
                return result

            await navigate_to_targets(page, config, logger)
            fill_results = await fill_main_form(page, config, logger)
            result["fill_results"] = fill_results

            if submit_card:
                check = await submit_and_check_card(page, config, logger)
                result["card_added"] = bool(check.get("added"))
                result["success"] = result["card_added"]
                result["message"] = str(check.get("message", ""))
                if not result["card_added"]:
                    await save_error_screenshot(page, screenshot_dir, "card_not_added", logger)
                    shot = sorted(screenshot_dir.glob("card_not_added_*.png"))
                    if shot:
                        result["screenshot"] = str(shot[-1])
            else:
                failed = [name for name, ok in fill_results.items() if not ok]
                result["success"] = len(failed) == 0
                result["message"] = "Form filled" if result["success"] else f"Some fields failed: {', '.join(failed)}"

            if interactive:
                print("\nBrowser ma7loul — press ENTER bash tsed.")
                await asyncio.to_thread(input, "Press ENTER to close browser... ")

            return result

    except Exception as exc:
        logger.exception("Unhandled error: %s", exc)
        await save_error_screenshot(page, screenshot_dir, "unhandled_error", logger)
        result["message"] = str(exc)
        return result

    finally:
        await safe_close(browser, context)


async def run() -> int:
    ensure_cookies_file()
    logger = setup_logging(load_config().get("log_file", "automation.log"))
    logger.info("Starting SignalWire automation (cookies only)")

    if not COOKIES_PATH.exists():
        print_cookies_instructions()
        print(f"ERROR: cookies.json not found — paste cookies f {COOKIES_PATH}", file=sys.stderr)
        return 1

    try:
        raw_cookies = load_json(COOKIES_PATH, "cookies.json")
    except Exception as exc:
        print_cookies_instructions()
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if cookies_still_placeholder(raw_cookies):
        print_cookies_instructions()
        print(f"ERROR: 3mer cookies dyalek f {COOKIES_PATH}", file=sys.stderr)
        return 1

    result = await run_automation(interactive=True, submit_card=False)
    if not result.get("success") and "Cookies" in result.get("message", ""):
        print_cookies_instructions()
        print(f"ERROR: {result['message']}", file=sys.stderr)
        return 1

    if not result.get("success"):
        print(f"WARNING: {result.get('message')}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
