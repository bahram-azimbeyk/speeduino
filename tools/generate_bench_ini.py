"""Generate the bench8 definition without modifying the stock EEPROM pages."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
s=(root/'reference/speeduino.ini').read_text()
s=s.replace('signature      = "speeduino 202504-dev"','signature      = "speeduino 202504-levinbench8"')
s=s.replace('#unset enablehardware_test','#set enablehardware_test',1)
s=s.replace('nPages              = 15','nPages              = 16',1)
extra={'pageSize':'24','pageIdentifier':r'"\x00\x10"',
       'pageReadCommand':r'"N\x03%2o%2c"','pageValueWrite':r'"N\x04%2o%2c%v"',
       'pageChunkWrite':r'"N\x04%2o%2c%v"','crc32CheckCommand':r'"N\x05"','burnCommand':'""'}
s='\n'.join(line+', '+extra[line.strip().split('=')[0].strip()]
            if line.strip().split('=')[0].strip() in extra else line
            for line in s.splitlines())+'\n'
options=', '.join('"'+x+'"' for x in ['All physical (1-8)']+list(map(str,range(1,9)))+['Configured outputs only']+['INVALID']*6)
constants=f'''
page = 16
  benchChannel = bits, U16, 0, [0:3], {options}
  benchOpen = scalar, U16, 2, "ms", 0.001, 0, 0.100, 20.000, 3, noMsqSave, controllerPriority
  benchPeriod = scalar, U16, 4, "ms", 0.01, 0, 0.200, 500.000, 2, noMsqSave, controllerPriority
  benchCount = scalar, U16, 6, "pulses", 1, 0, 1, 65535, 0, noMsqSave, controllerPriority
  coilChannel = bits, U16, 8, [0:3], {options}
  coilDwell = scalar, U16, 10, "ms", 0.001, 0, 0.100, 5.000, 3, noMsqSave, controllerPriority
  coilPeriod = scalar, U16, 12, "ms", 0.01, 0, 10.000, 500.000, 2, noMsqSave, controllerPriority
  coilCount = scalar, U16, 14, "sparks", 1, 0, 1, 65535, 0, noMsqSave, controllerPriority
  idleBenchHome = scalar, U16, 16, "steps", 1, 0, 1, 765, 0, noMsqSave, controllerPriority
  idleBenchPosition = scalar, U16, 18, "steps", 1, 0, 0, 255, 0, noMsqSave, controllerPriority
  idleBenchDuty = scalar, U16, 20, "%", 1, 0, 0, 100, 0, noMsqSave, controllerPriority
  auxFrequency = scalar, U16, 22, "Hz", 0.1, 0, 1, 200, 1, noMsqSave, controllerPriority

'''
s=s.replace('[EventTriggers]',constants+'[EventTriggers]',1)
extensions='''
  noMsqSave = benchChannel
  noMsqSave = coilChannel
  controllerPriority = benchChannel
  controllerPriority = coilChannel
'''
for name,value in [('benchChannel',0),('benchOpen',1),('benchPeriod',100),('benchCount',100),
                   ('coilChannel',0),('coilDwell',2.5),('coilPeriod',100),('coilCount',100),
                   ('idleBenchHome',250),('idleBenchPosition',0),('idleBenchDuty',50),('auxFrequency',100)]:
    extensions+=f'  defaultValue = {name}, {value}\n'
s=s.replace('[ConstantsExtensions]','[ConstantsExtensions]\n'+extensions,1)
s=s.replace('subMenu = outputtest1, "Test Output Hardware"','''subMenu = injectorBench, "Injector Output Test"
        subMenu = coilBench, "Coil Output Test"
        subMenu = auxBench, "Auxiliary Output Test"
        subMenu = idleBench, "Idle Valve Output Test"''',1)
a=s.index('    dialog = outputtest_warningmessage,');b=s.index('    dialog = stm32cmd,',a)
s=s[:a]+s[b:]
s=re.sub(r'^\s*(?:cmdEnableTestMode|cmdStopTestMode|cmdtest(?:inj|spk)\w+)\s*=.*\n','',s,flags=re.M)
ui=[]
commands=[r'cmdBenchDisable = "N\x00"',r'cmdBenchStop = "N\x0B"',r'cmdBenchStart = "N\x01"',
          r'cmdCoilStart = "N\x07"',r'cmdPumpOn = "N\x08\x01"',r'cmdPumpOff = "N\x08\x00"',
          r'cmdIdleHome = "N\x09\x00"',r'cmdIdleRun = "N\x09\x01"',r'cmdIdleCycle = "N\x09\x02"']
def dialog(name,title,body,layout='yAxis'):
    ui.append(f'  dialog = {name}, "{title}", {layout}\n'+''.join('    '+line+'\n' for line in body))
def button(label,command,condition='1',close=False):
    return f'commandButton = "{label}", {command}, {{{condition}}}'+(', clickOnClose' if close else '')
def controls(name,kind):
    command=f'cmdEnable{kind}';commands.append(f'{command} = "N\\x0A\\x{kind:02X}"')
    dialog(name,'Test Mode Controls',[button('Enable Test Mode',command,'rpm == 0 && !benchOwned'+(' && idleBenchFeatureEnabled' if kind==4 else '')),
        button('Disable Test Mode','cmdBenchDisable','benchOwned',True)],'xAxis')
controls('injControls',1);controls('coilControls',2);controls('auxControls',3);controls('idleControls',4)
for name,title,gauge in [('benchDurationPanel','Duration','benchDurationGauge'),
                         ('benchInjectorPanel','Single injector','benchInjectorRpmGauge'),
                         ('benchAggregatePanel','All cylinders','benchAggregateRpmGauge')]:
    dialog(name,title,['gauge = '+gauge])
dialog('benchCalculations','Estimates for entered settings',['panel = benchDurationPanel','panel = benchInjectorPanel','panel = benchAggregatePanel'],'xAxis')
dialog('injSettings','Injector settings',['field = "Injector output", benchChannel','field = "Open time", benchOpen',
    'field = "Pulse period", benchPeriod','field = "Number of pulses", benchCount'])
dialog('injPump','Fuel Pump',[button('Fuel Pump On','cmdPumpOn','benchEnabled && benchKind == 1'),
    button('Fuel Pump Off','cmdPumpOff','benchEnabled && benchKind == 1')],'xAxis')
dialog('injActions','Injector test',[button('Start','cmdBenchStart','benchEnabled && benchKind == 1 && !benchRunning && benchSettingsValid'),
    button('Stop','cmdBenchStop','benchEnabled && benchKind == 1')],'xAxis')
dialog('injectorBench','Injector Output Test - RAM only',['panel = injControls','panel = injSettings','panel = injPump',
    'panel = injActions','panel = benchCalculations','gauge = benchStateGauge'])
dialog('coilDurationPanel','Duration',['gauge = coilDurationGauge'])
dialog('coilRpmPanel','One spark per engine cycle',['gauge = coilRpmGauge'])
dialog('coilCalculations','Estimates',['panel = coilDurationPanel','panel = coilRpmPanel'],'xAxis')
dialog('coilSettings','Coil settings',['field = "Coil output", coilChannel','field = "Charge time (dwell)", coilDwell',
    'field = "Pulse period", coilPeriod','field = "Number of sparks", coilCount'])
dialog('coilActions','Coil test',[button('Start','cmdCoilStart','benchEnabled && benchKind == 2 && !benchRunning && coilSettingsValid'),
    button('Stop','cmdBenchStop','benchEnabled && benchKind == 2')],'xAxis')
dialog('coilBench','Coil Output Test - RAM only',['panel = coilControls','panel = coilSettings','panel = coilActions','panel = coilCalculations','gauge = benchStateGauge'])
aux_outputs={0:('Fuel Pump',False),1:('Fan',True),2:('Boost',True),3:('VVT 1',True),4:('VVT 2',True),5:('WMI',True),6:('A/C compressor',False),7:('A/C fan',False),8:('Idle 1',True),9:('Idle 2',True)}
aux_conditions={0:'1',1:'fanEnable == 1 || fanEnable == 2',2:'boostEnabled',3:'vvtEnabled',4:'vvtEnabled && vvt2Enabled && !wmiEnabled',5:'wmiEnabled && !vvt2Enabled',6:'airConEnable',7:'airConEnable && airConFanEnabled',8:'iacAlgorithm == 2 || iacAlgorithm == 3 || iacAlgorithm == 6',9:'(iacAlgorithm == 2 || iacAlgorithm == 3 || iacAlgorithm == 6) && iacChannels'}
for target,(label,pwm) in aux_outputs.items():
    rows=[]
    for mode,title in [(0,'Off'),(1,'On')]+([(2,'50%')] if pwm else []):
        name=f'cmdAux{target}Mode{mode}'
        commands.append(f'{name} = "N\\x06\\x{target:02X}\\x{mode:02X}"')
        rows.append(button(title,name,'benchEnabled && benchKind == 3 && ('+aux_conditions[target]+')'))
    dialog(f'auxColumn{target}',label,rows)
dialog('auxRow0','Outputs',['panel = auxColumn'+str(t) for t in (0,1,2,3)],'xAxis')
dialog('auxRow1','Outputs',['panel = auxColumn'+str(t) for t in (4,5,6,7)],'xAxis')
dialog('auxIdleRow','Idle electrical outputs',['panel = auxColumn8','panel = auxColumn9'],'xAxis')
dialog('auxPulseSettings','Pulse Settings',['field = "Pulse frequency", auxFrequency'])
dialog('auxBench','Auxiliary Output Test',['panel = auxControls','panel = auxPulseSettings','panel = auxRow0','panel = auxRow1','panel = auxIdleRow','gauge = benchStateGauge'])
dialog('idleSettings','Idle valve settings',['field = "Homing steps", idleBenchHome, {idleBenchIsStepper}',
    'field = "Run position", idleBenchPosition, {idleBenchIsStepper}',
    'field = "PWM duty", idleBenchDuty, {idleBenchFeatureEnabled && !idleBenchIsStepper}'])
dialog('idleActions','Idle valve test',[
    button('Home / 0% duty','cmdIdleHome','benchEnabled && benchKind == 4 && !benchRunning && idleBenchHomeValid'),
    button('Run position / Duty','cmdIdleRun','benchEnabled && benchKind == 4 && !benchRunning && idleBenchValid'),
    button('In / Out cycle','cmdIdleCycle','benchEnabled && benchKind == 4 && !benchRunning && idleBenchValid'),
    button('Stop','cmdBenchStop','benchEnabled && benchKind == 4')])
dialog('idleValuePanel','Position / duty',['gauge = idleBenchValueGauge'])
dialog('idleStatePanel','Test state',['gauge = benchStateGauge'])
dialog('idleFeedback','Idle test',['panel = idleValuePanel','panel = idleStatePanel'],'xAxis')
dialog('idleBench','Idle Valve Output Test - engine stopped',['panel = idleControls','panel = idleSettings','panel = idleActions','panel = idleFeedback'])
s=s.replace('[UserDefined]','[UserDefined]\n'+'\n'.join(ui),1)
s=s.replace('[ControllerCommands]','[ControllerCommands]\n'+'\n'.join(commands)+'\n',1)
help_text=(root/'tools/bench_help.txt').read_text()
help_text=re.sub(r'^\s*auxTestLimit =.*\n','',help_text,flags=re.M)
help_text=help_text.replace('Physical injector output 1-8, independent of firing order or batch pairing. Only the selected output pulses.',
    'All physical (1-8) selects every output; Configured outputs only follows the actual engine scheduler routing, including paired and staged outputs. One output 1-8 can also be selected. A conflict rejects the whole test before any pulse. Count is per selected output. Enable Test Mode first.')
help_text=help_text.replace('Physical ignition output 1-8.', 'All physical (1-8) selects every output; Configured outputs only follows actual ignition routing, including wasted COP and single-coil mode. One output 1-8 can also be selected. Any conflict rejects the whole test. Count is per selected coil. Enable Test Mode first.')
help_text=help_text.replace('Only the selected coil is charged.', 'The selected coil(s) are charged together.')
help_text=help_text.replace('Stop / Release','Disable').replace('Press Stop or Disable before restarting.', 'Stop ends the current test; Disable releases ECU control.')
help_text+='''
  auxFrequency = "Frequency shared by all pulsed auxiliary outputs, 1.0-200.0 Hz. Enter a value then press 50% to apply it. Tests require the corresponding feature enabled in the tune. WMI uses the VVT2 PWM pin plus its WMI enable output; WMI and VVT2 tests are mutually exclusive. Outputs can be combined; Off affects only its own output. There is no 30-second limit. Duty is fixed at 50%. Timing resolution is 1 ms, so fractional periods alternate between adjacent millisecond lengths. Idle 1/2 are independent electrical pin tests: On means HIGH, Off means LOW, 50% uses this frequency. Idle 2 requires dual-channel PWM idle. These are not stepper coils. Pump and A/C outputs are On/Off only. Use an appropriate frequency for the connected load. Disable, closing the window, trigger activity or loss of communication stops every test output."
'''
s=s.replace('[SettingContextHelp]','[SettingContextHelp]\n'+help_text,1)
s=s.replace('[OutputChannels]','''[OutputChannels]
  benchKindBits = bits, U08, 39, [0:1]
  benchKind = { benchKindBits + 1 }
  benchOwned = bits, U08, 39, [2:2]
  benchRunning = bits, U08, 39, [3:3]
  benchComplete = bits, U08, 39, [4:4]
  benchFault = bits, U08, 39, [5:5]
  benchEnabled = bits, U08, 39, [6:6]
  benchState = { benchFault ? 3 : (benchComplete ? 2 : (benchRunning ? 1 : 0)) }
  benchSettingsValid = { benchPeriod >= benchOpen + 0.100 && benchPeriod <= 500 && benchPeriod * benchCount <= 120000 }
  benchDuration = { (1 + (benchCount - 1) * benchPeriod + benchOpen) / 1000.0 }
  benchInjectorRpm = { benchPeriod > 0 ? (twoStroke == 1 ? 60000.0 : 120000.0) / benchPeriod : 0 }
  benchAggregateRpm = { nCylinders > 0 ? benchInjectorRpm / nCylinders : 0 }
  coilSettingsValid = { coilPeriod >= 10 && coilDwell <= 5 && coilPeriod > coilDwell && coilPeriod <= 500 && coilPeriod * coilCount <= 120000 }
  coilDuration = { (1 + (coilCount - 1) * coilPeriod + coilDwell) / 1000.0 }
  coilRpm = { coilPeriod > 0 ? (twoStroke == 1 ? 60000.0 : 120000.0) / coilPeriod : 0 }
  idleBenchFeatureEnabled = { iacAlgorithm >= 2 && iacAlgorithm <= 7 }
  idleBenchIsStepper = { iacAlgorithm == 4 || iacAlgorithm == 5 || iacAlgorithm == 7 }
  idleBenchHomeValid = { idleBenchIsStepper ? (idleBenchHome > 0 && iacStepTime > 0) : (iacAlgorithm == 2 || iacAlgorithm == 3 || iacAlgorithm == 6) }
  idleBenchValid = { idleBenchHomeValid && (!idleBenchIsStepper || (idleBenchPosition < idleBenchHome && idleBenchPosition <= iacMaxSteps)) }
  idleBenchRaw = scalar, U08, 38, "", 1, 0
  idleBenchValue = { benchOwned && benchKind == 4 ? idleBenchRaw : 0 }
''',1)
s=s.replace('[GaugeConfigurations]','''[GaugeConfigurations]
  benchDurationGauge = benchDuration, "Test duration", "s", 0, 120, -1, -1, 120, 120, 3, 3
  benchInjectorRpmGauge = benchInjectorRpm, "RPM: one pulse/cycle/injector", "RPM", 0, 30000, -1, -1, 600000, 600000, 0, 0
  benchAggregateRpmGauge = benchAggregateRpm, "RPM: all-cylinder event rate", "RPM", 0, 15000, -1, -1, 600000, 600000, 0, 0
  coilDurationGauge = coilDuration, "Test duration", "s", 0, 120, -1, -1, 120, 120, 3, 3
  coilRpmGauge = coilRpm, "RPM: one spark per cycle", "RPM", 0, 12000, -1, -1, 12000, 12000, 0, 0
  idleBenchValueGauge = idleBenchValue, "Position (steps) / duty (%)", "", 0, {idleBenchIsStepper ? 255 : 100}, -1, -1, 256, 256, 0, 0
  benchStateGauge = benchState, "0 ready / 1 run / 2 done / 3 fault", "", 0, 3, -1, -1, 2.5, 2.5, 0, 0
''',1)
s=re.sub(r'^\s*testenabled\s*=.*$', '  testenabled = { benchEnabled }',s,flags=re.M)
s=re.sub(r'^\s*testactive\s*=.*$', '  testactive = { benchRunning }',s,flags=re.M)
(root/'reference/levin-bench.ini').write_text(s,encoding='utf-8')
print('Generated reference/levin-bench.ini (bench8)')
