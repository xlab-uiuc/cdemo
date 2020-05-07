import os
import shutil
import utils

def log_anlyz(logf):
  tcnt = 0
  fcnt = 0
  pmap = {}
  """
  The format is as follows:
  L1: flag
  L2: class
  L3: caller method
  L4: callee method
  L5: argument list
  L6: blank (should skip)
  """
  f = open(logf, 'r')
  for l in f:
    if l.strip() == 'F':
      fcnt += 1
    elif l.strip() == 'T':
      tcnt += 1
    dclass = f.next().strip()
    method = f.next().strip()
    getter = f.next().strip()
    arglst = f.next().strip().split('\t')
    blank = f.next() 
    #if len(arglst) > 2:
    #  print '[ERROR] TOO MANY ARGS: ', arglst
    if len(arglst) == 1:
      #print '[ERROR] NO ARGS: ', getter, arglst
      continue
    param = arglst[0]
    defvl = arglst[1]
    defvl = utils.normalize(defvl)
    if param.startswith('\"') and param.endswith('\"'):
      param = param.replace('\"', '')
      if param not in pmap:
        pmap[param] = []
      pmap[param].append(defvl)
#      if param in pmap and pmap[param] != defvl:
#        print '[ERROR] DIFF DEF IN CODE', param, defvl, '<>', pmap[param]
#      else:
#        pmap[param] = defvl
    else:
      print '[ERROR] INVALID PARAM: ', arglst
  print logf, ' | tcnt/fcnt: ', str(tcnt) + '/' + str(fcnt)
  return pmap

def aggrParamsFromLogs(logdir):
  aggrmap = {}
  for log in os.listdir(logdir):
    pmap = log_anlyz(os.path.join(logdir, log))
    for pname in pmap:
      if pname not in aggrmap:
        aggrmap[pname] = []
      for pval in pmap[pname]:
        if pval not in aggrmap[pname]:
          aggrmap[pname].append(pval)
  return aggrmap
      

def checkIncons(pmap):
  for pname in pmap:
    if len(pmap[pname]) > 1:
      print '[ERROR] DIFF DEF IN CODE:', pname, ' | ', pmap[pname]

if __name__ == "__main__":
  #checkIncons(log_anlyz('../p.hdfs-dn.log'))
  checkIncons(aggrParamsFromLogs('../plogs'))
