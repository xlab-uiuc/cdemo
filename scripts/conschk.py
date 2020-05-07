def maxl(sl):
  maxlen = -1;
  for s in sl:
    if len(s) > maxlen:
      maxlen = len(s)
  return maxl

import sys

#print len(sys.argv)
#if len(sys.argv) <= 2:
#  print 'Input: logfile component'
#  sys.exit(-1) 

import log_anlyz
import xml_anlyz

xmlpmap = xml_anlyz.aggrParamsInRepo('/home/tianyin/conschk/app/hadoop-2.6.2-src-copy')
logpmap = log_anlyz.aggrParamsFromLogs('../plogs')
log_anlyz.checkIncons(logpmap)

phits = []
pmiss = []

for pname in xmlpmap:
#  if xmlpmap[pname] == '':
#    continue
  if pname not in logpmap:
    if pname not in pmiss:
      pmiss.append(pname)
    continue
  else:
    if pname not in phits:
      phits.append(pname)

    xmlv  = xmlpmap[pname]
    logvl = logpmap[pname]
 
    contains = False
    for logv in logvl:
      if logv == '0' and xmlv.lower() == 'false':
        contains = True
        break
      if logv == '1' and xmlv.lower() == 'true':
        contains = True
        break
      if logv.endswith('L') and logv[:-1] == xmlv:
        contains = True
        break
      if logv.endswith('F') and logv[:-1] == xmlv:
        contains = True
        break
      if logv.endswith('L') and xmlv.endswith('l') and logv[:-1] == xmlv[:-1]:
        contains = True
        break
      if logv.endswith('F') and xmlv.endswith('f') and logv[:-1] == xmlv[:-1]:
        contains = True
        break
      if logv.startswith('class "'):
        logv = logv.replace('class "', '')
        logv = logv[ : -1].replace('/', '.')
      if logv == xmlv:
        contains = True
        break
    if contains == False:
      print pname.ljust(25), ' : ', xmlv, '<>', str(logvl)
print 'hit: ', len(phits)
print 'miss:', len(pmiss)
     
for p in pmiss:
  print p
