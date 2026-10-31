"""Single-unit 40-pin chip schematic, derived from the supplied PCB's net map."""
from pathlib import Path
import json
import uuid

OUT=Path(__file__).resolve().parent
Q=lambda s:json.dumps(str(s),ensure_ascii=False)
UID=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'levitas3-singleblock-project/'+s))
fmt=lambda n:f'{n:.4f}'.rstrip('0').rstrip('.') if n else '0'


def effects(size=1.27,hide=False,justify=''):
    return f'(effects (font (size {size} {size}))'+(f' (justify {justify})' if justify else '')+(' (hide yes)' if hide else '')+')'


def prop(name,value,x=0,y=0,hide=False):
    return f'(property {Q(name)} {Q(value)} (at {fmt(x)} {fmt(y)} 0) {effects(hide=hide)})'


def pos(pin):
    # Conventional 40-pin ordering: 1..20 down left; 40..21 down right.
    left=pin<=20
    index=pin-1 if left else 40-pin
    return (-35.56 if left else 35.56),round(36.83-index*3.81,4),0 if left else 180


def library(m,qualified=False):
    name=m['symbol']
    block=[f'(symbol {Q("Levitas3:"+name if qualified else name)} (pin_names (offset 1.27)) (exclude_from_sim yes) (in_bom yes) (on_board yes)',
           prop('Reference','U',0,46.99),prop('Value',m['value'],0,44.45),
           prop('Footprint',m['footprint'],hide=True),prop('Datasheet','',hide=True),
           prop('Description','Levitas V3 chip; one 40-pin block; names and nets from supplied PCB',hide=True),
           prop('ki_fp_filters',m['footprint'].split(':')[1],hide=True),
           f'(symbol "{name}_0_1" (rectangle (start -30.48 41.91) (end 30.48 -40.64) (stroke (width .254) (type default)) (fill (type background)))',
           f'(text "LEVITAS V3" (at 0 2.54 0) {effects(2.032)}) (text "40 ELECTRODES" (at 0 -1.27 0) {effects(1.016)}))',
           f'(symbol "{name}_1_1"']
    for row in m['pins']:
        x,y,angle=pos(row['pin'])
        block.append(f'(pin passive line (at {fmt(x)} {fmt(y)} {angle}) (length 5.08) (name {Q(row["function"])} {effects(1.016)}) (number "{row["pin"]}" {effects(1.016)}))')
    block.extend([')',')'])
    return '\n'.join(block)


def main():
    m=json.loads((OUT/'source/pcb_pin_map.json').read_text())
    name=m['symbol'];project=m['project']
    (OUT/'Levitas3.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "levitas3_project")\n'+library(m)+'\n)\n')
    cx,cy=148.59,97.79
    sch=[f'(kicad_sch (version 20231120) (generator "levitas3_project") (uuid "{m["sheet_uuid"]}") (paper "A4")',
         '(title_block (title "Levitas V3 - 40-pin chip") (date "2026-10-29") (rev "1.0") (comment 1 "Schematic matched to supplied PCB"))',
         '(lib_symbols',library(m,True),')']
    def note(text,x,y,size=1.27):
        sch.append(f'(text {Q(text)} (at {x} {y} 0) {effects(size,justify="left")} (uuid "{UID(text)}"))')
    note('LEVITAS V3 | 40-PIN CHIP',20.32,17.78,2.54)
    note('One U1, one footprint. Net names and pad connections follow the supplied PCB.',20.32,25.4)
    sch.extend([f'(symbol (lib_id "Levitas3:{name}") (at {cx} {cy} 0) (unit 1) (exclude_from_sim yes) (in_bom yes) (on_board yes) (dnp no) (uuid "{m["symbol_uuid"]}")',
                prop('Reference','U1',cx,cy-48.26),prop('Value',m['value'],cx,cy-45.72),
                prop('Footprint',m['footprint'],cx,cy,True),prop('Datasheet','',cx,cy,True)])
    for row in m['pins']:sch.append(f'(pin "{row["pin"]}" (uuid "{UID("pin"+str(row["pin"]))}"))')
    sch.append(f'(instances (project "{project}" (path "/{m["sheet_uuid"]}" (reference "U1") (unit 1)))) )')
    for row in m['pins']:
        pin=row['pin'];px,py,angle=pos(pin)
        x,y=round(cx+px,4),round(cy-py,4)
        end=round(x+(-15.24 if pin<=20 else 15.24),4)
        sch.append(f'(wire (pts (xy {fmt(end)} {fmt(y)}) (xy {fmt(x)} {fmt(y)})) (stroke (width .1524) (type default)) (uuid "{UID("wire"+str(pin))}"))')
        # Global labels preserve exact PCB net names, without a root-sheet slash.
        sch.append(f'(global_label {Q(row["net"])} (shape passive) (at {fmt(end)} {fmt(y)} {angle}) {effects(1.016,justify="right" if pin<=20 else "left")} (uuid "{UID("label"+str(pin))}") {prop("Intersheetrefs","${INTERSHEET_REFS}",end,y,True)})')
    note('PCB MATCH',20.32,153.67,1.524)
    note('Pins 4 and 24 restored: ZS_XM_Q2 and ZS_XP_Q4. All 40 pins are passive electrode contacts.',20.32,159.0,1.016)
    note('The Pxx_ prefix preserves each existing PCB net. Ground and duplicate electrodes remain separate nets.',20.32,164.08,1.016)
    note('Drive range: -50 V to +50 V. Existing board geometry, cutout and routing are retained.',20.32,169.16,1.016)
    note('Add drive/readout circuitry as needed. No no-connect flags are placed on the chip.',20.32,174.24,1.016)
    sch.extend(['(sheet_instances (path "/" (page "1")))',')'])
    (OUT/(project+'.kicad_sch')).write_text('\n'.join(sch)+'\n')
    print('Created one symbol unit with 20 left pins and 20 right pins; all 40 exact PCB nets.')


if __name__=='__main__':main()
