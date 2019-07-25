from lxml import etree

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


# ead.xpath('/e:ead/e:archdesc',namespaces={'e': 'urn:isbn:1-931666-22-9'})

# files = r.tree.xpath('//e:c[@level="file" or @level="item"]',namespaces=r.XPATH_NS_MAP)
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

	def parse_FFTs(enumeration,URL):
		pass

	def check_headers(enumeration):
		pass

def parse_EAD(filepath):
	_ead = EAD(filepath)

	tree = _ead.tree

	items = _ead.tree.xpath(
		'//e:c[@level="file" or @level="item"]',
		namespaces=_ead.XPATH_NS_MAP
		)
	for item in items:
		_id = item.get("id") # this is the ArchivesSpace ID
		title = item.xpath("e:did/e:unittitle",namespaces=_ead.XPATH_NS_MAP)[0].text
		_269 = None # WTF is this supposed to be?
		_264 = item.xpath("e:did/e:unitdate",namespaces=_ead.XPATH_NS_MAP)[0].text
		containers = item.xpath("e:did/e:container",namespaces=_ead.XPATH_NS_MAP)
		boxLabel = containers[0].get("type")
		boxNumber = containers[0].text
		folder = containers[1].get("type")
		folderNumber = containers[1].text
