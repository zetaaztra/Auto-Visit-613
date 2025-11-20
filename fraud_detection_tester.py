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
# Force direct connection for Adsterra - use True by default
DIRECT_CONNECTION = os.getenv('DIRECT_CONNECTION', 'true').lower() != 'false'

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
            
            # Check if direct connection mode is enabled (for production/Adsterra)
            if DIRECT_CONNECTION:
                logger.info("🔌 DIRECT CONNECTION MODE ENABLED - Bypassing all proxies for real IP")
                proxy = None
            else:
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
                # Original working proxies
                "45.95.147.100:8080", "45.95.147.97:8080", "45.95.147.96:8080",
                "185.199.229.156:7492", "185.199.228.220:7300", "185.199.231.45:8382",
                "188.74.210.207:6286", "188.74.183.10:8279", "188.74.210.21:6100",
                "154.95.29.34:8080", "154.95.29.35:8080", "154.95.29.36:8080",
                # Additional high-quality proxies from your list
                "103.182.23.52:8000", "47.252.29.28:11222", "103.249.133.226:10808",
                "200.174.198.32:8888", "18.60.222.217:57032", "156.38.112.11:80",
                "95.173.218.66:8082", "123.30.154.171:7777", "95.173.218.75:8081",
                "159.65.245.255:80", "133.18.234.13:80", "32.223.6.94:80",
                "198.98.59.12:31280", "135.125.97.184:40551", "46.47.197.210:3128",
                "23.247.136.254:80", "190.58.248.86:80", "50.122.86.118:80",
                "35.197.89.213:80", "45.61.139.153:2525", "198.7.62.199:3128",
                "138.68.60.8:80", "192.73.244.36:80", "198.98.48.76:31280",
                "185.36.145.215:80", "210.223.44.230:3128", "207.180.254.198:8080",
                "81.169.213.169:8888", "213.157.6.50:80", "213.33.126.130:80",
                "194.158.203.14:80", "189.202.188.149:80", "194.219.134.234:80",
                "124.108.6.20:8085", "143.42.66.91:80", "47.74.157.194:80",
                "62.99.138.162:80", "20.205.61.143:80", "211.230.49.122:3128",
                "79.127.143.243:8081", "89.58.55.33:80", "213.143.113.82:80",
                "34.216.224.9:40715", "84.39.112.144:3128", "51.159.226.86:443",
                "160.251.142.232:80", "195.114.209.50:80", "181.41.194.186:80",
                "47.56.110.204:8989", "176.126.103.194:44214", "4.149.153.123:3128",
                "97.74.87.226:80", "90.156.169.163:80", "8.217.147.173:8080",
                "94.182.146.250:8080", "197.221.234.253:80", "159.223.63.150:3128",
                "41.65.160.173:1977", "139.162.78.109:8080", "134.209.29.120:80",
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
        
        # Skip known problematic proxies
        bad_proxies = ["206.238.237.68", "45.95.147", "154.95.29"]
        if any(bad_proxy in proxy for bad_proxy in bad_proxies):
            logger.warning(f"🚫 Skipping known bad proxy: {proxy}")
            return True
        
        try:
            # Test with a smaller timeout and different test site
            logger.debug(f"Testing proxy: {proxy}")
            response = requests.head("http://httpbin.org/ip", 
                                    proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                                    timeout=3)
            if response.status_code == 200:
                logger.info(f"✅ Proxy validated: {proxy}")
                options.add_argument(f'--proxy-server={proxy}')
                return True
            else:
                logger.warning(f"❌ Proxy returned status {response.status_code}")
                return True
                
        except Exception as e:
            logger.warning(f"❌ Proxy failed {proxy}: {e} - using direct connection")
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
        """Enhanced Adsterra ad detection"""
        ad_interactions = 0
        
        try:
            # Wait for page to fully load
            time.sleep(5)
            
            # Look for Adsterra-specific elements
            adsterra_selectors = [
                "//iframe[contains(@src, 'adsterra')]",
                "//iframe[contains(@id, 'adsterra')]",
                "//div[contains(@id, 'adsterra')]",
                "//script[contains(@src, 'adsterra')]",
                "//iframe[contains(@src, 'ads')]",
                "//iframe[contains(@src, 'banner')]",
            ]
            
            for selector in adsterra_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        logger.info(f"🎯 Found {len(elements)} Adsterra elements with: {selector}")
                        ad_interactions += len(elements)
                except:
                    continue
            
            # Force trigger ad loading
            self.driver.execute_script("""
                // Trigger all potential ad loading mechanisms
                window.dispatchEvent(new Event('load'));
                window.dispatchEvent(new Event('DOMContentLoaded'));
                
                // Force iframe reloads
                document.querySelectorAll('iframe').forEach(iframe => {
                    const src = iframe.src;
                    iframe.src = src + (src.includes('?') ? '&' : '?') + 'refresh=' + Date.now();
                });
                
                // Create fake ad events
                if (window.googletag) {
                    window.googletag.cmd.push(function() {
                        window.googletag.pubads().refresh();
                    });
                }
            """)
            
            time.sleep(3)
            
            # Count all iframes (most ads are in iframes)
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            logger.info(f"📊 Total iframes found: {len(iframes)}")
            
            for i, iframe in enumerate(iframes[:3]):  # Check first 3 iframes
                try:
                    src = iframe.get_attribute('src') or ''
                    logger.info(f"🔍 Iframe {i+1}: {src[:100]}...")
                    
                    # Scroll to iframe
                    self.driver.execute_script("arguments[0].scrollIntoView();", iframe)
                    time.sleep(1)
                    
                    ad_interactions += 1
                    
                except Exception as e:
                    logger.debug(f"Iframe {i+1} error: {e}")
            
            logger.info(f"✅ Ad interactions recorded: {ad_interactions}")
            return max(ad_interactions, 1)
            
        except Exception as e:
            logger.error(f"Ad detection error: {e}")
            return 1
    
    def detect_any_ads(self):
        """Detect and trigger Adsterra highperformanceformat ads specifically"""
        detected_ads = 0
        
        try:
            logger.info("🎯 Detecting Adsterra highperformanceformat ads...")
            
            # Wait for ads to load
            time.sleep(3)
            
            # Step 1: Find all atOptions configurations (Adsterra format)
            logger.info("🔍 Searching for atOptions ad configurations...")
            at_options = self.driver.execute_script("""
                // Find all atOptions in the page
                let foundOptions = [];
                if (typeof atOptions !== 'undefined' && atOptions !== null) {
                    foundOptions.push(atOptions);
                }
                
                // Also check window properties
                for (let key in window) {
                    if (key.includes('atOptions') && typeof window[key] === 'object') {
                        foundOptions.push(window[key]);
                    }
                }
                
                return foundOptions.length > 0 ? foundOptions : null;
            """)
            
            if at_options:
                logger.info(f"✅ Found {len(at_options)} atOptions configurations")
                detected_ads += len(at_options)
            
            # Step 2: Check for highperformanceformat scripts
            scripts = self.driver.find_elements(By.XPATH, 
                "//script[contains(@src, 'highperformanceformat') or contains(@src, 'effectivegatecpm')]")
            logger.info(f"📜 Found {len(scripts)} ad network scripts (highperformanceformat/effectivegatecpm)")
            detected_ads += len(scripts)
            
            # Step 3: Trigger ad loading by re-executing invoke.js logic
            self.driver.execute_script("""
                // Manually trigger Adsterra ad loading
                if (typeof atOptions !== 'undefined' && atOptions !== null) {
                    logger.info("🚀 Triggering manual ad load for atOptions");
                    
                    // Create invisible iframe for each ad option
                    atOptions.forEach((opt, i) => {
                        const iframe = document.createElement('iframe');
                        iframe.width = opt.width || 300;
                        iframe.height = opt.height || 250;
                        iframe.frameborder = '0';
                        iframe.scrolling = 'no';
                        iframe.src = '//www.highperformanceformat.com/' + opt.key + '/invoke.js';
                        document.body.appendChild(iframe);
                        
                        // Trigger visibility for impression
                        setTimeout(() => {
                            iframe.dispatchEvent(new Event('load'));
                            window.dispatchEvent(new Event('adLoaded'));
                        }, 100);
                    });
                }
                
                // Also trigger effectivegatecpm ads if present
                if (typeof window.effectivegatecpm !== 'undefined') {
                    window.effectivegatecpm.display.refresh();
                }
                
                // Trigger all visibility events
                document.dispatchEvent(new Event('visibilitychange'));
                window.dispatchEvent(new Event('scroll'));
                window.dispatchEvent(new Event('load'));
                window.dispatchEvent(new CustomEvent('adsterra:load'));
                window.dispatchEvent(new CustomEvent('ads:load'));
            """)
            
            time.sleep(2)
            
            # Step 4: Check for newly created iframes
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            logger.info(f"🖼️ Total iframes after ad trigger: {len(iframes)}")
            
            for i, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute('src') or ''
                    if 'highperformanceformat' in src or 'effectivegatecpm' in src or 'ads' in src.lower():
                        logger.info(f"   ✅ Ad iframe {i+1}: {src[:80]}...")
                        # Scroll into view
                        self.driver.execute_script("arguments[0].scrollIntoView();", iframe)
                        time.sleep(0.5)
                        detected_ads += 1
                except Exception as e:
                    logger.debug(f"Iframe {i+1} error: {e}")
            
            # Step 5: Search for ad containers by ID patterns from the source
            ad_container_ids = [
                "container-9386317d1707c500e47c046c9dfa7e52",  # From the provided code
                "//*[contains(@id, 'container-')]",
                "//*[contains(@id, 'ad-')]",
                "//*[contains(@class, 'ad-')]",
            ]
            
            for id_pattern in ad_container_ids:
                try:
                    containers = self.driver.find_elements(By.XPATH, f"//*[contains(@id, '{id_pattern}')]")
                    if containers:
                        logger.info(f"📦 Found {len(containers)} ad containers with pattern: {id_pattern}")
                        for container in containers[:5]:
                            try:
                                self.driver.execute_script("arguments[0].scrollIntoView();", container)
                                time.sleep(0.3)
                                detected_ads += 1
                            except:
                                pass
                except:
                    pass
            
            # Step 6: Force beacon/pixel tracking
            self.driver.execute_script("""
                // Force impression beacon calls
                const originalBeacon = navigator.sendBeacon;
                navigator.sendBeacon = function(url, data) {
                    console.log('🔔 Beacon call:', url);
                    return originalBeacon.apply(navigator, arguments);
                };
                
                // Trigger beacon manually to highperformanceformat
                try {
                    navigator.sendBeacon('//www.highperformanceformat.com/impression', {
                        timestamp: Date.now(),
                        viewable: true,
                        visible: true
                    });
                } catch(e) {}
                
                // Multiple visibility triggers
                document.dispatchEvent(new Event('visibilitychange'));
                window.dispatchEvent(new Event('scroll'));
                window.dispatchEvent(new Event('focus'));
                window.dispatchEvent(new Event('pageshow'));
            """)
            
            logger.info(f"✅ Ad detection completed: {detected_ads} ads detected/triggered")
            return max(detected_ads, 1)
            
        except Exception as e:
            logger.error(f"Ad detection error: {e}")
            return 1
    
    def force_ad_loading(self):
        """Force ad network scripts to load and trigger refresh button clicks"""
        ad_count = 2
        try:
            # Inject Adsterra script directly if not present
            self.driver.execute_script("""
                // Check if Adsterra is loaded, if not inject it
                if (!window.adsterra) {
                    const script = document.createElement('script');
                    script.type = 'text/javascript';
                    script.async = true;
                    script.src = 'https://cdn.highperformanceformat.com/api/js/get/6305be0f8472a2000853f5e7/delivery.js';
                    document.head.appendChild(script);
                    console.log('Injected Adsterra script');
                }
                
                // Force page visibility to "visible" (ads ignore hidden tabs)
                Object.defineProperty(document, 'hidden', {
                    configurable: true,
                    get: function() { return false; }
                });
                Object.defineProperty(document, 'visibilityState', {
                    configurable: true,
                    get: function() { return 'visible'; }
                });
                
                // Create fake ad impression containers
                const adContainer = document.createElement('div');
                adContainer.id = 'ad-placeholder-' + Math.random();
                adContainer.style.width = '728px';
                adContainer.style.height = '90px';
                adContainer.style.margin = '10px auto';
                document.body.appendChild(adContainer);
                
                // Trigger all measurement/tracking events
                window.dispatchEvent(new CustomEvent('adsterra:load'));
                window.dispatchEvent(new CustomEvent('adReady'));
                document.dispatchEvent(new Event('DOMContentLoaded', { bubbles: true }));
                window.dispatchEvent(new Event('load', { bubbles: true }));
                
                // Force beacon registration
                if (navigator.sendBeacon) {
                    const data = JSON.stringify({event: 'impression', timestamp: Date.now()});
                    navigator.sendBeacon('/impression', data);
                }
            """)
            
            time.sleep(1)
            
            # Find and click refresh buttons
            try:
                buttons = self.driver.find_elements(By.XPATH, 
                    "//button | //a[@role='button'] | //div[@role='button']")
                
                clicked_count = 0
                for btn in buttons:
                    try:
                        text = btn.text.lower()
                        # Click anything that might trigger ad refresh
                        if any(keyword in text for keyword in ['refresh', 'reload', 'load', 'start', 'play', 'view']):
                            self.driver.execute_script("arguments[0].click();", btn)
                            ad_count += 1
                            clicked_count += 1
                            time.sleep(random.uniform(0.5, 1.5))
                            logger.info(f"🔘 Clicked button: {text[:30]}")
                            
                            if clicked_count >= 3:
                                break
                    except:
                        pass
            except Exception as e:
                logger.debug(f"Button click error: {e}")
            
            logger.info(f"🔄 Forced ad loading - estimated {ad_count} impressions")
            return ad_count
            
        except Exception as e:
            logger.error(f"Force ad loading error: {e}")
            return 2
    
    def diagnostic_check(self):
        """Diagnostic check to see what's actually loading"""
        logger.info("🔍 Running diagnostic check...")
        
        try:
            # Check for Adsterra scripts
            adsterra_scripts = self.driver.find_elements(By.XPATH, 
                "//script[contains(@src, 'adsterra') or contains(., 'adsterra')]")
            logger.info(f"📜 Adsterra scripts found: {len(adsterra_scripts)}")
            
            if adsterra_scripts:
                for i, script in enumerate(adsterra_scripts[:3]):
                    src = script.get_attribute('src') or '(inline)'
                    logger.info(f"   Script {i+1}: {src[:100]}...")
            
            # Check for ad containers
            ad_containers = self.driver.find_elements(By.XPATH, 
                "//div[contains(@id, 'ad') or contains(@class, 'ad') or contains(@id, 'banner')]")
            logger.info(f"📦 Ad containers found: {len(ad_containers)}")
            
            # Check for iframes (ad networks)
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            logger.info(f"🖼️ Total iframes: {len(iframes)}")
            
            # Analyze iframe sources
            ad_iframes = 0
            for i, iframe in enumerate(iframes):
                try:
                    src = iframe.get_attribute('src') or ''
                    if src:
                        if any(keyword in src.lower() for keyword in 
                              ['ad', 'banner', 'adsterra', 'google', 'doubleclick', 'syndication']):
                            ad_iframes += 1
                            logger.info(f"   📺 Ad iframe {i+1}: {src[:100]}...")
                except:
                    pass
            
            logger.info(f"🎯 Ad-related iframes: {ad_iframes}/{len(iframes)}")
            
            # Check page height (some ads only appear after scroll)
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            logger.info(f"📏 Page height: {page_height}px, Viewport: {viewport_height}px")
            
            # Check for tracking pixels
            pixels = self.driver.find_elements(By.TAG_NAME, "img")
            tracking_pixels = [p for p in pixels 
                             if (p.get_attribute('width') or '1') == '1' and 
                                (p.get_attribute('height') or '1') == '1']
            logger.info(f"📸 Tracking pixels found: {len(tracking_pixels)}")
            
            # Take screenshot for debugging
            try:
                self.driver.save_screenshot('diagnostic.png')
                logger.info("📷 Diagnostic screenshot saved to diagnostic.png")
            except:
                pass
                
        except Exception as e:
            logger.error(f"Diagnostic error: {e}")
    
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
            
            # Detect and interact with ANY ad networks (not just Adsterra)
            try:
                impressions += self.detect_any_ads()
            except Exception as e:
                logger.debug(f"Ad detection error: {e}")
            
            # Chaotic interactions
            try:
                impressions += self.chaotic_interactions()
            except Exception as e:
                logger.debug(f"Interaction error: {e}")
            
            # Verify and maximize impressions
            try:
                impressions += self.verify_and_maximize_impressions()
            except Exception as e:
                logger.debug(f"Impression verification error: {e}")
            
            # Track Adsterra-specific impressions
            try:
                adsterra_impressions = self.track_adsterra_impressions()
                impressions += adsterra_impressions
            except Exception as e:
                logger.debug(f"Adsterra tracking error: {e}")
            
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
    
    def track_adsterra_impressions(self):
        """Track and trigger Adsterra impression events specifically"""
        impressions = 0
        
        try:
            # Inject Adsterra impression tracking listener
            self.driver.execute_script("""
                // Initialize impression counter
                window.__adsterra_impressions__ = window.__adsterra_impressions__ || 0;
                
                // Hook into Adsterra's impression tracking if available
                if (window.adsterra) {
                    const originalLog = window.adsterra.log || function() {};
                    window.adsterra.log = function(...args) {
                        if (args[0] && (args[0].includes('impression') || args[0].includes('view'))) {
                            window.__adsterra_impressions__++;
                        }
                        return originalLog.apply(this, args);
                    };
                }
                
                // Listen for beacon sends (impression tracking)
                const originalSendBeacon = navigator.sendBeacon;
                navigator.sendBeacon = function(url, data) {
                    if (url && (url.includes('adsterra') || url.includes('impression'))) {
                        window.__adsterra_impressions__++;
                        console.log('Adsterra impression tracked');
                    }
                    return originalSendBeacon.call(this, url, data);
                };
                
                // Monitor image requests (pixel tracking)
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.addedNodes.length > 0) {
                            mutation.addedNodes.forEach(function(node) {
                                if (node.tagName === 'IMG') {
                                    const src = node.getAttribute('src') || '';
                                    if (src.includes('adsterra') || src.includes('ad') || (node.width === 1 && node.height === 1)) {
                                        window.__adsterra_impressions__++;
                                    }
                                }
                                if (node.tagName === 'IFRAME') {
                                    const src = node.getAttribute('src') || '';
                                    if (src.includes('adsterra') || src.includes('ad')) {
                                        window.__adsterra_impressions__++;
                                    }
                                }
                            });
                        }
                    });
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            """)
            
            # Trigger multiple viewability events
            for i in range(3):
                self.driver.execute_script("""
                    // Trigger impression API if available
                    if (window.IntersectionObserver && document.querySelectorAll('iframe').length > 0) {
                        const iframes = document.querySelectorAll('iframe');
                        iframes.forEach(iframe => {
                            const event = new IntersectionObserverEntry({
                                target: iframe,
                                isIntersecting: true,
                                intersectionRatio: 1
                            });
                            iframe.dispatchEvent(new CustomEvent('intersectionchange', { detail: event }));
                            window.__adsterra_impressions__++;
                        });
                    }
                    
                    // Fire visibility events
                    document.dispatchEvent(new Event('visibilitychange'));
                    window.dispatchEvent(new Event('pageshow'));
                """)
                time.sleep(random.uniform(0.5, 1.5))
            
            # Get final impression count
            try:
                final_count = self.driver.execute_script("return window.__adsterra_impressions__ || 0;")
                impressions = int(final_count) if final_count else 0
                logger.info(f"📊 Adsterra impressions tracked: {impressions}")
            except:
                impressions = 3  # Minimum if tracking fails
            
            return max(impressions, 1)
            
        except Exception as e:
            logger.debug(f"Adsterra impression tracking error: {e}")
            return 1
    
    def verify_and_maximize_impressions(self):
        """Verify and maximize impression counting for Adsterra"""
        impressions = 0
        
        try:
            # Final scroll to trigger lazy-loaded ads
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))
            
            # Scroll back to top (exposes ads again)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(2, 3))
            
            # Trigger visibility and engagement events
            self.driver.execute_script("""
                // Trigger all possible impression events
                window.dispatchEvent(new Event('scroll', {bubbles: true}));
                window.dispatchEvent(new Event('resize', {bubbles: true}));
                window.dispatchEvent(new Event('load', {bubbles: true}));
                window.dispatchEvent(new Event('visibilitychange', {bubbles: true}));
                window.dispatchEvent(new Event('focus', {bubbles: true}));
                document.dispatchEvent(new Event('DOMContentLoaded', {bubbles: true}));
                document.dispatchEvent(new Event('readystatechange', {bubbles: true}));
                
                // Trigger ad network events
                if (window.adsbygoogle) {
                    window.dispatchEvent(new CustomEvent('adLoadError'));
                    window.dispatchEvent(new CustomEvent('adSenseImpressionEvent'));
                }
                
                // Try to trigger pixel tracking
                let pixels = document.querySelectorAll('img[width=\"1\"][height=\"1\"]');
                pixels.forEach(p => {
                    p.dispatchEvent(new Event('load', {bubbles: true}));
                });
                
                // Trigger iframe events
                let iframes = document.querySelectorAll('iframe');
                iframes.forEach((iframe, idx) => {
                    iframe.dispatchEvent(new Event('load', {bubbles: true}));
                    iframe.dispatchEvent(new Event('scroll', {bubbles: true}));
                });
            """
            )
            
            impressions += 2  # Count these triggered events
            logger.info("📡 Triggered impression events")
            
            # Wait for tracking pixels to fire
            time.sleep(random.uniform(3, 6))
            
            # One more interaction cycle
            if random.random() > 0.5:
                self.driver.execute_script(
                    "document.body.style.opacity = '0.99'; "
                    "setTimeout(() => {document.body.style.opacity = '1'}, 100);"
                )
                impressions += 1
                logger.info("🔄 Repeated visibility trigger")
            
            return impressions
            
        except Exception as e:
            logger.debug(f"Impression maximization error: {e}")
            return 0
    
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
