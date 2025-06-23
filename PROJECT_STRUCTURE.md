# Project Structure

## Directory Overview

```
bull_niu_statistics/
├── universal_niu_niu_analyzer.py      # Main universal analyzer
├── src/                               # Core modules
│   ├── niu_niu_engine.py             # Niu Niu game logic engine
│   ├── optimized_chatlog_importer.py # Data importer with API integration
│   └── dice_parser.py                # Dice data parser
├── tests/                             # Unit tests
│   ├── test_dice_parser.py           # Dice parser tests
│   ├── test_niu_niu_engine.py        # Game engine tests
│   └── README.md                     # Test documentation
├── docs/                              # Documentation
│   └── niu_niu_rules.md              # Game rules reference
├── chatlog-0.0.15/                   # Go chatlog tool (gitignored)
├── output/                            # Analysis output files
├── .gitignore                         # Git ignore patterns
├── requirements.txt                   # Python dependencies
├── run_tests.py                       # Unified test runner
├── CLAUDE.md                          # Development guide
├── PROJECT_STRUCTURE.md               # This file
└── README.md                          # Project overview
```

## Core Components

### Universal Analyzer (`universal_niu_niu_analyzer.py`)
Main entry point supporting any time period:
- Daily: `2025-06-23`
- Monthly: `2025-06`
- Quarterly: `2025-Q2`
- Half-yearly: `2025-H1`
- Yearly: `2025`
- Custom: `2025-06-01,2025-06-30`

### Core Modules (`src/`)

#### `niu_niu_engine.py`
- Game logic implementation
- Result calculation (Baozi, NiuNiu, etc.)
- Scoring system

#### `optimized_chatlog_importer.py`
- Chatlog API integration
- Batch data fetching (2000 records per request)
- Message filtering and preprocessing

#### `dice_parser.py`
- WeChat XML gameext parsing
- Content-to-dice mapping (4→1, 5→2, 6→3, 7→4, 8→5, 9→6)

## Data Flow

1. **Fetch**: API retrieves WeChat messages in batches
2. **Parse**: Extract dice values from XML gameext format
3. **Analyze**: Detect valid games and battles
4. **Report**: Generate CSV files and console output

## Output Files

- `raw_messages_*.json` - Raw API data
- `dice_data_*.csv` - Individual dice throws
- `games_*.csv` - Valid game records
- `battles_*.csv` - Player vs player battles
- `stats_*.csv` - Aggregated statistics

## Scoring System

- **Baozi (Triple)**: 5 points
- **NiuNiu**: 3 points
- **Niu 7/8/9**: 2 points
- **No Niu**: 0 points
- **Others**: 1 point

## Usage Examples

```bash
# Daily analysis
python universal_niu_niu_analyzer.py --time 2025-06-23 --group YOUR_GROUP --api-ip YOUR_API_IP

# Monthly analysis
python universal_niu_niu_analyzer.py --time 2025-06 --group YOUR_GROUP --api-ip YOUR_API_IP

# Custom range
python universal_niu_niu_analyzer.py --time 2025-06-01,2025-06-30 --group YOUR_GROUP --api-ip YOUR_API_IP

# Tests
python run_tests.py --all
```