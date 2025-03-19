from trankit import Pipeline

p = Pipeline(lang='english', gpu=True, cache_dir='./cache')

######## document-level processing ########
untokenized_doc = '''Hello! This is Trankit.'''
pretokenized_doc = [['Hello', '!'], ['This', 'is', 'Trankit', '.']]

# perform all tasks on the input
processed_doc1 = p(untokenized_doc)
processed_doc2 = p(pretokenized_doc)

######## sentence-level processing ####### 
untokenized_sent = '''This is Trankit.'''
pretokenized_sent = ['This', 'is', 'Trankit', '.']

# perform all tasks on the input
processed_sent1 = p(untokenized_sent, is_sent=True)
processed_sent2 = p(pretokenized_sent, is_sent=True)