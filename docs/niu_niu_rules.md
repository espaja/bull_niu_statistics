# Niu Niu Game Rules

## Basic Rules

### Game Setup
- **Dice Count**: Each player throws 5 dice
- **Dice Range**: Each die shows 1-6 points
- **Objective**: Calculate score through specific combination rules

### Scoring Rules

#### Step 1: Find "Niu" (Bull)
Select 3 dice from 5 whose sum is a multiple of 10 (10, 20, 30):
- If found: Has "Niu"
- If not found: "No Niu" (0 points)

#### Step 2: Calculate Points
If "Niu" exists, sum the remaining 2 dice and take the units digit:

**Niu Levels:**
- **Niu Niu**: Remaining sum = 10, 20 → 10 points (highest)
- **Niu 9**: Remaining sum = 9, 19 → 9 points
- **Niu 8**: Remaining sum = 8, 18 → 8 points
- **Niu 7**: Remaining sum = 7, 17 → 7 points
- **Niu 6**: Remaining sum = 6, 16 → 6 points
- **Niu 5**: Remaining sum = 5, 15 → 5 points
- **Niu 4**: Remaining sum = 4, 14 → 4 points
- **Niu 3**: Remaining sum = 3, 13 → 3 points
- **Niu 2**: Remaining sum = 2, 12 → 2 points
- **Niu 1**: Remaining sum = 1, 11 → 1 point
- **No Niu**: Cannot form multiple of 10 → 0 points

## Examples

### Example 1: Niu Niu (10 points)
**Dice**: `[5, 2, 4, 6, 3]`
- **Find Niu**: 5+2+3=10 ✅ (Has Niu)
- **Remaining**: 4+6=10
- **Result**: Niu Niu (10 points)

### Example 2: Niu 9 (9 points)
**Dice**: `[4, 5, 5, 4, 1]`
- **Find Niu**: 5+4+1=10 ✅ (Has Niu)
- **Remaining**: 4+5=9
- **Result**: Niu 9 (9 points)

### Example 3: No Niu (0 points)
**Dice**: `[3, 3, 3, 5, 1]`
- **Try combinations**: All fail to sum to multiple of 10
- **Result**: No Niu (0 points)

## Game Modes

### Battle Mode
1. Multiple players throw 5 dice simultaneously
2. Calculate individual scores
3. **Victory conditions**:
   - Highest score wins
   - Same score = draw
   - Priority: Niu Niu > Niu 9 > ... > Niu 1 > No Niu

## Algorithm Implementation

### Core Logic
1. **Combination Generation**: Choose 3 from 5 dice (C(5,3) = 10 combinations)
2. **Sum Calculation**: Check if 3-dice sum is multiple of 10
3. **Remaining Calculation**: Sum remaining 2 dice
4. **Score Determination**: Take units digit of remaining sum

### Special Cases
- Multiple valid "Niu" combinations: Choose highest remaining sum
- Dice must be in 1-6 range
- Must have exactly 5 dice

## Scoring System (Statistics)

- **Baozi (Triple)**: 5 points
- **Niu Niu**: 3 points  
- **Niu 7/8/9**: 2 points
- **No Niu**: 0 points
- **Others**: 1 point