def normalize(val):
  if val == None:
    return ''
  if val == 'null':
    return ''
  if val == 'None':
    return ''
  if val.strip() == '':
    return ''
  if val.startswith('\"') and val.endswith('\"'):
    val = val[1 : ]
    val = val[ : -1]
  res = ''
  if res.startswith('class "'):
    res = val.replace('class "', '')
    res = res[ : -1].replace('/', '.')
    return res
  elif val.lower().endswith('f') or val.lower().endswith('l'):
    res = val[ : -1]
    try:
      float(res) #for both float and int
      return res
    except ValueError:
      return val
  else:
    return val
