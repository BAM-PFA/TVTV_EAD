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


class Folder:
	def __init__(self,
		_2480a=None,
		_035__a=None,
		_245__a=None,
		_269__a=None,
		_264_0c=None,

		)