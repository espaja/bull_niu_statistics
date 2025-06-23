# Tests Directory

This directory contains unit tests for the project core modules.

## Test Structure

```
tests/
├── test_dice_parser.py     # Dice parser unit tests
├── test_niu_niu_engine.py  # Niu Niu game engine unit tests  
└── README.md               # This documentation
```

## Running Tests

```bash
# Run all tests
python run_tests.py --all

# Run unit tests only
python run_tests.py --unit

# Run individual tests
python tests/test_dice_parser.py
python tests/test_niu_niu_engine.py
```

## Test Coverage

### test_dice_parser.py
- WeChat XML gameext format parsing
- Content value to dice value mapping (4→1, 5→2, 6→3, 7→4, 8→5, 9→6)
- Invalid input handling
- Dice sequence validation

### test_niu_niu_engine.py  
- Baozi (triple) detection
- Niu Niu detection
- Various Niu value calculations
- Game result comparison logic

## Dependencies

```bash
pip install -r requirements.txt
```