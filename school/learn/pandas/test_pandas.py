import pandas as pd

'''
data = {
    'name': ['judy', 'kelly', 'morgen'],
    'age': ['18', '20', '25'],
    'note': ['20', '15', '18']

}

df = pd.DataFrame(data)

print(df)
'''
'''
s = pd.Series([10, 20, 30], index = ['a', 'b', 'c'])
print(s)
'''

'''
df = pd.read_csv('commit.csv', header = None)
df.index = range(1,len(df)+1)
print(df)
'''