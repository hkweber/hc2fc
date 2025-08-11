import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, interp1d

# Original data points
x = np.array([0, 1, 2, 3, 4, 5])
y = np.array([0, 1, 0, -1, 0, 1])

# Create a cubic spline
cs = CubicSpline(x, y)

# Create a linear spline
linear_spline = interp1d(x, y, kind='linear')

# Generate a dense range of x values for the smooth spline
x_dense = np.linspace(0, 5, 100)
y_dense_cubic = cs(x_dense)
y_dense_linear = linear_spline(x_dense)

# Plotting
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'o', label="Original Data Points", color="red")
plt.plot(x_dense, y_dense_cubic, '-', label="Cubic Spline Fit", color="blue")
plt.plot(x_dense, y_dense_linear, '--', label="Linear Spline Fit", color="green")
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Cubic and Linear Spline Interpolation Example")
plt.legend()
plt.grid(True)
plt.show()
