"""Check source PCB preservation and all 40 native KiCad-exported connections."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent
m=json.loads((OUT/'source/pcb_pin_map.json').read_text())
source=OUT/'source/levitas3_geometry_coupon.kicad_pcb'
assert hashlib.sha256(source.read_bytes()).hexdigest()==m['source_sha256']
assert hashlib.sha256(Path(m['source_file']).read_bytes()).hexdigest()==m['source_sha256']


def without_link_metadata(text):
    text=text.replace('(footprint "Levitas3:Levitas3_Chip_40Pad_Wirebond"',
                      '(footprint "Levitas3_Chip_40Pad_Wirebond"')
    return '\n'.join(line for line in text.splitlines()
                     if not re.match(r'^\s*\((?:descr|path|pinfunction|pintype)\b',line))


assert without_link_metadata(source.read_text())==without_link_metadata((OUT/'Levitas3_Chip.kicad_pcb').read_text()),'PCB geometry or net data changed'
xml=ET.parse(OUT/'verification/netlist.xml').getroot()
components=xml.findall('components/comp')
assert len(components)==1 and components[0].get('ref')=='U1'
assert components[0].findtext('value')==m['value']
assert components[0].findtext('footprint')==m['footprint']
units=components[0].findall('units/unit')
assert len(units)==1
assert sorted(int(p.get('num')) for p in units[0].findall('pins/pin'))==list(range(1,41))
expected={str(r['pin']):r['net'] for r in m['pins']}
actual={}
for net in xml.findall('nets/net'):
    nodes=net.findall('node')
    assert len(nodes)==1
    node=nodes[0]
    assert node.get('ref')=='U1' and node.get('pintype')=='passive'
    actual[node.get('pin')]=net.get('name')
assert actual==expected
sym=(OUT/'Levitas3.kicad_sym').read_text()
assert len(re.findall(r'\(pin passive line \(at -35\.56 ',sym))==20
assert len(re.findall(r'\(pin passive line \(at 35\.56 ',sym))==20
assert '(no_connect' not in (OUT/'Levitas3_Chip.kicad_sch').read_text()
drc=json.loads((OUT/'verification/drc.json').read_text())
erc=json.loads((OUT/'verification/erc.json').read_text())
e=[v for s in erc['sheets'] for v in s['violations']]
assert len(e)==40 and all(v['severity']=='warning' and v['type']=='isolated_pin_label' for v in e)
assert len(drc['violations'])==40 and all(v['severity']=='warning' and v['type']=='track_dangling' for v in drc['violations'])
assert not drc['unconnected_items'] and not drc['schematic_parity']
result={'kicad_version':drc['kicad_version'],'source_sha256':m['source_sha256'],
        'source_file_unchanged':True,'pcb_geometry_and_nets_identical':True,
        'permitted_copy_changes':['footprint library link','schematic instance path','pin function/type metadata','description'],
        'symbol_units':1,'left_pins':20,'right_pins':20,'pin_to_net_matches':40,
        'restored_pins':{'4':'ZS_XM_Q2','24':'ZS_XP_Q4'},
        'erc_errors':0,'erc_warnings':40,'erc_warning_type':'isolated_pin_label',
        'drc_errors':0,'drc_warnings':40,'drc_warning_type':'track_dangling',
        'schematic_parity_issues':0,'library_mismatch_issues':0}
(OUT/'verification/summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
