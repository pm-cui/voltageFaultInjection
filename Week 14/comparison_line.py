
import matplotlib.pyplot as plt
import numpy as np
 
#100Mhz
x = [620, 630, 640, 650, 660, 670, 680]
y = [0, 92, 40, 81, 8, 1, 0]

#x = [630, 650, 660]
#y = [0.329, 0.583, 0.9]

# first plot with X and Y data
plt.plot(x, y)
 
#200Mhz
x1 = [620, 630, 640, 660, 670, 680]
y1 = [0, 0, 120, 285, 2, 14]

#200Mhz Success / (Success+Reset) count, minimum 10 glitches 
#x1 = [640, 660, 680]
#y1 = [0.755, 0.567, 0.0215]
 
# second plot with x1 and y1 data
plt.plot(x1, y1, '-.')
 
plt.xlabel("Delay Duration")
plt.ylabel("Success Count")
plt.title('Success Count Compasion')
plt.show()
#plt.savefig('foo.png')