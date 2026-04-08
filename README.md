# EECS4312_W26_SpecChain

## instructions:
Please update to include: 
- App name: Calm - Sleep, Meditate, Relax
- Data collection method: google_play_scraper
- Original dataset: 1000
- Final cleaned dataset: 828
- Exact commands to run pipeline: from project root

(Optional)
```
python -m venv venv
venv\Scripts\activate 
```

IMPORTANT: I cannot push my groq api key onto the public repo so I have added the command you need to run and my groq api key onto the google doc i submited for the project cover

```
pip install -r requirements.txt #First install the dependencies
python src/run_all.py  
```

# example
Application: [Calm]

Dataset:
- reviews_raw.jsonl contains the collected reviews.
- reviews_clean.jsonl contains the cleaned dataset.
- The cleaned dataset contains 842 reviews.

Repository Structure:
- data/ contains datasets and review groups
- personas/ contains persona files
- spec/ contains specifications
- tests/ contains validation tests
- metrics/ contains all metric files
- src/ contains executable Python scripts
- reflection/ contains the final reflection

How to Run:
1. python src/00_validate_repo.py
2. python src/02_clean.py
3. python src/run_all.py
4. Open metrics/metrics_summary.json for comparison results

