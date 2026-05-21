# """
# JobBank Canada Scraper for JobBridge Alberta
# Updated with correct HTML selectors
# Version: 1.1
# Author: Showrav Deb Chowdhury
# """

# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import time
# from datetime import datetime
# import os
# import logging

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)


# class JobBankScraper:
#     """
#     Scraper for Job Bank Canada job postings
#     UPDATED WITH CORRECT SELECTORS
#     """
    
#     def __init__(self):
#         """Initialize the scraper"""
#         self.base_url = "https://www.jobbank.gc.ca"
#         self.headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#             'Accept-Language': 'en-US,en;q=0.5',
#             'Accept-Encoding': 'gzip, deflate',
#             'Connection': 'keep-alive',
#         }
#         logger.info("✅ JobBank Scraper initialized")
    
#     def search_jobs(self, keyword="", location="Alberta", max_pages=5):
#         """
#         Search for jobs and collect data
        
#         Args:
#             keyword (str): Search term (e.g., "software developer")
#             location (str): Location to search (default: "Alberta")
#             max_pages (int): Number of pages to scrape
        
#         Returns:
#             list: List of job dictionaries
#         """
#         logger.info(f"\n🔍 Starting job search...")
#         logger.info(f"   Keyword: '{keyword}'")
#         logger.info(f"   Location: '{location}'")
#         logger.info(f"   Max pages: {max_pages}")
        
#         all_jobs = []
        
#         for page_num in range(1, max_pages + 1):
#             logger.info(f"\n📄 Scraping page {page_num}/{max_pages}...")
            
#             # Construct URL with parameters
#             search_url = f"{self.base_url}/jobsearch/jobsearch"
#             params = {
#                 'searchstring': keyword,
#                 'locationstring': location,
#                 'page': page_num
#             }
            
#             try:
#                 # Make request
#                 response = requests.get(
#                     search_url, 
#                     headers=self.headers, 
#                     params=params, 
#                     timeout=15
#                 )
                
#                 # Check response
#                 if response.status_code == 200:
#                     logger.info(f"   ✅ Page loaded successfully (Status: {response.status_code})")
#                     soup = BeautifulSoup(response.content, 'html.parser')
                    
#                     # Extract jobs from page
#                     jobs = self._extract_jobs_from_page(soup, page_num)
                    
#                     if jobs:
#                         all_jobs.extend(jobs)
#                         logger.info(f"   ✅ Found {len(jobs)} jobs on page {page_num}")
#                     else:
#                         logger.warning(f"   ⚠️ No jobs found on page {page_num}")
#                         # If no jobs on page 1, something is wrong
#                         if page_num == 1:
#                             logger.error("   ⚠️ No jobs on first page - check selectors!")
#                         else:
#                             logger.info("   📍 Might have reached end of results")
#                             break
#                 else:
#                     logger.error(f"   ❌ Request failed (Status: {response.status_code})")
                
#                 # Be polite - wait between requests
#                 logger.info(f"   ⏳ Waiting 2 seconds before next request...")
#                 time.sleep(2)
                
#             except requests.exceptions.Timeout:
#                 logger.error(f"   ❌ Timeout on page {page_num}")
#                 continue
#             except requests.exceptions.RequestException as e:
#                 logger.error(f"   ❌ Request error on page {page_num}: {e}")
#                 continue
#             except Exception as e:
#                 logger.error(f"   ❌ Unexpected error on page {page_num}: {e}")
#                 continue
        
#         logger.info(f"\n✅ Scraping complete! Total jobs collected: {len(all_jobs)}")
#         return all_jobs
    
#     def _extract_jobs_from_page(self, soup, page_num):
#         """
#         Extract all jobs from a single page (SEARCH RESULTS PAGE)
        
#         Args:
#             soup: BeautifulSoup object
#             page_num: Current page number
        
#         Returns:
#             list: Jobs found on this page
#         """
#         jobs = []
        
#         # Try multiple selectors for job listings on search results page
#         # Job Bank search results might use different structure than detail pages
        
#         # Try finding job articles/sections
#         job_cards = soup.find_all('article')  # Generic article tags
        
#         if not job_cards:
#             # Try alternative selectors
#             job_cards = soup.find_all('div', class_='job')
        
#         if not job_cards:
#             # Try yet another alternative
#             job_cards = soup.find_all('section', class_='job-posting-brief')
        
#         if not job_cards:
#             logger.warning(f"      ⚠️ Could not find job cards with standard selectors")
#             logger.info(f"      🔍 Trying to find all links to job postings...")
            
#             # Alternative: Find all links to job postings
#             job_links = soup.find_all('a', href=True)
#             job_posting_links = [
#                 link for link in job_links 
#                 if '/jobposting/' in link.get('href', '')
#             ]
            
#             if job_posting_links:
#                 logger.info(f"      ✅ Found {len(job_posting_links)} job posting links")
#                 # Get details from each job posting page
#                 for idx, link in enumerate(job_posting_links[:25], 1):  # Limit to 25 per page
#                     job_url = self.base_url + link['href'] if not link['href'].startswith('http') else link['href']
#                     logger.info(f"      📄 Getting job {idx}/{len(job_posting_links[:25])}")
#                     job_data = self.get_job_details(job_url, page_num)
#                     if job_data:
#                         jobs.append(job_data)
#                     time.sleep(1)  # Be polite
                
#                 return jobs
#             else:
#                 logger.error(f"      ❌ No job links found either")
#                 return jobs
        
#         logger.info(f"      ✅ Found {len(job_cards)} job cards on page")
        
#         for idx, job_card in enumerate(job_cards, 1):
#             try:
#                 job_data = self._extract_single_job_from_card(job_card, page_num)
#                 if job_data:
#                     jobs.append(job_data)
#                     logger.info(f"      ✓ Job {idx}: {job_data.get('title', 'No title')[:50]}")
#             except Exception as e:
#                 logger.error(f"      ⚠️ Error extracting job {idx}: {e}")
#                 continue
        
#         return jobs
    
#     def _extract_single_job_from_card(self, job_element, page_num):
#         """
#         Extract basic data from a job card on search results page
        
#         Args:
#             job_element: BeautifulSoup element containing job
#             page_num: Page number
        
#         Returns:
#             dict: Basic job data
#         """
#         job_data = {
#             'title': None,
#             'company': None,
#             'location': None,
#             'url': None,
#             'page_number': page_num,
#             'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         }
        
#         try:
#             # Try to find title and URL from link
#             link_elem = job_element.find('a', href=True)
#             if link_elem:
#                 # Get URL
#                 href = link_elem.get('href', '')
#                 if href:
#                     job_data['url'] = self.base_url + href if not href.startswith('http') else href
                
#                 # Title might be in the link text
#                 if link_elem.text.strip():
#                     job_data['title'] = link_elem.text.strip()
            
#             # If we have a URL, get full details from job posting page
#             if job_data['url']:
#                 detailed_data = self.get_job_details(job_data['url'], page_num)
#                 if detailed_data:
#                     return detailed_data
        
#         except Exception as e:
#             logger.error(f"         ⚠️ Error in card extraction: {e}")
        
#         return job_data if job_data['title'] else None
    
#     def get_job_details(self, job_url, page_num=1):
#         """
#         Get full details from individual job posting page
#         THIS IS WHERE WE USE YOUR SELECTORS!
        
#         Args:
#             job_url (str): URL of the job posting
#             page_num (int): Page number for tracking
        
#         Returns:
#             dict: Complete job details
#         """
#         job_data = {
#             'title': None,
#             'company': None,
#             'location': None,
#             'city': None,
#             'postal_code': None,
#             'responsibilities': None,
#             'url': job_url,
#             'page_number': page_num,
#             'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         }
        
#         try:
#             logger.info(f"         🔗 Fetching: {job_url}")
#             response = requests.get(job_url, headers=self.headers, timeout=15)
            
#             if response.status_code != 200:
#                 logger.error(f"         ❌ Failed to load job page (Status: {response.status_code})")
#                 return None
            
#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             # ============================================================
#             # EXTRACT JOB TITLE
#             # ============================================================
#             # Looking for: id="wb-cont" class="title"
#             title_elem = soup.find(id='wb-cont', class_='title')
#             if title_elem:
#                 job_data['title'] = title_elem.text.strip()
#                 logger.info(f"         ✓ Title: {job_data['title'][:50]}")
#             else:
#                 # Alternative: just id="wb-cont"
#                 title_elem = soup.find(id='wb-cont')
#                 if title_elem:
#                     job_data['title'] = title_elem.text.strip()
            
#             # ============================================================
#             # EXTRACT COMPANY NAME
#             # ============================================================
#             # Looking for: class="business"
#             company_elem = soup.find(class_='business')
#             if company_elem:
#                 job_data['company'] = company_elem.text.strip()
#                 logger.info(f"         ✓ Company: {job_data['company']}")
            
#             # ============================================================
#             # EXTRACT LOCATION
#             # ============================================================
#             # Looking for: class="city"
#             city_elem = soup.find(class_='city')
#             if city_elem:
#                 job_data['city'] = city_elem.text.strip()
            
#             # Looking for: class="postalcode"
#             postal_elem = soup.find(class_='postalcode')
#             if postal_elem:
#                 job_data['postal_code'] = postal_elem.text.strip()
            
#             # Combine city and postal code for location
#             location_parts = []
#             if job_data['city']:
#                 location_parts.append(job_data['city'])
#             if job_data['postal_code']:
#                 location_parts.append(job_data['postal_code'])
            
#             if location_parts:
#                 job_data['location'] = ', '.join(location_parts)
#                 logger.info(f"         ✓ Location: {job_data['location']}")
            
#             # Also try the property="address" typeof="PostalAddress" selector
#             address_elem = soup.find(property='address', typeof='PostalAddress')
#             if address_elem and not job_data['location']:
#                 job_data['location'] = address_elem.text.strip()
            
#             # ============================================================
#             # EXTRACT RESPONSIBILITIES
#             # ============================================================
#             # Looking for: id="jobOverview-2" property="responsibilities"
#             responsibilities_section = soup.find(id='jobOverview-2', property='responsibilities')
            
#             if responsibilities_section:
#                 # Look for <ul class="csvlist"> inside
#                 csvlist = responsibilities_section.find('ul', class_='csvlist')
#                 if csvlist:
#                     # Extract all list items
#                     list_items = csvlist.find_all('li')
#                     responsibilities = [li.text.strip() for li in list_items]
#                     job_data['responsibilities'] = ' | '.join(responsibilities)
#                     logger.info(f"         ✓ Responsibilities: {len(responsibilities)} items found")
#                 else:
#                     # If no csvlist, get all text from the section
#                     job_data['responsibilities'] = responsibilities_section.text.strip()
            
#             # Alternative: try just id="jobOverview-2"
#             if not job_data['responsibilities']:
#                 overview_elem = soup.find(id='jobOverview-2')
#                 if overview_elem:
#                     job_data['responsibilities'] = overview_elem.text.strip()
            
#             # ============================================================
#             # ADDITIONAL FIELDS (Optional but useful)
#             # ============================================================
            
#             # Try to get salary if available
#             salary_elem = soup.find(class_='salary')
#             if salary_elem:
#                 job_data['salary'] = salary_elem.text.strip()
            
#             # Try to get education requirements
#             education_elem = soup.find(id='education')
#             if education_elem:
#                 job_data['education'] = education_elem.text.strip()
            
#             # Try to get experience requirements
#             experience_elem = soup.find(id='experience')
#             if experience_elem:
#                 job_data['experience'] = experience_elem.text.strip()
            
#             # Get full job description if available
#             description_elem = soup.find(id='description')
#             if description_elem:
#                 job_data['full_description'] = description_elem.text.strip()
            
#             logger.info(f"         ✅ Successfully extracted job details")
            
#         except requests.exceptions.Timeout:
#             logger.error(f"         ❌ Timeout loading job page")
#             return None
#         except Exception as e:
#             logger.error(f"         ❌ Error getting job details: {e}")
#             return None
        
#         # Only return if we got at least a title
#         if job_data['title']:
#             return job_data
#         else:
#             logger.warning(f"         ⚠️ No title found for job")
#             return None
    
#     def save_to_csv(self, jobs, filename='jobs_data.csv'):
#         """
#         Save jobs to CSV file
        
#         Args:
#             jobs (list): List of job dictionaries
#             filename (str): Output filename
#         """
#         if not jobs:
#             logger.warning("❌ No jobs to save!")
#             return
        
#         # Create DataFrame
#         df = pd.DataFrame(jobs)
        
#         # Ensure output directory exists
#         output_dir = 'data/raw'
#         os.makedirs(output_dir, exist_ok=True)
        
#         # Full path
#         filepath = os.path.join(output_dir, filename)
        
#         # Save to CSV
#         df.to_csv(filepath, index=False, encoding='utf-8')
        
#         logger.info(f"\n💾 Saved {len(jobs)} jobs to {filepath}")
        
#         # Print summary
#         print("\n" + "="*60)
#         print("  DATA SUMMARY")
#         print("="*60)
#         print(f"Total jobs: {len(df)}")
#         print(f"Columns: {list(df.columns)}")
#         print(f"\nMissing values:")
#         print(df.isnull().sum())
#         print(f"\nLocation distribution:")
#         if 'location' in df.columns:
#             print(df['location'].value_counts().head(10))
#         print(f"\nSample data:")
#         print(df.head(3).to_string())
#         print("="*60 + "\n")
    
#     def save_to_json(self, jobs, filename='jobs_data.json'):
#         """
#         Save jobs to JSON file
        
#         Args:
#             jobs (list): List of job dictionaries
#             filename (str): Output filename
#         """
#         if not jobs:
#             logger.warning("❌ No jobs to save!")
#             return
        
#         import json
        
#         output_dir = 'data/raw'
#         os.makedirs(output_dir, exist_ok=True)
#         filepath = os.path.join(output_dir, filename)
        
#         with open(filepath, 'w', encoding='utf-8') as f:
#             json.dump(jobs, f, indent=2, ensure_ascii=False)
        
#         logger.info(f"💾 Saved {len(jobs)} jobs to {filepath}")


# def main():
#     """
#     Main function to run the scraper
#     """
#     print("\n" + "="*60)
#     print("  JOBBRIDGE ALBERTA - JOB BANK SCRAPER v1.1")
#     print("  Updated with correct HTML selectors")
#     print("="*60 + "\n")
    
#     # Create scraper
#     scraper = JobBankScraper()
    
#     # Configuration - CHANGE THESE AS NEEDED
#     KEYWORD = "software developer"  # Change this to search different jobs
#     LOCATION = "Alberta"            # Can be "Calgary", "Edmonton", etc.
#     MAX_PAGES = 3                   # Start with 3 pages for testing
    
#     print(f"Search Configuration:")
#     print(f"  Keyword: {KEYWORD}")
#     print(f"  Location: {LOCATION}")
#     print(f"  Max Pages: {MAX_PAGES}")
#     print("\n")
    
#     # Search for jobs
#     jobs = scraper.search_jobs(
#         keyword=KEYWORD,
#         location=LOCATION,
#         max_pages=MAX_PAGES
#     )
    
#     # Save results
#     if jobs:
#         print(f"\n🎉 Successfully collected {len(jobs)} jobs!")
#         scraper.save_to_csv(jobs, filename='jobs_data.csv')
#         scraper.save_to_json(jobs, filename='jobs_data.json')
        
#         print("\n✅ Data saved successfully!")
#         print(f"   CSV: data/raw/jobs_data.csv")
#         print(f"   JSON: data/raw/jobs_data.json")
#     else:
#         print("\n❌ No jobs were scraped.")
#         print("\nPossible reasons:")
#         print("  1. No jobs match your search criteria")
#         print("  2. Website structure changed")
#         print("  3. Connection issues")
#         print("\nTry:")
#         print("  - Different search keywords")
#         print("  - Checking your internet connection")
#         print("  - Verifying the website is accessible")
    
#     print("\n" + "="*60)
#     print("  SCRAPING COMPLETE!")
#     print("="*60 + "\n")


# if __name__ == "__main__":
#     main()


"""
JobBridge Alberta - COMPREHENSIVE Job Bank Scraper
Version 2.0 - Collects ALL jobs from Job Bank Canada

This scraper systematically collects jobs from ALL categories and locations
across Canada, not just specific searches.

Author: Showrav Deb Chowdhury
Date: February 3, 2026
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveJobBankScraper:
    """
    Scraper that collects ALL jobs from Job Bank Canada
    Searches across all categories and provinces
    """
    
    def __init__(self):
        """Initialize the scraper"""
        self.base_url = "https://www.jobbank.gc.ca"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # All Canadian provinces/territories
        self.provinces = [
            'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick',
            'Newfoundland and Labrador', 'Northwest Territories', 'Nova Scotia',
            'Nunavut', 'Ontario', 'Prince Edward Island', 'Quebec', 
            'Saskatchewan', 'Yukon'
        ]
        
        # Major job categories (NOC - National Occupational Classification)
        self.job_categories = [
            # Management
            'manager', 'director', 'supervisor', 'administrator',
            # Business & Finance
            'accountant', 'analyst', 'consultant', 'coordinator',
            # Technology
            'developer', 'engineer', 'programmer', 'technician',
            # Healthcare
            'nurse', 'doctor', 'therapist', 'assistant',
            # Education
            'teacher', 'instructor', 'professor', 'educator',
            # Trades
            'electrician', 'plumber', 'mechanic', 'carpenter',
            # Sales & Service
            'sales', 'clerk', 'representative', 'agent',
            # General (catches everything else)
            '', # Empty search gets all jobs
        ]
        
        logger.info("✅ Comprehensive Job Bank Scraper initialized")
        logger.info(f"   Will search {len(self.provinces)} provinces")
        logger.info(f"   Using {len(self.job_categories)} search categories")
    
    def scrape_all_jobs(self, max_jobs=5000, pages_per_search=5):
        """
        Scrape ALL available jobs from Job Bank
        
        Args:
            max_jobs: Maximum total jobs to collect (default 5000)
            pages_per_search: Pages to scrape per search (default 5)
        
        Returns:
            list: All collected jobs
        """
        logger.info("\n" + "="*70)
        logger.info("  COMPREHENSIVE JOB COLLECTION")
        logger.info("="*70)
        logger.info(f"\n🎯 Target: {max_jobs} jobs")
        logger.info(f"📄 Pages per search: {pages_per_search}")
        logger.info(f"\n🚀 Starting collection...\n")
        
        all_jobs = []
        searches_completed = 0
        
        # Strategy: Search by category in each province
        for province in self.provinces:
            logger.info(f"\n{'='*70}")
            logger.info(f"  PROVINCE: {province.upper()}")
            logger.info(f"{'='*70}")
            
            for category in self.job_categories:
                # Stop if we've reached target
                if len(all_jobs) >= max_jobs:
                    logger.info(f"\n✅ Reached target of {max_jobs} jobs!")
                    break
                
                category_display = category if category else "All Jobs"
                logger.info(f"\n📍 Searching: {category_display} in {province}")
                
                # Search jobs
                jobs = self.search_jobs(
                    keyword=category,
                    location=province,
                    max_pages=pages_per_search
                )
                
                if jobs:
                    # Remove duplicates by URL before adding
                    existing_urls = {j['url'] for j in all_jobs}
                    new_jobs = [j for j in jobs if j['url'] not in existing_urls]
                    
                    all_jobs.extend(new_jobs)
                    logger.info(f"   ✅ Added {len(new_jobs)} new jobs (duplicates removed)")
                    logger.info(f"   📊 Total so far: {len(all_jobs)} jobs")
                else:
                    logger.info(f"   ⚠️  No jobs found")
                
                searches_completed += 1
                
                # Save progress every 10 searches
                if searches_completed % 10 == 0:
                    self.save_progress(all_jobs)
                
                # Be polite - wait between searches
                time.sleep(3)
            
            # Stop if target reached
            if len(all_jobs) >= max_jobs:
                break
        
        logger.info(f"\n{'='*70}")
        logger.info(f"  COLLECTION COMPLETE!")
        logger.info(f"{'='*70}")
        logger.info(f"\n📊 Final Statistics:")
        logger.info(f"   Total jobs collected: {len(all_jobs)}")
        logger.info(f"   Searches completed: {searches_completed}")
        logger.info(f"   Provinces covered: {len(set(j.get('province', '') for j in all_jobs))}")
        logger.info(f"\n")
        
        return all_jobs
    
    def search_jobs(self, keyword="", location="Alberta", max_pages=5):
        """
        Search for jobs (single search)
        """
        all_jobs = []
        
        for page_num in range(1, max_pages + 1):
            search_url = f"{self.base_url}/jobsearch/jobsearch"
            params = {
                'searchstring': keyword,
                'locationstring': location,
                'page': page_num
            }
            
            try:
                response = requests.get(search_url, headers=self.headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    jobs = self._extract_jobs_from_page(soup, page_num, location)
                    
                    if jobs:
                        all_jobs.extend(jobs)
                    else:
                        # No more jobs on this page, stop pagination
                        break
                else:
                    logger.error(f"      ❌ Failed (Status: {response.status_code})")
                    break
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"      ❌ Error: {e}")
                break
        
        return all_jobs
    
    def _extract_jobs_from_page(self, soup, page_num, province):
        """Extract jobs from search results page"""
        jobs = []
        
        # Find job posting links
        job_links = soup.find_all('a', href=True)
        job_posting_links = [
            link for link in job_links 
            if '/jobposting/' in link.get('href', '')
        ]
        
        if not job_posting_links:
            return jobs
        
        # Get details from each job
        for link in job_posting_links[:25]:  # Max 25 per page
            job_url = self.base_url + link['href'] if not link['href'].startswith('http') else link['href']
            
            job_data = self.get_job_details(job_url, page_num, province)
            if job_data:
                jobs.append(job_data)
            
            time.sleep(0.5)  # Small delay between job detail requests
        
        return jobs
    
    def get_job_details(self, job_url, page_num=1, province='Unknown'):
        """Get full details from job posting page"""
        job_data = {
            'title': None,
            'company': None,
            'location': None,
            'city': None,
            'province': province,
            'postal_code': None,
            'responsibilities': None,
            'salary': None,
            'education': None,
            'experience': None,
            'url': job_url,
            'page_number': page_num,
            'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            response = requests.get(job_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find(id='wb-cont', class_='title')
            if title_elem:
                job_data['title'] = title_elem.text.strip()
            else:
                title_elem = soup.find(id='wb-cont')
                if title_elem:
                    job_data['title'] = title_elem.text.strip()
            
            # Extract company
            company_elem = soup.find(class_='business')
            if company_elem:
                company_text = company_elem.text.strip()
                if company_text and company_text.lower() not in ['employer details', 'confidential', 'n/a']:
                    job_data['company'] = company_text
            
            # Extract city
            city_elem = soup.find(class_='city')
            if city_elem:
                job_data['city'] = city_elem.text.strip()
            
            # Extract postal code
            postal_elem = soup.find(class_='postalcode')
            if postal_elem:
                job_data['postal_code'] = postal_elem.text.strip()
            
            # Combine location
            location_parts = []
            if job_data['city']:
                location_parts.append(job_data['city'])
            if job_data['postal_code']:
                location_parts.append(job_data['postal_code'])
            if location_parts:
                job_data['location'] = ', '.join(location_parts)
            
            # Extract responsibilities
            resp_section = soup.find(id='jobOverview-2', property='responsibilities')
            if resp_section:
                csvlist = resp_section.find('ul', class_='csvlist')
                if csvlist:
                    items = csvlist.find_all('li')
                    responsibilities = [li.text.strip() for li in items]
                    job_data['responsibilities'] = ' | '.join(responsibilities)
                else:
                    job_data['responsibilities'] = resp_section.text.strip()
            
            # Extract salary (if available)
            salary_elem = soup.find(class_='salary')
            if salary_elem:
                job_data['salary'] = salary_elem.text.strip()
            
            # Extract education
            education_elem = soup.find(id='education')
            if education_elem:
                job_data['education'] = education_elem.text.strip()
            
            # Extract experience
            experience_elem = soup.find(id='experience')
            if experience_elem:
                job_data['experience'] = experience_elem.text.strip()
            
        except Exception as e:
            logger.error(f"         ❌ Error extracting {job_url}: {e}")
            return None
        
        return job_data if job_data['title'] else None
    
    def save_progress(self, jobs):
        """Save progress during collection"""
        if not jobs:
            return
        
        output_dir = 'data/raw'
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, 'jobs_data_progress.csv')
        
        df = pd.DataFrame(jobs)
        df.to_csv(filepath, index=False, encoding='utf-8')
        logger.info(f"\n💾 Progress saved: {len(jobs)} jobs")
    
    def save_to_csv(self, jobs, filename='jobs_data.csv'):
        """Save final results to CSV (appends if file exists)"""
        if not jobs:
            logger.warning("❌ No jobs to save!")
            return
        
        output_dir = 'data/raw'
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        df_new = pd.DataFrame(jobs)
        
        # Check if file exists
        if os.path.exists(filepath):
            # Read existing data
            df_existing = pd.read_csv(filepath)
            logger.info(f"📂 Existing file has {len(df_existing)} jobs")
            
            # Append new data
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            
            # Remove duplicates based on URL
            df_combined = df_combined.drop_duplicates(subset=['url'], keep='first')
            
            # Save
            df_combined.to_csv(filepath, index=False, encoding='utf-8')
            
            added = len(df_combined) - len(df_existing)
            logger.info(f"✅ Added {added} new jobs")
            logger.info(f"📊 Total jobs in database: {len(df_combined)}")
        else:
            # Create new file
            df_new.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"✅ Created new file with {len(df_new)} jobs")
        
        # Also save as JSON
        json_path = filepath.replace('.csv', '.json')
        df_new.to_json(json_path, orient='records', indent=2)
        logger.info(f"✅ Also saved as JSON: {json_path}")
    
    def generate_summary(self, jobs):
        """Generate collection summary"""
        if not jobs:
            return
        
        df = pd.DataFrame(jobs)
        
        print("\n" + "="*70)
        print("  COLLECTION SUMMARY")
        print("="*70)
        print(f"\n📊 Total Jobs: {len(df)}")
        
        if 'province' in df.columns:
            print(f"\n📍 Jobs by Province:")
            province_counts = df['province'].value_counts().head(10)
            for prov, count in province_counts.items():
                print(f"   {prov:<30} {count:>5} jobs")
        
        if 'city' in df.columns:
            print(f"\n🏙️  Top 10 Cities:")
            city_counts = df['city'].value_counts().head(10)
            for city, count in city_counts.items():
                if pd.notna(city):
                    print(f"   {str(city)[:30]:<32} {count:>5} jobs")
        
        if 'company' in df.columns:
            print(f"\n🏢 Top 10 Companies:")
            company_counts = df['company'].value_counts().head(10)
            for company, count in company_counts.items():
                if pd.notna(company):
                    print(f"   {str(company)[:40]:<42} {count:>3} jobs")
        
        print("\n" + "="*70 + "\n")


def main():
    """
    Main function to run comprehensive collection
    """
    print("\n" + "="*70)
    print("  JOBBRIDGE ALBERTA - COMPREHENSIVE JOB COLLECTOR")
    print("  Version 2.0 - Collects ALL Jobs from Job Bank")
    print("="*70 + "\n")
    
    scraper = ComprehensiveJobBankScraper()
    
    # Configuration
    MAX_JOBS = 5000  # Target number of jobs
    PAGES_PER_SEARCH = 3  # Keep this low to cover more categories
    
    print("⚙️  Configuration:")
    print(f"   Target jobs: {MAX_JOBS}")
    print(f"   Pages per search: {PAGES_PER_SEARCH}")
    print(f"   Estimated time: 3-5 hours")
    print()
    
    input("Press Enter to start collection (or Ctrl+C to cancel)...")
    
    # Collect all jobs
    jobs = scraper.scrape_all_jobs(
        max_jobs=MAX_JOBS,
        pages_per_search=PAGES_PER_SEARCH
    )
    
    # Save results
    if jobs:
        scraper.save_to_csv(jobs)
        scraper.generate_summary(jobs)
    else:
        print("\n❌ No jobs were collected")
    
    print("\n" + "="*70)
    print("  COLLECTION COMPLETE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Collection stopped by user")
        print("   Progress has been saved automatically")
        print()