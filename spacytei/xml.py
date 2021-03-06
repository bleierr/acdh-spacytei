import time
import datetime
import requests
import lxml.etree as ET


class XMLReader():

    """ a class to read an process tei-documents"""

    def __init__(self, xml):
        self.ns_tei = {'tei': "http://www.tei-c.org/ns/1.0"}
        self.ns_xml = {'xml': "http://www.w3.org/XML/1998/namespace"}
        self.ns_tcf = {'tcf': "http://www.dspin.de/data/textcorpus"}
        self.nsmap = {
            'tei': "http://www.tei-c.org/ns/1.0",
            'xml': "http://www.w3.org/XML/1998/namespace",
            'tcf': "http://www.dspin.de/data/textcorpus"
        }
        self.file = xml
        try:
            self.original = ET.parse(self.file)
        except Exception as e:
            print('could not parse file')
            try:
                self.original = ET.fromstring(self.file.encode('utf8'))
                print('read string worked')
            except Exception as e:
                print('read from string did not work')
                print('try to download resource')
                r = requests.get(self.file)
                self.original = ET.fromstring(r.text)
        try:
            self.tree = ET.parse(self.file)
        except Exception as e:
            print('could not parse tree')
            try:
                self.tree = ET.fromstring(self.file.encode('utf8'))
                print('read string worked')
            except Exception as e:
                print('read from string did not work')
                print('try to download resource')
                r = requests.get(self.file)
                self.tree = ET.fromstring(r.text)
        except Exception as e:
            print('parsing didnt work')
            self.parsed_file = "parsing didn't work"

    def return_byte_like_object(self):
        return ET.tostring(self.tree, encoding="utf-8")

    def return_string(self):
        return self.return_byte_like_object().decode('utf-8')

    def tree_to_file(self, file=None):
        """saves current tree to file"""
        if file:
            pass
        else:
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
            file = "{}.xml".format(timestamp)

        with open(file, 'wb') as f:
            f.write(ET.tostring(self.tree))
        return file
