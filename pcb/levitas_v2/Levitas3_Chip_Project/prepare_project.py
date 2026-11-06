"""Run with KiCad's Python to copy the supplied PCB and link it to the new schematic.
Only schematic/library identity and pin-function metadata are changed in the copy.
"""
from pathlib import Path
import hashlib
import json
import shutil
import uuid
import re
import pcbnew as k

OUT=Path(__file__).resolve().parent
SOURCE=OUT.parent/'Levitas3_40pad_KiCad_package/verification/levitas3_geometry_coupon.kicad_pcb'
PROJECT='Levitas3_Chip'
SYMBOL='Levitas3_Chip_40Pin'
FP='Levitas3_Chip_40Pad_Wirebond'
uid=lambda text:str(uuid.uuid5(uuid.NAMESPACE_URL,'levitas3-singleblock-project/'+text))


def main():
    (OUT/'source').mkdir(exist_ok=True)
    (OUT/'verification').mkdir(exist_ok=True)
    lib=OUT/'Levitas3.pretty';lib.mkdir(exist_ok=True)
    original=SOURCE.read_bytes()
    (OUT/'source'/SOURCE.name).write_bytes(original)
    b=k.LoadBoard(str(SOURCE))
    fps=list(b.GetFootprints())
    assert len(fps)==1
    fp=fps[0]
    assert fp.GetReference()=='U1'
    pads=sorted(fp.Pads(),key=lambda p:int(p.GetNumber()))
    assert [int(p.GetNumber()) for p in pads]==list(range(1,41))
    info=[]
    for p in pads:
        name=p.GetNetname()
        assert name
        function=re.sub(r'^P\d+_', '', name)
        info.append({'pin':int(p.GetNumber()),'net':name,'function':function,'pin_type':'passive'})
    # Store all source geometry in a portable text snapshot for independent checking.
    manifest={'source_file':str(SOURCE),'source_sha256':hashlib.sha256(original).hexdigest(),
              'project':PROJECT,'symbol':SYMBOL,'footprint':'Levitas3:'+FP,
              'reference':fp.GetReference(),'value':fp.GetValue(),'pins':info,
              'sheet_uuid':uid('sheet'),'symbol_uuid':uid('U1'),
              'track_count':len(list(b.GetTracks())),'copper_layers':b.GetCopperLayerCount()}
    (OUT/'source/pcb_pin_map.json').write_text(json.dumps(manifest,indent=2)+'\n')
    fp.SetFPIDAsString('Levitas3:'+FP)
    fp.SetLibDescription('Levitas V3 chip, 40 separate wire-bond pads. Pins 4 and 24 restored as sensing electrodes. Geometry and net names copied from the supplied PCB. No solder paste.')
    path=k.KIID_PATH()
    path.push_back(k.KIID(manifest['sheet_uuid']));path.push_back(k.KIID(manifest['symbol_uuid']))
    fp.SetPath(path)
    for p,row in zip(pads,info):
        p.SetPinFunction(row['function']);p.SetPinType('passive')
    assert k.SaveBoard(str(OUT/(PROJECT+'.kicad_pcb')),b)
    copy=k.FOOTPRINT(fp)
    copy.SetPosition(k.VECTOR2I(0,0))
    for p in copy.Pads():p.SetNetCode(0)
    k.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib),copy)
    assert (lib/(FP+'.kicad_mod')).is_file()
    pro=json.loads(SOURCE.with_suffix('.kicad_pro').read_text())
    pro['meta']['filename']=PROJECT+'.kicad_pro'
    classes=pro.setdefault('net_settings',{}).setdefault('classes',[])
    if not any(c['name']=='Drive_50V' for c in classes):
        classes.append({'name':'Drive_50V','description':'Drive range -50 to +50 V, up to 100 V differential',
                        'clearance':.6,'track_width':.2,'via_diameter':.6,'via_drill':.3})
    # Keep original project settings; add exact-name classes for drive nets only.
    patterns=pro['net_settings'].setdefault('netclass_patterns',[])
    patterns.extend({'netclass':'Drive_50V','pattern':r['net']} for r in info if r['function'].startswith(('XD_','YD_','ZD_')))
    (OUT/(PROJECT+'.kicad_pro')).write_text(json.dumps(pro,indent=2)+'\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "Levitas3") (type "KiCad") (uri "${KIPRJMOD}/Levitas3.pretty") (options "") (descr "Footprint extracted from supplied PCB")))\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Levitas3") (type "KiCad") (uri "${KIPRJMOD}/Levitas3.kicad_sym") (options "") (descr "Single 40-pin chip block")))\n')
    assert SOURCE.read_bytes()==original
    print(json.dumps({'pads':len(info),'tracks':manifest['track_count'],'source_unchanged':True,'path':fp.GetPath().AsString()},indent=2))


if __name__=='__main__':main()
