# Frontend Simplification Plan (Task 3)

## Objective
Remove arbitrary custom configurations from frontend and add CSV validation to match Pai Ho's validated tables.

## Current Issues

### 1. Arbitrary Corner Selection
**Problem**: Frontend allows manual selection of any corner combination
**CSV Table**: `table_corner_list.csv` defines 7 valid corner configurations:
- nom_tt: `TT`
- full_tt: `TT FSG SFG FFG FFAG SSG SSAG`
- full_tt_gsgf: `TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG`
- cross_default: `FSG SFG SSG FFG`
- cross_default_gsgf: `FSG SFG SSG FFG FFG_SSG SSG_FFG`
- cross_full: `TT FSG SFG FFG FFAG SSG SSAG`
- cross_full_gsgf: `TT FSG SFG FFG FFAG SSG SSAG FFG_SSG SSG_FFG`

**Solution**: Replace individual corner checkboxes with preset dropdown

### 2. Arbitrary Voltage Rail Selection
**Problem**: Frontend allows any voltage domain input
**CSV Table**: `table_supply_list.csv` defines 22 valid voltage rails:
- 1p1v, 1p05v, 1p0v
- vcc, vccana, vccana_0p70v
- vcctx_* (700, 650, 600, 550, 525, 500, 400, NA)
- vcc_vid_* (ff_h, ff_c, tt_h, tt_c, ss_h, ss_c)
- vcc_min_0p54, vccana_max_0p96

**Solution**: Replace text input with dropdown populated from CSV

### 3. Arbitrary Temperature/Voltage Strategy
**Problem**: Frontend allows custom temperature and voltage combinations
**CSV Columns**: func_min, perf_min, nom, perf_max, func_max, htol, hvqk

**Solution**: 
- Keep 3 strategy presets: "Pai Ho's Standard PVT", "Full Sweep", "Custom"
- For "Pai Ho's Standard PVT": Use predefined config from Pai Ho
- For "Full Sweep": Use all CSV-defined voltage conditions
- For "Custom": Still validate against CSV columns

## Implementation Steps

### Step 1: Add CSV Data to Frontend
Load corner and voltage rail lists from backend API

### Step 2: Replace Corner Selection UI
- Remove individual checkboxes
- Add dropdown with CSV-defined presets:
  ```
  - Typical Only (TT)
  - Quick (4 corners - cross_default)
  - Major (7 corners - full_tt)
  - All (9 corners - full_tt_gsgf)
  ```

### Step 3: Replace Voltage Domain Input
- Remove free-text input
- Add dropdown with all 22 valid voltage rails from CSV
- Add validation before form submission

### Step 4: Simplify Temperature/Voltage Strategy
- Keep only "Pai Ho's Standard PVT" and "Full Sweep" presets
- Remove arbitrary custom combinations
- Validate all voltage conditions against CSV columns

### Step 5: Add Frontend Validation
Before submission, validate:
- Selected corner preset exists in CSV
- Selected voltage rail exists in CSV
- Selected voltage condition exists in CSV columns

## Expected Outcome

### Before (Current)
- ❌ User can select any arbitrary corner combination
- ❌ User can enter any voltage domain (custom, invalid)
- ❌ User can create custom temp/voltage strategies not in CSV
- ❌ No validation until backend processes

### After (Simplified)
- ✅ User selects from CSV-defined corner presets only
- ✅ User selects from CSV-defined voltage rails only
- ✅ User selects from validated temperature/voltage strategies
- ✅ Frontend validates before submission
- ✅ Clear error messages for invalid selections
- ✅ Matches Pai Ho's validated configurations exactly

## Files to Modify

1. `automation/frontend/index.html`
   - Add CSV data loading functions
   - Replace corner selection UI
   - Replace voltage domain input
   - Add validation logic

2. `automation/backend/main_tornado.py`
   - Add API endpoint to serve CSV data as JSON
   - Return valid corners and voltage rails

3. `automation/TASK_LIST.md`
   - Mark Task 3 as complete

## Success Criteria

- ✅ Frontend only allows CSV-validated configurations
- ✅ No arbitrary custom inputs
- ✅ Clear dropdown selections
- ✅ Validation errors displayed to user
- ✅ Matches ULTIMATE_MASTER_PLAN.md requirements
