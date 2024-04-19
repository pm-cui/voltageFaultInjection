import numpy as np  
import matplotlib.pyplot as plt  
  
x = [620, 630, 640, 650, 660, 670, 680]

# Success Count
y_100Mhz = [0, 92, 40, 81, 8, 1, 0]
z_200Mhz = [0, 0, 120, 0, 285, 2, 14]
  
X_axis = np.arange(len(x)) 
  
plt.bar(X_axis - 0.2, y_100Mhz, 0.4, label = '100Mhz') 
plt.bar(X_axis + 0.2, z_200Mhz, 0.4, label = '200Mhz') 
  
plt.xticks(X_axis, x) 
plt.xlabel("Delay Duration") 
plt.ylabel("Success Count") 
plt.title("100Mhz vs 200Mhz") 
plt.legend() 
plt.show() 