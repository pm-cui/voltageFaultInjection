import os

# Open a file
fd = open("output.txt", "r")

data = fd.read()
print(data)

fd.close()


#Empties the file
#open("output.txt", 'w').close()
