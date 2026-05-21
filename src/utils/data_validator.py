"""
Data Validation Script for JobBridge Alberta
Checks the quality of scraped job data
"""

import pandas as pd
import os

def validate_job_data(csv_path='data/raw/jobs_data.csv'):
    """
    Validate the scraped job data and generate a quality report
    """
    print("\n" + "="*60)
    print("  JOBBRIDGE ALBERTA - DATA VALIDATION REPORT")
    print("="*60 + "\n")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return None
    
    # Load data
    print(f"📂 Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # ============================================================
    # BASIC STATISTICS
    # ============================================================
    print(f"\n📊 BASIC STATISTICS:")
    print(f"{'─'*60}")
    print(f"   Total records: {len(df)}")
    print(f"   Columns: {len(df.columns)}")
    print(f"   Column names: {', '.join(df.columns)}")
    
    # ============================================================
    # DATA COMPLETENESS
    # ============================================================
    print(f"\n📋 DATA COMPLETENESS:")
    print(f"{'─'*60}")
    
    total_cells = len(df) * len(df.columns)
    filled_cells = total_cells - df.isnull().sum().sum()
    completeness = (filled_cells / total_cells) * 100
    
    print(f"   Overall data completeness: {completeness:.1f}%")
    print(f"\n   Missing values by column:")
    
    for col in df.columns:
        missing = df[col].isnull().sum()
        missing_pct = (missing / len(df)) * 100
        status = "✅" if missing_pct < 10 else "⚠️" if missing_pct < 30 else "❌"
        print(f"   {status} {col:.<30} {missing:>3} ({missing_pct:>5.1f}%)")
    
    # ============================================================
    # UNIQUE VALUES
    # ============================================================
    print(f"\n🔢 UNIQUE VALUES:")
    print(f"{'─'*60}")
    
    if 'title' in df.columns:
        print(f"   Unique job titles: {df['title'].nunique()}")
    if 'company' in df.columns:
        print(f"   Unique companies: {df['company'].nunique()}")
    if 'location' in df.columns:
        print(f"   Unique locations: {df['location'].nunique()}")
    if 'city' in df.columns:
        print(f"   Unique cities: {df['city'].nunique()}")
    
    # ============================================================
    # LOCATION DISTRIBUTION
    # ============================================================
    print(f"\n📍 LOCATION DISTRIBUTION:")
    print(f"{'─'*60}")
    
    if 'city' in df.columns:
        city_counts = df['city'].value_counts().head(10)
        for city, count in city_counts.items():
            pct = (count / len(df)) * 100
            print(f"   {city:.<35} {count:>3} ({pct:>5.1f}%)")
    elif 'location' in df.columns:
        loc_counts = df['location'].value_counts().head(10)
        for loc, count in loc_counts.items():
            pct = (count / len(df)) * 100
            print(f"   {loc:.<35} {count:>3} ({pct:>5.1f}%)")
    
    # ============================================================
    # TOP COMPANIES
    # ============================================================
    print(f"\n🏢 TOP COMPANIES (Hiring Most):")
    print(f"{'─'*60}")
    
    if 'company' in df.columns:
        company_counts = df['company'].value_counts().head(10)
        for company, count in company_counts.items():
            if pd.notna(company):
                print(f"   {str(company)[:40]:.<42} {count:>3}")
    
    # ============================================================
    # TOP JOB TITLES
    # ============================================================
    print(f"\n💼 TOP JOB TITLES:")
    print(f"{'─'*60}")
    
    if 'title' in df.columns:
        title_counts = df['title'].value_counts().head(10)
        for title, count in title_counts.items():
            if pd.notna(title):
                print(f"   {str(title)[:50]:.<52} {count:>3}")
    
    # ============================================================
    # SAMPLE RECORDS
    # ============================================================
    print(f"\n📋 SAMPLE RECORDS (First 3):")
    print(f"{'─'*60}")
    
    for idx, row in df.head(3).iterrows():
        print(f"\n   Job {idx + 1}:")
        print(f"   Title: {row.get('title', 'N/A')}")
        print(f"   Company: {row.get('company', 'N/A')}")
        print(f"   Location: {row.get('location', 'N/A') or row.get('city', 'N/A')}")
        if 'responsibilities' in row and pd.notna(row['responsibilities']):
            resp_preview = str(row['responsibilities'])[:100]
            print(f"   Responsibilities: {resp_preview}...")
    
    # ============================================================
    # DATA QUALITY SCORE
    # ============================================================
    print(f"\n⭐ DATA QUALITY ASSESSMENT:")
    print(f"{'─'*60}")
    
    # Calculate quality score
    key_fields = ['title', 'company', 'location']
    key_fields_present = [f for f in key_fields if f in df.columns]
    
    if key_fields_present:
        key_completeness = df[key_fields_present].notna().all(axis=1).sum()
        key_completeness_pct = (key_completeness / len(df)) * 100
    else:
        key_completeness_pct = 0
    
    quality_score = (completeness * 0.5) + (key_completeness_pct * 0.5)
    
    print(f"   Overall Quality Score: {quality_score:.1f}/100")
    print(f"   Data Completeness: {completeness:.1f}%")
    print(f"   Key Fields Complete: {key_completeness_pct:.1f}%")
    
    if quality_score >= 80:
        print(f"\n   ✅ EXCELLENT - Data quality is very good!")
    elif quality_score >= 60:
        print(f"\n   ⚠️ GOOD - Data quality is acceptable but can be improved")
    else:
        print(f"\n   ❌ POOR - Data quality needs improvement")
    
    # ============================================================
    # RECOMMENDATIONS
    # ============================================================
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"{'─'*60}")
    
    recommendations = []
    
    for col in ['title', 'company', 'location']:
        if col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 10:
                recommendations.append(f"   • Improve {col} extraction (currently {missing_pct:.1f}% missing)")
    
    if len(df) < 100:
        recommendations.append(f"   • Collect more data (currently only {len(df)} jobs)")
    
    if 'responsibilities' in df.columns:
        resp_missing = (df['responsibilities'].isnull().sum() / len(df)) * 100
        if resp_missing > 50:
            recommendations.append(f"   • Improve responsibilities extraction ({resp_missing:.1f}% missing)")
    
    if recommendations:
        for rec in recommendations:
            print(rec)
    else:
        print("   ✅ No major issues found!")
    
    print("\n" + "="*60 + "\n")
    
    return df


def generate_summary_stats(df):
    """
    Generate additional summary statistics
    """
    stats = {
        'total_jobs': len(df),
        'unique_companies': df['company'].nunique() if 'company' in df.columns else 0,
        'unique_titles': df['title'].nunique() if 'title' in df.columns else 0,
        'data_completeness': ((len(df) * len(df.columns) - df.isnull().sum().sum()) / (len(df) * len(df.columns))) * 100,
        'cities_covered': df['city'].nunique() if 'city' in df.columns else 0
    }
    return stats


if __name__ == "__main__":
    # Run validation
    df = validate_job_data('data/raw/jobs_data.csv')
    
    if df is not None:
        # Generate summary
        stats = generate_summary_stats(df)
        
        print("📊 Quick Stats:")
        print(f"   Total Jobs: {stats['total_jobs']}")
        print(f"   Unique Companies: {stats['unique_companies']}")
        print(f"   Data Quality: {stats['data_completeness']:.1f}%")
        print()