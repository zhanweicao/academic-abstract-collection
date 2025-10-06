#!/usr/bin/env python3
"""
Incremental Mode Runner - Fill missing authors without redoing successful ones
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from cs_abstract_collector import AbstractCollector

def main():
    print("🔄 INCREMENTAL MODE - Fill Missing Authors")
    print("=" * 50)
    print("This will find additional authors to reach your target count")
    print("Existing successful authors will be preserved")
    print("=" * 50)
    
    # Configuration
    api_key = "ba46hmA8hP1k1MzFVloTC2S2VbTAFwPD11wD6Mr7"
    field = "CS"
    target_authors = 20  # Adjust as needed
    
    # Create collector
    collector = AbstractCollector(field=field, output_dir=f"output_{field}", api_key=api_key)
    
    # Run in incremental mode
    print(f"🎯 Target: {target_authors} authors")
    print(f"📁 Output directory: output_{field}/")
    print()
    
    collector.run(target_authors=target_authors, fill_missing=True)
    
    print("\n✅ INCREMENTAL RUN COMPLETED!")
    print(f"📊 Check output_{field}/collection_report.txt for details")

if __name__ == "__main__":
    main()
