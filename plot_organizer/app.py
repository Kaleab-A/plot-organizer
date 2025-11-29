from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from plot_organizer.ui.main_window import MainWindow


def run() -> int:
    """Main entry point with CLI argument support."""
    parser = argparse.ArgumentParser(
        description="PlotOrganizer: Organize multiple plots in a grid layout"
    )
    parser.add_argument(
        "project",
        nargs="?",
        help="Project file (.ppo) to load"
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run in headless mode (requires --export)"
    )
    parser.add_argument(
        "--export",
        metavar="OUTPUT",
        help="Export grid to file and exit"
    )
    parser.add_argument(
        "--format",
        choices=["pdf", "svg", "eps", "png"],
        default="pdf",
        help="Export format (default: pdf)"
    )
    parser.add_argument(
        "--width",
        type=float,
        default=11.0,
        help="Export width in inches (default: 11.0)"
    )
    parser.add_argument(
        "--height",
        type=float,
        default=8.5,
        help="Export height in inches (default: 8.5)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Export DPI for PNG (default: 150)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.no_gui and not args.export:
        parser.error("--no-gui requires --export")
    
    if args.export and not args.project:
        parser.error("--export requires a project file to be specified")
    
    # Headless export mode
    if args.no_gui and args.export:
        return run_headless_export(
            args.project,
            args.export,
            fmt=args.format,
            width=args.width,
            height=args.height,
            dpi=args.dpi
        )
    
    # GUI mode
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Load project if specified
    if args.project:
        if not Path(args.project).exists():
            print(f"Error: Project file not found: {args.project}", file=sys.stderr)
            return 1
        
        success = window.load_project_from_file(args.project)
        if not success:
            return 1
    
    # Export and exit if requested
    if args.export:
        return export_and_exit(
            window,
            args.export,
            fmt=args.format,
            width=args.width,
            height=args.height,
            dpi=args.dpi
        )
    
    window.show()
    return app.exec()


def run_headless_export(
    project_path: str,
    output_path: str,
    fmt: str = "pdf",
    width: float = 11.0,
    height: float = 8.5,
    dpi: int = 150
) -> int:
    """Run in headless mode: load project, export, and exit without showing GUI."""
    from plot_organizer.services.project_service import load_workspace
    from plot_organizer.services.load_service import load_csv_to_datasource
    from plot_organizer.services.export_service import export_grid
    from plot_organizer.ui.grid_board import GridBoard
    
    # Create QApplication even in headless mode (required for Qt widgets)
    app = QApplication([])
    
    try:
        # Load workspace
        print(f"Loading project: {project_path}")
        workspace = load_workspace(project_path)
        
        # Load data sources
        datasources = {}
        for ds_data in workspace.get("data_sources", []):
            ds_path = ds_data["path"]
            if not Path(ds_path).exists():
                print(f"Warning: Data file not found: {ds_path}", file=sys.stderr)
                continue
            
            ds = load_csv_to_datasource(ds_path)
            ds.id = ds_data["id"]
            ds.name = ds_data["name"]
            datasources[ds.id] = ds
            print(f"  Loaded data source: {ds.name}")
        
        # Create grid board (no parent, headless)
        grid_info = workspace.get("grid", {})
        rows = grid_info.get("rows", 2)
        cols = grid_info.get("cols", 3)
        grid_board = GridBoard(rows=rows, cols=cols, parent=None)
        
        # Reconstruct plots
        plot_count = 0
        for plot_data in workspace.get("plots", []):
            ds_id = plot_data.get("datasource_id")
            if not ds_id or ds_id not in datasources:
                continue
            
            ds = datasources[ds_id]
            grid_pos = plot_data.get("grid_position", {})
            row = grid_pos.get("row", 0)
            col = grid_pos.get("col", 0)
            rowspan = grid_pos.get("rowspan", 1)
            colspan = grid_pos.get("colspan", 1)
            
            tile = grid_board.tile_at(row, col)
            if tile:
                tile.set_plot_from_data(ds.dataframe, plot_data)
                if rowspan > 1 or colspan > 1:
                    grid_board.move_plot(row, col, row, col, rowspan, colspan)
                plot_count += 1
        
        print(f"  Reconstructed {plot_count} plots")
        
        # Export
        print(f"Exporting to: {output_path}")
        export_grid(
            grid_board,
            output_path,
            fmt=fmt,
            width_in=width,
            height_in=height,
            dpi=dpi
        )
        print(f"Export successful!")
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def export_and_exit(
    window: MainWindow,
    output_path: str,
    fmt: str = "pdf",
    width: float = 11.0,
    height: float = 8.5,
    dpi: int = 150
) -> int:
    """Export grid and exit (GUI mode with immediate export)."""
    from plot_organizer.services.export_service import export_grid
    
    try:
        print(f"Exporting to: {output_path}")
        export_grid(
            window.grid_board,
            output_path,
            fmt=fmt,
            width_in=width,
            height_in=height,
            dpi=dpi
        )
        print(f"Export successful!")
        return 0
    except Exception as e:
        print(f"Export error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())


