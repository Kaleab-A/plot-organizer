# Pre-computed SEM Feature - Quick Summary

## What It Does

Allows you to use SEM (Standard Error of the Mean) values that are **already computed** in your data, instead of having the tool compute them for you.

## Two SEM Modes

### Mode 1: Computed SEM (Default)
**Checkbox unchecked**

- Tool groups your data by a SEM column (e.g., `subject_id`)
- Computes mean within each group
- Calculates SEM across groups
- Example: 10 subjects × 5 timepoints = compute SEM across 10 subjects at each timepoint

### Mode 2: Pre-computed SEM (New!)
**Checkbox checked**

- Tool uses SEM values directly from your column
- No computation needed - values are ready to use
- Example: You already have a `sem` column with error estimates
- If duplicates exist, averages both y and SEM values (with warning)

## How to Use

1. Open **Plot → Quick Plot...**
2. Select your x, y columns as usual
3. Select **SEM column** (the column with your SEM values)
4. ✅ **Check "Pre-computed SEM"**
5. Click **OK**

Your plot will show the mean line with a shaded region for mean ± SEM!

## When to Use Pre-computed SEM

Use this feature when:

✅ You've already aggregated your data externally (R, Excel, MATLAB)  
✅ Your data has one row per condition with pre-computed statistics  
✅ You have summary statistics from another analysis  
✅ Your SEM column contains actual SEM/SE values (not a grouping variable)  

**Example data structure**:
```
time | accuracy | sem
-----|----------|-----
0    | 0.65     | 0.03
1    | 0.72     | 0.025
2    | 0.78     | 0.02
```

## When to Use Computed SEM

Use the default (unchecked) when:

✅ You have raw data with multiple observations per condition  
✅ Your SEM column is a grouping variable (e.g., `subject_id`)  
✅ You want the tool to compute SEM for you  

**Example data structure**:
```
time | accuracy | subject_id
-----|----------|------------
0    | 0.62     | s1
0    | 0.68     | s2
0    | 0.65     | s3
1    | 0.70     | s1
1    | 0.74     | s2
...
```

## Handling Duplicates

If you have multiple rows for the same x-value with pre-computed SEM:

```
x | y  | sem
--|----|----- 
1 | 10 | 1.0
1 | 12 | 1.5  ← Duplicate x=1
2 | 20 | 2.0
```

The tool will:
1. Average the y-values: (10+12)/2 = 11
2. Average the SEM values: (1.0+1.5)/2 = 1.25
3. Show a warning in the console:
   ```
   WARNING: Multiple rows found for some x-values.
   Averaged y-values and SEM values for plotting.
   Consider pre-aggregating your data.
   ```

## Visual Result

Both modes produce the same visual output:
- A line showing the mean values
- A shaded region showing mean ± SEM
- Shaded region uses 20% opacity with matching color

**No visual difference** - the choice is about how the data is processed.

## Works With

✅ Hue grouping (different colors, each with own SEM region)  
✅ Group faceting (multiple plots, all with SEM regions)  
✅ Reference lines (horizontal and vertical)  
✅ Shared axes across grouped plots  
✅ All export formats (PDF/SVG/EPS/PNG)  

## Examples

### Example 1: Pre-aggregated Time Series
```python
# You have summary statistics from your experiment
data = {
    'day': [1, 2, 3, 4, 5],
    'mean_score': [45.2, 52.1, 58.7, 63.4, 67.9],
    'standard_error': [2.1, 2.3, 2.0, 1.8, 1.7]
}

Settings:
- x: day
- y: mean_score
- SEM column: standard_error
- ✅ Check "Pre-computed SEM"
```

### Example 2: Multiple Conditions
```python
# Pre-computed stats for different treatments
data = {
    'dose': [10, 20, 30, 40, 50] * 2,
    'response': [12, 18, 24, 29, 31, 15, 22, 28, 33, 35],
    'sem': [1.2, 1.5, 1.8, 2.0, 2.1, 1.1, 1.4, 1.7, 1.9, 2.0],
    'treatment': ['A']*5 + ['B']*5
}

Settings:
- x: dose
- y: response
- hue: treatment
- SEM column: sem
- ✅ Check "Pre-computed SEM"
```

## Info Label

The info label below the checkbox updates automatically:

**Unchecked**:
> SEM column: Groups data before averaging, then computes mean ± SEM as shaded region

**Checked**:
> SEM column: Uses pre-computed SEM values from selected column

## Comparison

| Feature | Computed SEM | Pre-computed SEM |
|---------|--------------|------------------|
| **Data format** | Multiple rows per x | One row per x (ideal) |
| **SEM column** | Grouping variable | Actual SEM values |
| **Computation** | Tool computes SEM | Uses your values |
| **Best for** | Raw data | Summary statistics |
| **Duplicates** | Expected | Will average (warning) |

## Tips

1. **Check your data first**: Make sure your SEM column has the right values
2. **One row per x**: Pre-aggregate your data for best results
3. **Watch for warnings**: Console warnings help identify data issues
4. **Test both modes**: Try both to see which fits your data better

## Backward Compatibility

- Checkbox is **unchecked by default**
- All existing workflows work unchanged
- No breaking changes to any features

---

**Version**: v0.7  
**Tests**: 54/54 passing ✅  
**Status**: Production ready

