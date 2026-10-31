# Levitas V3 — single-block KiCad project

Open **`Levitas3_Chip.kicad_pro`** in KiCad. The PCB and schematic have the same base filename and are linked as one project:

- `Levitas3_Chip.kicad_pcb`: copied from the PCB you supplied.
- `Levitas3_Chip.kicad_sch`: one **U1**, a single 40-pin block.
- `Levitas3.kicad_sym`: reusable **Levitas3:Levitas3_Chip_40Pin** symbol.
- `Levitas3.pretty/`: footprint extracted from the supplied PCB.
- `sym-lib-table` and `fp-lib-table`: project-local library registrations; keep them beside the project.
- `schematic_preview.png`: preview exported through KiCad.

## Pin layout and nets

Pins **1–20** run top-to-bottom on the left. Pins **40–21** run top-to-bottom on the right. There are no separate A/B/C/D units.

Pins **4 = ZS_XM_Q2** and **24 = ZS_XP_Q4** have their original electrode names. All 40 pins are passive electrode contacts; neither 4 nor 24 has a no-connect flag.

The schematic matches the supplied PCB's **exact 40 net names**, including `P04_ZS_XM_Q2` and `P24_ZS_XP_Q4`. Global labels preserve those names without adding a root-sheet slash. No net names use a test prefix. `Pxx_` identifies the existing pad-specific net and is deliberately retained.

The source PCB has separate nets for ground contacts and for contacts with the same electrode name. The schematic preserves that connectivity. Thus `P10_GND`, `P20_GND`, `P30_GND`, and `P40_GND` are not implicitly shorted together. Likewise, duplicate sensing names do not implicitly merge their PCB nets. Join or rename nets in the schematic when designing the rest of the circuit if those connections are desired, then update the PCB from the schematic.

## Board preservation and linking

The source was `Levitas3_40pad_KiCad_package/verification/levitas3_geometry_coupon.kicad_pcb`. A byte-identical source copy and its hash are retained under `source/`; the supplied file was not edited.

The new project PCB retains all original geometry, including its 40 pads, 40 escape tracks, cutout, outline, keepouts, placement, layer stack and existing net assignments. Only the library link, schematic instance path, pin function/type metadata and descriptive text were updated in the new copy. The board's U1 is linked to the single U1 schematic instance, so Update PCB from Schematic can recognize it without adding another chip.

The source PCB's project settings were copied. The 12 drive nets additionally use `Drive_50V`, with 0.60 mm clearance and 0.20 mm default routing width for the previously specified ±50 V drive range. Existing track widths were preserved.

## Verification

Checked with **KiCad 10.0.3**:

- One schematic unit; exactly 20 pins on each side.
- All 40 exported schematic pin-to-net assignments match the source PCB.
- No schematic/PCB parity issues and no footprint-library mismatch.
- No electrical-rule errors or PCB design-rule errors.
- 40 schematic warnings identify labels connected only to the chip, pending drive/readout circuitry.
- 40 PCB warnings identify the existing open escape-track ends.

The project is a chip carrier starting point; those open interfaces remain available for the rest of the circuitry. No checks were disabled to remove warnings. Detailed reports and an independent preservation check are in `verification/` and `verify_project.py`.

`prepare_project.py` and `build_schematic.py` record the creation process. Do not rerun them over later manual work without first preserving that work. The original PCB location is needed by the preparation script; it is not needed to open or edit this completed project.
