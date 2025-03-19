import sys
tout = sys.stdin.read()
print("tout:", tout)
# une = next(sys.stdin)
# print ("xx:", une)

for line in sys.stdin:
    print("line:",line)


# 照理说应该把txt文件内的内容一次性全部打印出来并且有格式，试一试
# 哦原来line和tout不能放在一起，顺序问题，先用line就会显示line,tout同理。
# 是因为只有一个文件吗？