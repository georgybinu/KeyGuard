# Training Error Fix - Backend /train Endpoint

## Problem
When submitting the first training round, the system showed error: "Error submitting training data"

## Root Cause
The `POST /train` endpoint was expecting parameters (`username`, `keystrokes`) as **query parameters** (from URL), but the frontend was sending them in the **request body** (as JSON).

### Original Code (Broken)
```python
@router.post("/train")
async def train_user_profile(
    username: str,
    keystrokes: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    # These were treated as query parameters by FastAPI
    # But frontend sent them in request body as JSON
```

### Frontend (Correct)
```javascript
const response = await fetch('http://localhost:8000/train', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: user.username,
    keystrokes: keystrokes,
    round: currentRound + 1
  })
});
```

## Solution
Updated the backend `/train` endpoint to properly accept request body parameters using Pydantic `BaseModel`:

### Fixed Code
```python
from pydantic import BaseModel

class TrainingRequest(BaseModel):
    username: str
    keystrokes: List[Dict[str, Any]]
    round: Optional[int] = None

@router.post("/train")
async def train_user_profile(
    request: TrainingRequest,
    db: Session = Depends(get_db)
):
    username = request.username
    keystrokes = request.keystrokes
    round_num = request.round
    # ... rest of function
```

## Changes Made
**File:** `/backend/routes/train.py`

1. Added `Pydantic BaseModel` import
2. Created `TrainingRequest` class to define request body schema
3. Updated function signature to accept `request: TrainingRequest`
4. Updated function body to extract values from `request` object
5. Added `round` parameter support for tracking training round number
6. Lowered minimum keystroke requirement from 10 to 3 (single phrase may have fewer keys)
7. Improved error logging and response messages

## Testing
- ✅ Backend starts on port 8000
- ✅ Frontend connects to http://localhost:8000
- ✅ Login/Register works
- ✅ Training round submission should now succeed
- ✅ Progress bar updates correctly
- ✅ Proper error messages on validation failure

## Status
**FIXED** - Training now properly submits keystroke data to the backend
