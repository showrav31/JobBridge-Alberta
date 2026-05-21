"""
JobBridge Alberta - Complete Analysis & Chart Generator
Generates: location_chart.png, category_chart.png, companies_chart.png, summary_report.txt

Author: Showrav Deb Chowdhury
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from collections import Counter

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

def load_data():
    """Load the jobs data"""
    print("="*70)
    print("  JOBBRIDGE ALBERTA - DATA ANALYSIS")
    print("="*70)
    print()
    
    csv_path = 'data/raw/jobs_data.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return None
    
    print(f"📂 Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} jobs")
    print()
    
    return df


def create_location_chart(df):
    """Create location distribution chart"""
    print("📍 Creating location_chart.png...")
    
    # Create output directory
    os.makedirs('data/analysis', exist_ok=True)
    
    # Get top 20 provinces/cities
    if 'province' in df.columns and df['province'].notna().sum() > 0:
        location_data = df['province'].value_counts().head(20)
        title = 'Jobs by Province (Top 20)'
        xlabel = 'Number of Jobs'
        ylabel = 'Province'
    elif 'city' in df.columns:
        location_data = df['city'].value_counts().head(20)
        title = 'Jobs by City (Top 20)'
        xlabel = 'Number of Jobs'
        ylabel = 'City'
    else:
        print("   ⚠️  No location data found")
        return
    
    # Create horizontal bar chart
    plt.figure(figsize=(12, 10))
    colors = plt.cm.viridis(range(len(location_data)))
    location_data.plot(kind='barh', color=colors)
    plt.xlabel(xlabel, fontsize=12, fontweight='bold')
    plt.ylabel(ylabel, fontsize=12, fontweight='bold')
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Save
    plt.savefig('data/analysis/location_chart.png', dpi=300, bbox_inches='tight')
    print("   ✅ Saved: data/analysis/location_chart.png")
    plt.close()


def create_category_chart(df):
    """Create job category pie chart"""
    print("📊 Creating category_chart.png...")
    
    # Categorize jobs based on title
    def categorize_job(title):
        if pd.isna(title):
            return 'Other'
        
        title_lower = str(title).lower()
        
        if any(word in title_lower for word in ['developer', 'programmer', 'software', 'engineer', 'architect', 'analyst', 'data']):
            return 'Technology & IT'
        elif any(word in title_lower for word in ['nurse', 'doctor', 'medical', 'health', 'therapist', 'pharmacist']):
            return 'Healthcare'
        elif any(word in title_lower for word in ['manager', 'director', 'supervisor', 'coordinator', 'administrator']):
            return 'Management'
        elif any(word in title_lower for word in ['accountant', 'financial', 'sales', 'marketing', 'business']):
            return 'Business & Finance'
        elif any(word in title_lower for word in ['teacher', 'professor', 'instructor', 'educator']):
            return 'Education'
        elif any(word in title_lower for word in ['electrician', 'plumber', 'mechanic', 'welder', 'carpenter', 'technician']):
            return 'Trades & Technical'
        elif any(word in title_lower for word in ['chef', 'cook', 'server', 'retail', 'clerk', 'cashier']):
            return 'Service & Retail'
        else:
            return 'Other'
    
    df['job_category'] = df['title'].apply(categorize_job)
    
    # Get category counts
    category_counts = df['job_category'].value_counts()
    
    # Create pie chart
    plt.figure(figsize=(12, 10))
    colors = sns.color_palette('Set3', len(category_counts))
    
    wedges, texts, autotexts = plt.pie(
        category_counts, 
        labels=category_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 11, 'weight': 'bold'}
    )
    
    # Make percentage text more visible
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_weight('bold')
    
    plt.title('Job Distribution by Category', fontsize=16, fontweight='bold', pad=20)
    plt.axis('equal')
    plt.tight_layout()
    
    # Save
    plt.savefig('data/analysis/category_chart.png', dpi=300, bbox_inches='tight')
    print("   ✅ Saved: data/analysis/category_chart.png")
    plt.close()


def create_companies_chart(df):
    """Create top companies bar chart"""
    print("🏢 Creating companies_chart.png...")
    
    if 'company' not in df.columns:
        print("   ⚠️  No company data found")
        return
    
    # Filter out generic company names
    df_companies = df[df['company'].notna()].copy()
    
    # Remove generic placeholders
    generic_names = ['employer details', 'confidential', 'n/a', 'not specified', 'company not disclosed']
    for generic in generic_names:
        df_companies = df_companies[~df_companies['company'].str.lower().str.contains(generic, na=False)]
    
    # Get top 25 companies
    top_companies = df_companies['company'].value_counts().head(25)
    
    if len(top_companies) == 0:
        print("   ⚠️  No valid company data")
        return
    
    # Create horizontal bar chart
    plt.figure(figsize=(14, 10))
    colors = plt.cm.coolwarm(range(len(top_companies)))
    top_companies.plot(kind='barh', color=colors)
    plt.xlabel('Number of Job Postings', fontsize=12, fontweight='bold')
    plt.ylabel('Company', fontsize=12, fontweight='bold')
    plt.title('Top 25 Companies by Number of Postings', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Save
    plt.savefig('data/analysis/companies_chart.png', dpi=300, bbox_inches='tight')
    print("   ✅ Saved: data/analysis/companies_chart.png")
    plt.close()


def generate_summary_report(df):
    """Generate comprehensive summary report"""
    print("📄 Creating summary_report.txt...")
    
    # Calculate statistics
    total_jobs = len(df)
    
    # Provinces
    if 'province' in df.columns:
        provinces_covered = df['province'].nunique()
        top_provinces = df['province'].value_counts().head(10)
    else:
        provinces_covered = 0
        top_provinces = None
    
    # Cities
    if 'city' in df.columns:
        cities_covered = df['city'].nunique()
        top_cities = df['city'].value_counts().head(10)
    else:
        cities_covered = 0
        top_cities = None
    
    # Companies
    if 'company' in df.columns:
        unique_companies = df['company'].nunique()
        top_companies = df['company'].value_counts().head(10)
    else:
        unique_companies = 0
        top_companies = None
    
    # Job titles
    if 'title' in df.columns:
        unique_titles = df['title'].nunique()
        top_titles = df['title'].value_counts().head(10)
    else:
        unique_titles = 0
        top_titles = None
    
    # Data completeness
    total_cells = len(df) * len(df.columns)
    filled_cells = total_cells - df.isnull().sum().sum()
    completeness = (filled_cells / total_cells) * 100
    
    # Job categories
    if 'job_category' in df.columns:
        category_counts = df['job_category'].value_counts()
    else:
        # Categorize on the fly
        def categorize_job(title):
            if pd.isna(title):
                return 'Other'
            title_lower = str(title).lower()
            if any(word in title_lower for word in ['developer', 'programmer', 'software', 'engineer']):
                return 'Technology & IT'
            elif any(word in title_lower for word in ['nurse', 'doctor', 'medical', 'health']):
                return 'Healthcare'
            elif any(word in title_lower for word in ['manager', 'director', 'supervisor']):
                return 'Management'
            elif any(word in title_lower for word in ['accountant', 'sales', 'marketing']):
                return 'Business & Finance'
            elif any(word in title_lower for word in ['teacher', 'professor', 'instructor']):
                return 'Education'
            elif any(word in title_lower for word in ['electrician', 'plumber', 'mechanic']):
                return 'Trades & Technical'
            else:
                return 'Other'
        
        df['job_category'] = df['title'].apply(categorize_job)
        category_counts = df['job_category'].value_counts()
    
    # Create report
    report = f"""
================================================================================
  JOBBRIDGE ALBERTA - COMPREHENSIVE DATA SUMMARY REPORT
================================================================================

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Data Source: Job Bank Canada (Government of Canada)

================================================================================
  DATASET OVERVIEW
================================================================================

Total Jobs Collected:              {total_jobs:,}
Unique Companies:                  {unique_companies:,}
Unique Job Titles:                 {unique_titles:,}
Provinces/Territories Covered:     {provinces_covered}
Cities Covered:                    {cities_covered}

Data Completeness:                 {completeness:.1f}%

================================================================================
  GEOGRAPHIC DISTRIBUTION
================================================================================
"""
    
    if top_provinces is not None:
        report += "\nTop 10 Provinces by Job Count:\n"
        report += "-" * 70 + "\n"
        for idx, (province, count) in enumerate(top_provinces.items(), 1):
            pct = (count / total_jobs) * 100
            report += f"  {idx:2d}. {str(province)[:30]:<32} {count:>6,} jobs ({pct:>5.1f}%)\n"
    
    if top_cities is not None:
        report += "\nTop 10 Cities by Job Count:\n"
        report += "-" * 70 + "\n"
        for idx, (city, count) in enumerate(top_cities.items(), 1):
            if pd.notna(city):
                pct = (count / total_jobs) * 100
                report += f"  {idx:2d}. {str(city)[:30]:<32} {count:>6,} jobs ({pct:>5.1f}%)\n"
    
    report += f"""
================================================================================
  JOB CATEGORIES
================================================================================

"""
    
    for category, count in category_counts.items():
        pct = (count / total_jobs) * 100
        report += f"  {category:<30} {count:>6,} jobs ({pct:>5.1f}%)\n"
    
    report += f"""
================================================================================
  TOP HIRING COMPANIES
================================================================================

"""
    
    if top_companies is not None:
        report += "Top 10 Companies:\n"
        report += "-" * 70 + "\n"
        for idx, (company, count) in enumerate(top_companies.items(), 1):
            if pd.notna(company) and str(company).lower() not in ['employer details', 'confidential']:
                report += f"  {idx:2d}. {str(company)[:45]:<47} {count:>4} positions\n"
    
    report += f"""
================================================================================
  MOST COMMON JOB TITLES
================================================================================

"""
    
    if top_titles is not None:
        report += "Top 10 Job Titles:\n"
        report += "-" * 70 + "\n"
        for idx, (title, count) in enumerate(top_titles.items(), 1):
            if pd.notna(title):
                report += f"  {idx:2d}. {str(title)[:50]:<52} {count:>4} postings\n"
    
    report += f"""
================================================================================
  DATA QUALITY METRICS
================================================================================

Field Completeness:
"""
    
    for col in df.columns:
        filled = df[col].notna().sum()
        filled_pct = (filled / len(df)) * 100
        status = "✓" if filled_pct >= 80 else "⚠" if filled_pct >= 50 else "✗"
        report += f"  {status} {col:<25} {filled:>6,} / {len(df):>6,} ({filled_pct:>5.1f}%)\n"
    
    report += f"""
================================================================================
  DATA COLLECTION STATISTICS
================================================================================

Collection Method:         Comprehensive systematic search
Search Coverage:           All provinces × Multiple job categories
Duplicate Removal:         Automatic (by URL)
Data Source:               Job Bank Canada (official government database)
Scraping Period:           {df['scraped_date'].min()} to {df['scraped_date'].max()}

================================================================================
  PROJECT INFORMATION
================================================================================

Project Name:              JobBridge Alberta
Purpose:                   AI-Powered Job Matching Platform
Technology:                Graph Neural Networks + NLP
Student:                   Showrav Deb Chowdhury
Institution:               Concordia University of Edmonton
Supervisor:                [Professor Name]

================================================================================
  NEXT STEPS
================================================================================

1. Data Cleaning:
   - Standardize location names
   - Remove duplicates
   - Handle missing values
   - Validate company names

2. NLP Processing:
   - Extract skills from job descriptions
   - Categorize jobs using BERT embeddings
   - Build skill taxonomy

3. Graph Construction:
   - Create job-skill relationship graph
   - Build candidate-job matching network
   - Implement recommendation system

4. Model Training:
   - Train Graph Neural Network
   - Validate with real job matching scenarios
   - Optimize for Alberta job market

================================================================================
  END OF REPORT
================================================================================
"""
    
    # Save report
    report_path = 'data/analysis/summary_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"   ✅ Saved: {report_path}")
    
    # Also print key stats to console
    print()
    print("="*70)
    print("  KEY STATISTICS")
    print("="*70)
    print(f"  Total Jobs: {total_jobs:,}")
    print(f"  Provinces: {provinces_covered}")
    print(f"  Cities: {cities_covered}")
    print(f"  Companies: {unique_companies:,}")
    print(f"  Data Quality: {completeness:.1f}%")
    print("="*70)
    print()


def main():
    """Main function"""
    print()
    print("="*70)
    print("  JOBBRIDGE ALBERTA - ANALYSIS & CHART GENERATION")
    print("="*70)
    print()
    
    # Load data
    df = load_data()
    
    if df is None:
        print("❌ Cannot proceed without data")
        return
    
    print("="*70)
    print("  GENERATING CHARTS & REPORTS")
    print("="*70)
    print()
    
    # Create all outputs
    create_location_chart(df)
    create_category_chart(df)
    create_companies_chart(df)
    generate_summary_report(df)
    
    print()
    print("="*70)
    print("  ANALYSIS COMPLETE!")
    print("="*70)
    print()
    print("📊 Generated Files:")
    print("   • data/analysis/location_chart.png")
    print("   • data/analysis/category_chart.png")
    print("   • data/analysis/companies_chart.png")
    print("   • data/analysis/summary_report.txt")
    print()
    print("✅ All files ready for professor presentation!")
    print()


if __name__ == "__main__":
    main()