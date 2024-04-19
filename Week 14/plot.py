
import matplotlib.pyplot as plt
 
# Success of 100Mhz
#x = [620, 630, 640, 650, 660, 670, 680]
#y = [0, 92, 40, 81, 8, 1, 0]

# Success of 200Mhz
x = [620, 630, 640, 660, 670, 680]
y = [0, 0, 120, 285, 2, 14]
 
# Create a line chart
plt.figure(figsize=(8, 6))
plt.plot(x, y, marker='o', linestyle='-')
 
# Add annotations
for i, (xi, yi) in enumerate(zip(x, y)):
    plt.annotate(f'({xi}, {yi})', (xi, yi), textcoords="offset points", xytext=(0, 10), ha='center')
 
# Add title and labels
plt.title('Success Count for 200Mhz')
plt.xlabel('Delay Duration')
plt.ylabel('Success count')
 
# Display grid
plt.grid(True)
 
# Show the plot
#plt.show()
plt.savefig('foo.png')