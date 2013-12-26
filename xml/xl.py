#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__='zhongkeshun'
__date__='2013/12/09'
#TODO: Do not want to sort attributs of tag when write

from optparse import OptionParser, OptionValueError
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os,sys

def indent(elem, level=0):
 i = "\n" + level*"    "   #Error Here!!
 if len(elem):
     if not elem.text or not elem.text.strip():
         elem.text = i + "  "
     if not elem.tail or not elem.tail.strip():
         elem.tail = i
     for elem in elem:
         indent(elem, level+1)
     if not elem.tail or not elem.tail.strip():
         elem.tail = i
 else:
     if level and (not elem.tail or not elem.tail.strip()):
         elem.tail = i

usage = """usage: %prog [options] -f arg1 -p arg2 -k arg3 [-v arg4]
        python xl.py -f dbuserconfig.xml -p .//db_node[@name='JYGLRAC']//db_user -k text
        python xl.py -f as_secutrans1.xml -p './/plugin[@lib='fsc_f2hsmdb']//hsmdb/table' -k name -v XXX
        python xl.py -f as_eall.xml -p .//functions -a "<component dll='s_ls_prodprebusinflow.110' arg=''/>"
        """
parser = OptionParser(usage=usage)
parser.add_option("-f", dest="filename", type="string", action="store", help="[must] file name of xml profile.")
parser.add_option("-p", dest="xpath", type="string", action="store", help="[must] xpath of xml profile to locate node U want to handle.")
parser.add_option("-k", "--key", dest="keyword", action="store", help="[must] key, such as conn_count_upper_limit or text.")
parser.add_option("-v", "--value", dest="value", action="store", help="value, such as '50' or 'text'.")
parser.add_option("-n", dest="nsort", action="store_true", help="output not sort. ")
parser.add_option("-a", "--append", type="string", dest="add_node", action="store", help="append node. ")
(opts, args) = parser.parse_args()

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    #lines = reparsed.toxml(encoding="GB18030").split('\n')
    lines = reparsed.toprettyxml(indent="    ", encoding="GB18030").split('\n')
    xmls = ""
    for line in lines:
        if line.strip() == "":
            continue
        xmls += line + '\n'
    return xmls

def file_rebuild(filename):
    filename_t = filename + '.temp'
    fpt = open(filename_t, 'wb')
    with open(filename, 'rb') as fp:
        i = 0
        for line in fp.readlines():
            if i == 0:
                fpt.write('<?xml version="1.0" encoding="utf-8"?> \n')
            else:
                try:
                    fpt.write(line.decode('gbk').encode('utf-8'))
                except:
                    fpt.write(line)
            i += 1
    fpt.close()
    return filename_t

def print_list(array):
    for item in array:
        if item:
            print item

def parse_xml(filename):
    fn = filename
    try:
        tree = ET.parse(filename)
    except:
        filename_tmp = file_rebuild(filename)
        tree = ET.parse(filename_tmp)
        os.remove(filename_tmp)
        fn = filename_tmp
    return tree

def get_node_acc_to_xpath(tree, xpath):
    root = tree.getroot()
    try:
        es = root.findall(xpath)
    except:
        print 'can not reach %s' %xpath
        return
    if es == None:
        print 'xpath [%s] can not be located.'
        return None
    else:
        return es

def search_xml(filename, xpath):
    tree = parse_xml(filename)
    nodes = get_node_acc_to_xpath(tree, xpath)
    rels = []
    if nodes == None:
        return
    for e in nodes:
        if opts.keyword == 'text':
            rels.append(e.text)
        else:
            rels.append(e.attrib.get(opts.keyword))
    if not opts.nsort:
        rels.sort()
    print_list(rels)

def alter_xml(filename, xpath, **kwargs):
    tree = parse_xml(filename)
    nodes = get_node_acc_to_xpath(tree, xpath)
    if not kwargs:
        return
    for e in nodes:
        for key, value in kwargs.iteritems():
            e.set(key, value)
    tree.write(filename, encoding='GB18030')

def add_xml(filename, xpath, elestrings, key):
    tree = parse_xml(filename)
    node = get_node_acc_to_xpath(tree, xpath)
    if len(node) != 1:
        print 'father node should be unique,but find %s in all'%len(node)
        return
    father_node = node[0]
    try:
        ele = ET.fromstring(elestrings)
    except ET.ParseError:
        ele = ET.fromstring(elestrings.decode('gbk').encode('utf8'))
    ele.tail = '\n'
    if key is not None:
        assert ele.get(key) not in [t.get(key) for t in father_node.findall(ele.tag)], \
            'add node already exist, Please take care. '
    father_node.append(ele)
    indent(tree.getroot())
    tree.write(filename, encoding='GB18030')
    #write_xml(filename, tree)

def write_xml(filename, tree):
    file_out=open(filename + '.write.xml', 'wb')
    file_out.write(prettify(tree.getroot()).decode("GB18030").encode("utf8"))
    file_out.close()

if __name__ == '__main__':
    if not (opts.filename and opts.xpath):
        parser.print_help()
        sys.exit()
    if opts.keyword is None and opts.add_node is None:
        print 'What do U want to do ?'
    elif opts.keyword is not None and opts.add_node is None:
        if opts.value == None:
            search_xml(opts.filename, opts.xpath)
        else:
            kws = {}
            kws[opts.keyword]=opts.value
            print kws
            alter_xml(opts.filename, opts.xpath, **kws)
    elif opts.add_node is not None:
        if os.path.isfile(opts.add_node):
            with open(opts.add_node) as fp:
                for line in fp.readlines():
                    if line.strip() == '' or line.startswith('#'):
                        continue
                    add_xml(opts.filename, opts.xpath, line, opts.keyword)
        else:
            add_xml(opts.filename, opts.xpath, opts.add_node, opts.keyword)
