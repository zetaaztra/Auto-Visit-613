#!/usr/bin/env python3
"""
Ad Fraud Detection Engine - Automated Testing Suite
Simulates realistic user behavior to test prediction and behavior-based detection
"""

import os
import sys
import time
import random
import json
import logging
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

# ============================================================================
# CONFIGURATION
# ============================================================================

WEBSITES = [
    "https://your-test-site-1.com",
    "https://your-test-site-2.com",
    "https://your-test-site-3.com",
    "https://your-test-site-4.com",
    "https://your-test-site-5.com",
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
    "scroll_delay": (0.5, 3.0),  # Random delay between scrolls
    "read_time": (2, 8),  # Time spent reading content
    "mouse_jitter": True,
    "random_clicks": True,
    "viewport_variations": [(1920, 1080), (1366, 768), (1536, 864), (1440, 900)],
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]
}

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fraud_detection_test.log'),
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
            driver = uc.Chrome(options=options, version_main=120)
            
            # Override webdriver detection
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    window.chrome = {runtime: {}};
                '''
            })
            
            self.driver = driver
            logger.info("Browser created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            raise
    
    def human_scroll(self):
        """Simulate human-like scrolling with randomness"""
        if not self.driver:
            return
        
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        
        current_position = 0
        
        while current_position < total_height:
            # Random scroll amount (not uniform)
            scroll_amount = random.randint(100, 500)
            current_position += scroll_amount
            
            # Scroll with random speed
            self.driver.execute_script(f"window.scrollTo(0, {current_position});")
            
            # Random pause (reading time)
            time.sleep(random.uniform(*HUMAN_BEHAVIOR["scroll_delay"]))
            
            # Occasional mouse movement
            if HUMAN_BEHAVIOR["mouse_jitter"] and random.random() > 0.7:
                try:
                    actions = ActionChains(self.driver)
                    x_offset = random.randint(-100, 100)
                    y_offset = random.randint(-100, 100)
                    actions.move_by_offset(x_offset, y_offset).perform()
                except:
                    pass
        
        logger.info("Completed human-like scroll")
    
    def accept_cookies(self):
        """Find and click cookie consent with multiple strategies"""
        if not self.driver:
            return
        
        cookie_selectors = [
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]",
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'understand')]",
            "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
            "//*[@id='cookie-accept']",
            "//*[@class='cookie-accept']",
        ]
        
        for selector in cookie_selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                # Human-like click delay
                time.sleep(random.uniform(0.5, 2.0))
                element.click()
                logger.info("Cookie consent accepted")
                return
            except (TimeoutException, NoSuchElementException):
                continue
        
        logger.info("No cookie consent found (or already accepted)")
    
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
        """Clean up driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

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
        self.visit_count = 0
        self.session_stats = {
            "total_visits": 0,
            "successful_visits": 0,
            "failed_visits": 0,
            "proxies_used": 0,
            "start_time": datetime.now()
        }
    
    def visit_website(self, url: str, proxy: Optional[str] = None) -> bool:
        """Perform single website visit with human behavior"""
        browser = None
        
        try:
            logger.info(f"Starting visit to: {url}")
            
            # Create browser with proxy
            browser = HumanBrowser(proxy=proxy)
            driver = browser.create_driver()
            
            # Random initial delay
            time.sleep(random.uniform(1, 3))
            
            # Navigate to website
            driver.get(url)
            logger.info(f"Page loaded: {url}")
            
            # Wait for page load
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Accept cookies
            time.sleep(random.uniform(1, 3))
            browser.accept_cookies()
            
            # Human reading time
            time.sleep(random.uniform(*HUMAN_BEHAVIOR["read_time"]))
            
            # Scroll through page
            browser.human_scroll()
            
            # Random interactions
            browser.random_interactions()
            
            # Random refresh (50% chance)
            if random.random() > 0.5:
                logger.info("Performing page refresh")
                driver.refresh()
                time.sleep(random.uniform(2, 5))
                browser.human_scroll()
            
            # Final reading time
            time.sleep(random.uniform(2, 5))
            
            self.session_stats["successful_visits"] += 1
            logger.info(f"✅ Visit completed successfully: {url}")
            return True
            
        except Exception as e:
            self.session_stats["failed_visits"] += 1
            logger.error(f"❌ Visit failed for {url}: {e}")
            
            if proxy:
                self.proxy_manager.mark_failed(proxy)
            
            return False
        
        finally:
            if browser:
                browser.close()
    
    def run_daily_visits(self, target_visits: int = 25):
        """Execute daily visit quota with randomization"""
        logger.info(f"🚀 Starting daily visit cycle (Target: {target_visits} visits)")
        
        last_visit_time = None
        
        for visit_num in range(1, target_visits + 1):
            try:
                # Wait for next scheduled time (with jitter)
                if last_visit_time:
                    while not VisitScheduler.should_visit_now(last_visit_time):
                        sleep_time = random.randint(30, 90)
                        logger.info(f"⏳ Waiting {sleep_time}s before next visit...")
                        time.sleep(sleep_time)
                
                # Get fresh proxy
                proxy = self.proxy_manager.get_proxy()
                if proxy:
                    self.session_stats["proxies_used"] += 1
                
                # Select random website
                website = random.choice(WEBSITES)
                
                logger.info(f"\n{'='*60}")
                logger.info(f"Visit {visit_num}/{target_visits} - {website}")
                logger.info(f"Proxy: {proxy if proxy else 'Direct'}")
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
    
    # Get target visits from environment or default
    target_visits = int(os.getenv('DAILY_VISITS', 25))
    
    # Run test suite
    tester = AdFraudTester()
    tester.run_daily_visits(target_visits)
    
    logger.info("🏁 Testing session completed")

if __name__ == "__main__":
    main()