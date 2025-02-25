import pandas as pd 
import scipy as sp
import numpy as np

a = pd.read_json('expr1.json')

a = a[a['function'].str.contains('time')]
a.loc[:,'event'] = a['event'].astype("int")

b = pd.DataFrame({
    "n":a.groupby("function")['event'].count(),
    "mean":a.groupby("function")['event'].mean()/10**6,
    "std":a.groupby('function')['event'].std()/10**6
    })

b['ci'] = b.apply(lambda x: sp.stats.t.ppf(0.95,x['n'])*x['std']/np.sqrt(x['n']),axis=1)

print(b)
b.to_latex('results.tex')
