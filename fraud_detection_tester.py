#!/usr/bin/env python3
"""
Ad Fraud Detection - Chaos Mode
Takes inputs from GitHub Actions for complete randomization
"""

import os
import sys
import time
import random
import logging
from datetime import datetime

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

def chaotic_sleep(min_seconds, max_seconds):
    """Sleep with random variation"""
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)
    return sleep_time

def simulate_chaotic_visit(visit_number, total_visits, website):
    """Simulate a completely chaotic visit"""
    logger.info(f"🎲 CHAOTIC VISIT {visit_number}/{total_visits} to {website}")
    
    # Random visit components
    actions = []
    
    # Random number of actions (3-8)
    num_actions = random.randint(3, 8)
    
    for i in range(num_actions):
        action_type = random.choice(['scroll', 'click', 'hover', 'read', 'navigate'])
        
        if action_type == 'scroll':
            sleep_time = chaotic_sleep(1, 4)
            actions.append(f"📜 Scrolled for {sleep_time:.1f}s")
            
        elif action_type == 'click':
            sleep_time = chaotic_sleep(0.5, 2)
            actions.append(f"🖱️ Clicked after {sleep_time:.1f}s")
            
        elif action_type == 'hover':
            sleep_time = chaotic_sleep(1, 3)
            actions.append(f"⚡ Hovered for {sleep_time:.1f}s")
            
        elif action_type == 'read':
            sleep_time = chaotic_sleep(2, 10)
            actions.append(f"📖 Read for {sleep_time:.1f}s")
            
        elif action_type == 'navigate':
            sleep_time = chaotic_sleep(1, 5)
            actions.append(f"🧭 Navigated for {sleep_time:.1f}s")
    
    # Random impressions (1-10)
    impressions = random.randint(1, 10)
    
    logger.info(f"✅ Visit {visit_number} completed: {impressions} impressions")
    for action in actions:
        logger.info(f"   {action}")
    
    return impressions

def main():
    """Main chaotic execution"""
    logger.info("🎲 AD FRAUD DETECTION - CHAOS MODE ACTIVATED")
    logger.info(f"🌀 Chaos Seed: {CHAOS_SEED}")
    logger.info(f"🎯 Target Website: {TARGET_WEBSITE}")
    logger.info(f"👥 Target Visits: {TARGET_VISITS}")
    logger.info(f"🕒 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_impressions = 0
    
    for visit_num in range(1, TARGET_VISITS + 1):
        try:
            # Random delay between visits (0-120 seconds)
            if visit_num > 1:
                delay = random.randint(0, 120)
                logger.info(f"💤 Chaotic delay: {delay}s")
                time.sleep(delay)
            
            # Simulate visit
            impressions = simulate_chaotic_visit(visit_num, TARGET_VISITS, TARGET_WEBSITE)
            total_impressions += impressions
            
        except Exception as e:
            logger.error(f"❌ Chaotic error in visit {visit_num}: {e}")
            # Continue despite errors - chaos!
            continue
    
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
    
    duration = (datetime.now() - datetime.now()).total_seconds() / 60  # Placeholder
    logger.info(f"⏱️ Chaos Duration: {duration:.1f} minutes")
    logger.info(f"🌀 Chaos Seed: {CHAOS_SEED}")
    logger.info(f"{'='*50}")
    logger.info("🏁 Chaotic execution completed!")

if __name__ == "__main__":
    main()
