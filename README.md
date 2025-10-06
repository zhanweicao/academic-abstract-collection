# Academic Abstract Collection System

A scalable system to collect academic paper abstracts from Semantic Scholar across multiple research fields, with strict quality and continuity requirements.

## Features

- Multi-field support: CS, Chemistry, Biology, Physics, Medicine (extensible)
- Scholar list driven: load field-specific scholar names from `scholars/{FIELD}_scholars.txt`
- Strict continuity: finds authors with first/second-author papers in each year 2021–2024
- Exactly one paper per year per author (highest citation count); 4 files per qualified author
- Abstract completeness: authors with any missing abstract are skipped entirely
- Caching and resume: avoids repeated API calls and supports interruption recovery
- Incremental fill: preserve existing results and only top-up missing authors
- Reporting: generates a summary report with real saved files

## Repository Layout

```
abstract_collection/
├── src/
│   └── cs_abstract_collector.py     # Main collector (generic, multi-field)
├── scholars/
│   └── cs_scholars.txt              # CS field scholar list (one name per line)
├── run_incremental.py               # Incremental top-up runner
├── requirements.txt
├── README.md
├── DEBUG_GUIDE.md                   # Optional: debug-mode instructions
├── INCREMENTAL_GUIDE.md             # Optional: incremental-mode instructions
├── OPTIMIZED_LOGIC.md               # Optional: logic summary
└── output_CS/                       # Output directory (gitignored)
```

## Requirements

- Python 3.9+
- A Semantic Scholar API key (recommended for stable rate limits)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configure

- Obtain a Semantic Scholar API key: `https://www.semanticscholar.org/product/api/tutorial`
- Ensure your scholar list exists under `scholars/{FIELD}_scholars.txt` (e.g., `scholars/cs_scholars.txt`).

## Usage

### Standard run (first pass)

Find up to 25 qualified authors (each with 4 abstracts, one per year 2021–2024) and save files to `output_{FIELD}`.

```python
# src/cs_abstract_collector.py (main section)
api_key = "YOUR_SEMANTIC_SCHOLAR_API_KEY"
field = "CS"  # Options: "CS", "CHEMISTRY", "BIOLOGY", "PHYSICS", "MEDICINE"

collector = AbstractCollector(field=field, output_dir=f"output_{field}", api_key=api_key)
collector.run(target_authors=25)
```

Run it:

```bash
python src/cs_abstract_collector.py
```

Outputs:
- Files: `Academic_{Field}_{Year}_{Index}.txt` (Index is the author index; same author has the same index across 4 years)
- Report: `output_{FIELD}/collection_report.txt`

Example for one author (index 01):
```
Academic_CS_2021_01.txt
Academic_CS_2022_01.txt
Academic_CS_2023_01.txt
Academic_CS_2024_01.txt
```

### Incremental top-up (only fill missing authors)

If the first run produced fewer than target authors (e.g., 20/25):

```bash
python run_incremental.py
```

What it does:
- Scans existing `output_{FIELD}` and counts complete authors
- Finds only the missing number of authors (e.g., 5 more to reach 25)
- Assigns next continuous indices (e.g., 21–25)
- Saves files and updates the report

## Data Quality Rules (strict)

- Field relevance: paper title/venue/abstract must include field keywords
- Author position: only first or second author papers are eligible
- Year span: must have papers in each of 2021, 2022, 2023, 2024
- Abstract completeness: if any chosen paper lacks an abstract, skip the entire author
- One-per-year: choose one paper per year (highest citation count)

## Scholar List Format

- File: `scholars/{FIELD}_scholars.txt`
- One scholar name per line; lines starting with `#` are comments

Example (`scholars/cs_scholars.txt`):
```
# CS Field Scholars List
# Each line is a scholar's name, comments start with #

# ===== Senior Scholars =====
Yoshua Bengio
Geoffrey Hinton
Yann LeCun
...
```

## Rate Limiting

- With API key: ~1 request/second. The collector applies a small buffer and caching to avoid throttling.

## Output Files

- Naming: `Academic_{Field}_{Year}_{Index}.txt`
- Content template:
```
Author: <Name>
Title: <Title>
Paper ID: <Semantic Scholar Paper ID>
Year: <Year>
Author Index: <Index>

Abstract:
<Full abstract text>
```

## Tips

- If you change logic, rerun incrementally to avoid reprocessing qualified authors
- Ensure `output_{FIELD}/` has enough space (up to 100 text files per field per full run)
- Use the generated report to verify file counts by year and author completeness

## License

MIT License