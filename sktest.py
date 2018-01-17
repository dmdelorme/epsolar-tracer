#import logging
#logging.basicConfig()
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.mei_message import *
ports = ['/dev/ttyXRUSB0','/dev/ttyXRUSB1']
for item in ports:
  client = ModbusClient(method = 'rtu', port = item, baudrate = 115200, timeout = 0.2 )
  client.connect()
  request = ReadDeviceInformationRequest(unit=1)
  response = client.execute(request)
  unitid = repr(response.information[1])
  unitid = unitid.strip('\'')
  result = client.read_input_registers(0x3100,12,unit=1)
  pvVolts = float(result.registers[0] *.01)
  pvAmps = float(result.registers[1] * .01)
  pL = result.registers[2]
  pH = result.registers[3]
  pvpower = float(((pH << 16)|pL))/100
  batVolts = float(result.registers[4] / 100.0)
  batchgAmps = float(result.registers[5] / 100.0)
  pL = result.registers[6]
  pH = result.registers[7]
  batchgpower = float(((pH << 16)|pL))/100

  ldVolts = float(result.registers[8] / 100.00)
  ldAmps = float(result.registers[9] / 100.00)
  pL = result.registers[10]
  pH = result.registers[11]
  ldpower = float(((pH << 16)|pL))/100

  ldnetAmps = batchgAmps-ldAmps

  result2 = client.read_input_registers(0x3110,1,unit=1)
  batTemp = float((result2.registers[0] / 100)+ 273.15)
  result2 = client.read_input_registers(0x311a,1,unit=1)
  soc = float(result2.registers[0] *.01)
  result = client.read_input_registers(0x3201,1,unit =1)
  chgeqstat = result.registers[0]
  mask = (1)
  chgrunning = chgeqstat & mask
  #print 'running:', bool(chgrunning)
  mask  = (1 << 2)
  chgfault = chgeqstat & mask
  #print 'chargerfault:',bool(chgfault)
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
  chargestate = chgstat
#  print 'charge stage:',chgstate,' :',chgstat
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
#  print 'Input volt status:',chgstate,' :',chgstat

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
  SignalK += ',{"path": "electrical.chargers.'+str(unitid)+'.mode","value":'+str(chargestate)+'}'
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
  #print (pvpower)
  #print (batchgpower)
  #print (ldpower)
  #print chargestate
  client.close()
  sock.close()

