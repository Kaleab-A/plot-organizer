# SEM Feature - Quick Summary

## What It Does

The SEM (Standard Error of the Mean) feature allows you to visualize variability in your data by:

1. **Grouping** data by a "SEM column" (e.g., subject ID, trial number)
2. **Computing** the mean and SEM across those groups
3. **Displaying** the result as a line (mean) with a shaded region (±1 SEM)

## How It Works

### The Algorithm

Given data with columns `x`, `y`, and a `sem_column`:

```
Step 1: Group by (sem_column, x) and compute mean of y
  → Gives one y-value per (sem_column_value, x_value) pair

Step 2: For each x-value, aggregate across sem_column groups
  → Compute overall mean(y) and sem(y)

Step 3: Plot
  → Line: x vs mean(y)
  → Shaded region: x vs [mean(y) - sem(y), mean(y) + sem(y)]
```

### Example

```python
# Your data
data = {
    'time': [1, 1, 1, 2, 2, 2],
    'score': [10, 12, 14, 20, 22, 24],
    'subject': ['A', 'B', 'C', 'A', 'B', 'C']
}

# In Quick Plot Dialog:
# x: time
# y: score
# sem_column: subject

# Result:
# time=1: subjects have scores 10,12,14 → mean=12, SEM=1.15
# time=2: subjects have scores 20,22,24 → mean=22, SEM=1.15
# Plot shows line through (1,12) and (2,22) with shaded regions
```

## How to Use

1. Open **Plot → Quick Plot...**
2. Select your data source
3. Choose **x** and **y** columns
4. (Optional) Choose **hue** for color grouping
5. **NEW**: Choose **SEM column** (must be different from x, y, hue, groups)
6. Click **Create**

The plot will show:
- A line representing the mean
- A translucent shaded region showing mean ± SEM

## Works With

✅ **Hue grouping**: Each hue category gets its own line + SEM region  
✅ **Group faceting**: Each faceted plot has its own SEM computation  
✅ **Export**: SEM regions are preserved in PDF/SVG/EPS/PNG exports  
✅ **Shared axes**: SEM regions work correctly with shared axis limits  

## Validation

The dialog prevents you from selecting a SEM column that conflicts with other columns:

```
❌ Can't use same column for x and sem_column
❌ Can't use same column for y and sem_column
❌ Can't use same column for hue and sem_column
❌ Can't use same column for groups and sem_column
```

## Visual Example

**Without SEM**:
```
   │
 y │  ─────────  (just a line)
   │
   └─────────────
        x
```

**With SEM**:
```
   │  ░░░░░░░
 y │  ██████████  (line with shaded region)
   │  ░░░░░░░
   └─────────────
        x
```

The shaded region shows where mean ± 1 SEM falls.

## When to Use SEM Column

Use a SEM column when:
- You have **repeated measurements** (e.g., multiple trials, subjects, replicates)
- You want to show **variability** in your data
- You need to communicate **uncertainty** in your measurements

Common SEM columns:
- `subject_id` or `participant_id`
- `trial_number` or `run_number`
- `replicate` or `sample_id`
- `mouse_id`, `batch`, etc.

## Implementation Details

- **Algorithm**: Two-stage groupby with pandas `.agg(['mean', 'sem'])`
- **Rendering**: Matplotlib `fill_between()` with 20% opacity
- **Color matching**: Shaded region uses same color as line
- **Performance**: Efficient even with large datasets
- **Testing**: 5 comprehensive tests verify correctness

## Files Modified

1. `plot_organizer/ui/dialogs.py` - Added SEM combo box
2. `plot_organizer/ui/grid_board.py` - Added `_plot_with_sem()` method
3. `plot_organizer/ui/main_window.py` - Passes SEM column to plots
4. `plot_organizer/services/export_service.py` - Renders SEM in exports
5. `plot_organizer/tests/test_sem_plotting.py` - New test file

## Future Enhancements

Potential improvements:
- Support for different error types (SD, 95% CI, bootstrap)
- Adjustable opacity for shaded regions
- Option for error bars instead of shaded regions
- Asymmetric error bounds

---

**Version**: v0.5  
**Tests**: 29/29 passing ✅  
**Status**: Production ready

