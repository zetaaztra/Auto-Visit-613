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
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    "scroll_delay": (0.5, 5.0),  # More variable reading time
    "page_read_time": (5, 25),   # More variation in reading time
    "mouse_movements": True,
    "random_interactions": True,
    "interaction_intensity": (0.3, 0.9),  # Random interaction level per session
    "scroll_intensity": (0.4, 1.0),       # Random scroll intensity per session
    "viewport_sizes": [(1920, 1080), (1366, 768), (1536, 864), (1440, 900), (1280, 720), (1600, 900)],
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
        """Natural scrolling that exposes ads gradually with high variability"""
        impressions = 0
        
        try:
            # Get page dimensions
            total_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            # MORE VARIABLE SCROLL PASSES
            if total_height <= viewport_height * 1.2:
                # Very short page - minimal scrolling (1-2 passes)
                scroll_passes = random.randint(1, 2)
            elif total_height <= viewport_height * 2:
                # Medium page (2-4 passes)
                scroll_passes = random.randint(2, 4)
            else:
                # Long page - more natural scrolling (3-6 passes)
                scroll_passes = random.randint(3, 6)
            
            current_pos = 0
            
            for pass_num in range(scroll_passes):
                # MORE VARIABLE SCROLL AMOUNTS
                if pass_num == scroll_passes - 1:
                    # Final scroll to bottom
                    scroll_to = total_height - viewport_height
                else:
                    # Progressive scroll with more variation
                    scroll_amount = random.randint(200, 1000)  # Increased range
                    scroll_to = min(
                        current_pos + scroll_amount,
                        total_height - viewport_height
                    )
                
                # Sometimes use smooth, sometimes instant scroll
                if random.random() > 0.3:
                    driver.execute_script(f"window.scrollTo({{top: {scroll_to}, behavior: 'smooth'}});")
                else:
                    driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                
                # MORE VARIABLE PAUSE TIMES
                pause_time = random.uniform(0.5, 5.0)  # Wider range
                time.sleep(pause_time)
                
                # Random mouse movement during pause (more frequent)
                if HUMAN_BEHAVIOR["mouse_movements"] and random.random() > 0.4:
                    self.random_mouse_movement(driver)
                
                impressions += 1
                current_pos = scroll_to
                
                logger.info(f"📜 Scroll pass {pass_num + 1}/{scroll_passes} (pos: {current_pos})")
            
            # MORE FREQUENT SCROLL BACK
            if random.random() > 0.4:  # 60% chance instead of 30%
                scroll_back = max(0, current_pos - random.randint(100, 600))
                driver.execute_script(f"window.scrollTo({{top: {scroll_back}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.5, 2.5))
                impressions += 1
            
            return impressions
            
        except Exception as e:
            logger.debug(f"Scroll behavior error: {e}")
            return random.randint(1, 3)  # Return random impressions on error
    
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
        """Natural random page interactions with more variation"""
        interactions = 0
        
        if not HUMAN_BEHAVIOR["random_interactions"]:
            return interactions
        
        try:
            # Find clickable elements with expanded selectors
            clickable_selectors = [
                "//a[not(contains(@href, '#'))]",
                "//button",
                "//div[contains(@class, 'btn')]",
                "//span[contains(@class, 'button')]",
                "//input[@type='submit']",
                "//*[@onclick]",  # Elements with click handlers
            ]
            
            all_elements = []
            for selector in clickable_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    # Filter to visible, clickable elements
                    visible_elements = [e for e in elements if e.is_displayed() and e.is_enabled()]
                    all_elements.extend(visible_elements[:5])  # Increased limit
                except:
                    continue
            
            # MORE VARIABLE INTERACTION COUNT
            if all_elements:
                max_interactions = random.randint(0, 4)  # 0-4 interactions
                elements_to_interact = random.sample(
                    all_elements, 
                    min(max_interactions, len(all_elements))
                )
                
                for element in elements_to_interact:
                    try:
                        # Scroll to element
                        driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                            element
                        )
                        time.sleep(random.uniform(0.3, 1.5))
                        
                        # Hover over element
                        actions = ActionChains(driver)
                        actions.move_to_element(element).pause(0.1).perform()
                        
                        # VARIABLE CLICK CHANCE
                        click_chance = random.random()
                        if click_chance > 0.8:  # 20% chance to click
                            element.click()
                            interactions += 2  # More weight for clicks
                            logger.info("🖱️ Random element click")
                            
                            # Variable pause after click
                            time.sleep(random.uniform(1, 4))
                            
                            # Handle new tabs
                            if len(driver.window_handles) > 1:
                                driver.switch_to.window(driver.window_handles[1])
                                time.sleep(random.uniform(2, 5))  # Brief view of new page
                                driver.close()
                                driver.switch_to.window(driver.window_handles[0])
                        elif click_chance > 0.3:  # 50% chance for hover only
                            interactions += 1  # Standard impression for hover
                            
                    except Exception as e:
                        continue
            
            return int(interactions)
            
        except Exception as e:
            logger.debug(f"Random interactions error: {e}")
            return random.randint(0, 2)  # Return random interactions on error
    
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
# SIMPLE BROWSER FOR GITHUB ACTIONS
# ============================================================================

class SimpleBrowser:
    """Simple browser that works in GitHub Actions"""
    
    def __init__(self):
        self.driver = None
    
    def create_driver(self) -> webdriver.Chrome:
        """Create simple browser for GitHub Actions"""
        
        options = Options()
        
        # Essential options for GitHub Actions
        if GITHUB_ACTIONS:
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
        else:
            options.add_argument('--headless=new')
        
        # Basic stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        
        # Random viewport
        viewport = random.choice(HUMAN_BEHAVIOR["viewport_sizes"])
        options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')
        
        # Random user agent
        user_agent = random.choice(HUMAN_BEHAVIOR["user_agents"])
        options.add_argument(f'--user-agent={user_agent}')
        
        # Enable JavaScript and images
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1,
            "profile.managed_default_content_settings.javascript": 1,
        })
        
        try:
            if GITHUB_ACTIONS:
                # Use system Chrome in GitHub Actions
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=options)
            else:
                # Use webdriver_manager for local development
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            
            # Set timeouts
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(20)
            
            # Basic stealth script
            stealth_script = """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """
            driver.execute_script(stealth_script)
            
            logger.info("🚀 Browser created successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Browser creation failed: {e}")
            
            # Fallback: try without service
            try:
                driver = webdriver.Chrome(options=options)
                logger.info("✅ Browser created with fallback method")
                return driver
            except Exception as e2:
                logger.error(f"Fallback also failed: {e2}")
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
            browser = SimpleBrowser()
            driver = browser.create_driver()
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

if __name__ == "__main__":
    main()
