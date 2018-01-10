#import logging
#logging.basicConfig()
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)
from datetime import *
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.mei_message import *
#import subprocess
ports = ['/dev/ttyXRUSB0','/dev/ttyXRUSB1']
#output = subprocess.check_output(['ls','/dev/tty*'])
#print output

for item in ports:
  print len(ports)
  #port = item
  print item 
  client = ModbusClient(method = 'rtu', port = item, baudrate = 115200, timeout = 0.2)
  client.connect()
  request = ReadDeviceInformationRequest(unit=1)
  response = client.execute(request)
  unitid = repr(response.information[1])
  unitid = unitid.strip('\'')
  print unitid
  #print client.connect()
  result = client.read_input_registers(0x3100,12,unit=1)
  #print result
  pvVolts = float(result.registers[0] *.01)
  pvAmps = float(result.registers[1] * .01)
  #pL = 0x93E0
  #pH = 0x0004
  pL = result.registers[2]
  pH = result.registers[3]
  pvpower = float(((pH << 16)|pL))/100
  batVolts = float(result.registers[4] / 100.0)
  batchgAmps = float(result.registers[5] / 100.0)
  pL = result.registers[6]
  pH = result.registers[7]
  batchgpower = float (((pH << 16)|pL))/100
  ldVolts = float(result.registers[8] / 100.00)
  ldAmps = float(result.registers[9] / 100.00)
  pL = result.registers[10]
  pH = result.registers[11]
  ldpower = float(((pH << 16)|pL))/100

  ldnetAmps = batchgAmps-ldAmps
  result = client.read_input_registers(0x3304,2,unit =1)
  pL = result.registers[0]
  pH = result.registers[1]
  powerconsumedtoday = float (((pH << 16)|pL))*10
  print 'power consumed: ', powerconsumedtoday

  result = client.read_input_registers(0x330C,2,unit =1)
  #pL = 0x93E0
  #pH = 0x0004
  pL = result.registers[0]
  pH = result.registers[1]
  powerintoday = float ((pH << 16)|pL) * 10
  print 'power generated: ', powerintoday

  result = client.read_input_registers(0x3201,1,unit =1)
  chgeqstat = result.registers[0]
  mask = (1)
  chgrunning = chgeqstat & mask
  print 'running:', bool(chgrunning)
  mask  = (1 << 2)
  chgfault = chgeqstat & mask
  print 'chargerfault:',bool(chgfault)
  mask = (3 << 2)
  chgstat = chgeqstat & mask
  chgstat = chgstat >> 2
  if chgstat == 0:
    chgstate = "Off"
  elif chgstat == 1:
    chgstate = "float"
  elif chgstat == 2:
    chgstate = "Boost"
  elif chgstat == 3:
    chgstate = "Equilzation" 
  else:
    chgstate = "Unknown"
  print 'charge stage:',chgstate,' :',chgstat
  mask = (15 << 2)
  chgstat = chgeqstat & mask
  chgstat = chgstat >> 2
  if chgstat == 0:
    chgstate = "Normal"
  elif chgstat == 1:
    chgstate = "No Power Connected"
  elif chgstat == 2:
    chgstate = "high Volt Input"
  elif chgstat == 3:
    chgstate = "Input volt error "
  else:
    chgstate = "Unknown"
  print 'Input volt status:',chgstate,' :',chgstat

  result = client.read_input_registers(0x3008,1,unit =1) 
  chargemode = result.registers[0]
  if chargemode == 0:
    chargemode = 'connect/disconnect'
  elif chargemode == 1:
    chargemode = 'PWM'
  elif chargemode == 2:
    chargemode = 'mppt'
  else:
    chargemode = 'error'
  print 'charging mode: ', chargemode 
  result2 = client.read_input_registers(0x3110,1,unit=1)
  batTemp = float((result2.registers[0] / 100)+ 273.15)
  result2 = client.read_input_registers(0x311a,1,unit=1)
  soc = float(result2.registers[0] *.01)

# battery charging registers read and write
  result = client.read_holding_registers(0x9000,10,unit=1)
  #print result.registers
  battype = (result.registers[0])
  if battype == 0:
    battype = 'User defined'
  elif battype == 1:
    battype = 'Sealed'
  elif battype == 2:
    battype = 'GEL'
  elif battype == 3:
    battype = 'Flooded'
  else:
    battype = 'error'

  batcapacity = (result.registers[1])
  battempcomp = (result.registers[2])/100
  highvoltdisconnect = float(result.registers[3]) / 100
  chargelimitvolt = float(result.registers[4])/100
  overvoltreconnect = float(result.registers[5])/100
  equalizevolt = float(result.registers[6])/100
  boostvolt = float(result.registers[7])/100
  floatvolt = float(result.registers[8])/100
  boostreconnectvolt = float(result.registers[9])/100
  print 'battype', battype
  print 'batcapacity', batcapacity
  print 'battempcomp', battempcomp
  print 'highvoltdisconnect', highvoltdisconnect
  print 'chargelimitvolt', chargelimitvolt
  print 'overvoltreconnect', overvoltreconnect
  print 'equalizevolt', equalizevolt
  print 'boostvolt', boostvolt
  print 'floatvolt', floatvolt
  print 'boostreconnectvolt', boostreconnectvolt

#####read clock
  result = client.read_holding_registers(0x9013,3,unit=1)
  secmin = result.registers[0]
  secs = float(secmin & 0xff)
  minuits = secmin >> 8
  hrday = result.registers[1]
  hr = (hrday & 0xff)
  day = hrday >> 8
  monthyear = result.registers[2]
  month = (monthyear & 0xff)
  year = monthyear >> 8




  print year,'/',month,'/',day, hr,':',minuits,':',secs



#print (chgstat)
#print 'send'
  import socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  SignalK = '{"updates": [{"source": {"type": "solar","src" : "epsolar"},"values":['
  SignalK += '{"path": "electrical.solar.'+str(unitid)+'.voltage","value":'+str(round(batVolts, 2))+'}'
  SignalK += ',{"path": "electrical.solar.'+str(unitid)+'.current","value":'+str(batchgAmps)+'}'
  SignalK += ',{"path": "electrical.solar.'+str(unitid)+'.power","value":'+str(batchgpower)+'}'
  SignalK += ',{"path": "electrical.solar.'+str(unitid)+'.panelVoltage","value":'+str(round(pvVolts,2))+'}'
  SignalK += ',{"path": "electrical.solar.'+str(unitid)+'.panelCurrent","value":'+str(pvAmps)+'}'
  SignalK += ',{"path": "electrical.solar.'+str(unitid)+'.panelpower","value":'+str(pvpower)+'}'
  SignalK += ',{"path": "electrical.solar.'+str(unitid)+'.loadVoltage","value":'+str(ldVolts)+'}'
  SignalK += ',{"path": "electrical.solar.'+str(unitid)+'.loadCurrent","value":'+str(ldAmps)+'}'
  SignalK += ',{"path": "electrical.solar.'+str(unitid)+'.loadPower","value":'+str(ldpower)+'}'
  SignalK += ',{"path": "electrical.chargers.'+str(unitid)+'.loadnet.current","value":'+str(ldnetAmps)+'}'
  SignalK += ',{"path": "electrical.batteries.'+str(unitid)+'.temperature","value":'+str(batTemp)+'}'
  SignalK += ',{"path": "electrical.batteries.'+str(unitid)+'.capacity.stateOfCharge","value":'+str(soc)+'}'
  SignalK += ']}]}\n'
  sock.sendto(SignalK, ('localhost', 55559))
  #print (pvVolts)
  #print pvAmps
  #print result2.registers[0]/100
  #print batteryAmps
  #print (batVolts)
  #print (batTemp)
  print 'pvpower',pvpower
  print 'batpower',batchgpower
  print 'ldpower',ldpower
  sock.close()
  client.close()
