# script to add filenames to FFT columns for TIND
# still don't know what FFT stands for

# this was abandoned in favor of just redoing the source CSV
# keeping this as a reminder?

import os
import pandas
import re

inpath = 'bampfa_TVTV.csv'
df = pandas.read_csv(inpath)
for col in df.columns:
	if col.startswith('FFT__a'):
		idxA = df.columns.get_loc(col)
		number = re.match("(.*-)([0-9]+)",col).group(2)
		d = "FFT__d-"+number
		df.insert(idxA+1,d,'')

for index, row in df.iterrows():
	for col in df.columns:
		if col.startswith('FFT__a'):
			number = re.match("(.*-)([0-9]+)",col).group(2)
			d = "FFT__d-"+number
			print(row[col])
			print(df.loc[row.name,col])
			print(pandas.isnull(df.loc[row.name,col]))
			if not pandas.isnull(df.loc[row.name,col]):
				base = os.path.basename(row[col])
				df.at[row.name,d] = base

df.to_csv('bampfa_TVTV_with-FFT-d.csv')