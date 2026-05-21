"""
JobBank Canada Scraper for JobBridge Alberta
This script scrapes job postings from Job Bank Canada
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import os

class JobBankScraper:
    """
    A class to scrape job postings from Job Bank Canada
    """
    
    def __init__(self):
        """Initialize the scraper with base URL and headers"""
        self.base_url = "https://www.jobbank.gc.ca"
        # Headers to make our scraper look like a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print("✅ JobBank Scraper initialized")
    
    def search_jobs(self, keyword="", location="Alberta", max_pages=5):
        """
        Search for jobs and return list of job data
        
        Args:
            keyword (str): Job search keyword (e.g., "software developer")
            location (str): Location to search (default: "Alberta")
            max_pages (int): Number of pages to scrape (default: 5)
        
        Returns:
            list: List of job dictionaries
        """
        print(f"\n🔍 Starting job search...")
        print(f"   Keyword: {keyword}")
        print(f"   Location: {location}")
        print(f"   Max pages: {max_pages}")
        
        all_jobs = []
        
        for page_num in range(1, max_pages + 1):
            print(f"\n📄 Scraping page {page_num}/{max_pages}...")
            
            # Construct the search URL
            search_url = f"{self.base_url}/jobsearch/jobsearch"
            params = {
                'searchstring': keyword,
                'locationstring': location,
                'page': page_num
            }
            
            try:
                # Make the request
                response = requests.get(search_url, headers=self.headers, params=params, timeout=10)
                
                # Check if request was successful
                if response.status_code == 200:
                    print(f"   ✅ Page loaded successfully")
                    
                    # Parse the HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract jobs from this page
                    jobs_on_page = self.extract_jobs_from_page(soup, page_num)
                    
                    if jobs_on_page:
                        all_jobs.extend(jobs_on_page)
                        print(f"   ✅ Found {len(jobs_on_page)} jobs on this page")
                    else:
                        print(f"   ⚠️ No jobs found on this page")
                else:
                    print(f"   ❌ Failed to load page (Status code: {response.status_code})")
                
                # Be polite - wait between requests
                print(f"   ⏳ Waiting 2 seconds before next request...")
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Error occurred: {e}")
                continue
        
        print(f"\n✅ Scraping complete! Total jobs found: {len(all_jobs)}")
        return all_jobs
    
    def extract_jobs_from_page(self, soup, page_num):
        """
        Extract job information from a single page
        
        Args:
            soup: BeautifulSoup object of the page
            page_num: Current page number
        
        Returns:
            list: List of job dictionaries from this page
        """
        jobs = []
        
        # TODO: You need to inspect the actual website and update these selectors
        # This is a template - the actual class names may be different
        
        # Find all job postings on the page
        # You need to find the correct HTML element that contains job postings
        job_cards = soup.find_all('article', class_='jobposting')  # UPDATE THIS
        
        if not job_cards:
            print(f"      ⚠️ Could not find job cards. HTML structure may have changed.")
            return jobs
        
        for idx, job_card in enumerate(job_cards, 1):
            try:
                job_data = self.extract_single_job(job_card)
                if job_data:
                    job_data['page_number'] = page_num
                    jobs.append(job_data)
                    print(f"      Job {idx}: {job_data['title']}")
            except Exception as e:
                print(f"      ⚠️ Error extracting job {idx}: {e}")
                continue
        
        return jobs
    
    def extract_single_job(self, job_element):
        """
        Extract data from a single job posting element
        
        Args:
            job_element: BeautifulSoup element containing job data
        
        Returns:
            dict: Job information
        """
        # TODO: Update these selectors based on actual website structure
        # You need to inspect the website and find the correct class names
        
        job_data = {
            'title': 'N/A',
            'company': 'N/A',
            'location': 'N/A',
            'description': 'N/A',
            'url': 'N/A',
            'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Extract job title
            title_elem = job_element.find('span', class_='jobtitle')  # UPDATE THIS
            if title_elem:
                job_data['title'] = title_elem.text.strip()
            
            # Extract company name
            company_elem = job_element.find('span', class_='employer-name')  # UPDATE THIS
            if company_elem:
                job_data['company'] = company_elem.text.strip()
            
            # Extract location
            location_elem = job_element.find('span', class_='location')  # UPDATE THIS
            if location_elem:
                job_data['location'] = location_elem.text.strip()
            
            # Extract job URL
            link_elem = job_element.find('a', href=True)
            if link_elem:
                job_data['url'] = self.base_url + link_elem['href']
            
            # Extract description (if available on listing page)
            desc_elem = job_element.find('div', class_='description')  # UPDATE THIS
            if desc_elem:
                job_data['description'] = desc_elem.text.strip()[:500]  # First 500 chars
        
        except Exception as e:
            print(f"         ⚠️ Error extracting job details: {e}")
        
        return job_data
    
    def save_to_csv(self, jobs, filename='jobs_data.csv'):
        """
        Save scraped jobs to CSV file
        
        Args:
            jobs (list): List of job dictionaries
            filename (str): Name of CSV file
        """
        if not jobs:
            print("❌ No jobs to save!")
            return
        
        # Create DataFrame
        df = pd.DataFrame(jobs)
        
        # Ensure data/raw directory exists
        os.makedirs('data/raw', exist_ok=True)
        
        # Save to CSV
        filepath = os.path.join('data', 'raw', filename)
        df.to_csv(filepath, index=False)
        
        print(f"\n💾 Saved {len(jobs)} jobs to: {filepath}")
        print(f"\n📊 Data Preview:")
        print(df.head())
        print(f"\n📈 Data Summary:")
        print(f"   Total jobs: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Date range: {df['scraped_date'].min()} to {df['scraped_date'].max()}")


def main():
    """
    Main function to run the scraper
    """
    print("=" * 60)
    print("  JOBBRIDGE ALBERTA - JOB BANK SCRAPER")
    print("=" * 60)
    
    # Create scraper instance
    scraper = JobBankScraper()
    
    # Search for jobs
    jobs = scraper.search_jobs(
        keyword="software developer",  # Change this to search different jobs
        location="Alberta",
        max_pages=3  # Start with just 3 pages for testing
    )
    
    # Save results
    if jobs:
        scraper.save_to_csv(jobs, filename='jobs_data.csv')
    else:
        print("\n❌ No jobs were scraped. Check the website structure and selectors.")
    
    print("\n" + "=" * 60)
    print("  SCRAPING COMPLETE!")
    print("=" * 60)


# This runs when you execute the file
if __name__ == "__main__":
    main()