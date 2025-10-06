"""
Universal Field Continuous Author Paper Abstract Collector
Goal: Find researchers who continuously published papers as any author in top conferences from 2020-2024
Output: Abstract files saved as Academic_Field_Year_Index.txt
Supports different fields through scholar list files
"""

import requests
import time
import os
import re
from typing import List, Dict, Optional
from tqdm import tqdm
import json


class AbstractCollector:
    def __init__(self, field: str = "CS", output_dir: str = "output", api_key: str = None):
        """
        Initialize the collector
        
        Args:
            field: Research field (CS, Chemistry, Biology, Physics, Medicine, etc.)
            output_dir: Output directory path
            api_key: Semantic Scholar API key
        """
        self.field = field.upper()
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.session = requests.Session()
        self.output_dir = output_dir
        self.api_key = api_key
        
        # Add API key to request headers if provided
        if self.api_key:
            self.session.headers.update({"x-api-key": self.api_key})
            print("Using API key for enhanced request quota")
            
        # Set keywords based on field
        self.field_keywords = self._get_field_keywords()
        
        # Set top conferences based on field
        self.top_conferences = self._get_top_conferences()
        
        # Create output directory (ensure absolute path)
        if not os.path.isabs(output_dir):
            # If relative path, base on project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            output_dir = os.path.join(project_root, output_dir)
        
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir  # Update to absolute path
        
        # Initialize cache
        self.cache_dir = os.path.join(self.output_dir, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.author_cache = {}  # In-memory cache for author data
        self.paper_cache = {}   # In-memory cache for paper data
        
    def _get_field_keywords(self) -> List[str]:
        """Return relevant keywords based on field"""
        keywords_map = {
            'CS': [
                'computer science', 'machine learning', 'artificial intelligence',
                'deep learning', 'neural network', 'algorithm', 'software engineering',
                'data structure', 'computational', 'programming', 'system',
                'ai', 'ml', 'nlp', 'computer', 'software', 'computing', 'data',
                'information', 'technology', 'digital', 'electronic', 'cyber',
                'network', 'database', 'model', 'learning', 'intelligence'
            ],
            'CHEMISTRY': [
                'chemistry', 'chemical', 'molecule', 'compound', 'synthesis',
                'reaction', 'catalyst', 'organic', 'inorganic', 'analytical',
                'physical chemistry', 'biochemistry', 'materials science'
            ],
            'BIOLOGY': [
                'biology', 'biological', 'cell', 'gene', 'protein', 'dna',
                'genetics', 'molecular biology', 'cell biology', 'evolution',
                'ecology', 'biochemistry', 'microbiology'
            ],
            'PHYSICS': [
                'physics', 'physical', 'quantum', 'mechanics', 'thermodynamics',
                'electromagnetism', 'optics', 'particle', 'nuclear', 'atomic',
                'solid state', 'condensed matter'
            ],
            'MEDICINE': [
                'medicine', 'medical', 'clinical', 'health', 'disease',
                'treatment', 'therapy', 'diagnosis', 'patient', 'drug',
                'pharmaceutical', 'healthcare'
            ]
        }
        return keywords_map.get(self.field, keywords_map['CS'])
        
    def _get_top_conferences(self) -> List[str]:
        """Return top conference/journal names based on field"""
        conferences_map = {
            'CS': [
                # AI/ML
                'NeurIPS', 'ICML', 'ICLR', 'AAAI', 'IJCAI',
                # Computer Vision
                'CVPR', 'ICCV', 'ECCV',
                # NLP
                'ACL', 'EMNLP', 'NAACL',
                # Database
                'SIGMOD', 'VLDB', 'ICDE',
                # Networks
                'SIGCOMM', 'INFOCOM', 'NSDI',
                # Software Engineering
                'ICSE', 'FSE', 'ASE',
                # Security
                'IEEE S&P', 'USENIX Security', 'CCS',
                # HCI
                'CHI', 'UIST', 'CSCW',
                # Theory
                'STOC', 'FOCS', 'SODA',
                # Systems
                'OSDI', 'SOSP', 'ASPLOS',
                # Web
                'WWW', 'KDD', 'WSDM'
            ],
            'CHEMISTRY': [
                # Top Journals
                'Nature', 'Science', 'JACS', 'Angewandte Chemie',
                'Chemical Reviews', 'Chemical Society Reviews',
                'Nature Chemistry', 'Nature Materials',
                'Advanced Materials', 'Chemistry of Materials',
                'Inorganic Chemistry', 'Organic Letters',
                'Journal of Organic Chemistry', 'Analytical Chemistry',
                'Journal of Physical Chemistry', 'Physical Chemistry Chemical Physics',
                # Top Conferences
                'ACS National Meeting', 'Gordon Research Conferences',
                'International Symposium on Organometallic Chemistry'
            ],
            'BIOLOGY': [
                # Top Journals
                'Nature', 'Science', 'Cell', 'Nature Methods',
                'Nature Biotechnology', 'Nature Genetics',
                'Nature Medicine', 'Nature Immunology',
                'PLOS Biology', 'Current Biology',
                'Genome Research', 'Molecular Cell',
                'Developmental Cell', 'Cell Stem Cell',
                'Immunity', 'Nature Reviews Immunology',
                # Top Conferences
                'Keystone Symposia', 'Cold Spring Harbor',
                'Gordon Research Conferences', 'FASEB'
            ],
            'PHYSICS': [
                # Top Journals
                'Nature', 'Science', 'Physical Review Letters',
                'Physical Review', 'Nature Physics',
                'Physical Review X', 'Reviews of Modern Physics',
                'Nature Materials', 'Advanced Materials',
                'Applied Physics Letters', 'Journal of Applied Physics',
                # Top Conferences
                'American Physical Society', 'March Meeting',
                'Gordon Research Conferences'
            ],
            'MEDICINE': [
                # Top Journals
                'Nature', 'Science', 'NEJM', 'The Lancet',
                'JAMA', 'Nature Medicine', 'Cell',
                'Nature Reviews', 'BMJ', 'Annals of Internal Medicine',
                'PLOS Medicine', 'Nature Genetics',
                'Nature Immunology', 'Nature Cancer',
                # Top Conferences
                'American Medical Association', 'World Health Organization',
                'American College of Physicians'
            ]
        }
        return conferences_map.get(self.field, conferences_map['CS'])
        
    def _get_search_queries(self) -> List[str]:
        """Return search query keywords based on field"""
        queries_map = {
            'CS': [
                'machine learning', 'deep learning', 'neural network', 'computer vision',
                'natural language processing', 'artificial intelligence', 'algorithm',
                'data science', 'robotics', 'computer graphics'
            ],
            'CHEMISTRY': [
                'organic chemistry', 'inorganic chemistry', 'analytical chemistry',
                'physical chemistry', 'biochemistry', 'materials chemistry',
                'catalysis', 'synthesis', 'molecular chemistry'
            ],
            'BIOLOGY': [
                'molecular biology', 'cell biology', 'genetics', 'evolution',
                'ecology', 'microbiology', 'biochemistry', 'genomics',
                'proteomics', 'systems biology'
            ],
            'PHYSICS': [
                'quantum mechanics', 'thermodynamics', 'electromagnetism',
                'optics', 'particle physics', 'nuclear physics', 'atomic physics',
                'condensed matter', 'solid state physics'
            ],
            'MEDICINE': [
                'clinical medicine', 'pharmacology', 'pathology', 'immunology',
                'oncology', 'cardiology', 'neurology', 'pediatrics',
                'surgery', 'public health'
            ]
        }
        return queries_map.get(self.field, queries_map['CS'])
        
    def rate_limit_delay(self):
        """Control request frequency to avoid rate limiting"""
        time.sleep(1.2)  # Slightly over 1 second to ensure we don't exceed limits
    
    def _get_cache_file(self, cache_type: str, identifier: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_type}_{identifier}.json")
    
    def _load_from_cache(self, cache_type: str, identifier: str):
        """Load data from cache file"""
        cache_file = self._get_cache_file(cache_type, identifier)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def _save_to_cache(self, cache_type: str, identifier: str, data):
        """Save data to cache file"""
        cache_file = self._get_cache_file(cache_type, identifier)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")
    
    def _get_author_cache_key(self, author_name: str) -> str:
        """Generate cache key for author"""
        return author_name.replace(' ', '_').replace('.', '').lower()
    
    def _get_paper_cache_key(self, author_id: str, years: List[int]) -> str:
        """Generate cache key for author papers"""
        years_str = '_'.join(map(str, sorted(years)))
        return f"{author_id}_{years_str}"
        
    def load_scholars_from_file(self, scholars_file: str = None) -> List[str]:
        """
        Load scholar list from file
        
        Args:
            scholars_file: Scholar list file path, defaults to scholars/{field}_scholars.txt
            
        Returns:
            List of scholar names
        """
        if scholars_file is None:
            # Get project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            scholars_file = os.path.join(project_root, "scholars", f"{self.field}_scholars.txt")
            
        if not os.path.exists(scholars_file):
            print(f"Scholar list file not found: {scholars_file}")
            return []
            
        scholars = []
        try:
            with open(scholars_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comment lines
                    if line and not line.startswith('#'):
                        scholars.append(line)
                        
            print(f"Loaded {len(scholars)} scholars from {scholars_file}")
            return scholars
            
        except Exception as e:
            print(f"Failed to read scholar list file: {e}")
            return []
        
    def search_field_authors(self, limit: int = 100, scholars_file: str = None) -> List[Dict]:
        """
        Search authors in specified field
        
        Args:
            limit: Search limit
            scholars_file: Scholar list file path
            
        Returns:
            List of author information
        """
        print(f"Searching {self.field} field authors...")
        
        # Use multiple strategies to search scholars
        authors = []
        
        # Strategy 1: Load known scholars from file
        known_scholars = self.load_scholars_from_file(scholars_file)
        
        if not known_scholars:
            print("Unable to load scholar list, using default strategy")
            known_scholars = [
                'Yoshua Bengio', 'Geoffrey Hinton', 'Yann LeCun', 'Andrew Ng',
                'Fei-Fei Li', 'Jürgen Schmidhuber', 'Ian Goodfellow',
                'Jeffrey Dean', 'Peter Norvig', 'Stuart Russell', 'Michael Jordan'
            ]
        
        # Strategy 1: Search known scholars with caching
        print(f"   Searching {len(known_scholars)} known scholars...")
        for i, author_name in enumerate(known_scholars):
            if i % 10 == 0:  # Show progress every 10 scholars
                print(f"   Progress: {i+1}/{len(known_scholars)} - Current: {author_name}")
            
            # Check cache first
            cache_key = self._get_author_cache_key(author_name)
            cached_result = self._load_from_cache("author_search", cache_key)
            
            if cached_result:
                print(f"     Using cached result for {author_name}")
                for author in cached_result:
                    if not any(a.get('authorId') == author.get('authorId') for a in authors):
                        authors.append(author)
                continue
            
            # API call if not cached
            url = f"{self.base_url}/author/search"
            params = {
                'query': author_name,
                'fields': 'authorId,name,papers',
                'limit': 3  # Reduce to 3 results for efficiency
            }
            
            try:
                self.rate_limit_delay()
                response = self.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    author_results = data.get('data', [])
                    
                    # Filter out entries that look like real authors
                    valid_authors = []
                    found_author = False
                    for author in author_results:
                        name = author.get('name', '').strip()
                        # Check if it's a real author name (not institution name)
                        if self.is_real_author(name):
                            # Check if already exists
                            author_id = author.get('authorId')
                            if author_id and not any(a.get('authorId') == author_id for a in authors):
                                authors.append(author)
                                valid_authors.append(author)
                                found_author = True
                                if i % 10 == 0:  # Only print details when showing progress
                                    print(f"     Found real author: {name}")
                    
                    # Cache the valid results
                    if valid_authors:
                        self._save_to_cache("author_search", cache_key, valid_authors)
                            
                elif response.status_code == 429:
                    print("   Rate limited, waiting longer...")
                    time.sleep(5)
                    continue
                else:
                    if i % 10 == 0:
                        print(f"   Request failed: {response.status_code}")
                    
            except Exception as e:
                if i % 10 == 0:
                    print(f"   Request exception: {e}")
        
        # Strategy 2: Find active authors through paper search
        print(f"\nSearching active {self.field} field authors through papers...")
        paper_search_queries = self._get_search_queries()
        
        print(f"   Will search {len(paper_search_queries)} keywords...")
        for i, query in enumerate(paper_search_queries):
            if i % 3 == 0:  # Show progress every 3 queries
                print(f"   Progress: {i+1}/{len(paper_search_queries)} - Search keyword: {query}")
            
            url = f"{self.base_url}/paper/search"
            params = {
                'query': query,
                'year': '2020-2024',
                'fields': 'paperId,title,authors,year',
                'limit': 15  # Reduce to 15 papers for efficiency
            }
            
            try:
                self.rate_limit_delay()
                response = self.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    papers = data.get('data', [])
                    
                    # Extract first and second authors from papers
                    new_authors_found = 0
                    for paper in papers:
                        authors_list = paper.get('authors', [])
                        if authors_list:
                            # Check first two authors
                            for author in authors_list[:2]:
                                author_id = author.get('authorId')
                                author_name = author.get('name', '').strip()
                                
                                if author_id and self.is_real_author(author_name):
                                    # Check if already exists
                                    if not any(a.get('authorId') == author_id for a in authors):
                                        authors.append({
                                            'authorId': author_id,
                                            'name': author_name
                                        })
                                        new_authors_found += 1
                                        
                    if new_authors_found > 0 and i % 3 == 0:
                        print(f"     Found {new_authors_found} new authors from papers")
                                    
                elif response.status_code == 429:
                    print("   Rate limited, waiting...")
                    time.sleep(5)
                    continue
                    
            except Exception as e:
                if i % 3 == 0:
                    print(f"   Request exception: {e}")
                
        # Strategy 3: Search authors from highly cited papers (additional strategy)
        if len(authors) < limit:  # If first two strategies didn't find enough authors
            print(f"\nSearching more {self.field} field authors through highly cited papers...")
            
            for year in [2020, 2021, 2022, 2023, 2024]:
                print(f"   Searching highly cited papers from {year}...")
                
                url = f"{self.base_url}/paper/search"
                params = {
                    'query': f'"{self.field}" OR "computer science"',  # General query
                    'year': str(year),
                    'fields': 'paperId,title,authors,year,citationCount',
                    'limit': 20,
                    'sort': 'citationCount:desc'  # Sort by citation count
                }
                
                try:
                    self.rate_limit_delay()
                    response = self.session.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        papers = data.get('data', [])
                        
                        # Extract authors from highly cited papers
                        new_authors_found = 0
                        for paper in papers:
                            authors_list = paper.get('authors', [])
                            if authors_list:
                                # Check first author
                                first_author = authors_list[0]
                                author_id = first_author.get('authorId')
                                author_name = first_author.get('name', '').strip()
                                
                                if author_id and self.is_real_author(author_name):
                                    # Check if already exists
                                    if not any(a.get('authorId') == author_id for a in authors):
                                        authors.append({
                                            'authorId': author_id,
                                            'name': author_name
                                        })
                                        new_authors_found += 1
                                        
                        if new_authors_found > 0:
                            print(f"     Found {new_authors_found} new authors from {year} highly cited papers")
                            
                    elif response.status_code == 429:
                        print("   Rate limited, waiting...")
                        time.sleep(5)
                        continue
                        
                except Exception as e:
                    print(f"   Request exception: {e}")
        
        # Remove duplicates
        unique_authors = {}
        for author in authors:
            author_id = author.get('authorId')
            if author_id and author_id not in unique_authors:
                unique_authors[author_id] = author
                
        print(f"\nTotal found {len(unique_authors)} real authors")
        return list(unique_authors.values())
    
    def is_real_author(self, name: str) -> bool:
        """
        Determine if it's a real author name (not institution name)
        
        Args:
            name: Author name
            
        Returns:
            Whether it's a real author
        """
        if not name:
            return False
            
        # Convert to lowercase for checking
        name_lower = name.lower()
        
        # Exclude obvious institution/project name keywords
        institution_keywords = [
            'department', 'institute', 'university', 'college', 'school',
            'center', 'centre', 'laboratory', 'lab', 'faculty', 'dept',
            'machine learning', 'artificial intelligence', 'computer science',
            'b.s.c', 'm.s.c', 'm.e', 'm.tech', 'ph.d', 'student', 'professor',
            'assistant', 'associate', 'full', 'board', 'corporate', 'technology'
        ]
        
        # If contains institution keywords, likely institution name
        for keyword in institution_keywords:
            if keyword in name_lower:
                return False
        
        # Check name format (should contain space-separated names)
        name_parts = name.strip().split()
        if len(name_parts) < 2:
            return False
            
        # Check if contains common name patterns
        # Real author names usually don't contain too many uppercase letters or special characters
        if len(name) > 50:  # Institution names are usually long
            return False
            
        return True
    
    def get_author_papers(self, author_id: str, years: List[int] = None) -> List[Dict]:
        """
        Get author papers from specified years with caching
        
        Args:
            author_id: Author ID
            years: Year list, defaults to 2020-2024
            
        Returns:
            List of papers
        """
        if years is None:
            years = list(range(2020, 2025))
        
        # Check cache first
        cache_key = self._get_paper_cache_key(author_id, years)
        cached_result = self._load_from_cache("author_papers", cache_key)
        
        if cached_result:
            print(f"     Using cached papers for author {author_id}")
            return cached_result
            
        url = f"{self.base_url}/author/{author_id}/papers"
        params = {
            'fields': 'paperId,title,abstract,authors,year,venue,citationCount',
            'limit': 1000
        }
        
        try:
            self.rate_limit_delay()
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                papers = data.get('data', [])
                print(f"     Original papers: {len(papers)}")
                
                # First filter by year (handle both int and string types)
                year_filtered = []
                for paper in papers:
                    paper_year = paper.get('year')
                    if paper_year is not None:
                        try:
                            # Convert to int if it's a string
                            year_int = int(paper_year) if isinstance(paper_year, str) else paper_year
                            if year_int in years:
                                year_filtered.append(paper)
                        except (ValueError, TypeError):
                            # Skip papers with invalid year data
                            continue
                print(f"     After year filter: {len(year_filtered)}")
                
                # Then filter by field
                field_filtered = [paper for paper in year_filtered if self.is_field_paper(paper)]
                print(f"     After {self.field} field filter: {len(field_filtered)}")
                
                # Then filter by top conferences
                top_conf_filtered = [paper for paper in field_filtered if self.is_top_conference_paper(paper)]
                print(f"     After top conference filter: {len(top_conf_filtered)}")
                
                # Finally filter by author presence (any position)
                author_papers = [paper for paper in top_conf_filtered if self.is_author_in_paper(paper, author_id)]
                print(f"     After author filter: {len(author_papers)}")
                
                # Cache the filtered results
                self._save_to_cache("author_papers", cache_key, author_papers)
                
                return author_papers
                
            elif response.status_code == 429:
                print("   Rate limited, waiting...")
                time.sleep(5)
                return []
            else:
                print(f"   Failed to get papers: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   Request exception: {e}")
            return []
    
    def is_field_paper(self, paper: Dict) -> bool:
        """
        Determine if paper belongs to specified field
        
        Args:
            paper: Paper information
            
        Returns:
            Whether it's a paper in this field
        """
        title = paper.get('title', '') or ''
        abstract = paper.get('abstract', '') or ''
        venue = paper.get('venue', '') or ''
        
        text_to_check = f"{title} {abstract} {venue}".lower()
        
        # Check if contains field keywords
        for keyword in self.field_keywords:
            if keyword in text_to_check:
                return True
                
        return False
    
    def is_top_conference_paper(self, paper: Dict) -> bool:
        """
        Check if paper is from a top conference/journal
        
        Args:
            paper: Paper information
            
        Returns:
            Whether paper is from top conference/journal
        """
        venue = paper.get('venue', '') or ''
        venue_lower = venue.lower()
        
        # Check if venue contains any of the top conference names
        for top_conf in self.top_conferences:
            if top_conf.lower() in venue_lower:
                return True
                
        return False
    
    def is_author_in_paper(self, paper: Dict, author_id: str) -> bool:
        """
        Determine if specified author is any author of the paper (any position)
        
        Args:
            paper: Paper information
            author_id: Author ID
            
        Returns:
            Whether the author is in the paper
        """
        authors = paper.get('authors', [])
        if not authors or len(authors) < 1:
            return False
            
        # Check if there's a match in any author position
        for author in authors:
            if author.get('authorId') == author_id:
                return True
                
        return False
    
    def check_author_continuity(self, author: Dict, required_years: List[int] = None) -> bool:
        """
        Check if author has published first/second author papers continuously for 4 years
        
        Args:
            author: Author information
            required_years: Required year list
            
        Returns:
            Whether requirements are met
        """
        if required_years is None:
            required_years = list(range(2020, 2025))
            
        author_id = author.get('authorId')
        if not author_id:
            return False
            
        print(f"   Checking author: {author.get('name', 'Unknown')} (ID: {author_id})")
        
        papers = self.get_author_papers(author_id, years=required_years)
        print(f"     Retrieved {len(papers)} papers")
        
        # Group by year
        papers_by_year = {}
        for paper in papers:
            year = paper.get('year')
            if year not in papers_by_year:
                papers_by_year[year] = []
            papers_by_year[year].append(paper)
        
        print(f"     Year distribution: {list(papers_by_year.keys())}")
        
        # Statistics
        years_with_papers = len(papers_by_year)
        total_papers = len(papers)
        
        print(f"     Stats: {years_with_papers} years with papers, total {total_papers} papers")
        
        # Strict condition: Must have CS field papers in all 5 consecutive years (2020-2024)
        missing_years = []
        for year in required_years:
            year_found = False
            for paper_year in papers_by_year.keys():
                try:
                    # Handle both int and string year types
                    paper_year_int = int(paper_year) if isinstance(paper_year, str) else paper_year
                    if paper_year_int == year:
                        year_found = True
                        break
                except (ValueError, TypeError):
                    continue
            # Check if year_found is True and has papers
            if not year_found:
                missing_years.append(year)
            else:
                # Find the actual papers for this year
                year_papers = []
                for paper_year, papers in papers_by_year.items():
                    try:
                        paper_year_int = int(paper_year) if isinstance(paper_year, str) else paper_year
                        if paper_year_int == year:
                            year_papers.extend(papers)
                            break
                    except (ValueError, TypeError):
                        continue
                if len(year_papers) == 0:
                    missing_years.append(year)
        
        if len(missing_years) == 0:
            print(f"     Meets criteria: 4 consecutive years with first/second author papers")
            # Store the papers in the author dict for later use
            author['_validated_papers'] = papers
            return True
        else:
            print(f"     Does not meet criteria: missing years {missing_years}")
            return False
    
    def check_author_continuity_with_abstracts(self, author: Dict, required_years: List[int] = None) -> bool:
        """
        Check if author has published papers continuously for 5 years
        AND all selected papers have complete abstracts
        
        Args:
            author: Author information
            required_years: Required year list
            
        Returns:
            Whether requirements are met (4 years + all abstracts)
        """
        if required_years is None:
            required_years = list(range(2020, 2025))
            
        author_id = author.get('authorId')
        if not author_id:
            return False
            
        print(f"   Checking author: {author.get('name', 'Unknown')} (ID: {author_id})")
        
        papers = self.get_author_papers(author_id, years=required_years)
        print(f"     Retrieved {len(papers)} papers")
        
        # Group by year
        papers_by_year = {}
        for paper in papers:
            year = paper.get('year')
            if year not in papers_by_year:
                papers_by_year[year] = []
            papers_by_year[year].append(paper)
        
        # Check continuity AND abstract completeness
        selected_papers = []
        missing_years = []
        
        for year in required_years:
            year_papers = []
            # Find papers for this year (handle both int and string year types)
            for paper_year, papers in papers_by_year.items():
                try:
                    paper_year_int = int(paper_year) if isinstance(paper_year, str) else paper_year
                    if paper_year_int == year:
                        year_papers.extend(papers)
                        break
                except (ValueError, TypeError):
                    continue
            
            if year_papers:
                # Sort by citation count, select highest
                year_papers = sorted(year_papers, 
                                   key=lambda x: x.get('citationCount', 0), 
                                   reverse=True)
                selected_paper = year_papers[0]  # Select highest citation count
                
                # Check if paper has abstract
                if not selected_paper.get('abstract'):
                    print(f"     ❌ {year}: Selected paper lacks abstract")
                    missing_years.append(f"{year}(no_abstract)")
                    break
                
                selected_paper['author_name'] = author.get('name', 'Unknown')
                selected_papers.append(selected_paper)
                print(f"     ✅ {year}: Selected paper with abstract")
            else:
                print(f"     ❌ {year}: No eligible papers found")
                missing_years.append(f"{year}(no_papers)")
                break
        
        # Only return True if we have all 5 years with abstracts
        if len(selected_papers) == 5:
            print(f"     ✅ Author qualifies: 5 consecutive years with complete abstracts")
            # Store the validated papers for later use
            author['_validated_papers'] = selected_papers
            return True
        else:
            print(f"     ❌ Author disqualified: missing {missing_years}")
            return False
    
    def find_continuous_authors(self, target_count: int = 20, debug_mode: bool = False) -> List[Dict]:
        """
        Find specified number of continuous 5-year authors (2020-2024)
        Only return authors that have complete abstracts for all 5 years
        
        Args:
            target_count: Target number of authors
            debug_mode: Use debug data instead of API calls
            
        Returns:
            List of continuous authors with complete abstracts
        """
        if debug_mode:
            return self._load_debug_authors(target_count)
        
        print(f"Starting to find {target_count} continuous 5-year authors with complete abstracts...")
        
        # Search field authors
        field_authors = self.search_field_authors(limit=200)  # Search more to ensure enough continuous authors
        print(f"Total found {len(field_authors)} {self.field} authors")
        
        continuous_authors = []
        
        for i, author in enumerate(tqdm(field_authors, desc="Checking author continuity")):
            if len(continuous_authors) >= target_count:
                break
                
            print(f"\n[{i+1}/{len(field_authors)}] Checking author...")
            
            # Check continuity AND abstract completeness in one go
            if self.check_author_continuity_with_abstracts(author):
                continuous_authors.append(author)
                print(f"   ✅ Found {len(continuous_authors)}th qualified author with complete abstracts!")
                
                # Save progress
                self.save_progress(continuous_authors)
            else:
                print(f"   ❌ Author skipped: missing years or abstracts")
        
        print(f"\nCompleted! Found {len(continuous_authors)} qualified authors with complete 5-year abstracts")
        return continuous_authors
    
    def _load_debug_authors(self, target_count: int) -> List[Dict]:
        """Load debug authors from file"""
        debug_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "debug_data", "debug_authors.json")
        
        if not os.path.exists(debug_file):
            print(f"❌ Debug file not found: {debug_file}")
            print("Please run: python3 debug_mode.py")
            return []
        
        try:
            with open(debug_file, 'r', encoding='utf-8') as f:
                debug_authors = json.load(f)
            
            print(f"🐛 DEBUG MODE: Loaded {len(debug_authors)} debug authors")
            print("🚀 No API calls needed - using pre-generated test data")
            
            # Return up to target_count authors
            return debug_authors[:target_count]
            
        except Exception as e:
            print(f"❌ Failed to load debug data: {e}")
            return []
    
    def collect_abstracts(self, authors: List[Dict]) -> List[Dict]:
        """
        Collect abstracts from pre-validated authors
        Authors have already been validated to have complete 5-year abstracts
        
        Args:
            authors: List of pre-validated authors with _validated_papers
            
        Returns:
            List of paper abstracts
        """
        print(f"Collecting abstracts from {len(authors)} pre-validated authors...")
        print("All authors have been verified to have complete 5-year abstracts")
        
        all_papers = []
        
        # Get the starting author index (for incremental mode)
        existing_authors = self._count_existing_successful_authors()
        next_author_index = existing_authors + 1
        
        for i, author in enumerate(tqdm(authors, desc="Collecting papers")):
            author_name = author.get('name', f'Author_{i+1:02d}')
            
            print(f"\n[{i+1}/{len(authors)}] Processing author {author_name}...")
            
            # Get pre-validated papers (guaranteed to have complete abstracts)
            if '_validated_papers' in author:
                selected_papers = author['_validated_papers']
                print(f"     Using {len(selected_papers)} pre-validated papers with complete abstracts")
                
                # Assign author index to each paper
                for paper in selected_papers:
                    paper['author_index'] = next_author_index
                
                all_papers.extend(selected_papers)
                print(f"     ✅ Added {len(selected_papers)} papers (index: {next_author_index})")
                next_author_index += 1
                
            else:
                print(f"     ❌ No pre-validated papers found for {author_name}")
        
        successful_author_count = len(all_papers) // 4 if all_papers else 0
        print(f"\nTotal collected {len(all_papers)} papers ({successful_author_count} complete authors)")
        return all_papers
    
    def save_abstracts_to_files(self, papers: List[Dict]):
        """
        Save abstracts to files in specified format
        Each author has only 1 paper per year, so filename format is fixed as Academic_Field_Year_Index.txt
        
        Args:
            papers: List of papers
        """
        print(f"Starting to save {len(papers)} abstracts to files...")
        print("Filename format: Academic_{Field}_{Year}_{Index:02d}.txt")
        
        for paper in tqdm(papers, desc="Saving files"):
            abstract = paper.get('abstract', '')
            year = paper.get('year')
            author_index = paper.get('author_index')
            title = paper.get('title', 'Unknown Title')
            paper_id = paper.get('paperId', '')
            author_name = paper.get('author_name', 'Unknown Author')
            
            if not abstract or not year or not author_index:
                print(f"   Skipping {filename}: missing abstract, year, or author_index")
                continue
                
            # Generate standard filename (each author has only 1 paper per year, no conflicts)
            # Ensure year is converted to string for consistent filename format
            year_str = str(year) if year is not None else "unknown"
            filename = f"Academic_{self.field}_{year_str}_{author_index:02d}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            # Prepare file content (all papers now guaranteed to have abstracts)
            content = f"Author: {author_name}\nTitle: {title}\nPaper ID: {paper_id}\nYear: {year}\nAuthor Index: {author_index}\n\nAbstract:\n{abstract}"
            
            # Save file
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   Saved: {filename}")
            except Exception as e:
                print(f"Failed to save file {filename}: {e}")
        
        print(f"File saving completed! Saved in directory: {self.output_dir}")
    
    def save_progress(self, authors: List[Dict]):
        """Save progress to JSON file"""
        progress_file = os.path.join(self.output_dir, "progress.json")
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(authors, f, ensure_ascii=False, indent=2)
    
    def run(self, target_authors: int = 20, resume: bool = True, debug_mode: bool = False, fill_missing: bool = False):
        """
        Run complete collection process with resume capability and debug mode
        
        Args:
            target_authors: Target number of authors
            resume: Whether to resume from previous progress
            debug_mode: Use debug data instead of API calls (for testing)
            fill_missing: Fill missing authors to reach target count (incremental mode)
        """
        if debug_mode:
            print(f"🐛 DEBUG MODE: {self.field} field continuous 5-year author abstract collection...")
            print(f"🚀 No API calls - using pre-generated test data")
        else:
            print(f"Starting {self.field} field continuous 5-year author abstract collection...")
        
        print(f"Goal: Find up to {target_authors} authors, 5 abstracts per author (1 from each year 2020-2024)")
        print(f"Expected output: Up to {target_authors * 5} abstract files")
        
        if fill_missing:
            return self._run_incremental_mode(target_authors, debug_mode)
        
        # Check for existing progress if resume is enabled and not in debug mode
        progress_file = os.path.join(self.output_dir, "progress.json")
        if resume and not debug_mode and os.path.exists(progress_file):
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    continuous_authors = json.load(f)
                print(f"Found existing progress: {len(continuous_authors)} authors already found")
                
                if len(continuous_authors) >= target_authors:
                    print(f"Target already reached! Using existing {len(continuous_authors)} authors")
                else:
                    print(f"Resuming from {len(continuous_authors)} authors, need {target_authors - len(continuous_authors)} more")
                    # Continue finding more authors
                    additional_authors = self.find_continuous_authors(target_authors - len(continuous_authors))
                    continuous_authors.extend(additional_authors)
            except:
                print("Failed to load progress, starting fresh")
                continuous_authors = self.find_continuous_authors(target_authors)
        else:
            # 1. Find continuous authors
            continuous_authors = self.find_continuous_authors(target_authors, debug_mode=debug_mode)
        
        if not continuous_authors:
            print("No qualifying continuous authors found")
            return
        
        # 2. Collect abstracts
        all_papers = self.collect_abstracts(continuous_authors)
        
        # 3. Save files
        self.save_abstracts_to_files(all_papers)
        
        # 4. Generate statistical report
        self.generate_report(continuous_authors, all_papers)
    
    def _run_incremental_mode(self, target_authors: int, debug_mode: bool = False):
        """Run in incremental mode - only find missing authors to reach target"""
        print(f"🔄 INCREMENTAL MODE: Filling missing authors to reach {target_authors}")
        
        # 1. Count existing successful authors from saved files
        existing_count = self._count_existing_successful_authors()
        print(f"Found {existing_count} existing successful authors")
        
        if existing_count >= target_authors:
            print(f"✅ Target already reached! Have {existing_count} successful authors")
            print("💡 Use 'fill_missing=False' to regenerate all files if needed")
            return
        
        missing_count = target_authors - existing_count
        print(f"🎯 Need to find {missing_count} more authors")
        
        # 2. Find additional authors
        additional_authors = self.find_continuous_authors(missing_count, debug_mode=debug_mode)
        
        if not additional_authors:
            print("❌ No additional qualifying authors found")
            return
        
        # 3. Collect abstracts for new authors only
        all_papers = self.collect_abstracts(additional_authors)
        
        # 4. Save files (will automatically use correct author indices)
        self.save_abstracts_to_files(all_papers)
        
        # 5. Generate updated report
        self._generate_incremental_report()
    
    def _count_existing_successful_authors(self) -> int:
        """Count how many authors already have complete 4-year abstracts saved"""
        if not os.path.exists(self.output_dir):
            return 0
        
        # Count unique author indices from saved files
        author_indices = set()
        for filename in os.listdir(self.output_dir):
            if filename.startswith(f"Academic_{self.field}_") and filename.endswith('.txt'):
                # Extract author index from filename: Academic_CS_2021_01.txt -> 01
                parts = filename.split('_')
                if len(parts) >= 4:
                    try:
                        author_index = int(parts[-1].split('.')[0])
                        author_indices.add(author_index)
                    except:
                        continue
        
        # Check that each author has all 5 years
        complete_authors = 0
        for author_index in author_indices:
            has_all_years = True
            for year in [2020, 2021, 2022, 2023, 2024]:
                expected_filename = f"Academic_{self.field}_{year}_{author_index:02d}.txt"
                if not os.path.exists(os.path.join(self.output_dir, expected_filename)):
                    has_all_years = False
                    break
            
            if has_all_years:
                complete_authors += 1
        
        return complete_authors
    
    def _generate_incremental_report(self):
        """Generate report for incremental run"""
        report_file = os.path.join(self.output_dir, "collection_report.txt")
        
        # Count actual saved files by year
        actual_year_counts = {}
        actual_total_files = 0
        saved_files = []
        
        # Get list of actual saved files
        for filename in os.listdir(self.output_dir):
            if filename.startswith(f"Academic_{self.field}_") and filename.endswith('.txt'):
                saved_files.append(filename)
                # Extract year from filename
                parts = filename.split('_')
                if len(parts) >= 3:
                    year = parts[2]
                    actual_year_counts[year] = actual_year_counts.get(year, 0) + 1
                    actual_total_files += 1
        
        # Count complete authors
        complete_authors = self._count_existing_successful_authors()
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"{self.field} Field Continuous 4-Year First/Second Author Abstract Collection Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Collection Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mode: INCREMENTAL (Fill Missing Authors)\n")
            f.write(f"Number of Complete Authors: {complete_authors}\n")
            f.write(f"Total Files Saved: {actual_total_files}\n")
            f.write(f"All papers include complete abstracts\n\n")
            
            f.write(f"Year Distribution (Based on Actual Saved Files):\n")
            f.write("-" * 30 + "\n")
            for year in sorted(actual_year_counts.keys()):
                f.write(f"{year}: {actual_year_counts[year]} files\n")
            
            f.write(f"\nAuthor Completeness Analysis:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Complete Authors (4 years): {complete_authors}\n")
            f.write(f"Expected files per complete author: 4\n")
            f.write(f"Total expected files: {complete_authors * 4}\n")
            f.write(f"Actual saved files: {actual_total_files}\n")
            
            if actual_total_files == complete_authors * 4:
                f.write("✅ All authors have complete 4-year data\n")
            else:
                f.write("⚠️  Some authors may have incomplete data\n")
        
        print(f"Incremental report saved: {report_file}")
        print(f"Complete authors: {complete_authors}, Total files: {actual_total_files}")
    
    def generate_report(self, authors: List[Dict], papers: List[Dict]):
        """Generate statistical report based on actual saved files"""
        report_file = os.path.join(self.output_dir, "collection_report.txt")
        
        # Count actual saved files by year
        actual_year_counts = {}
        actual_total_files = 0
        saved_files = []
        
        # Get list of actual saved files
        for filename in os.listdir(self.output_dir):
            if filename.startswith(f"Academic_{self.field}_") and filename.endswith('.txt'):
                saved_files.append(filename)
                # Extract year from filename
                parts = filename.split('_')
                if len(parts) >= 3:
                    year = parts[2]
                    actual_year_counts[year] = actual_year_counts.get(year, 0) + 1
                    actual_total_files += 1
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"{self.field} Field Continuous 4-Year First/Second Author Abstract Collection Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Collection Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Number of Continuous Authors: {len(authors)}\n")
            f.write(f"Total Papers Collected: {len(papers)}\n")
            f.write(f"Total Files Saved: {actual_total_files}\n")
            f.write(f"All papers include complete abstracts\n\n")
            
            f.write("Author List:\n")
            f.write("-" * 30 + "\n")
            for i, author in enumerate(authors, 1):
                f.write(f"{i:2d}. {author.get('name', 'Unknown')} (ID: {author.get('authorId', 'Unknown')})\n")
            
            f.write(f"\nYear Distribution (Based on Actual Saved Files):\n")
            f.write("-" * 30 + "\n")
            for year in sorted(actual_year_counts.keys()):
                f.write(f"{year}: {actual_year_counts[year]} files\n")
            
            f.write(f"\nMissing Files Analysis:\n")
            f.write("-" * 30 + "\n")
            expected_per_year = len(authors)
            for year in [2020, 2021, 2022, 2023, 2024]:
                actual_count = actual_year_counts.get(str(year), 0)
                missing_count = expected_per_year - actual_count
                if missing_count > 0:
                    f.write(f"{year}: Missing {missing_count} files (Expected: {expected_per_year}, Actual: {actual_count})\n")
                else:
                    f.write(f"{year}: Complete ({actual_count} files)\n")
        
        print(f"Statistical report saved: {report_file}")
        print(f"Actual files saved: {actual_total_files} (Expected: {len(authors) * 4})")


if __name__ == "__main__":
    # Create collector instance with API key
    api_key = "ba46hmA8hP1k1MzFVloTC2S2VbTAFwPD11wD6Mr7"
    
    # Can easily switch between different fields
    field = "CS"  # Options: CS, Chemistry, Biology, Physics, Medicine
    collector = AbstractCollector(field=field, output_dir=f"output_{field}", api_key=api_key)
    
    # Run collection process - Goal: up to 20 authors, up to 100 abstracts
    collector.run(target_authors=20)
