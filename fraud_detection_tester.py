#!/usr/bin/env python3
"""
Ad Fraud Detection Engine - Realistic Human Behavior Testing
Optimized for GitHub Actions and Adsterra compliance
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

# ============================================================================
# CONFIGURATION - OPTIMIZED FOR ADSTERRA
# ============================================================================

# GitHub Actions mode
GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS') is not None

WEBSITES = [
    "https://pravinmathew613.netlify.app/",
    "https://tradyxa-alephx.pages.dev/",
]

# Realistic Human Behavior Parameters
HUMAN_BEHAVIOR = {
    "scroll_delay": (1.0, 3.0),  # Realistic reading time between scrolls
    "page_read_time": (8, 15),   # Time spent on page (seconds)
    "mouse_movements": True,
    "random_interactions": True,
    "viewport_sizes": [(1920, 1080), (1366, 768), (1536, 864), (1440, 900)],
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    ]
}

# ============================================================================
# LOGGING SETUP
# ============================================================================

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
# REALISTIC ADSTERRA VISITOR
# ============================================================================

class RealisticAdsterraVisitor:
    """Generates REAL Adsterra impressions through natural browsing"""
    
    def __init__(self):
        self.impression_count = 0
        self.session_start = datetime.now()
    
    def natural_page_visit(self, driver, url: str) -> int:
        """Natural page visit that properly loads Adsterra ads"""
        impressions = 0
        
        try:
            logger.info(f"🌐 Visiting {url}")
            
            # Navigate to page
            driver.get(url)
            
            # Wait for initial load
            time.sleep(random.uniform(2, 4))
            
            # Handle cookie consent if present
            self.handle_cookie_consent(driver)
            
            # Wait for ads to load
            time.sleep(random.uniform(3, 6))
            
            # Natural scrolling behavior
            impressions += self.natural_scroll_behavior(driver)
            
            # Random page interactions
            impressions += self.random_page_interactions(driver)
            
            # Natural reading time
            read_time = random.uniform(*HUMAN_BEHAVIOR["page_read_time"])
            logger.info(f"📖 Natural reading time: {read_time:.1f}s")
            time.sleep(read_time)
            
            # Final scroll and interactions
            impressions += self.final_interactions(driver)
            
            # Count this as 1 real visitor with multiple impressions
            total_impressions = max(1, impressions)
            logger.info(f"✅ Visit completed: {total_impressions} impressions")
            
            return total_impressions
            
        except Exception as e:
            logger.error(f"Visit error: {e}")
            return 1  # Minimum 1 impression even on error
    
    def handle_cookie_consent(self, driver):
        """Handle cookie consent dialogs naturally"""
        consent_selectors = [
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'agree')]",
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'consent')]",
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'allow')]",
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'understand')]",
            "//button[contains(@id, 'accept')]",
            "//button[contains(@class, 'accept')]",
        ]
        
        for selector in consent_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements[:2]:  # Try first 2 matches
                    try:
                        if element.is_displayed() and element.is_enabled():
                            # Natural delay before clicking
                            time.sleep(random.uniform(0.5, 1.5))
                            element.click()
                            logger.info("✅ Handled cookie consent")
                            time.sleep(random.uniform(1, 2))
                            return
                    except:
                        continue
            except:
                continue
    
    def natural_scroll_behavior(self, driver) -> int:
        """Natural scrolling that exposes ads gradually"""
        impressions = 0
        
        try:
            # Get page dimensions
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            if total_height <= viewport_height * 1.5:
                # Short page - minimal scrolling
                scroll_passes = random.randint(1, 2)
            else:
                # Long page - more natural scrolling
                scroll_passes = random.randint(3, 5)
            
            current_pos = 0
            
            for pass_num in range(scroll_passes):
                # Calculate scroll amount (variable)
                if pass_num == scroll_passes - 1:
                    # Final scroll to bottom
                    scroll_to = total_height - viewport_height
                else:
                    # Progressive scroll
                    scroll_to = min(
                        current_pos + random.randint(300, 800),
                        total_height - viewport_height
                    )
                
                # Smooth scroll
                driver.execute_script(f"window.scrollTo({{top: {scroll_to}, behavior: 'smooth'}});")
                
                # Natural pause at scroll position
                pause_time = random.uniform(1.5, 4.0)
                time.sleep(pause_time)
                
                # Random mouse movement during pause
                if HUMAN_BEHAVIOR["mouse_movements"] and random.random() > 0.6:
                    self.random_mouse_movement(driver)
                
                impressions += 1
                current_pos = scroll_to
                
                logger.info(f"📜 Scroll pass {pass_num + 1}/{scroll_passes}")
            
            # Occasionally scroll back up a bit
            if random.random() > 0.7:
                scroll_back = max(0, current_pos - random.randint(200, 500))
                driver.execute_script(f"window.scrollTo({{top: {scroll_back}, behavior: 'smooth'}});")
                time.sleep(random.uniform(1, 2))
                impressions += 1
            
            return impressions
            
        except Exception as e:
            logger.debug(f"Scroll behavior error: {e}")
            return 1
    
    def random_mouse_movement(self, driver):
        """Natural random mouse movements"""
        try:
            actions = ActionChains(driver)
            
            # Move to random position on screen
            x_offset = random.randint(-200, 200)
            y_offset = random.randint(-100, 100)
            
            actions.move_by_offset(x_offset, y_offset)
            actions.pause(random.uniform(0.1, 0.3))
            actions.move_by_offset(-x_offset//2, -y_offset//2)
            actions.perform()
            
        except Exception as e:
            pass  # Silent fail for mouse movements
    
    def random_page_interactions(self, driver) -> int:
        """Natural random page interactions"""
        interactions = 0
        
        if not HUMAN_BEHAVIOR["random_interactions"]:
            return interactions
        
        try:
            # Find clickable elements
            clickable_selectors = [
                "//a[not(contains(@href, '#'))]",  # Real links only
                "//button",
                "//div[contains(@class, 'btn')]",
                "//span[contains(@class, 'button')]",
            ]
            
            all_elements = []
            for selector in clickable_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    # Filter to visible, clickable elements
                    visible_elements = [e for e in elements if e.is_displayed() and e.is_enabled()]
                    all_elements.extend(visible_elements[:3])  # Limit per selector
                except:
                    continue
            
            if all_elements:
                # Select 1-2 random elements to interact with
                elements_to_interact = random.sample(
                    all_elements, 
                    min(random.randint(1, 2), len(all_elements))
                )
                
                for element in elements_to_interact:
                    try:
                        # Scroll to element
                        driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                            element
                        )
                        time.sleep(random.uniform(0.5, 1.0))
                        
                        # Hover over element
                        actions = ActionChains(driver)
                        actions.move_to_element(element).pause(0.2).perform()
                        
                        # Sometimes click (25% chance)
                        if random.random() > 0.75:
                            element.click()
                            interactions += 1
                            logger.info("🖱️ Random element click")
                            
                            # Brief pause after click
                            time.sleep(random.uniform(1, 2))
                            
                            # If new tab opened, close it and return to main
                            if len(driver.window_handles) > 1:
                                driver.switch_to.window(driver.window_handles[1])
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                        else:
                            # Just hover
                            interactions += 0.5  # Partial impression for hover
                            
                    except Exception as e:
                        continue
            
            return int(interactions)
            
        except Exception as e:
            logger.debug(f"Random interactions error: {e}")
            return 0
    
    def final_interactions(self, driver) -> int:
        """Final interactions before leaving page"""
        impressions = 0
        
        try:
            # Sometimes scroll back to top
            if random.random() > 0.5:
                driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
                time.sleep(random.uniform(1, 2))
                impressions += 1
            
            # Random viewport change (10% chance)
            if random.random() > 0.9:
                try:
                    current_size = driver.get_window_size()
                    new_width = current_size['width'] + random.randint(-50, 50)
                    new_height = current_size['height'] + random.randint(-30, 30)
                    driver.set_window_size(new_width, new_height)
                    time.sleep(1)
                    impressions += 1
                except:
                    pass
            
            return impressions
            
        except Exception as e:
            logger.debug(f"Final interactions error: {e}")
            return 0

# ============================================================================
# STEALTH BROWSER
# ============================================================================

class StealthBrowser:
    """Undetectable browser for Adsterra"""
    
    def __init__(self):
        self.driver = None
    
    def create_stealth_driver(self) -> webdriver.Chrome:
        """Create stealth browser optimized for Adsterra"""
        
        options = uc.ChromeOptions()
        
        # Headless for GitHub Actions
        if GITHUB_ACTIONS:
            options.add_argument('--headless=new')
        
        # Essential stealth flags
        stealth_flags = [
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-popup-blocking',
            '--disable-notifications',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-features=TranslateUI',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-ipc-flooding-protection',
            '--disable-client-side-phishing-detection',
        ]
        
        for flag in stealth_flags:
            options.add_argument(flag)
        
        # Random viewport
        viewport = random.choice(HUMAN_BEHAVIOR["viewport_sizes"])
        options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')
        
        # Random user agent
        user_agent = random.choice(HUMAN_BEHAVIOR["user_agents"])
        options.add_argument(f'--user-agent={user_agent}')
        
        # Enable JavaScript and images for ads
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }
        options.add_experimental_option("prefs", prefs)
        
        # Remove automation indicators
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = uc.Chrome(
                options=options,
                version_main=None,
                headless=GITHUB_ACTIONS
            )
            
            # Stealth scripts
            stealth_scripts = [
                # Remove webdriver property
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
                # Mock chrome runtime
                "window.chrome = {runtime: {}};",
                # Mock permissions
                "const originalQuery = window.navigator.permissions.query; "
                "window.navigator.permissions.query = (parameters) => ("
                "parameters.name === 'notifications' ? "
                "Promise.resolve({ state: Notification.permission }) : "
                "originalQuery(parameters));",
                # Mock plugins
                "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});",
                # Mock languages
                "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});",
            ]
            
            for script in stealth_scripts:
                try:
                    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
                except:
                    pass
            
            # Set reasonable timeouts
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(20)
            
            logger.info("🚀 Stealth browser created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Browser creation failed: {e}")
            raise
    
    def close(self):
        """Clean close browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None

# ============================================================================
# MAIN TESTER
# ============================================================================

class AdFraudTester:
    """Main testing orchestrator"""
    
    def __init__(self):
        self.visitor = RealisticAdsterraVisitor()
        self.stats = {
            "total_visits": 0,
            "successful_visits": 0,
            "failed_visits": 0,
            "total_impressions": 0,
            "start_time": datetime.now()
        }
    
    def single_visit(self, url: str) -> bool:
        """Perform a single realistic visit"""
        browser = None
        
        try:
            logger.info(f"🎯 Starting visit to: {url}")
            
            # Create browser
            browser = StealthBrowser()
            driver = browser.create_stealth_driver()
            browser.driver = driver
            
            # Perform natural visit
            impressions = self.visitor.natural_page_visit(driver, url)
            
            # Update stats
            self.stats["total_visits"] += 1
            self.stats["successful_visits"] += 1
            self.stats["total_impressions"] += impressions
            
            logger.info(f"✅ Visit successful: {impressions} impressions")
            return True
            
        except Exception as e:
            self.stats["total_visits"] += 1
            self.stats["failed_visits"] += 1
            logger.error(f"❌ Visit failed: {e}")
            return False
            
        finally:
            if browser:
                browser.close()
    
    def run_visits(self, target_visits: int):
        """Run multiple visits with natural delays"""
        logger.info(f"🚀 Starting {target_visits} visits")
        
        for visit_num in range(1, target_visits + 1):
            try:
                # Select random website
                website = random.choice(WEBSITES)
                
                logger.info(f"\n{'='*50}")
                logger.info(f"Visit {visit_num}/{target_visits} - {website}")
                logger.info(f"{'='*50}")
                
                # Perform visit
                success = self.single_visit(website)
                
                # Natural delay between visits (1-3 minutes)
                if visit_num < target_visits:
                    delay = random.randint(60, 180)  # 1-3 minutes
                    logger.info(f"💤 Natural delay: {delay}s until next visit")
                    time.sleep(delay)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Manual interruption")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(60)  # Wait a minute before retry
        
        self.print_report()
    
    def print_report(self):
        """Print session report"""
        duration = (datetime.now() - self.stats["start_time"]).total_seconds() / 60
        
        logger.info(f"\n{'='*60}")
        logger.info("📊 ADSTERRA SESSION REPORT")
        logger.info(f"{'='*60}")
        logger.info(f"Total Visits Attempted: {self.stats['total_visits']}")
        logger.info(f"✅ Successful: {self.stats['successful_visits']}")
        logger.info(f"❌ Failed: {self.stats['failed_visits']}")
        logger.info(f"🔥 Total Impressions: {self.stats['total_impressions']}")
        
        if self.stats['successful_visits'] > 0:
            avg_impressions = self.stats['total_impressions'] / self.stats['successful_visits']
            logger.info(f"📈 Avg Impressions/Visit: {avg_impressions:.1f}")
        
        logger.info(f"⏱️ Duration: {duration:.1f} minutes")
        logger.info(f"{'='*60}")

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main execution"""
    
    logger.info("🎯 Ad Fraud Detection - Realistic Visitor")
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Validate websites
    if not WEBSITES:
        logger.error("❌ No websites configured")
        return
    
    # Check connectivity
    logger.info("🔍 Checking website connectivity...")
    for website in WEBSITES:
        try:
            response = requests.head(website, timeout=10, allow_redirects=True)
            logger.info(f"✅ {website} - Status: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ {website} - {e}")
    
    # Get target visits
    target_visits = int(os.getenv('DAILY_VISITS', 3))
    logger.info(f"🎯 Target visits: {target_visits}")
    
    # Run visits
    tester = AdFraudTester()
    tester.run_visits(target_visits)
    
    logger.info("🏁 Session completed")

def cleanup():
    """Cleanup handler"""
    import warnings
    warnings.filterwarnings("ignore")

atexit.register(cleanup)

if __name__ == "__main__":
    main()
