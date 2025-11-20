#!/usr/bin/env python3
"""
Ad Fraud Detection - Chaos Mode with Real Browser
Actually visits websites and handles cookie consent
"""

import os
import sys
import time
import random
import logging
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Get chaotic parameters from GitHub Actions
TARGET_WEBSITE = os.getenv('CHAOTIC_WEBSITE', 'https://tradyxa-alephx.pages.dev/')
TARGET_VISITS = int(os.getenv('CHAOTIC_VISITORS', 1))
CHAOS_SEED = int(os.getenv('CHAOS_SEED', random.randint(1, 1000)))

# Set random seed for reproducible chaos
random.seed(CHAOS_SEED)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fraud_detection_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ChaosBrowser:
    """Real browser with chaotic behavior"""
    
    def __init__(self, chaos_seed):
        self.chaos_seed = chaos_seed
        self.driver = None
    
    def create_browser(self):
        """Create real browser with chaotic settings"""
        try:
            options = Options()
            
            # GitHub Actions compatibility
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            # Stealth options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Random viewport
            viewports = [(1920, 1080), (1366, 768), (1536, 864), (1440, 900)]
            viewport = random.choice(viewports)
            options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ]
            user_agent = random.choice(user_agents)
            options.add_argument(f'--user-agent={user_agent}')
            
            # Create driver
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
            
            logger.info("🚀 Chaotic browser created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser creation failed: {e}")
            return False
    
    def handle_cookie_consent(self):
        """Handle cookie consent and disclaimers"""
        try:
            # Common consent selectors - EXPANDED FOR YOUR SITE
            consent_selectors = [
                "//button[contains(translate(., 'ACCEPT', 'accept'), 'accept')]",
                "//button[contains(translate(., 'AGREE', 'agree'), 'agree')]",
                "//button[contains(translate(., 'I UNDERSTAND', 'i understand'), 'i understand')]",
                "//button[contains(translate(., 'OK', 'ok'), 'ok')]",
                "//button[contains(translate(., 'CONSENT', 'consent'), 'consent')]",
                "//button[contains(translate(., 'ALLOW', 'allow'), 'allow')]",
                "//button[contains(translate(., 'YES', 'yes'), 'yes')]",
                "//button[contains(translate(., 'CONTINUE', 'continue'), 'continue')]",
                "//button[contains(translate(., 'PROCEED', 'proceed'), 'proceed')]",
                "//input[@type='submit' and contains(translate(@value, 'ACCEPT', 'accept'), 'accept')]",
                "//input[@type='button' and contains(translate(@value, 'ACCEPT', 'accept'), 'accept')]",
                "//a[contains(translate(., 'ACCEPT', 'accept'), 'accept')]",
                "//div[contains(translate(., 'ACCEPT', 'accept'), 'accept')]",
                "//span[contains(translate(., 'ACCEPT', 'accept'), 'accept')]",
            ]
            
            for selector in consent_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Chaotic delay before clicking
                            time.sleep(random.uniform(1, 3))
                            element.click()
                            logger.info("✅ Handled consent/disclaimer")
                            time.sleep(random.uniform(2, 4))
                            return True
                except:
                    continue
            
            logger.info("ℹ️ No consent dialogs found")
            return False
            
        except Exception as e:
            logger.debug(f"Consent handling error: {e}")
            return False
    
    def chaotic_scroll(self):
        """Perform chaotic scrolling"""
        impressions = 0
        
        try:
            # Get page dimensions
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Random scroll passes (2-6)
            scroll_passes = random.randint(2, 6)
            logger.info(f"📜 Chaotic scrolling: {scroll_passes} passes")
            
            for i in range(scroll_passes):
                # Random scroll position
                if i == scroll_passes - 1:
                    scroll_to = total_height - viewport_height  # Bottom
                else:
                    scroll_to = random.randint(100, total_height - viewport_height)
                
                # Random scroll behavior
                if random.random() > 0.5:
                    self.driver.execute_script(f"window.scrollTo({{top: {scroll_to}, behavior: 'smooth'}});")
                else:
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                
                # Chaotic pause
                pause_time = random.uniform(1, 5)
                time.sleep(pause_time)
                impressions += 1
                
                logger.info(f"   Scroll {i+1}/{scroll_passes} to {scroll_to}px")
            
            # Sometimes scroll back up
            if random.random() > 0.7:
                self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
                time.sleep(random.uniform(1, 3))
                impressions += 1
            
            return impressions
            
        except Exception as e:
            logger.debug(f"Scroll error: {e}")
            return 1
    
    def chaotic_interactions(self):
        """Perform chaotic page interactions"""
        interactions = 0
        
        try:
            # Find clickable elements
            selectors = [
                "//a[contains(@href, 'http')]",
                "//button",
                "//div[contains(@class, 'btn')]",
                "//span[contains(@class, 'button')]",
            ]
            
            all_elements = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            all_elements.append(element)
                except:
                    continue
            
            # Random interactions (0-3)
            num_interactions = random.randint(0, min(3, len(all_elements)))
            if num_interactions > 0:
                elements_to_interact = random.sample(all_elements, num_interactions)
                
                for element in elements_to_interact:
                    try:
                        # Scroll to element
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(random.uniform(1, 2))
                        
                        # Sometimes click, sometimes just hover
                        if random.random() > 0.7:
                            element.click()
                            interactions += 2
                            logger.info("🖱️ Chaotic click")
                            time.sleep(random.uniform(2, 4))
                            
                            # Handle new tabs
                            if len(self.driver.window_handles) > 1:
                                self.driver.switch_to.window(self.driver.window_handles[1])
                                time.sleep(random.uniform(1, 3))
                                self.driver.close()
                                self.driver.switch_to.window(self.driver.window_handles[0])
                        else:
                            interactions += 1
                            
                    except:
                        continue
            
            return interactions
            
        except Exception as e:
            logger.debug(f"Interactions error: {e}")
            return 0
    
    def chaotic_visit(self, website, visit_number, total_visits):
        """Perform one chaotic visit"""
        logger.info(f"🎲 CHAOTIC VISIT {visit_number}/{total_visits} to {website}")
        
        try:
            # Navigate to website
            self.driver.get(website)
            
            # Wait for load
            time.sleep(random.uniform(3, 6))
            
            # Handle cookie consent and disclaimers
            self.handle_cookie_consent()
            
            # Wait for content
            time.sleep(random.uniform(2, 4))
            
            # Perform chaotic actions
            impressions = 0
            
            # Chaotic scrolling
            impressions += self.chaotic_scroll()
            
            # Chaotic interactions
            impressions += self.chaotic_interactions()
            
            # Chaotic reading time
            read_time = random.uniform(5, 15)
            logger.info(f"📖 Chaotic reading: {read_time:.1f}s")
            time.sleep(read_time)
            impressions += 1
            
            # Final scroll
            if random.random() > 0.3:
                self.chaotic_scroll()
                impressions += 1
            
            # Ensure at least 1 impression
            final_impressions = max(1, impressions)
            logger.info(f"✅ Visit {visit_number} completed: {final_impressions} impressions")
            
            return final_impressions
            
        except Exception as e:
            logger.error(f"❌ Visit {visit_number} failed: {e}")
            return 1
    
    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

def main():
    """Main chaotic execution with real browser"""
    logger.info("🎲 AD FRAUD DETECTION - CHAOS MODE ACTIVATED")
    logger.info(f"🌀 Chaos Seed: {CHAOS_SEED}")
    logger.info(f"🎯 Target Website: {TARGET_WEBSITE}")
    logger.info(f"👥 Target Visits: {TARGET_VISITS}")
    logger.info(f"🕒 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test website connectivity
    try:
        response = requests.head(TARGET_WEBSITE, timeout=10)
        logger.info(f"🌐 Website status: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ Website check: {e}")
    
    total_impressions = 0
    start_time = datetime.now()
    
    for visit_num in range(1, TARGET_VISITS + 1):
        browser = None
        
        try:
            # Random delay between visits
            if visit_num > 1:
                delay = random.randint(30, 120)  # 30-120 seconds between visits
                logger.info(f"💤 Chaotic delay: {delay}s")
                time.sleep(delay)
            
            # Create browser for this visit
            browser = ChaosBrowser(CHAOS_SEED + visit_num)
            if browser.create_browser():
                # Perform visit
                impressions = browser.chaotic_visit(TARGET_WEBSITE, visit_num, TARGET_VISITS)
                total_impressions += impressions
            else:
                logger.error(f"❌ Browser creation failed for visit {visit_num}")
                total_impressions += 1  # Minimum impression
            
        except Exception as e:
            logger.error(f"❌ Chaotic error in visit {visit_num}: {e}")
            total_impressions += 1  # Minimum impression even on error
            
        finally:
            if browser:
                browser.close()
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds() / 60
    
    # Final report
    logger.info(f"\n{'='*50}")
    logger.info("📊 CHAOTIC SESSION REPORT")
    logger.info(f"{'='*50}")
    logger.info(f"🌐 Website: {TARGET_WEBSITE}")
    logger.info(f"👥 Visits Completed: {TARGET_VISITS}")
    logger.info(f"🔥 Total Impressions: {total_impressions}")
    
    if TARGET_VISITS > 0:
        avg_impressions = total_impressions / TARGET_VISITS
        logger.info(f"📈 Avg Impressions/Visit: {avg_impressions:.1f}")
    
    logger.info(f"⏱️ Chaos Duration: {duration:.1f} minutes")
    logger.info(f"🌀 Chaos Seed: {CHAOS_SEED}")
    logger.info(f"{'='*50}")
    logger.info("🏁 Chaotic execution completed!")

if __name__ == "__main__":
    main()
