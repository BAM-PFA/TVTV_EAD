#!/usr/bin/env python3
import csv
import json
from lxml import etree
import os
import pandas
import sys

# manual processes: headers are copied from sample csv
# I know there need to be 349 FFT columns.....

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

class ItemRow:
	def __init__(
		self,
		ID=None,
		_245__a="",
		_269__a="",
		_264_0c="",
		_500__a=""
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
		self._542__a = (
			"Property rights reside with the Berkeley Art Museum and Pacific "\
			"Film Archive, University of California, Berkeley. Literary "\
			"rights are retained by the creators of the records and their "\
			"heirs. For permission to reproduce or publish, please contact "\
			"the Head of the Pacific Film Archive Library."\
			)
		self.FFTs=[]
		self.imageEnumeration = None

	def parse_FFTs(self,jpegs):
		# take in the dict like this: {cbpf_id:{image1,image2}}
		# return a list of images with full URI and filename
		for k,v in jpegs.items():
			if self._2480a in k:
				for jpg in v:
					# print(jpg)
					jpgURI = "http://digitalassets.lib.berkeley.edu/tvtv/ucb/images/{}".format(jpg)
					self.FFTs.append(jpgURI)
					self.FFTs.append(jpg)
					# add the current count of images 
					# for the TIND enumeration of each image
					self.FFTs.append(str(sum('http://' in img for img in self.FFTs)))
		# print(self.FFTs)

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

	# print(boxFolder)

	row = ItemRow(
		ID=_id,
		_245__a=title,
		_269__a=_269,
		_264_0c=_264,
		_500__a=boxFolder
		)
	row.parse_FFTs(jpegs)

	return row

def parse_row(row):
	row_data = [
		row._2480a,
		row._035__a,
		row._245__a,
		row._269__a,
		row._264_0c,
		row._336__a,
		row._7001_a1,
		row._7001_e1,
		row._7001_a2,
		row._7001_e2,
		row._7001_a3,
		row._7001_e3,
		row._7001_a4,
		row._7001_e4,
		row._980__a,
		row._982__a,
		row._982__b,
		row._852__a,
		row.linkToFindingAid,
		row._542__a,
		row._500__a
]
	for image in row.FFTs:
		row_data.append(image)
	# print(row_data)
	return row_data

def do_csv(items,_ead,jpegs):
	headers = get_headers()
	with open("out.csv","w+") as f:
		out = csv.writer(f)
		out.writerow(headers)
		for item in items:
			row = parse_item(item,_ead,jpegs)
			row_data = parse_row(row)
			out.writerow(row_data)


def read_jpegs(path):
	# this returns the folder of jpegs represented as dict
	# {ITEM1[jpeg1,jpeg2,etc],ITEM2:[etc]}
	jpegs = {}
	for root,dirs,files in os.walk(path):
		for _dir in dirs:
			jpegs[_dir] = []
			for jpg in os.listdir(os.path.join(root,_dir)):
				jpegs[_dir].append(jpg)

	return jpegs

def get_headers():
	# headers for TIND defined in main library's sample
	headers = ["02480a","035__a","245__a","269__a","260__c","336__a","7001_a-1","7001_e-1","7001_a-2","7001_e-2","7001_a-3","7001_e-3","7001_a-4","7001_e-4","980__a","982__a","982__b","852__a","Link to Finding Aid","542__f","500__a"]

	# gets the columns needed for the FFT columns
	# I know there need to be 349 of them.
	for t in range(1,350):
		headers.append("FFT__a-"+str(t))
		headers.append("FFT__d-"+str(t))
		headers.append("FFT__n-"+str(t))

	return headers

def main():
	EADfilepath = sys.argv[1]
	imageFolderPath = sys.argv[2]

	items,_ead = parse_EAD(EADfilepath)
	jpegs = read_jpegs(imageFolderPath) 

	do_csv(items,_ead,jpegs)

if __name__ == "__main__":
	main()

