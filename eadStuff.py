#!/usr/bin/env python3
import csv
from lxml import etree
import os
import sys

class EAD:
	def __init__(self,path):

		self.tree = etree.parse(path)

		self.XMLNS = "urn:isbn:1-931666-22-9"
		self._EAD = "{{}}".format(self.XMLNS)
		self.XSI_NS = "http://www.w3.org/2001/XMLSchema-instance" 
		self.SCHEMA_LOCATION = ("urn:isbn:1-931666-22-9 "
			"http://www.loc.gov/ead/ead.xsd")
		# reference for namespace inclusion: 
		# https://stackoverflow.com/questions/46405690/how-to-include-the-namespaces-into-a-xml-file-using-lxml
		self.attr_qname = etree.QName(self.XSI_NS, "schemaLocation")

		self.NS_MAP = {
			None:self.XMLNS,
			'xsi':self.XSI_NS
			}
		# can't use an empty namespace alias with xpath
		self.XPATH_NS_MAP = {
			'e':self.XMLNS
			}

class FFT:
	'''
	TIND csv should have 
	FFT__a-1 [this is the URL to the first item, http://path1.jpg]
	FFT__n-1 [this is the enumeration of the first item, e.g. 1]
	FFT__a-2 [this is the URL to the second item, http://path2.jpg]
	FFT__n-2 [this is the enumeration of the second item, e.g. 2]

	there will need to be a check in the list of headers whether 
	the header needs to be added as there can be an arbitrary number of
	JPGs associated with an item (which is represented by one row)
	'''
	def __init__(self,enumeration=None,URL=None):
		self.enumeration = enumeration
		self.URL = URL

		self.headerA = "FFT__a-{}".format(self.enumeration)
		self.headerN = "FFT__n-{}".format(self.enumeration)


class ItemRow:
	def __init__(
		self,
		ID=None,
		_245__a=None,
		_269__a=None,
		_264_0c=None,
		_500__a=None
		):
		self.ID = ID
		self._2480a = "cbpf_pfa-mss-008_{}".format(self.ID) # our manuscript identifier?
		self._035__a = "cbpf_x711{}".format(self.ID) # local control number? this is basically the archivespace id
		self._245__a = _245__a
		self._269__a = _269__a
		self._264_0c = _264_0c
		self._336__a = "Text"
		self._500__a = _500__a
		self._7001_a1 = "Michael Shamberg"
		self._7001_e1 = "creator"
		self._7001_a2 = "Megan Williams"
		self._7001_e2 = "creator"
		self._7001_a3 = "Wendy Apple"
		self._7001_e3 = "creator"
		self._7001_a4 = "Allen Rucker"
		self._7001_e4 = "creator"
		self._7002_a = "Top Value Television (Production company)"
		self._7002_e = "creator"
		self._980__a = "TVTV"
		self._982__a = "Top Value Television papers"
		self._982__b = "Top Value Television papers, 1964-2004 (bulk 1971-1977)"
		self._852__a = "UC Berkeley Art Museum and Pacific Film Archive Film Library and Study Center"
		self.linkToFindingAid = "https://oac.cdlib.org/findaid/ark:/13030/c87m0fns/"
		self._542__a = '''
			Property rights reside with the Berkeley Art Museum and Pacific 
			Film Archive, University of California, Berkeley. Literary 
			rights are retained by the creators of the records and their 
			heirs. For permission to reproduce or publish, please contact 
			the Head of the Pacific Film Archive Library.
			'''
		self.FFTs=[]
		self.imageEnumeration = None

	def parse_FFTs(self,jpegs):
		if self._2480a in jpegs:
			self.FFTs.extend(jpegs[self._2480a])
			for x in self.FFTs:
				x = "http://path/blah/{}".format(x)

			self.imageEnumeration = len(self.FFTs)

	def check_headers(self):
		pass

def parse_EAD(filepath):
	_ead = EAD(filepath)

	tree = _ead.tree

	items = _ead.tree.xpath(
		'//e:c[@level="file" or @level="item"]',
		namespaces=_ead.XPATH_NS_MAP
		)

	return items,_ead

def parse_item(item,_ead,jpegs):
	# parse individual folders or items from EAD XML
	# items is a list of XPATH results
	# for item in items:
	_id = item.get("id") # this is the ArchivesSpace ID
	_id = _id.replace("aspace_x711","")
	title = item.xpath("e:did/e:unittitle",namespaces=_ead.XPATH_NS_MAP)[0].text
	_269 = None # WTF is this supposed to be?
	try:
		_264 = item.xpath("e:did/e:unitdate",namespaces=_ead.XPATH_NS_MAP)[0].text
	except:
		_264 = ""
	containers = item.xpath("e:did/e:container",namespaces=_ead.XPATH_NS_MAP)
	boxLabel = containers[0].get("type")
	boxNumber = containers[0].text
	try:
		folder = containers[1].get("type")
		folderNumber = containers[1].text
		boxFolder = "{} {}, {} {}".format(boxLabel, boxNumber,folder,folderNumber)
	except:
		boxFolder = "{} {}".format(boxLabel, boxNumber)

	print(boxFolder)

	row = ItemRow(
		ID=_id,
		_245__a=title,
		_269__a=_269,
		_264_0c=_264,
		_500__a=boxFolder
		)
	row.parse_FFTs(jpegs)

	return row

# def parse_row(row):
# 	row_data = "{}|{}|{}|{}".format(
# 		row._245__a,
# 		row._269__a,
# 		row._264_0c,
# 		row._500__a
# 		) # ETC
# 	return row_data

def parse_row(row):
	row_data = [
		row._245__a,
		row._269__a,
		row._264_0c,
		row._500__a
		] # ETC
	for image in row.FFTs:
		row_data.append(image)
	return row_data

def parse_item_list(items,_ead,jpegs):
	csvRaw = ""
	for item in items:
		row = parse_item(item,_ead,jpegs)
		row_data = parse_row(row)
		csvRaw="{}\n{}".format(csvRaw,row_data)

	return csvRaw

def main():
	EADfilepath = sys.argv[1]
	items,_ead = parse_EAD(EADfilepath)

	with open('files.json','r') as f:
		# this is the folder of jpegs represented as JSON
		# {ITEM:[jpeg1,jpeg2,etc],ITEM2:[etc]}
		jpegs = json.load(f) 

	with open('out.csv','w+') as f:
		csvRaw = parse_item_list(items,_ead,jpegs)
		f.write(csvRaw)

if __name__ == "__main__":
	main()

