import numpy as np
import matplotlib.pyplot as plt
import matplot;ib.animation as FuncAnimation
from scipy.spatial import distance_matrix
from scipy.optimize import linear_sum_assignment
import random

# Definitions
radius = 2
hexagon_twist_angle = 60
grid_twist_angle = 60
gap_factor = 0.999

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
rotated_center_x = center_x * np.cos(hexagon_twist_angle_rad) - center_y * np.sin(hexagon_twist_angle_rad)
rotated_center_y = center_x * np.sin(hexagon_twist_angle_rad) + center_y * np.cos(hexagon_twist_angle_rad)

grid_center_x = rotated_center_x * np.cos(grid_twist_angle_rad) - rotated_center_y * np.sin(grid_twist_angle_rad)
grid_center_y = rotated_center_x * np.sin(grid_twist_angle_rad) + rotated_center_y * np.cos(grid_twist_angle_rad)

# Generate twisted honeycomb grid
x = []
y = []
waypoints = []

for i in range(len(grid_center_x)):
    t = np.linspace(0, 2 * np.pi, 7) + hexagon_twist_angle_rad
    x_cell = grid_center_x[i] + gap_factor * radius * np.cos(t + grid_twist_angle_rad)
    y_cell = grid_center_y[i] + gap_factor * radius * np.sin(t + grid_twist_angle_rad)

    x.extend(x_cell)
    y.extend(y_cell)

    cx = grid_center_x[i]
    cy = grid_center_y[i]

    waypoints.append([cx, cy])

# Generate a circular fence
num_no_go_circles = 2
no_go_circle_radius = 5
no_go_circle_centers = np.array([[-5, 5], [5, -5]])

fence_radius = 15
center_fence_x = 0
center_fence_y = 0
theta = np.linspace(0, 2 * np.pi, 100)
fence_x = center_fence_x + fence_radius * np.cos(theta)
fence_y = center_fence_y + fence_radius * np.sin(theta)

# Generate waypoints inside and outside the fence, excluding no-go zones
waypoints_inside_fence = []
waypoints_outside_fence = []

for waypoint in waypoints:
    x, y = waypoint
    distance_to_fence_center = np.sqrt((x - center_fence_x)**2 + (y - center_fence_y)**2)

    # Check if the waypoint is inside the fence but outside of the no-go zones
    inside_fence = distance_to_fence_center <= fence_radius
    inside_no_go_zones = any(
        np.sqrt((x - no_go_circle_centers[:, 0])**2 + (y - no_go_circle_centers[:, 1])**2) <= no_go_circle_radius
    )
    if inside_fence and not inside_no_go_zones:
        waypoints_inside_fence.append(waypoint)
    else:
        waypoints_outside_fence.append(waypoint)

# Plot the hexagon grid with blue centers
for x, y in zip(grid_center_x, grid_center_y):
    hexagon_vertices_x = x + radius * np.cos(np.linspace(0, 2 * np.pi, 7))
    hexagon_vertices_y = y + radius * np.sin(np.linspace(0, 2 * np.pi, 7))
    plt.plot(hexagon_vertices_x, hexagon_vertices_y, 'k')
    plt.plot(x, y, 'b.', markersize=4)

# Plot the circular fence
plt.plot(fence_x, fence_y, 'r-', linewidth=1.5)

# Plot an interactive hexagon grid
originalCenterX= center_x
originalCenterY = center_y

plt.figure(figsize=(6, 6))
h = plt.plot(x, y, 'k')[0]
h_centers = plt.plot(center_x, center_y, 'b.', markerfacecolor='b')[0]
h_fence = plt.plot(fence_x, fence_y, 'r-', linewidth=1.5)[0]
plt.title('Interactive Hexagon Grid')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend(['Hexagon Grid', 'Hexagon Centers', 'Fence'])
plt.axis('equal')

# Enable interactive mode
plt.ion()

# Capture mouse clicks to move the grid
while True:
    try:
        x_click, y_click = plt.ginput(1, timeout=0)[0]

        # Calculate the translation based on click position
        translationX = x_click
        translationY = y_click

        # Apply translation to grid center coordinates
        center_x = originalCenterX + translationX
        center_y = originalCenterY + translationY

        # Update plot
        h_centers.set_xdata(center_x)
        h_centers.set_ydata(center_y)
        h.set_xdata(x + translationX)
        h.set_ydata(y + translationY)

        plt.draw()
        plt.pause(0.01)  # Small pause to allow the plot to update

    except ValueError:
        break  # Right-click or empty click to exit

# Disable interactive mode
plt.ioff()
