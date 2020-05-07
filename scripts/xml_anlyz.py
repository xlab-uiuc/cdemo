import os
from lxml import etree
from lxml.html import fromstring
import lxml.html as lh
import csv
import subprocess
import os
import fnmatch
import filecmp
import utils

def findXmls(repop, pattern='*default.xml', verbose=False):
  """
  Hadoop's config file is all named XXX-default.xml,
  and we want to automatically find these config files given a repository
  """
  flst = []
  ignore = []
  for dname, sdname, flist in os.walk(repop):
    for fname in flist:
      if fnmatch.fnmatch(fname, pattern):
        if fname.find('test') != -1:
          if verbose:
            print 'IGNORE: ', fname
          ignore.append(fname)
        elif dname.find('/test') != -1: # it is located in a test dir
          if verbose:
            print 'IGNORE: ', fname
          ignore.append(fname)
        else:
          if verbose:
            print 'FIND XML: ', os.path.join(dname, fname)
          flst.append(os.path.join(dname, fname))
  return flst, ignore

def getParamsFromXml(defxml):
  """
  Get all the parameters from the config files $defxml
  """
  pmap = {}
  f = open(defxml)
  xml = f.read()
  f.close()
  doc = fromstring(xml)
  for prop in doc.iter('property'):
    p = {}
    p['file'] = defxml
    for name in prop.iter('name'):
      p['name'] = name.text_content()
    for value in prop.iter('value'):
      p['default'] = utils.normalize(value.text_content().strip())
    for value in prop.iter('description'):
      p['desc'] = value.text_content()
    pmap[p['name']] = p
  #handle values like ${xxx}
  for pn in pmap:
    if 'default' in pmap[pn]:
      defv = pmap[pn]['default']
      lb = defv.find('${')
      rb = defv.find('}')
      if lb != -1 and rb != -1 and rb > lb:
        ref = defv[lb+2 : rb]
        if ref in pmap and 'default' in pmap[ref]:
          refv = pmap[ref]['default']
          defv = defv.replace('${'+ref+'}', refv)
          pmap[pn]['default'] = utils.normalize(defv)
    else:
      pmap[pn]['default'] = utils.normalize(None)
  return pmap


def checkXml(xmlpath, chkdef=True, chkdesc=False):
  """
  Check 1 xml file for lack of default value and descriptions
  """
  pmap = getParamsFromXML(xml)
  noDefs = []
  for pn in pmap:
    p = pmap[pn]
    if p['default'] == None:
      noDefs.append(pn)
  if chkdef > 0 and len(noDefs) > 0:
    print '>>>>>', len(noDefs), 'PARAMS W/O DEFAULT VALUES |', xmlpath
    for pn in noDefs:
      print pn
  noDescs = []
  for pn in pmap:
    p = pmap[pn]
    if 'desc' not in p:
      noDescs.append(pn)
  if chkdef > 0 and len(noDescs) > 0:
    print '>>>>>', len(noDescs), 'PARAMS W/O DESCRIPTIONS |', xmlpath
    for pn in noDescs:
      print pn

def detectXmlDiffs(repop):
  """
  For multiple xmls, we want to know whether their values are the same.
  For example, we have yarn-site.xml and yarn-default.xml, we want to know
  if all the settings in yarn-site.xml are the same in yarn-default.xml,
  what settings are not?
  """
  xmlmap = {}
  suffices = ['default.xml', 'site.xml']
  for s in suffices:
    xmls, igns = findXmls(repop, '*' + s)
    for xml in xmls:
      fname = os.path.basename(xml)
      comp = fname.replace(s, '')
      if comp not in xmlmap:
        xmlmap[comp] = [xml]
      else:
        xmlmap[comp].append(xml)
  for comp in xmlmap:
    if len(xmlmap[comp]) <= 1:
      continue
    print comp, ':', len(xmlmap[comp])
    pmap = {}
    for xml in xmlmap[comp]:
      tpmap = getParamsFromXml(xml)
      for pname in tpmap:
        p = tpmap[pname]
        if pname not in pmap:
          pmap[pname] = {}
          pmap[pname][p['default']] = [xml] 
        elif p['default'] not in pmap[pname]:
          pmap[pname][p['default']] = [xml]
        else:
          pmap[pname][p['default']].append(xml)
    for pn in pmap:
      if len(pmap[pn]) > 1:
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>', pn
        for val in pmap[pn]:
          print val, ' : ', len(pmap[pn][val])

def getParamsInRepo(repop):
  """
  Aggregate all the params in the repo
  """
  pmap = {}
  suffices = ['default.xml', 'site.xml']
  for s in suffices:
    xmls, igns = findXmls(repop, '*' + s)
    for xml in xmls:
      tpmap = getParamsFromXml(xml)
      for pname in tpmap:
        p = tpmap[pname]
        if pname not in pmap:
          pmap[pname] = {}
          pmap[pname][p['default']] = [xml] 
        elif p['default'] not in pmap[pname]:
          pmap[pname][p['default']] = [xml]
        else:
          pmap[pname][p['default']].append(xml)
  return pmap


def aggrParamsInRepo(repop):
  resmap = {}
  pmap = getParamsInRepo(repop)
  for pn in pmap:
    if len(pmap[pn]) == 1:
      for val in pmap[pn]:
        resmap[pn] = val
    else:
      for val in pmap[pn]:
        for xml in pmap[pn][val]:
          if isPrimaryXml(xml):
            if pn in resmap:
              print '[FATAL] at least two primary xmls have different vals for', pn
            else:
              resmap[pn] = val
  return resmap

def isPrimaryXml(xml):
  pcomps = ['hadoop-common', 'hadoop-hdfs', 'hadoop-yarn', 'hadoop-mapreduce']
  xmlname = os.path.basename(xml)
  for c in pcomps:
    if c in xmlname:
      return True
  return False

def detectValDiffs(repop):
  pmap = getParamsInRepo(repop)
  for pn in pmap:
    if len(pmap[pn]) > 1:
      print '>>>>>>>>>>>>>>>>>>>>>>>>>>>', pn
      for val in pmap[pn]:
        print val, ' : ', len(pmap[pn][val])

if __name__ == "__main__":
  """
  xmls, igns = findXmls('/home/tianyin/conschk/app/hadoop-2.6.2-src-copy', '*site.xml')
  for xml in xmls:
    checkXml(xml)
  """
  #detectXmlDiffs('/home/tianyin/conschk/app/hadoop-2.6.2-src-copy')
  #detectValDiffs('/home/tianyin/conschk/app/hadoop-2.6.2-src-copy')
  for pname in aggrParamsInRepo('/home/tianyin/conschk/app/hadoop-2.6.2-src-copy'):
    print pname
