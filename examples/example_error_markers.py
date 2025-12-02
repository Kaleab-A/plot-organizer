"""Example demonstrating error marker annotations feature.

This example shows how to add error bar markers to plots for annotating
significant events, thresholds, or other important points.
"""

from plot_organizer.api import (
    create_datasource,
    create_plot,
    create_project,
    save_project_file,
)
import tempfile
from pathlib import Path

# Create sample data
data_csv = """time,accuracy,loss,model
0,0.45,2.1,ModelA
1,0.52,1.8,ModelA
2,0.61,1.5,ModelA
3,0.68,1.3,ModelA
4,0.74,1.1,ModelA
5,0.79,0.9,ModelA
6,0.83,0.8,ModelA
7,0.86,0.7,ModelA
0,0.42,2.3,ModelB
1,0.49,2.0,ModelB
2,0.58,1.7,ModelB
3,0.65,1.4,ModelB
4,0.71,1.2,ModelB
5,0.76,1.0,ModelB
6,0.81,0.9,ModelB
7,0.84,0.8,ModelB"""

# Write to temporary CSV
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write(data_csv)
    csv_path = f.name

try:
    # Create datasource
    ds = create_datasource("Training Results", csv_path)
    
    # Example 1: Plot with X error bars (horizontal)
    # Use case: marking time intervals or time uncertainty
    plot1 = create_plot(
        ds["id"],
        x="time",
        y="accuracy",
        hue=["model"],
        row=0,
        col=0,
        title="Accuracy with Time Markers",
        error_markers=[
            # Mark a significant event at time 3.5 with uncertainty
            {
                "x": 3.5,
                "xerr": 0.5,  # ±0.5 time units
                "marker": "v",  # Triangle down
                "color": "red",
                "label": "Checkpoint Saved"
            },
            # Mark another event at time 5.2
            {
                "x": 5.2,
                "xerr": 0.3,
                "marker": "^",  # Triangle up
                "color": "blue",
                "label": "Learning Rate Drop"
            }
        ]
    )
    
    # Example 2: Plot with Y error bars (vertical)
    # Use case: marking threshold values or value uncertainty
    plot2 = create_plot(
        ds["id"],
        x="time",
        y="loss",
        hue=["model"],
        row=0,
        col=1,
        title="Loss with Threshold Markers",
        error_markers=[
            # Mark a performance threshold at loss=1.0 with tolerance
            {
                "y": 1.0,
                "yerr": 0.1,  # ±0.1 loss units
                "marker": "o",  # Circle
                "color": "green",
                "label": "Target Loss"
            }
        ]
    )
    
    # Example 3: Mixed markers with auto-positioning
    # When x or y is not provided, position is auto-computed
    plot3 = create_plot(
        ds["id"],
        x="time",
        y="accuracy",
        hue=["model"],
        row=1,
        col=0,
        colspan=2,
        title="Accuracy with Multiple Event Markers (Stacked)",
        error_markers=[
            # These will be auto-positioned vertically and stacked with different shapes
            {"x": 2.0, "xerr": 0.2, "marker": "s", "color": "red", "label": "Event 1"},
            {"x": 4.0, "xerr": 0.3, "marker": "D", "color": "orange", "label": "Event 2"},
            {"x": 6.0, "xerr": 0.2, "marker": "*", "color": "purple", "label": "Event 3"},
        ]
    )
    
    # Create project
    project = create_project(
        grid_size=(2, 2),
        datasources=[ds],
        plots=[plot1, plot2, plot3]
    )
    
    # Save project
    output_path = "error_markers_example.ppo"
    save_project_file(project, output_path)
    
    print(f"✓ Created example project with error markers: {output_path}")
    print(f"\nTo view the project:")
    print(f"  python -m plot_organizer {output_path}")
    print(f"\nFeatures demonstrated:")
    print(f"  • X error bars (horizontal) for time uncertainty")
    print(f"  • Y error bars (vertical) for value thresholds")
    print(f"  • Different marker shapes (v, ^, o, s, D, *)")
    print(f"  • Auto-positioning and stacking of multiple markers")
    print(f"  • Color customization for different marker types")
    print(f"  • Labels for legend entries")
    print(f"\nIn the UI, you can also:")
    print(f"  • Right-click on a plot → 'Manage Error Markers...'")
    print(f"  • Add, edit, or delete markers interactively")

finally:
    # Cleanup temporary CSV
    Path(csv_path).unlink()

