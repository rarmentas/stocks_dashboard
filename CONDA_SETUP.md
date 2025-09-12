# Cursor Conda Environment Setup

## What Works ✅

**Global Conda Script Method** - This is the only method that works reliably across all Cursor sessions.

## Essential Files

1. **Global Script**: `C:\Users\rarme\AppData\Local\conda_cursor.bat`
2. **Workspace Settings**: `.vscode/settings.json`

## How to Replicate This Setup

### Step 1: Create Global Script
Create file: `C:\Users\rarme\AppData\Local\conda_cursor.bat`
```batch
@echo off
REM Global conda activation for Cursor
call "C:\Users\rarme\anaconda3\condabin\conda.bat" activate stockdashboard
set CONDA_DEFAULT_ENV=stockdashboard
set CONDA_PREFIX=C:\Users\rarme\anaconda3\envs\stockdashboard
cmd /k
```

### Step 2: Configure Cursor
Create/update `.vscode/settings.json`:
```json
{
    "terminal.integrated.defaultProfile.windows": "Conda (stockdashboard)",
    "terminal.integrated.profiles.windows": {
        "Conda (stockdashboard)": {
            "path": "C:\\Users\\rarme\\AppData\\Local\\conda_cursor.bat"
        }
    },
    "terminal.integrated.shell.windows": "C:\\Users\\rarme\\AppData\\Local\\conda_cursor.bat"
}
```

### Step 3: Restart Cursor
Close and reopen Cursor completely.

## Verification
Open new terminal - you should see `(stockdashboard)` in the prompt.

## For Other Projects
Just copy the `.vscode/settings.json` file to any new project folder.
