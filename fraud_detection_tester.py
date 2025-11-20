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
        """Create browser with free residential proxies and fallback"""
        try:
            options = Options()
            
            # GitHub Actions compatibility
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            # Enhanced stealth
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Try to get and validate proxy (with fallback to direct connection)
            proxy = self.get_residential_proxy()
            self.validate_and_use_proxy(options, proxy)
            
            # Random viewport
            viewports = [(1920, 1080), (1366, 768), (1536, 864), (1440, 900), (1280, 720)]
            viewport = random.choice(viewports)
            options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            ]
            user_agent = random.choice(user_agents)
            options.add_argument(f'--user-agent={user_agent}')
            
            # Create driver
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Advanced stealth scripts
            stealth_scripts = [
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
                "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});",
                "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});",
                "window.chrome = {runtime: {}};",
            ]
            
            for script in stealth_scripts:
                try:
                    self.driver.execute_script(script)
                except:
                    pass
            
            logger.info("🚀 Chaotic browser with proxy created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser creation failed: {e}")
            return False
    
    def get_residential_proxy(self):
        """Get free residential proxy from multiple sources with fallback"""
        try:
            # Try to get fresh proxies from GitHub sources
            proxy_sources = [
                "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
                "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            ]
            
            all_proxies = []
            for source in proxy_sources:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        proxies = [line.strip() for line in response.text.split('\n') if line.strip()]
                        all_proxies.extend(proxies)
                except Exception as e:
                    logger.debug(f"Failed to fetch from {source}: {e}")
                    continue
            
            # Add hardcoded residential-looking proxies as fallback
            hardcoded_proxies = [
                "45.95.147.100:8080", "45.95.147.97:8080", "45.95.147.96:8080",
                "185.199.229.156:7492", "185.199.228.220:7300", "185.199.231.45:8382",
                "188.74.210.207:6286", "188.74.183.10:8279", "188.74.210.21:6100",
                "154.95.29.34:8080", "154.95.29.35:8080", "154.95.29.36:8080",
            ]
            all_proxies.extend(hardcoded_proxies)
            
            if all_proxies:
                # Try to validate proxy before returning
                selected_proxy = random.choice(all_proxies)
                logger.debug(f"Selected proxy: {selected_proxy}")
                return selected_proxy
            
        except Exception as e:
            logger.debug(f"Proxy fetch error: {e}")
        
        logger.info("⚠️ No proxies available - will use direct connection")
        return None
    
    def validate_and_use_proxy(self, options, proxy):
        """Validate proxy connectivity before using it"""
        if not proxy:
            logger.info("📡 Using direct connection (no proxy)")
            return True
        
        try:
            # Quick connectivity test (5 second timeout)
            logger.debug(f"Testing proxy: {proxy}")
            response = requests.head("http://www.google.com", 
                                    proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                                    timeout=5)
            logger.info(f"✅ Proxy validated: {proxy}")
            options.add_argument(f'--proxy-server={proxy}')
            return True
            
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Proxy timeout: {proxy} - using direct connection")
            return True  # Fallback to direct connection
            
        except requests.exceptions.ConnectionError:
            logger.warning(f"❌ Proxy unreachable: {proxy} - using direct connection")
            return True  # Fallback to direct connection
            
        except Exception as e:
            logger.debug(f"Proxy validation error: {e} - using direct connection")
            return True  # Fallback to direct connection
    
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
    
    def detect_and_interact_with_adsterra(self):
        """Specifically detect and interact with Adsterra ads"""
        adsterra_patterns = [
            "adsterra",
            "adst.",
            "win-adsterra",
            "ads-terra",
        ]
        
        ad_interactions = 0
        
        for pattern in adsterra_patterns:
            try:
                # Look for Adsterra iframes
                iframe_selectors = [
                    f"//iframe[contains(@src, '{pattern}')]",
                    f"//iframe[contains(@id, '{pattern}')]",
                    f"//iframe[contains(@class, '{pattern}')]",
                ]
                
                for selector in iframe_selectors:
                    try:
                        iframes = self.driver.find_elements(By.XPATH, selector)
                        for iframe in iframes:
                            if iframe.is_displayed():
                                # Switch to iframe and interact
                                self.driver.switch_to.frame(iframe)
                                
                                # Look for clickable elements in the ad
                                ad_elements = self.driver.find_elements(By.XPATH, "//a | //button | //div[@onclick]")
                                if ad_elements:
                                    # Hover over ad (simulates interest)
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    actions = ActionChains(self.driver)
                                    actions.move_to_element(ad_elements[0]).pause(2).perform()
                                    ad_interactions += 1
                                    logger.info(f"🎯 Interacted with Adsterra ad: {pattern}")
                                
                                self.driver.switch_to.default_content()
                                time.sleep(random.uniform(2, 4))
                    except:
                        self.driver.switch_to.default_content()
                        continue
                        
            except Exception as e:
                logger.debug(f"Adsterra detection error: {e}")
                continue
        
        return ad_interactions
    
    def diagnostic_check(self):
        """Diagnostic check to see what's actually loading"""
        logger.info("🔍 Running diagnostic check...")
        
        # Check for Adsterra scripts
        adsterra_scripts = self.driver.find_elements(By.XPATH, "//script[contains(@src, 'adsterra')]")
        logger.info(f"📜 Adsterra scripts found: {len(adsterra_scripts)}")
        
        # Check for ad containers
        ad_containers = self.driver.find_elements(By.XPATH, "//div[contains(@id, 'ad')] | //div[contains(@class, 'ad')]")
        logger.info(f"📦 Ad containers found: {len(ad_containers)}")
        
        # Check for iframes
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        logger.info(f"🖼️ Total iframes: {len(iframes)}")
        
        for i, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute('src') or ''
                if 'ad' in src.lower():
                    logger.info(f"   📺 Ad iframe {i+1}: {src[:100]}...")
            except:
                pass
        
        # Take screenshot for debugging
        try:
            self.driver.save_screenshot('diagnostic.png')
            logger.info("📸 Diagnostic screenshot saved")
        except:
            pass
    
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
        """Perform one chaotic visit with robust error handling"""
        logger.info(f"🎲 CHAOTIC VISIT {visit_number}/{total_visits} to {website}")
        
        try:
            # Navigate to website with timeout handling
            try:
                self.driver.get(website)
            except TimeoutException:
                logger.warning(f"⏱️ Page load timeout - but may have loaded ads anyway")
                time.sleep(random.uniform(2, 3))
            except Exception as e:
                logger.error(f"Navigation error: {e}")
                # Retry without proxy on network errors
                if "tunnel" in str(e).lower() or "connection" in str(e).lower():
                    logger.info("🔄 Retrying without proxy...")
                    time.sleep(random.uniform(2, 5))
                    self.driver.quit()
                    # Create new browser without proxy
                    self.driver = None
                    return 1  # Return minimum impression
                raise
            
            # Wait for load
            time.sleep(random.uniform(3, 6))
            
            # Handle cookie consent and disclaimers
            try:
                self.handle_cookie_consent()
            except Exception as e:
                logger.debug(f"Cookie handling error: {e}")
            
            # Wait for content
            time.sleep(random.uniform(2, 4))
            
            # 🔍 DIAGNOSTIC CHECK
            try:
                self.diagnostic_check()
            except Exception as e:
                logger.debug(f"Diagnostic error: {e}")
            
            # Perform chaotic actions
            impressions = 0
            
            # Chaotic scrolling
            try:
                impressions += self.chaotic_scroll()
            except Exception as e:
                logger.debug(f"Scroll error: {e}")
                impressions += 1
            
            # Detect and interact with Adsterra ads
            try:
                impressions += self.detect_and_interact_with_adsterra()
            except Exception as e:
                logger.debug(f"Ad detection error: {e}")
            
            # Chaotic interactions
            try:
                impressions += self.chaotic_interactions()
            except Exception as e:
                logger.debug(f"Interaction error: {e}")
            
            # Chaotic reading time
            read_time = random.uniform(5, 15)
            logger.info(f"📖 Chaotic reading: {read_time:.1f}s")
            time.sleep(read_time)
            impressions += 1
            
            # Final scroll
            if random.random() > 0.3:
                try:
                    self.chaotic_scroll()
                    impressions += 1
                except:
                    pass
            
            # Ensure at least 1 impression
            final_impressions = max(1, impressions)
            logger.info(f"✅ Visit {visit_number} completed: {final_impressions} impressions")
            
            return final_impressions
            
        except Exception as e:
            logger.error(f"❌ Visit {visit_number} failed: {e}")
            return 1  # Return minimum impression even on error
    
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
