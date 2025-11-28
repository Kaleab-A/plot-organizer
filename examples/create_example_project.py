#!/usr/bin/env python3
"""Example: Create a PlotOrganizer project programmatically.

This script demonstrates how to create a project file (.ppo) using the
programmatic API, which can then be loaded in the GUI or exported via CLI.

Usage:
    python examples/create_example_project.py
    
    # Then open in GUI:
    python -m plot_organizer.app examples/example_project.ppo
    
    # Or export directly:
    python -m plot_organizer.app examples/example_project.ppo --export output.pdf --no-gui
"""

from plot_organizer.api import create_plot, quick_project, save_project_file


def main():
    """Create an example project with multiple plots."""
    
    # Note: Using the organizations-10000.csv test file
    # In a real scenario, replace with your actual data file path
    data_path = "plot_organizer/tests/test_csv/organizations-10000.csv"
    
    # Create plots programmatically
    plots = [
        # Plot 1: Basic line plot in top-left
        create_plot(
            "",  # Will be auto-filled by quick_project
            x="Number of employees",
            y="Founded",
            row=0,
            col=0,
            title="Organizations by Size",
            style_line=True,
            style_marker=False,
        ),
        
        # Plot 2: Plot with markers spanning 2 columns
        create_plot(
            "",
            x="Number of employees",
            y="Index",
            row=0,
            col=1,
            colspan=2,
            title="Wide Plot (2 columns)",
            style_line=False,
            style_marker=True,
        ),
        
        # Plot 3: Plot with reference lines
        create_plot(
            "",
            x="Number of employees",
            y="Founded",
            row=1,
            col=0,
            title="With Reference Lines",
            hlines=[1990, 2000, 2010],
            vlines=[500, 1000],
            style_line=True,
            style_marker=True,
        ),
        
        # Plot 4: Tall plot spanning 2 rows
        create_plot(
            "",
            x="Number of employees",
            y="Index",
            row=1,
            col=1,
            rowspan=2,
            title="Tall Plot (2 rows)",
            style_line=True,
            style_marker=False,
        ),
        
        # Plot 5: Bottom left with custom y-limits
        create_plot(
            "",
            x="Founded",
            y="Index",
            row=2,
            col=0,
            title="Custom Y-axis",
            ylim=(0, 5000),
            style_line=True,
            style_marker=False,
        ),
    ]
    
    # Create project with auto-sized grid
    project = quick_project(
        datasource_name="Organizations",
        datasource_path=data_path,
        plots=plots
    )
    
    # Save to file
    output_path = "examples/example_project.ppo"
    save_project_file(project, output_path)
    
    print(f"✓ Created example project: {output_path}")
    print(f"\nTo open in GUI:")
    print(f"  python -m plot_organizer.app {output_path}")
    print(f"\nTo export without GUI:")
    print(f"  python -m plot_organizer.app {output_path} \\")
    print(f"    --export output.pdf --no-gui --format pdf")


if __name__ == "__main__":
    main()

