import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path

# Definitions
radius = 2
hexagon_twist_angle = 60
grid_twist_angle = 60
gap_factor = 0.999
translation_step = 0.5
rotation_steps = np.linspace(0, 2 * np.pi, 100)

# Function to rotate points
def rotate_points(x, y, angle):
    rotated_x = x * np.cos(angle) - y * np.sin(angle)
    rotated_y = x * np.sin(angle) + y * np.cos(angle)
    return rotated_x, rotated_y

# Function to analyze the grid and find the optimal placement
def analyze_grid(grid_center_x, grid_center_y, custom_fence_path):
    max_waypoints_inside = 0
    optimal_placement = None
    current_waypoints_inside = 0

    for i in range(len(grid_center_x)):
        x = grid_center_x[i]
        y = grid_center_y[i]

        if custom_fence_path.contains_point((x, y)):
            current_waypoints_inside += 1

        if current_waypoints_inside > max_waypoints_inside:
            max_waypoints_inside = current_waypoints_inside
            optimal_placement = x, y

    return optimal_placement, max_waypoints_inside, current_waypoints_inside

# Convert angles to radians
hexagon_twist_angle_rad = np.deg2rad(hexagon_twist_angle)
grid_twist_angle_rad = np.deg2rad(grid_twist_angle)

# Generate honeycomb centers
center_x = []
center_y = []

range_val = 10
for i in range(-range_val, range_val + 1):
    for j in range(-range_val, range_val + 1):
        cx = (3 * radius * j) - (j) * 1.5 * radius
        cy = np.sqrt(3) * radius * i + (j % 2) * np.sqrt(3) * radius / 2

        center_x.append(cx)
        center_y.append(cy)

# Convert lists to NumPy arrays for element-wise operations
center_x = np.array(center_x)
center_y = np.array(center_y)

# Perform rotation transformations
rotated_center_x, rotated_center_y = rotate_points(center_x, center_y, hexagon_twist_angle_rad)

grid_center_x, grid_center_y = rotate_points(rotated_center_x, rotated_center_y, grid_twist_angle_rad)

# Generate twisted honeycomb grid
x = []
y = []

for i in range(len(grid_center_x)):
    t = np.linspace(0, 2 * np.pi, 7) + hexagon_twist_angle_rad
    x_cell = grid_center_x[i] + gap_factor * radius * np.cos(t + grid_twist_angle_rad)
    y_cell = grid_center_y[i] + gap_factor * radius * np.sin(t + grid_twist_angle_rad)

    x.extend(x_cell)
    y.extend(y_cell)

# Custom coordinates for a non-geometric fence shape
custom_fence_x = [0, 5, 8, 10, 8, 5, 0, -5, -8, -10, -8, -5, 0]
custom_fence_y = [15, 10, 5, 0, -5, -10, -15, -10, -5, 0, 5, 10, 15]

# Create a path for the custom fence
custom_fence_path = Path(np.column_stack((custom_fence_x, custom_fence_y)))

# Create a figure and axis
fig, ax = plt.subplots(figsize=(8, 8))

# Plot the hexagon grid with blue centers
for x, y in zip(grid_center_x, grid_center_y):
    hexagon_vertices_x = x + radius * np.cos(np.linspace(0, 2 * np.pi, 7))
    hexagon_vertices_y = y + radius * np.sin(np.linspace(0, 2 * np.pi, 7))
    ax.plot(hexagon_vertices_x, hexagon_vertices_y, 'k')
    ax.plot(x, y, 'b.', markersize=4)

# Plot the custom fence shape
ax.plot(custom_fence_x + [custom_fence_x[0]], custom_fence_y + [custom_fence_y[0]], 'r-', linewidth=1.5)

# Initialize empty arrays to store the trajectory
trajectory_x_inside_fence = []
trajectory_y_inside_fence = []

# Maximum number of waypoints inside the fence
max_waypoints_inside = 0

# Data list to store placement and waypoints information
data_list = []

# Simulation
change_direction = False
direction_change_counter = 0
max_direction_change = 4  # Set the threshold for a full loop

optimal_placement = None

for translation_x in [-translation_step, 0, translation_step]:
    for translation_y in [-translation_step, 0, translation_step]:
        for rotation_step in rotation_steps:
            # Move the entire grid translation_step units
            grid_center_x += translation_x
            grid_center_y += translation_y

            rotated_center_x, rotated_center_y = rotate_points(grid_center_x, grid_center_y, rotation_step)

            # Analyze the grid and find the optimal placement
            _, max_inside, current_inside = analyze_grid(rotated_center_x, rotated_center_y, custom_fence_path)

            # Update the maximum number of waypoints inside the fence
            if current_inside > max_waypoints_inside:
                max_waypoints_inside = current_inside

                # Store the trajectory
                trajectory_x_inside_fence = rotated_center_x.tolist()
                trajectory_y_inside_fence = rotated_center_y.tolist()

                # Store the optimal placement
                optimal_placement = (rotated_center_x.copy(), rotated_center_y.copy())

            if current_inside > 0:
                change_direction = True
            elif change_direction:
                # If at least one waypoint was inside, change direction of translation
                translation_x *= -1
                translation_y *= -1
                change_direction = False
                direction_change_counter += 1

            ax.clear()
            for x, y in zip(rotated_center_x, rotated_center_y):
                hexagon_vertices_x = x + radius * np.cos(np.linspace(0, 2 * np.pi, 7))
                hexagon_vertices_y = y + radius * np.sin(np.linspace(0, 2 * np.pi, 7))
                ax.plot(hexagon_vertices_x, hexagon_vertices_y, 'k')
                ax.plot(x, y, 'b.', markersize=4)

            # Plot the custom fence shape
            ax.plot(custom_fence_x + [custom_fence_x[0]], custom_fence_y + [custom_fence_y[0]], 'r-', linewidth=1.5)

            ax.set_title(f'Max Waypoints Inside: {max_inside}')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.axis('equal')

            # Pause to make the animation visible
            plt.pause(0.01)

            # Check if a full loop has been made
            if direction_change_counter >= max_direction_change:
                break

        # Check if a full loop has been made
        if direction_change_counter >= max_direction_change:
            break

    # Check if a full loop has been made
    if direction_change_counter >= max_direction_change:
        break

# Return to the optimal placement
ax.clear()
ax.plot(trajectory_x_inside_fence, trajectory_y_inside_fence, 'g-', linewidth=1.5)
ax.plot(optimal_placement[0], optimal_placement[1], 'co', markersize=8)
ax.plot(custom_fence_x + [custom_fence_x[0]], custom_fence_y + [custom_fence_y[0]], 'r-', linewidth=1.5)
ax.set_title(f'Returned to Optimal Placement')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.axis('equal')

# Show the final plot
plt.show()

# Display optimal placement and max waypoints inside the fence
print(f'Optimal Placement: {optimal_placement}')
print(f'Max Waypoints Inside: {max_waypoints_inside}')

# Display data for each placement
for i, data in enumerate(data_list):
    print(f"Placement {i + 1}: {data['placement']}, Waypoints Inside: {data['waypoints_inside']}")
