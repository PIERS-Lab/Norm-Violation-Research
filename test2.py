import matplotlib.pyplot as plt
plt.ion()
plt.plot([1,2,3])
plt.pause(0.01) # <---- add pause
plt.show()

print('is this fig good? (y/n)')
x = input()
if x=="y":
    plt.savefig(r'C:\figures\papj.png')
else:
    print("big sad")