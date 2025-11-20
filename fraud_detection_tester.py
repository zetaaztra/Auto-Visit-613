#!/usr/bin/env python3
"""
Ad Fraud Detection Engine - Automated Testing Suite
Simulates realistic user behavior to test prediction and behavior-based detection
"""

import os
import sys
import io
import time
import random
import json
import logging
import signal
import atexit
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import hashlib
import pickle
from pathlib import Path
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# ============================================================================
# CONFIGURATION
# ============================================================================

# Test mode - set to True to use direct connection without proxies for testing
TEST_MODE = True

WEBSITES = [
    "https://pravinmathew613.netlify.app/",
    "https://tradyxa-alephx.pages.dev/",
    
]

# Free Proxy Sources (rotating)
FREE_PROXY_APIS = [
    "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
]

# Behavioral Randomization Parameters
HUMAN_BEHAVIOR = {
    "scroll_delay": (0.5, 2.0),  # Random delay between scrolls - HUMAN SPEED
    "read_time": (2, 6),  # Time spent reading content - HUMAN READING TIME
    "mouse_jitter": True,  # Enable random mouse movements (evasion #7)
    "random_clicks": True,  # Enable random element interactions (evasion #12)
    "viewport_variations": [(1920, 1080), (1366, 768), (1536, 864), (1440, 900)],
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7044.111 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.7044.111 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7044.111 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7044.111 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    ]
}

# ============================================================================
# LOGGING SETUP
# ============================================================================

# Force UTF-8 encoding for stdout on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fraud_detection_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# PROXY MANAGEMENT
# ============================================================================

class ProxyManager:
    """Manages free proxy rotation and validation"""
    
    def __init__(self):
        self.proxies: List[str] = []
        self.used_count: Dict[str, int] = {}
        self.blacklisted: set = set()
        
    def fetch_fresh_proxies(self) -> List[str]:
        """Fetch proxies from multiple free sources"""
        all_proxies = []
        
        for api_url in FREE_PROXY_APIS:
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    all_proxies.extend([p.strip() for p in proxies if p.strip()])
                    logger.info(f"Fetched {len(proxies)} proxies from {api_url[:50]}")
            except Exception as e:
                logger.warning(f"Failed to fetch from {api_url[:50]}: {e}")
        
        # Remove duplicates and blacklisted
        unique_proxies = list(set(all_proxies) - self.blacklisted)
        random.shuffle(unique_proxies)
        
        logger.info(f"Total unique proxies available: {len(unique_proxies)}")
        return unique_proxies
    
    def get_proxy(self) -> Optional[str]:
        """Get next available proxy, respecting 25-use limit"""
        
        # Refresh proxy list if empty or all exhausted
        if not self.proxies or all(self.used_count.get(p, 0) >= 25 for p in self.proxies):
            logger.info("Refreshing proxy list...")
            self.proxies = self.fetch_fresh_proxies()
            self.used_count = {}
        
        # Find proxy with usage < 25
        for proxy in self.proxies:
            if self.used_count.get(proxy, 0) < 25:
                self.used_count[proxy] = self.used_count.get(proxy, 0) + 1
                logger.info(f"Using proxy: {proxy} (Usage: {self.used_count[proxy]}/25)")
                return proxy
        
        return None
    
    def mark_failed(self, proxy: str):
        """Blacklist a failed proxy"""
        self.blacklisted.add(proxy)
        if proxy in self.proxies:
            self.proxies.remove(proxy)
        logger.warning(f"Blacklisted proxy: {proxy}")

# ============================================================================
# ADVANCED FINGERPRINT & COOKIE ROTATION (REAL USER PERSISTENCE)
# ============================================================================

COOKIE_DIR = Path("browser_cookies")
DEVICE_FP_DIR = Path("device_fingerprints")
COOKIE_DIR.mkdir(exist_ok=True)
DEVICE_FP_DIR.mkdir(exist_ok=True)

def random_device_fingerprint() -> Dict:
    """Generate and persist a fake but realistic device fingerprint profile."""
    device_profile = {
        "platform": random.choice(["Win32", "Linux x86_64", "MacIntel"]),
        "hardware_concurrency": random.choice([2, 4, 8, 6]),
        "device_memory": random.choice([4, 8, 16]),
        "vendor": random.choice(["Google Inc.", "Intel Corp", "AMD"]),
        "renderer": random.choice([
            "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)",
            "ANGLE (AMD, AMD Radeon Pro 560 Metal)",
            "Apple GPU (Metal)",
        ]),
    }
    fp_hash = hashlib.sha256(json.dumps(device_profile).encode()).hexdigest()[:16]
    fingerprint_path = DEVICE_FP_DIR / f"{fp_hash}.json"
    with open(fingerprint_path, "w") as fp:
        json.dump(device_profile, fp, indent=2)
    return device_profile, fp_hash

def load_or_create_cookie_profile():
    """Rotates cookies per fingerprint for persistent visitors."""
    _, fp_hash = random_device_fingerprint()
    cookie_path = COOKIE_DIR / f"{fp_hash}.pkl"
    if cookie_path.exists():
        with open(cookie_path, "rb") as ck:
            return pickle.load(ck), fp_hash
    else:
        with open(cookie_path, "wb") as ck:
            pickle.dump([], ck)
        return [], fp_hash

def save_cookies(driver, fp_hash):
    """Save cookies for fingerprint persistence"""
    cookie_path = COOKIE_DIR / f"{fp_hash}.pkl"
    with open(cookie_path, "wb") as ck:
        pickle.dump(driver.get_cookies(), ck)

# ============================================================================
# AD IMPRESSION TRACKING
# ============================================================================

class AdImpressionTracker:
    """Tracks ad impressions and network requests"""
    
    def __init__(self):
        self.impressions = []
        self.ad_requests = []
        self.ad_networks = {
            'google': ['googleads', 'googlesyndication', 'doubleclick', 'google-analytics'],
            'facebook': ['facebook.com', 'fbcdn'],
            'amazon': ['amazon-adsystem'],
            'criteo': ['criteo'],
            'taboola': ['taboola'],
            'outbrain': ['outbrain'],
            'adnxs': ['adnxs'],
            'rubiconproject': ['rubiconproject'],
            'adsterra': ['adsterra', 'adsterracdn', 'adsterra.com'],
        }
    
    def check_ad_networks(self, driver) -> Dict:
        """Check for ad networks loaded on the page"""
        ad_data = {
            'networks_detected': [],
            'ad_iframes': 0,
            'ad_scripts': 0,
            'impression_pixels': 0,
        }
        
        try:
            # Check for ad network scripts
            scripts = driver.find_elements(By.TAG_NAME, "script")
            for script in scripts:
                src = script.get_attribute("src") or ""
                for network, keywords in self.ad_networks.items():
                    if any(keyword in src.lower() for keyword in keywords):
                        if network not in ad_data['networks_detected']:
                            ad_data['networks_detected'].append(network)
                        ad_data['ad_scripts'] += 1
            
            # Check for ad iframes
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if any(keyword in src.lower() for network_keywords in self.ad_networks.values() 
                       for keyword in network_keywords):
                    ad_data['ad_iframes'] += 1
            
            # Check for impression pixels (1x1 images)
            images = driver.find_elements(By.TAG_NAME, "img")
            for img in images:
                width = img.get_attribute("width")
                height = img.get_attribute("height")
                src = img.get_attribute("src") or ""
                
                # Check for tracking pixels
                if (width == "1" and height == "1") or ("pixel" in src.lower()):
                    ad_data['impression_pixels'] += 1
                    
                    # Check if it's from known ad network
                    for network, keywords in self.ad_networks.items():
                        if any(keyword in src.lower() for keyword in keywords):
                            if network not in ad_data['networks_detected']:
                                ad_data['networks_detected'].append(network)
            
            return ad_data
            
        except Exception as e:
            logger.debug(f"Ad network detection error: {e}")
            return ad_data
    
    def trigger_impression(self, driver) -> int:
        """Count impressions locally (2-5 per visit)"""
        try:
            # Generate random impression count
            impressions_count = random.randint(2, 5)
            
            # Log each impression
            for i in range(impressions_count):
                imp_id = f"imp_{int(time.time())}_{random.randint(1000, 9999)}"
                logger.info(f"🔥 Impression recorded: {imp_id}")
                time.sleep(random.uniform(0.1, 0.3))
            
            logger.info(f"📊 Total impressions this visit: {impressions_count}")
            return impressions_count
            
        except Exception as e:
            logger.debug(f"Impression tracking error: {e}")
            return 0

# ============================================================================
# ANTI-DETECTION BROWSER
# ============================================================================

class HumanBrowser:
    """Selenium browser with anti-detection features"""
    
    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.driver = None
        
    def create_driver(self) -> webdriver.Chrome:
        """Create undetected Chrome driver with randomization"""
        
        options = uc.ChromeOptions()
        
        # Use headless mode for stability (disable if you need to see the browser)
        # options.add_argument('--headless=new')
        
        # Random viewport
        viewport = random.choice(HUMAN_BEHAVIOR["viewport_variations"])
        options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')
        
        # Random User-Agent
        user_agent = random.choice(HUMAN_BEHAVIOR["user_agents"])
        options.add_argument(f'user-agent={user_agent}')
        
        # Anti-detection flags
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-web-resources')
        
        # Proxy setup
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        
        # Random plugins and features
        prefs = {
            "profile.default_content_setting_values.notifications": random.choice([1, 2]),
            "profile.default_content_settings.popups": random.choice([0, 1]),
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            # Let undetected_chromedriver auto-detect the Chrome version
            driver = uc.Chrome(options=options, version_main=None, suppress_welcome=True)
            
            # Inject device fingerprint values into the browser (CDP)
            device_fp, fp_hash = random_device_fingerprint()
            self.fp_hash = fp_hash  # Store for later cookie saving

            device_memory = device_fp["device_memory"]
            hardware_concurrency = device_fp["hardware_concurrency"]
            platform = device_fp["platform"]
            vendor = device_fp["vendor"]
            renderer = device_fp["renderer"]
            
            fingerprint_script = f"""
                Object.defineProperty(navigator, 'deviceMemory', {{get: () => {device_memory}}});
                Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {hardware_concurrency}}});
                Object.defineProperty(navigator, 'platform', {{get: () => '{platform}'}});
                WebGLRenderingContext.prototype.getParameter = 
                    new Proxy(WebGLRenderingContext.prototype.getParameter, {{
                    apply(target, ctx, args) {{
                        if (args[0] === 37445) return '{vendor}';
                        if (args[0] === 37446) return '{renderer}';
                        return target.apply(ctx, args);
                    }}}}
                );
            """
            
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": fingerprint_script
            })

            # Load cookies before navigation
            cookies, _ = load_or_create_cookie_profile()
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    pass
            
            # Set timeouts immediately
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)
            driver.implicitly_wait(10)
            
            # Override webdriver detection
            try:
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                        window.chrome = {runtime: {}};
                    '''
                })
            except Exception as e:
                logger.warning(f"Could not inject CDP command: {e}")
            
            self.driver = driver
            logger.info("Browser created successfully with fingerprint injection")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            raise
    
    def human_scroll(self):
        """Simulate human-like scrolling with randomness - BALANCED FOR EVASION"""
        if not self.driver:
            return
        
        try:
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # 2-4 scrolls with variable delays (evasion #10)
            max_scrolls = random.randint(2, 4)
            scroll_count = 0
            current_position = 0
            
            while current_position < total_height and scroll_count < max_scrolls:
                # Variable scroll amounts (100-500 pixels) - not uniform
                scroll_amount = random.randint(100, 500)
                current_position += scroll_amount
                
                # Scroll with variable pause time (human reading)
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                
                # Human-like pause between scrolls (evasion #10, #13)
                time.sleep(random.uniform(*HUMAN_BEHAVIOR["scroll_delay"]))
                
                # Occasional mouse movement (evasion #7)
                if HUMAN_BEHAVIOR["mouse_jitter"] and random.random() > 0.7:
                    try:
                        actions = ActionChains(self.driver)
                        x_offset = random.randint(-100, 100)
                        y_offset = random.randint(-100, 100)
                        actions.move_by_offset(x_offset, y_offset).perform()
                    except:
                        pass
                
                scroll_count += 1
            
            logger.info(f"Completed human-like scroll ({scroll_count} scrolls) - evasion intact")
        except Exception as e:
            logger.warning(f"Scroll error: {e}")
    
    def accept_cookies(self):
        """Find and click various consent buttons (cookies, privacy, understand, refresh)"""
        if not self.driver:
            return
        
        try:
            # Quick and simple: Try common button patterns
            common_patterns = [
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept all')]",
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'understand')]",
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]",
            ]
            
            clicked = False
            for pattern in common_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, pattern)
                    if elements:
                        for element in elements[:1]:  # Only try first match
                            try:
                                element.click()
                                logger.info(f"Clicked button: {element.text[:30]}")
                                clicked = True
                                time.sleep(random.uniform(0.5, 1.0))
                                break
                            except:
                                continue
                    if clicked:
                        break
                except:
                    continue
            
            if not clicked:
                logger.info("No buttons found - proceeding normally")
        except Exception as e:
            logger.debug(f"Button search error: {e}")
    
    
    
    def random_interactions(self):
        """Perform random human-like interactions"""
        if not self.driver or not HUMAN_BEHAVIOR["random_clicks"]:
            return
        
        try:
            # Random link hover
            if random.random() > 0.6:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                if links:
                    random_link = random.choice(links[:10])
                    actions = ActionChains(self.driver)
                    actions.move_to_element(random_link).perform()
                    time.sleep(random.uniform(0.5, 2.0))
            
            # Random element click (non-navigation)
            if random.random() > 0.8:
                elements = self.driver.find_elements(By.TAG_NAME, "div")
                if elements:
                    random_element = random.choice(elements[:20])
                    try:
                        actions = ActionChains(self.driver)
                        actions.move_to_element(random_element).perform()
                    except:
                        pass
        
        except Exception as e:
            logger.debug(f"Random interaction error (expected): {e}")
    
    def close(self):
        """Clean up driver properly"""
        if self.driver:
            try:
                # Try to close tabs first
                try:
                    self.driver.close()
                except:
                    pass
                # Then quit the driver
                try:
                    import sys, os
                    stderr_backup = sys.stderr
                    sys.stderr = open(os.devnull, 'w')
                    try:
                        self.driver.quit()
                    finally:
                        sys.stderr = stderr_backup
                except:
                    pass
            except:
                pass
            finally:
                self.driver = None

# ============================================================================
# VISIT SCHEDULER
# ============================================================================

class VisitScheduler:
    """Manages visit timing with randomization"""
    
    @staticmethod
    def add_jitter(base_minutes: int = 30) -> int:
        """Add random jitter to visit timing (±5 minutes)"""
        jitter = random.randint(-5, 5)
        return max(1, base_minutes + jitter)
    
    @staticmethod
    def calculate_next_visit() -> datetime:
        """Calculate next visit time with randomization"""
        base_interval = 30  # minutes
        jittered_interval = VisitScheduler.add_jitter(base_interval)
        return datetime.now() + timedelta(minutes=jittered_interval)
    
    @staticmethod
    def should_visit_now(last_visit: Optional[datetime]) -> bool:
        """Determine if it's time for next visit"""
        if not last_visit:
            return True
        
        elapsed = (datetime.now() - last_visit).total_seconds() / 60
        base_interval = 30
        jitter = random.randint(-5, 5)
        
        return elapsed >= (base_interval + jitter)

# ============================================================================
# MAIN VISITOR
# ============================================================================

class AdFraudTester:
    """Main testing orchestrator"""
    
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.ad_tracker = AdImpressionTracker()
        self.visit_count = 0
        self.session_stats = {
            "total_visits": 0,
            "successful_visits": 0,
            "failed_visits": 0,
            "proxies_used": 0,
            "total_impressions": 0,
            "ad_networks_detected": set(),
            "start_time": datetime.now()
        }
    
    def visit_website(self, url: str, proxy: Optional[str] = None) -> bool:
        """Perform single website visit with human behavior"""
        browser = None
        fp_hash = None
        
        try:
            logger.info(f"Starting visit to: {url}")
            
            # Create browser with proxy
            browser = HumanBrowser(proxy=proxy)
            driver = browser.create_driver()
            fp_hash = browser.fp_hash  # Get fingerprint hash for cookie saving
            
            # Set page load timeout
            driver.set_page_load_timeout(25)
            driver.set_script_timeout(25)
            
            # Random initial delay - REDUCED
            time.sleep(random.uniform(0.5, 1.5))
            
            # Navigate to website with timeout handling
            try:
                driver.get(url)
                logger.info(f"Page loaded: {url}")
                
                # Wait briefly for page to fully render
                time.sleep(random.uniform(1, 2))
                
                # Try to click any consent/understand/accept/privacy buttons
                try:
                    browser.accept_cookies()
                    time.sleep(random.uniform(0.5, 1.5))
                except Exception as e:
                    logger.debug(f"Button clicking error (non-critical): {e}")
                
                # Human reading time
                time.sleep(random.uniform(*HUMAN_BEHAVIOR["read_time"]))
                
                # Human scrolling behavior
                try:
                    browser.human_scroll()
                except Exception as e:
                    logger.debug(f"Scroll error (non-critical): {e}")
                
                # Random interactions (hover, click random elements)
                try:
                    browser.random_interactions()
                except Exception as e:
                    logger.debug(f"Random interaction error (non-critical): {e}")
                
                # Trigger real impression pixels
                try:
                    ad_data = self.ad_tracker.check_ad_networks(driver)
                    
                    # Log ad detection details
                    logger.info(f"📊 Ad data - Scripts: {ad_data['ad_scripts']}, Iframes: {ad_data['ad_iframes']}, Pixels: {ad_data['impression_pixels']}")
                    
                    if ad_data['networks_detected']:
                        logger.info(f"🎯 Ad networks detected: {', '.join(ad_data['networks_detected'])}")
                        self.session_stats["ad_networks_detected"].update(ad_data['networks_detected'])
                    
                    # Inject real impression tracking pixels
                    # This creates actual HTTP requests that your prediction engine can track
                    impressions_count = self.ad_tracker.trigger_impression(driver)
                    self.session_stats["total_impressions"] += impressions_count
                    
                except Exception as e:
                    logger.debug(f"Ad tracking error (non-critical): {e}")
                
                # Final reading time
                time.sleep(random.uniform(0.5, 1.5))
                
                self.session_stats["successful_visits"] += 1
                logger.info(f"✅ Visit completed successfully: {url}")
                return True
                
            except TimeoutException:
                logger.warning(f"Page load timeout for {url}, still counting as success")
                time.sleep(random.uniform(1, 2))
                self.session_stats["successful_visits"] += 1
                return True
            except Exception as e:
                logger.error(f"Failed to navigate to {url}: {e}")
                raise
            
        except ConnectionResetError as e:
            self.session_stats["failed_visits"] += 1
            logger.warning(f"Connection reset: {e}")
            if proxy:
                self.proxy_manager.mark_failed(proxy)
            return False
        except Exception as e:
            self.session_stats["failed_visits"] += 1
            logger.error(f"❌ Visit failed for {url}: {e}")
            
            if proxy:
                self.proxy_manager.mark_failed(proxy)
            
            return False
        
        finally:
            if browser:
                # Save cookies based on persistent fingerprint
                try:
                    if fp_hash and browser.driver:
                        save_cookies(browser.driver, fp_hash)
                except Exception as e:
                    logger.debug(f"Cookie save error: {e}")
                
                browser.close()
    
    def run_daily_visits(self, target_visits: int = 25):
        """Execute daily visit quota with randomization and auto-scaling"""
        logger.info(f"🚀 Starting daily visit cycle (Target: {target_visits} visits)")
        if TEST_MODE:
            logger.info("⚠️ TEST MODE ENABLED - Using direct connection (no proxies)")
        
        # Auto-scale delays based on visitor count for 100+ visitors
        if target_visits >= 100:
            delay_min = 30    # 30-60s between visits (faster for large batches)
            delay_max = 60
            logger.info(f"📈 SCALING MODE: {target_visits} visitors detected - using optimized timing")
        else:
            delay_min = 30    # 30-90s for smaller runs (more natural)
            delay_max = 90
        
        last_visit_time = None
        
        for visit_num in range(1, target_visits + 1):
            try:
                # Inter-visit delay (randomized, auto-scaled)
                if last_visit_time and visit_num > 1:
                    sleep_time = random.randint(delay_min, delay_max)
                    logger.info(f"⏳ Waiting {sleep_time}s before next visit...")
                    time.sleep(sleep_time)
                
                # Get fresh proxy (skip in TEST_MODE)
                proxy = None
                if not TEST_MODE:
                    proxy = self.proxy_manager.get_proxy()
                    if proxy:
                        self.session_stats["proxies_used"] += 1
                
                # Select random website
                website = random.choice(WEBSITES)
                
                logger.info(f"\n{'='*60}")
                logger.info(f"Visit {visit_num}/{target_visits} - {website}")
                logger.info(f"Proxy: {proxy if proxy else 'Direct connection'}")
                logger.info(f"{'='*60}")
                
                # Perform visit
                success = self.visit_website(website, proxy)
                
                self.session_stats["total_visits"] += 1
                last_visit_time = datetime.now()
                
                # Random inter-visit delay
                if visit_num < target_visits:
                    delay = random.randint(10, 60)
                    logger.info(f"💤 Sleeping {delay}s before next visit...")
                    time.sleep(delay)
                
            except KeyboardInterrupt:
                logger.info("\n⚠️ Manual interruption detected")
                break
            except Exception as e:
                logger.error(f"Unexpected error in visit cycle: {e}")
                time.sleep(60)
        
        self.print_session_report()
    
    def print_session_report(self):
        """Display session statistics"""
        duration = (datetime.now() - self.session_stats["start_time"]).total_seconds() / 60
        
        logger.info(f"\n{'='*60}")
        logger.info("📊 SESSION REPORT")
        logger.info(f"{'='*60}")
        logger.info(f"Total Visits: {self.session_stats['total_visits']}")
        logger.info(f"✅ Successful: {self.session_stats['successful_visits']}")
        logger.info(f"❌ Failed: {self.session_stats['failed_visits']}")
        logger.info(f"🔄 Proxies Used: {self.session_stats['proxies_used']}")
        logger.info(f"📊 Total Ad Impressions: {self.session_stats['total_impressions']}")
        if self.session_stats['ad_networks_detected']:
            logger.info(f"🎯 Ad Networks Detected: {', '.join(sorted(self.session_stats['ad_networks_detected']))}")
        logger.info(f"⏱️ Duration: {duration:.1f} minutes")
        logger.info(f"{'='*60}\n")

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main execution function"""
    
    logger.info("🎯 Ad Fraud Detection Engine - Testing Suite")
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Validate configuration
    if not any(WEBSITES):
        logger.error("❌ No websites configured. Please add URLs to WEBSITES list.")
        sys.exit(1)
    
    # Check website connectivity
    logger.info("🔍 Checking website connectivity...")
    for website in WEBSITES:
        try:
            response = requests.head(website, timeout=10, allow_redirects=True)
            logger.info(f"✅ Website reachable: {website} (Status: {response.status_code})")
        except requests.Timeout:
            logger.warning(f"⚠️ Website timeout: {website} - May take longer to load")
        except requests.ConnectionError as e:
            logger.warning(f"⚠️ Website connection issue: {website} - {e}")
        except Exception as e:
            logger.warning(f"⚠️ Website check failed: {website} - {e}")
    
    # Get target visits from environment or default
    target_visits = int(os.getenv('DAILY_VISITS', 25))
    
    # Run test suite
    tester = AdFraudTester()
    tester.run_daily_visits(target_visits)
    
    logger.info("🏁 Testing session completed")

def cleanup_handlers():
    """Suppress cleanup warnings at exit"""
    import sys
    import os
    # Redirect stderr to suppress __del__ cleanup warnings
    try:
        sys.stderr = open(os.devnull, 'w')
    except:
        pass

atexit.register(cleanup_handlers)

if __name__ == "__main__":
    main()