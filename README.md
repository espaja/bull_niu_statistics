# Bull Niu Statistics

WeChat group chat Niu Niu dice game data analysis tool. Extracts dice data from chat records and generates statistical reports.

## Core Features

- Parse real dice values from WeChat animated expressions
- Detect battle rounds with strict seq ordering
- Generate personal statistics and ranking reports
- Support universal time period analysis (daily/monthly/quarterly/yearly/custom)
- Comprehensive battle analysis with scoring system

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Analyze any time period
python universal_niu_niu_analyzer.py --time 2025-06-23 --group YOUR_GROUP --api-ip YOUR_API_IP
python universal_niu_niu_analyzer.py --time 2025-06 --group YOUR_GROUP --api-ip YOUR_API_IP
python universal_niu_niu_analyzer.py --time 2025-Q2 --group YOUR_GROUP --api-ip YOUR_API_IP

# Run tests
python run_tests.py --all
```

## Project Structure

```
bull_niu_statistics/
├── universal_niu_niu_analyzer.py   # Main universal analyzer
├── src/                            # Core modules
│   ├── niu_niu_engine.py          # Niu Niu game logic
│   ├── optimized_chatlog_importer.py # Data importer
│   └── dice_parser.py             # Dice data parser
├── tests/                          # Unit tests
├── chatlog-0.0.15/                 # Go chatlog tool (gitignored)
├── run_tests.py                    # Test runner
└── CLAUDE.md                       # Development guide
```

## Time Period Support

- **Daily**: `2025-06-23`
- **Monthly**: `2025-06`
- **Quarterly**: `2025-Q2`
- **Half-yearly**: `2025-H1`
- **Yearly**: `2025`
- **Custom range**: `2025-06-01,2025-06-30`

## Output Files

- `dice_data_*.csv` - Raw dice throws
- `games_*.csv` - Valid game records
- `battles_*.csv` - Battle details
- `stats_*.csv` - Player statistics

## Scoring System

- Baozi (Triple): 5 points
- Niu Niu: 3 points
- Niu 7/8/9: 2 points
- No Niu: 0 points
- Others: 1 point

## Technical Details

- WeChat XML gameext parsing: `content` values 4→1, 5→2, 6→3, 7→4, 8→5, 9→6
- Batch API requests: 2000 records per request with offset increment
- Strict seq ordering for temporal consistency
- Battle detection: 10 dice = 1 round (2 players × 5 dice each)