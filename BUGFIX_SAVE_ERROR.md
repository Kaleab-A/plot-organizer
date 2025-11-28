# Bug Fix: Save Project Errors

## Issue 1: 'str' object has no attribute 'dataframe'
When trying to save a project in the GUI, users initially encountered:
```
Failed to save project:
'str' object has no attribute 'dataframe'
```

### Root Cause
The `serialize_layout()` method was iterating over string IDs instead of datasource objects.

### Fix
Changed `serialize_layout()` to accept `{id: datasource}` map directly and iterate correctly:
```python
for ds_id, ds_obj in datasources.items():
    if tile._df is ds_obj.dataframe:
        datasource_id = ds_id
        break
```

## Issue 2: unhashable type: 'DataSource'
After fixing Issue 1, users encountered:
```
Failed to save project:
unhashable type: 'DataSource'
```

### Root Cause
Attempted to use `DataSource` dataclass objects as dictionary keys, but dataclasses are not hashable by default (would need `frozen=True`).

The initial fix tried to invert the map:
```python
# This fails because DataSource is not hashable
datasource_map = {ds: ds_id for ds_id, ds in self._datasources.items()}
```

### Final Fix
Changed the API entirely. Instead of trying to use objects as keys:

1. **Updated `GridBoard.serialize_layout()`** to accept `{id: datasource}` directly
2. **Removed map inversion** from `MainWindow._save_to_path()`
3. **Updated matching logic** to iterate over the dict correctly

**grid_board.py:**
```python
def serialize_layout(self, datasources: dict[str, object]) -> list[dict]:
    """Args: datasources: {id: datasource_object}"""
    for ds_id, ds_obj in datasources.items():
        if tile._df is ds_obj.dataframe:
            datasource_id = ds_id
            break
```

**main_window.py:**
```python
# Clean and simple - no inversion needed
grid_layout = self.grid_board.serialize_layout(self._datasources)
```

## Test Added
Added `test_datasource_matching()` in `test_project_save_load.py` to ensure:
1. Datasource matching by dataframe works correctly
2. The {id: object} map format is used properly

## Verification
✅ All 106 tests pass
✅ Save functionality now works in GUI

## Files Changed
- `plot_organizer/ui/grid_board.py` - Updated serialize_layout() signature and logic
- `plot_organizer/ui/main_window.py` - Simplified to pass datasources directly
- `plot_organizer/tests/test_project_save_load.py` - Updated test for new API

## Lesson Learned
Don't try to use non-hashable objects as dictionary keys. Keep the API simple by using the natural {id: object} format that MainWindow already has.

