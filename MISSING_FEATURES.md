# Missing Features from Original Design Plan

_Comparison between design.md goals and current implementation (v0.2.1)_

---

## ✅ IMPLEMENTED FEATURES

### Core Plotting
- ✅ Desktop Python GUI with PySide6
- ✅ Load multiple CSV files as data sources
- ✅ Create line plots with x, y, optional hue
- ✅ Group faceting (cross-product expansion, capped at 50)
- ✅ Shared axes across grouped plots
- ✅ Automatic aggregation of duplicate (x, hue) values
- ✅ Empty combination handling ("No data" message)
- ✅ Matplotlib canvas per tile
- ✅ Type inference (categorical, continuous, ordinal)

### Grid Operations
- ✅ Add rows/columns dynamically
- ✅ GridBoard with PlotTile widgets
- ✅ Automatic plot placement in first empty cell

### UI
- ✅ Main window with menus
- ✅ Data Manager dock (left side)
- ✅ Create Plot dialog with x/y/hue/groups selection
- ✅ Clean UI with maximized plot space (no toolbar/headers)

---

## ❌ MISSING FEATURES (from design.md)

### 1. CSV Load Wizard (Advanced) ❌
**Design Goal:** Full-featured CSV loading with:
- Delimiter options (auto + manual)
- Encoding options (auto + manual)
- Header row selection
- Custom NA strings
- **Missing Values Handling:**
  - Per-column summary (count NA, % NA)
  - Per-column actions: Drop rows, Drop column, Keep as is
  - Global quick actions: "Drop rows with any NA", "Drop columns with >X% NA"
- **Type Confirmation Dialog:**
  - Editable table to override inferred types
  - Preview categories for categorical/ordinal
  - Reorder categories for ordinal

**Current Status:** Basic CSV load only (auto-detect, no NA handling, auto-infer types with no GUI confirmation)

**Priority:** Medium-High (nice to have for production use)

---

### 2. Remove Rows/Columns from Grid ❌
**Design Goal:** Remove grid rows/columns with prompts if tiles contain plots

**Current Status:** Can only add rows/columns, not remove them

**Priority:** Medium

---

### 3. Drag & Drop Plot Tiles ❌
**Design Goal:** 
- Drag a tile's header and drop onto another cell
- Swap if destination is occupied
- Optional confirm prompt

**Current Status:** No drag-and-drop; plots are fixed once placed

**Priority:** High (core UX feature)

---

### 4. Cell Context Menu ❌
**Design Goal:**
- Replace plot
- Duplicate plot (clone PlotInstance)
- Clear cell
- Export this plot

**Current Status:** No context menu on tiles

**Priority:** Medium-High

---

### 5. Whole-Grid Export ❌
**Design Goal:**
- Export entire grid layout to PDF/SVG/EPS/PNG
- Create new offscreen Figure with GridSpec
- Re-render all plots into subplots
- Options dialog:
  - Page size (A4, Letter, custom)
  - Margins & gutters
  - DPI (for PNG, default 150)
  - Font embedding for vector formats
  - Filename pattern

**Current Status:** No export functionality at all

**Priority:** High (core feature per design)

---

### 6. Per-Plot Export ❌
**Design Goal:** Export single plot from context menu at chosen size/format

**Current Status:** No per-plot export

**Priority:** Medium

---

### 7. Project Save/Load (.ppo.json) ❌
**Design Goal:**
- Save workspace state to JSON file
- Store data source paths (relative when possible)
- Store plot specs, instances, grid layout
- Load project with file relinking dialog if paths missing

**Current Status:** 
- `project_service.py` has save stub
- No load implementation
- No File → Save/Open menu actions

**Priority:** High (persistence is essential)

---

### 8. Plot Wizard Enhancements ❌
**Design Goal:**
- Preview combo count before creating grouped plots
- Show expected number of plots
- Title & Style options (line width, markers)
- Validation: Hue requires categorical type

**Current Status:** 
- ✅ Groups multi-select
- ✅ Combo count message
- ❌ No preview of actual combinations
- ❌ No style options (linewidth, markers)
- ❌ No title field
- ❌ No hue type validation

**Priority:** Low-Medium

---

### 9. Threaded CSV Loading ❌
**Design Goal:** Non-blocking worker thread for large file IO with progress bar

**Current Status:** Synchronous loading (UI blocks on large files)

**Priority:** Medium (important for large datasets)

---

### 10. DateTime Axis Formatting ❌
**Design Goal:** Detect datetime columns and format with AutoDateLocator

**Current Status:** No special datetime handling

**Priority:** Low-Medium

---

### 11. Style Overrides ❌
**Design Goal:** Per-plot customization:
- Line width
- Markers (toggle on/off, style)
- Colors
- Legend toggle

**Current Status:** Uses matplotlib defaults only

**Priority:** Low

---

### 12. Variable Cell Sizes ❌
**Design Goal (v1.1):** Resize column widths/row heights; row/col spanning

**Current Status:** Uniform grid cell sizes only

**Priority:** Low (marked as v1.1 feature)

---

## 📊 SUMMARY

### Implementation Status
- **Fully Implemented:** 9 features
- **Partially Implemented:** 2 features
- **Not Implemented:** 12 features

### Priority Breakdown
**High Priority (Core Features):**
1. ❌ Whole-grid export (PDF/SVG/EPS/PNG)
2. ❌ Project save/load
3. ❌ Drag & drop tiles

**Medium-High Priority:**
4. ❌ CSV Load Wizard (NA handling, type confirmation)
5. ❌ Cell context menu

**Medium Priority:**
6. ❌ Remove rows/columns
7. ❌ Per-plot export
8. ❌ Threaded CSV loading

**Low-Medium Priority:**
9. ❌ Plot wizard enhancements (style, validation)
10. ❌ DateTime axis formatting

**Low Priority:**
11. ❌ Style overrides
12. ❌ Variable cell sizes

---

## 🎯 RECOMMENDED NEXT STEPS

Based on the original design's "Definition of Done (v1)", the critical missing features are:

1. **Drag plots between cells** → Essential for "organizing" plots
2. **Export entire grid to PDF/SVG/EPS/PNG** → Core deliverable
3. **Project save/load** → Persistence is essential
4. **Remove rows/columns** → Complete grid management
5. **CSV NA handling & type confirmation** → Data quality

These 5 features would complete the v1 design specification.

---

## 💡 NOTES

- Current implementation (v0.2.1) successfully demonstrates the core concept
- Group faceting with shared axes works well
- Automatic aggregation is a nice addition beyond the design
- The foundation is solid for adding remaining features
- Most missing features are UI/UX polish rather than architectural gaps

