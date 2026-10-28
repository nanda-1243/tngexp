"""MagPress M4 Rev E assembly manual: step images (from the 3D assembly), Markdown and PDF.

python3 docs/assembly/manual.py            # render images, write docs/assembly-manual.md and the PDF in release/RevE/
python3 docs/assembly/manual.py --no-render  # text only (reuse the existing images)

Needs Node with Playwright (Chromium). The step images come from models/assembly/MagPress-M4_assembly.glb,
so build the models first (models/build_models.py).
"""
import csv
import html
import json
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
GLB = os.path.join(ROOT, 'models', 'assembly', 'MagPress-M4_assembly.glb')
IMG = os.path.join(HERE, 'img')
MD_OUT = os.path.join(ROOT, 'docs', 'assembly-manual.md')
PDF_OUT = os.path.join(ROOT, 'release', 'RevE', 'MagPress-M4_Assembly-Manual_RevE.pdf')

NAMES, FILES = {}, {}
with open(os.path.join(ROOT, 'models', 'parts.csv')) as f:
    for r in csv.DictReader(f):
        NAMES[r['id']] = r['name']
        FILES[r['id']] = r['file_base']


def glb_nodes(path):
    with open(path, 'rb') as f:
        f.read(12)
        n, _ = struct.unpack('<II', f.read(8))
        doc = json.loads(f.read(n))
    return [nd['name'] for nd in doc['nodes'] if 'name' in nd and 'mesh' in nd]


NODES = glb_nodes(GLB)


def I(pid, *nums):
    """instance names of a part (all, or the given 1-based instance numbers)."""
    out = [n for n in NODES if n.rsplit('_', 1)[0] == pid]
    if nums:
        out = ['%s_%d' % (pid, k) for k in nums]
    assert out, pid
    return out


def G(ex, *items, row=None, label='auto'):
    """a group of parts that moves together in the picture. items: part ids or (pid, nums...) tuples."""
    names = []
    for it in items:
        names += I(it) if isinstance(it, str) else I(it[0], *it[1:])
    return {'names': names, 'ex': list(ex), 'row': row, 'label': label}


V_ISO = (-0.55, -0.80, 0.45)
V_HIGH = (-0.45, -0.62, 0.65)
V_LOW = (-0.55, -0.80, 0.08)
V_BELOW = (-0.55, -0.72, -0.42)
V_RIGHT = (0.55, -0.80, 0.42)
UP = 'from below'

# =====================================================================================
# the steps
# =====================================================================================
CHANGES = [
    ('Size kits', 'Sharp R1 corners. Stroke 1 folds a flat tin blank (X + 12, corners clipped 45°) round a taller 23 mm pedestal; ring A has a 0.6 mm recess for the blank, photo and film. The crimp anvil folds the edge twice, flat, under the back plate: a two-layer hem with the cut tin edge hidden. Round kits keep the Rev D rolled edge.', 17),
    ('Upper die MP-201, springs', 'Die body 20 thick with a Ø54 counterbore for the holder; 8 red Ø12.5 × 44 springs (1.6 kN) hold the upper ring while the tin folds.', 15),
    ('Plug locking pin', 'A Ø6 detent pin along the die body from the left end (the Rev D cross pin was blocked by the front column).', 18),
    ('Crown MP-108, handle stop', 'Crown 120 wide (was 80). The handle stop is on its own post MP-121 on the crown, not in the column top.', 12),
    ('Return springs', 'POM guide sleeves on the rods.', 12),
    ('Screws, pads, pilot', 'Rail and keeper screws M5 × 30, station-base screws M5 × 20 into tapped-through bases; six pads; Ø10 station pilot in tough steel.', 3),
]

TABLE = ['MP-105', 'MP-205', 'BUY-40', 'BUY-41', 'BUY-32']
RAM = ['MP-109', 'BUY-13', 'MP-110', ('BUY-16', 2), 'BUY-27', 'MP-111', 'BUY-28', 'BUY-29', 'MP-120', 'MP-118', 'BUY-23']
CROWN = ['MP-108', 'BUY-26', 'MP-112', 'BUY-14', 'BUY-25', 'BUY-24']
LEVER = ['MP-113', 'BUY-15', ('BUY-16', 1), 'BUY-30']
UPPER = ['MP-201', 'MP-202', 'BUY-42', 'BUY-34', 'MP-210', ('BUY-37', 5, 6), 'BUY-38', 'BUY-35']
K = '6363'
PSI_DIR = (0, -0.4236, 0.9058)

STEPS = [
    # ------------------------------------------------------------------ A
    dict(part='A', title='Prepare the base plate', view=V_ISO, frame='all', install=True,
         add=[G((0, 0, 0), 'MP-101')],
         tools='Straightedge, feeler gauges, bore gauge, two wooden bearers about 50 mm high',
         do=['Deburr and clean the plate. Check the counterbores C1/C2 (Ø33 × 8.5) are on the underside and the tongue is at the front.',
             'Check flatness of the slide area (X ±230 × Y ±75): 0.05 mm with a straightedge and feelers.',
             'Check the column holes C1/C2: Ø20 H7, 210.00 ±0.01 apart.',
             'Put the plate on two wooden bearers for the rest of the build, so you can reach the screws underneath.'],
         check='Flat within 0.05 mm under the die table; column holes to size and position.'),
    dict(part='A', title='Columns', view=(-0.6, -0.78, 0.15), frame='all', install=True,
         add=[G((0, 0, 150), 'MP-107'), G((0, 0, -50), 'BUY-07'), G((0, 0, -100), 'BUY-06')],
         tools='Arbor or hydraulic press (5 t), flat support block, square, dial indicator, torque wrench, 8 mm hex key, Loctite 243',
         do=['Support the base on the press bed directly under the first hole.',
             'Press the column\'s Ø20 p6 spigot (the short end) into C1 from the top until the Ø25 shoulder seats on the plate. Press straight; a light oil film on the spigot helps.',
             'Repeat for the second column in C2.',
             'From underneath, fit the hardened Ø32 × 2.5 washer into each counterbore and pull the column down with the M10 × 16 low-head clamp screw, Loctite 243, 40 N·m. The head ends flush with the base underside.'],
         check='Each column square to the base within 0.05 per 100 mm; centres 210.00 ±0.01 at the top.'),
    dict(part='A', title='Die table on the bench', view=(-0.5, -0.8, -0.2), frame='all',
         add=[G((0, 0, 0), 'MP-105'), G((0, 0, 25), 'BUY-41'), G((0, 0, 60), 'MP-205'), G((0, 0, -40), 'BUY-40'),
              G((0, 0, 40), 'BUY-32')],
         tools='Soft-face mallet, 3 mm hex key, torque wrench',
         do=['The station bases go on now because their screws are under the table.',
             'Press two Ø6 × 12 dowels into each pair of G holes in the table top, 6 mm proud.',
             'Put a station base (MP-205) on each pair of dowels: base A over the left station, base B over the right. The Ø4 hole Q in each base goes to the front.',
             'From underneath, fit the eight M5 × 20 countersunk screws (F1 to F8) flush, 6 N·m. The holes in the bases are tapped right through.',
             'Screw the two Ø14 push knobs into the M5 holes K1/K2 on the table top, one at each end.'],
         check='Screw heads flush or below the table underside; bases sit flat on the table.'),
    dict(part='A', title='Guide rails, keepers and the die table', view=V_ISO, frame='all', install=True,
         add=[G((0, 0, 0), *TABLE, row='Die table from step 3', label=('MP-105', 'Die table', 'from step 3')),
              G((0, 0, 30), 'MP-102-F', 'MP-102-B'), G((0, 0, 70), 'MP-103-F', 'MP-103-B'), G((0, 0, 110), 'BUY-02')],
         tools='0.05 mm shim, 3 mm hex key, torque wrench, light oil',
         do=['Lay the front rail (-F, 8 holes) and the back rail (-B, 10 holes) on the base over the rail screw holes.',
             'Put the die table between them as a gauge, with a 0.05 mm shim between the table and one rail.',
             'Lay the keepers on the rails with the hole line toward the outside, so the inner edge overlaps the table by 5 mm: front keeper (-F) at the front, back keeper (-B, with four plain holes) at the back.',
             'Fit the fourteen M5 × 30 countersunk screws through keeper and rail into the base, 6 N·m, working from the centre out; the heads end just below the keeper top. Leave the four plain holes in the back keeper for the stop blocks.',
             'Pull out the shim. Put a few drops of light oil on the rails.'],
         check='The table runs end to end with fingertip force, with no rock and no lift at the ends; running clearance 0.03 to 0.05 mm.'),
    dict(part='A', title='Stop blocks, stop pin and ball plunger', view=(-0.35, 0.78, 0.55), frame='new', install=True, zoom=1.1,
         add=[G((0, 0, 60), 'MP-104'), G((0, 0, 110), 'BUY-03'), G((40, 0, 0), ('BUY-04', 1)), G((-40, 0, 0), ('BUY-04', 2)),
              G((22, 0, 0), ('BUY-05', 1)), G((-22, 0, 0), ('BUY-05', 2)), G((0, 0, 50), 'MP-106'), G((0, 0, 50), 'BUY-31')],
         tools='4 mm hex key, 10 mm spanner, screwdriver, torque wrench, Loctite 243 and 222',
         do=['Put a stop block (MP-104) over each pair of plain holes in the back keeper, the overhang toward the table.',
             'Fit two M5 × 35 cap screws per block through keeper and rail into the base, Loctite 243, 6 N·m.',
             'Screw an M6 × 0.75 × 40 stop screw with its lock nut into each block from the outside, tip toward the centre. Leave the lock nuts loose: the stations are set in step 14.',
             'Screw the stop pin (MP-106) into hole S on the table top, Loctite 243, 2.5 N·m.',
             'Screw the ball plunger into hole BP from the top until it clicks into the detent spots at both stations. Lock it with Loctite 222.'],
         check='The table clicks at both stations and the stop pin meets a stop screw at each end.'),
    # ------------------------------------------------------------------ B
    dict(part='B', title='Ram sub-assembly', view=V_ISO, frame='all',
         add=[G((0, 0, 0), 'MP-109'), G((0, 0, 50), 'BUY-13'), G((0, 0, 45), 'MP-110'), G((45, 0, 45), ('BUY-16', 2)),
              G((0, 0, 95), 'BUY-27'), G((0, 0, -45), 'MP-111'), G((0, 0, -85), 'BUY-28'), G((40, 0, -45), 'BUY-29'),
              G((0, 0, -70), 'MP-120'), G((0, 0, 70), 'MP-118'), G((0, 0, 35), 'BUY-23')],
         tools='Press and stepped mandrels (25/32 and 12/14 bushings), 3 and 4 mm hex keys, 17 mm spanner, torque wrench, Loctite 243',
         do=['Press the two flanged bronze bushings into the ram\'s Ø32 bores from the top, flange on the top face, flush with the underside.',
             'Press the 12 × 14 × 20 PTFE-composite bushing into the clevis bore, flush both sides. Never ream or grease these bushings.',
             'Check the two link-clearance pockets L1/L2 beside the clevis pocket are clean and deburred: the links\' lower ends run in them. Put the clevis in the 2 mm pocket on the ram top, bore running left to right. Fit two M5 × 25 cap screws, Loctite 243, 6 N·m.',
             'Push the die holder\'s Ø24 spigot into the ram underside, its Ø4 orientation hole to the front. Fit four M5 × 16 low-head screws from below, Loctite 243, 6 N·m. Screw the M5 cone-point lock screw into the holder\'s side hole and back it off.',
             'Push the station pilot\'s Ø10 body into hole PL under the ram (back side) and screw it home, Loctite 243 on the M6 thread. The tip ends 84 mm below the ram.',
             'Screw the two return rods into R1/R2 on the ram top with a spanner on their flats, Loctite 243, 20 N·m.',
             'Screw the two urethane bumpers into U1/U2 on the ram top, Loctite 243, hand tight.'],
         check='Clevis bore parallel to the ram underside within 0.02; pilot square to the ram.'),
    dict(part='B', title='Crown sub-assembly', view=(-0.6, -0.75, 0.2), frame='all',
         add=[G((0, 0, 0), 'MP-108'), G((0, 0, 30), 'BUY-26'), G((0, 0, 70), 'MP-112'), G((50, 0, 70), ('BUY-14', 1)), G((-50, 0, 70), ('BUY-14', 2)),
              G((0, 0, -35), 'BUY-25'), G((0, 0, -75), 'BUY-24')],
         tools='Ø18 H7 line reamer with pilot, press and 16/18 mandrel, 6 mm hex key, torque wrench',
         do=['Deburr the four reliefs in the slot walls (N1/N2 underneath, N3/N4 on top): the ends of pins B and A pass through them.',
             'Press the two Ø6 × 16 dowels into P1/P2 on the crown top, 8 mm proud.',
             'Put a pivot cheek on each dowel, the bore running left to right. Fix each with two M8 × 30 cap screws and Nord-Lock washers from below, 25 N·m.',
             'Line-ream both cheek bores together to Ø18 H7 in one pass.',
             'Press a 16 × 18 × 15 PTFE-composite bushing into each cheek, 0.5 mm in from each face. Do not ream the bushings afterwards.'],
         check='A Ø16 g6 test pin slides through both cheeks freely with no binding.'),
    dict(part='B', title='Ram and crown onto the columns', view=V_ISO, frame='all', install=True,
         add=[G((0, 0, 90), *RAM, row='Ram sub-assembly from step 6', label=('MP-109', 'Ram', 'from step 6')),
              G((0, 0, 170), *CROWN, row='Crown sub-assembly from step 7', label=('MP-108', 'Crown', 'from step 7')),
              G((0, 0, 230), 'BUY-08'), G((0, 0, 260), 'BUY-09')],
         tools='24 mm socket, torque wrench (100 N·m), wooden block about 60 mm high',
         do=['Wipe the columns clean and dry: the graphite-plugged bushings run without grease.',
             'Slide the ram down over the column tops, bushing flanges up. Let it rest low on a wooden block on the die table.',
             'Lower the crown over the column spigots, cheeks on top, with the return rods passing up through holes R1/R2.',
             'Fit a Nord-Lock washer pair and an M16 × 1.5 nut on each column. Tighten to 100 N·m in two passes, alternating.'],
         check='The ram slides the full column length under its own weight. If it binds, loosen the nuts and re-seat the crown.'),
    # ------------------------------------------------------------------ C
    dict(part='C', title='Lever and links on the bench', view=V_ISO, frame='all',
         add=[G((0, 0, 0), 'MP-113'), G((-45, 0, 0), 'BUY-15', ('BUY-16', 1)), G(tuple(90 * v for v in PSI_DIR), 'BUY-30'),
              G((-60, 0, 0), ('MP-114', 1)), G((60, 0, 0), ('MP-114', 2)), G((90, 0, 0), ('BUY-17', 1, 2)), G((-90, 0, 0), ('BUY-17', 3, 4))],
         tools='Press and 16/18 and 12/14 mandrels, rubber adhesive',
         do=['Press the 16 × 18 × 20 bushing into the lever\'s pivot bore O and the 12 × 14 × 20 bushing into the crank bore A, flush both faces.',
             'Push the red grip onto the grip zone with rubber adhesive, centred 320 mm from O (it covers 260 to 380).',
             'Press a 12 × 14 × 6 bushing into each bore of both links, flush with the outer face. The links are a matched pair: keep their stamp marks together and facing out.'],
         check='Pins slide through every bushing by hand with no play you can feel.'),
    dict(part='C', title='Hang the lever on pin O', view=V_ISO, frame='new', install=True, zoom=1.2,
         add=[G((0, 0, 60), *LEVER, row='Lever from step 9', label=('MP-113', 'Lever', 'from step 9')),
              G((22, 0, 60), ('MP-119', 1)), G((-22, 0, 60), ('MP-119', 2)),
              G((-110, 0, 0), 'MP-117'), G((40, 0, 0), ('BUY-19', 1)), G((-150, 0, 0), ('BUY-19', 2))],
         tools='External retaining-ring pliers (Ø16)',
         do=['Hold the lever between the cheeks, handle pointing to the front, with a bronze spacer each side of it.',
             'Push pin O through: left cheek, spacer, lever, spacer, right cheek.',
             'Fit a DIN 471-16 retaining ring in the groove at each end.'],
         check='The lever swings freely through its whole arc; end float 0.1 to 0.5 mm.'),
    dict(part='C', title='Links, pin A and pin B', view=(0.62, 0.62, 0.45), frame='new', install=True, zoom=1.45,
         add=[G((-40, 0, 0), ('MP-114', 1), ('BUY-17', 3, 4)), G((40, 0, 0), ('MP-114', 2), ('BUY-17', 1, 2)),
              G((-90, 0, 0), 'MP-116'), G((70, 0, 0), ('BUY-18', 1, 2)), G((-130, 0, 0), ('BUY-18', 3, 4))],
         tools='External retaining-ring pliers (Ø12)',
         do=['Put a link each side of the lever at the crank bore A, stamp marks out. Push pin A through and fit a DIN 471-12 ring at each end.',
             'With the ram still resting low, swing the links down either side of the clevis. Raise the ram until the bores line up and push pin B through link, clevis and link.',
             'Fit a DIN 471-12 ring at each end of pin B. Pin B can only go in with the ram low: with the handle up its ends sit in the crown reliefs.'],
         check='Lifting the handle lifts the ram smoothly; nothing touches the crown or the ram top through the full stroke.'),
    dict(part='C', title='Return springs and handle stop', view=(-0.25, -0.92, 0.38), frame='new', install=True, zoom=1.3,
         add=[G((0, 0, 25), 'BUY-49'), G((0, 0, 40), 'BUY-20'), G((0, 0, 100), 'BUY-21'), G((0, 0, 120), 'BUY-22'),
              G((0, 0, 20), 'MP-121'), G((0, 0, 40), 'BUY-10'), G((0, 0, 60), 'BUY-12')],
         tools='17 mm socket, 5 mm hex key, 17 mm spanner, torque wrench, calipers, protractor or angle gauge, Loctite 243',
         do=['Take the wooden block out. Slide a POM guide sleeve over each return rod down onto the crown, then drop a return spring over it, then a Ø32 × 3 washer and an M10 nylock nut.',
             'Tighten each nut until the ram is pulled up against the bumpers and the spring measures 109.5 mm (about 80 N).',
             'Screw the handle-stop post (MP-121) into hole T on the crown top, 62 mm in front of the centre, Loctite 243, 40 N·m. Screw the M10 × 1 × 12 stop screw (nylon patch) into the post and put the urethane cap on it.',
             'Pull the handle down onto the stop. Adjust the screw until the lever rests 3° above horizontal; the nylon patch holds the setting.'],
         check='Handle swings 65° to 3° and springs back to the open stop from fully down, 20 times out of 20. Ram travel 38.9 ±0.3 mm.'),
    # ------------------------------------------------------------------ D
    dict(part='D', title='Lower dies', view=(-0.6, -0.55, 0.6), frame='new', install=True, zoom=1.2,
         add=[G((0, 0, 25), 'BUY-33'), G((0, 0, 55), 'MP-211-A', ('BUY-37', 1, 2)), G((0, 0, 55), 'MP-211-B', ('BUY-37', 3, 4)),
              G((0, 0, 95), 'BUY-36')],
         tools='5 mm hex key, torque wrench',
         do=['Check the key pins are pressed flush in each carrier: carrier A (green band) has them at KA, carrier B (red band) at KB.',
             'Put four green die springs in the pockets of each station base.',
             'Lay carrier A on the left station and carrier B on the right, spring pockets down over the springs.',
             'Fit four Ø6 × 12 shoulder screws through each carrier into its base, 8 N·m, in a cross pattern.'],
         check='Each carrier moves 8 mm freely and springs back square.'),
    dict(part='D', title='Align the stations', img=False,
         tools='Ø16 centring pin with a point (fits the die holder), Ø12 centring plug (fits hole C), 10 mm spanner, dial indicator',
         do=['Do this before the upper die goes on: the die holder must be empty.',
             'Put the Ø16 centring pin in the die holder and lock it with the holder\'s cone-point screw. Put the Ø12 plug in hole C of station base A.',
             'Push the table to the right until it clicks (station A under the ram). Lower the handle slowly and adjust the right-hand stop screw until the pin point lands on the plug centre. Lock the nut.',
             'Push the table to the left (station B under the ram) and set the left-hand stop screw the same way.',
             'Rev E: then back each stop screw off 0.4 of a turn (0.3 mm) before you lock it, so the table stops just past its station and the pilot always pulls it back onto the station.',
             'Move the table 3 mm off a station and make a slow stroke: the station pilot must land on the table and stop the stroke. Repeat at the other station.'],
         check='±0.05 mm at both stations; off station the stroke stops with the dies at least 5 mm apart.'),
    dict(part='D', title='Upper die on the bench', view=V_BELOW, frame='all',
         add=[G((0, 0, 0), 'MP-201'), G((0, 0, 40), 'MP-202'), G((0, 0, 30), 'BUY-42'), G((0, 0, -22), 'BUY-34'),
              G((0, 0, -55), 'MP-210', ('BUY-37', 5, 6)), G((30, 0, -55), ('BUY-38', 1)), G((-30, 0, -55), ('BUY-38', 2)),
              G((0, 0, -100), 'BUY-35')],
         tools='16 mm spanner on the shank flats or soft jaws, 5 mm hex key, torque wrench, Loctite 243, a block with a Ø20 hole, a vise or the press to compress the springs',
         do=['Screw the shank (MP-202) into the M10 hole in the floor of the counterbore on the die body top, Loctite 243, until the Ø16 face seats: 25 N·m. Its Ø12 spigot locates it.',
             'Press the Ø4 × 12 orientation pin into hole O in the counterbore floor, 6 mm proud.',
             'Check the two key pins are flush in the upper carrier. Screw the two dog-point thumb screws into the carrier ends and back them out of the pocket.',
             'Turn the body over onto the block (shank down through the hole). Put the eight red Ø12.5 × 44 die springs in its spring pockets.',
             'Lay the carrier on the springs, pocket side up. The springs push back with about 1.6 kN, so press the carrier down onto the body in a vise or under the press first. Fit the four Ø6 × 10 shoulder screws through the carrier into the body, then release slowly. Finish at 8 N·m.'],
         check='The carrier pushes up 5.5 mm evenly and springs back square to the body.'),
    dict(part='D', title='Mount the upper die', view=(-0.9, -0.38, 0.14), frame='new', install=True, fitExtra=I('MP-111'), zoom=1.35,
         hide=['MP-211-A', 'MP-211-B', 'BUY-33', 'BUY-36', 'BUY-37'],
         add=[G((0, 0, -45), *UPPER, row='Upper die from step 15', label=('MP-201', 'Upper die', 'from step 15')),
              G((0, 0, -30), 'BUY-43')],
         tools='2.5 mm hex key',
         do=['Put the shim pack on the body top over the shank and orientation pin. Start with no shims; the depth is set in step 19.',
             'Push the shank up into the die holder, the orientation pin into the holder\'s Ø4 hole (front).',
             'Tighten the cone-point lock screw into the shank\'s V-groove with the hex key through slot W in the die body (from the right-hand end), firmly (about 3 N·m).'],
         check='Upper die face parallel to the table within 0.05 at all four corners.'),
    # ------------------------------------------------------------------ E
    dict(part='E', title='Prepare a size kit', view=V_ISO, frame='all',
         add=[G((0, 0, 40), 'MP-203-' + K), G((0, 0, 65), 'BUY-46'), G((0, 0, 70), 'MP-212'),
              G((0, 0, 0), 'MP-204-' + K), G((0, -25, 0), ('BUY-45', 1, 3)), G((0, 25, 0), ('BUY-45', 2, 4)),
              G((0, 0, 0), 'MP-206-' + K), G((0, 0, -30), ('BUY-47', 1), ('BUY-48', 1)),
              G((0, 0, 0), 'MP-208-' + K), G((0, 0, -30), ('BUY-47', 2), ('BUY-48', 2))],
         tools='Press, 3 mm hex key, depth gauge or feelers, torque wrench, Loctite 243 and 222',
         do=['Do this once per kit; every kit is prepared the same way. Kit 6363 is shown.',
             'Plug: press the two Ø5 × 14 dowels into the D holes on the top face, 5.5 mm proud. Screw the stud (MP-212) into the M6 hole, Loctite 243, 8 N·m. A round plug (MP-223) is prepared the same way.',
             'Upper ring: screw the four M3 ball plungers into the side holes until each ball stands 0.2 to 0.3 mm into the opening. Lock with Loctite 222.',
             'Pickup pedestal and crimp anvil: press a Ø12 × 15 dowel into the underside hole C (7 mm proud) and a Ø4 × 10 pin into hole Q (4 mm proud). Round kits (Rev D) have no hole Q and no Ø4 pin: a round pedestal or anvil can turn.',
             'Rings A and B need no preparation. Check every part carries the kit\'s size code (and U, A or B).'],
         check='Plug dowels and stud square to the face; plungers all the same protrusion.'),
    dict(part='E', title='Fit the size kit', view=V_ISO, frame='new', install=True, zoom=1.15,
         add=[G((0, 0, -45), 'MP-203-' + K, 'BUY-46', 'MP-212', row='Plug from step 17', label=('MP-203-' + K, 'Plug', 'from step 17')),
              G((-60, 0, 0), 'BUY-39'),
              G((0, 0, -75), 'MP-204-' + K, 'BUY-45', row='Upper ring from step 17', label=('MP-204-' + K, 'Upper ring', 'from step 17')),
              G((0, 0, 45), 'MP-207-' + K), G((0, 0, 85), 'MP-206-' + K, ('BUY-47', 1), ('BUY-48', 1), row='Pickup pedestal from step 17', label=('MP-206-' + K, 'Pickup pedestal', 'from step 17')),
              G((0, -120, 20), 'MP-209-' + K), G((0, -120, 50), 'MP-208-' + K, ('BUY-47', 2), ('BUY-48', 2), row='Crimp anvil from step 17', label=('MP-208-' + K, 'Crimp anvil', 'from step 17'))],
         tools='None',
         do=['With the handle up on its stop, offer the plug up to the die body: dowels into the D holes, stud into hole K. It only fits one way. A round plug (Rev D) goes on the inner holes instead: dowels into D2, stud into K2.',
             'Push the detent pin in from the left end of the die body until it clicks. It passes through the stud and holds the plug.',
             'Push the upper ring up into the upper carrier with its key slots on the key pins, and tighten the two thumb screws.',
             'Drop pickup ring A into carrier A, then the pickup pedestal through it, dowel into hole C and pin into hole Q (round kits: dowel only).',
             'Drop crimp ring B into carrier B, then the crimp anvil the same way. The key pins stop a ring going into the wrong carrier.'],
         check='One slow dry stroke on each station: the upper ring enters both lower rings without touching.'),
    # ------------------------------------------------------------------ F
    dict(part='F', title='Feet, set-up and first magnets', view=(-0.55, -0.8, 0.22), frame='all', install=True, zoom=0.75,
         add=[G((0, 0, -40), 'BUY-01')],
         tools='Calipers, 10 kN load cell and dummy block, hanging scale, marker',
         do=['Stick the six pads under the base, clear of the six bench holes: four at (±200, ±80) and two under the tongue.',
             'Put the press on a flat bench (two people: it weighs about 48 kg). For all-day use bolt it down through the Ø9 holes.',
             'Set the depth: make a magnet, then add shims (0.1 / 0.2 / 0.5) until the crimp finishes with the handle about 5 to 10° above horizontal. Write the shim value on the frame label.',
             'Run the tests in the table below, then make two test magnets per kit and check the corners and the crimp.',
             'Consumables for a square kit: flat tin blanks X + 12 cut from 0.20 mm soft tinplate, photo and film X + 12, all with the corners clipped on the 45° line printed by the Magnet Studio (`web/magnet-studio.html`); 1.2 mm back plates X − 1.4; magnet sheet X − 8. Round kits use drawn round cups.'],
         check='Every test in the table below passes.'),
]

PARTS_TITLE = {'A': 'Part A — Frame and die table', 'B': 'Part B — Ram and crown', 'C': 'Part C — Toggle drive',
               'D': 'Part D — Universal die', 'E': 'Part E — Size kit', 'F': 'Part F — Set-up and tests'}

TORQUE = [
    ('Rail and keeper screws', 'M5 × 30 ISO 10642', '6 N·m', '—'),
    ('Stop-block screws', 'M5 × 35 ISO 4762', '6 N·m', 'Loctite 243'),
    ('Column clamp screws', 'M10 × 16 DIN 7984', '40 N·m', 'Loctite 243'),
    ('Column nuts', 'M16 × 1.5 + Nord-Lock', '100 N·m, two passes', '—'),
    ('Clevis screws', 'M5 × 25 ISO 4762', '6 N·m', 'Loctite 243'),
    ('Die-holder screws', 'M5 × 16 DIN 7984', '6 N·m', 'Loctite 243'),
    ('Station pilot', 'M6', 'hand tight', 'Loctite 243'),
    ('Return rods into the ram', 'M10', '20 N·m *', 'Loctite 243'),
    ('Bumpers', 'M6 stud', 'hand tight', 'Loctite 243'),
    ('Cheek screws', 'M8 × 30 + Nord-Lock', '25 N·m *', '—'),
    ('Return-spring nuts', 'M10 nylock', 'to 109.5 mm spring length', '—'),
    ('Shank into the die body', 'M10', '25 N·m *', 'Loctite 243'),
    ('Die-holder lock screw', 'M5 cone point', 'about 3 N·m', 'nylon patch'),
    ('Station-base screws', 'M5 × 20 ISO 10642', '6 N·m', '—'),
    ('Handle-stop post', 'M10 stud', '40 N·m', 'Loctite 243'),
    ('Carrier shoulder screws', 'ISO 7379 Ø6', '8 N·m', '—'),
    ('Plug stud', 'M6', '8 N·m *', 'Loctite 243'),
    ('Table stop pin', 'M4', '2.5 N·m *', 'Loctite 243'),
    ('Stop screws', 'M6 × 0.75 × 40 + lock nut', 'set, then lock', '—'),
    ('Handle-stop screw', 'M10 × 1 × 12', 'set to the 3° rest', 'nylon patch'),
    ('Ball plunger, ring plungers', 'M6, M3', 'set, then lock', 'Loctite 222'),
    ('Ring thumb screws', 'M5 dog point', 'finger tight', '—'),
]

TESTS = [
    ('Station alignment', 'Step 14.', '±0.05 mm at both stations'),
    ('Station pilot', 'Table 3 mm off station, slow stroke; repeat at the other station and on the other side.', 'Stroke stops with the dies at least 5 mm apart'),
    ('Handle return', 'Pull the handle fully down onto its stop and let go, 20 times.', 'Returns to the open stop every time'),
    ('Stroke and handle stop', 'Measure ram travel from handle up to handle down.', '38.9 ±0.3 mm; handle stops 3° above horizontal'),
    ('Depth', 'Shims so the crimp finishes with the handle 5 to 10° above horizontal (step 19).', 'Full crimp with a firm push, no hard knock'),
    ('Force', '10 kN load cell on station B with a dummy block; 200 N on the grip with a hanging scale.', '≥ 5.5 kN'),
    ('Ring alignment', 'Marker blue on the lower ring tops, slow stroke on each station.', 'Even contact all round; the upper ring never touches a lower ring edge'),
    ('Stroke 1 fold', 'Slow stroke 1 at station A with a flat tin blank only; lift the ram and look at the shell in the upper ring.', 'Four straight walls about 5.6 mm deep, square corners with a small flat gusset, nothing left in the recess'),
    ('Magnet quality', 'Make 20 of each size.', 'No white paper at the edges, no torn film, sharp corners with neat mitres on the back, a flat two-layer border about 2.8 mm wide all round, no cut tin edge in sight'),
    ('Size-kit change', 'Change the kit, timing it; try each wrong ring in each carrier.', 'Under 2 minutes; no wrong ring seats'),
    ('Reference height', 'Handle on its closed stop: die-holder face to table top. Write it on the frame label.', 'Re-check after any service; within 0.1 mm'),
    ('Proof load (prototype only)', '20 kN cell on station B, push the grip to 16 kN; dial indicator before and after.', 'No permanent set; stroke still 38.9 ±0.3'),
    ('Endurance (prototype)', '1,000 strokes, then 10,000; repeat alignment and quality checks.', 'No change; no galling; ≤ 1 mm handle play at the grip'),
]

TOOLS = ['Arbor or hydraulic press (5 t) with a flat bed, support blocks and stepped bushing mandrels for 12/14, 16/18 and 25/32 bushings',
         'Torque wrenches 2–25 N·m and 20–110 N·m; hex keys 2.5, 3, 4, 5, 6, 8 mm; spanners and sockets 10, 16, 17, 24 mm',
         'External retaining-ring pliers for Ø12 and Ø16 shafts',
         'Ø18 H7 line reamer with a long pilot (for the pivot cheeks)',
         'Straightedge, feeler gauges, 0.05 mm shim, dial indicator on a magnetic base, calipers, depth gauge, square, bore gauge',
         'Ø16 centring pin with a point and a Ø12 centring plug (station alignment, step 14)',
         'Loctite 243 (medium) and 222 (low strength), rubber adhesive, light machine oil',
         'Two wooden bearers about 50 mm high and a wooden block about 60 mm high',
         'For the tests: 10 kN load cell (20 kN for the proof load), hanging scale, dummy die block']


# =====================================================================================
# build the render spec and the document blocks
# =====================================================================================
def build():
    installed, renders = [], []
    for n, s in enumerate(STEPS, 1):
        s['no'] = n
        if s.get('img', True):
            labels, auto = [], {}
            for g in s['add']:
                if g['label'] is None:
                    continue
                if g['label'] != 'auto':
                    pid, t, sub = g['label']
                    labels.append({'name': I(pid)[0], 'text': t, 'sub': sub})
                    continue
                for nm in g['names']:
                    pid = nm.rsplit('_', 1)[0]
                    if pid not in auto:
                        auto[pid] = {'name': nm, 'n': 0}
                    auto[pid]['n'] += 1
            for pid, a in auto.items():
                labels.append({'name': a['name'], 'text': pid + (' ×%d' % a['n'] if a['n'] > 1 else ''), 'sub': short(NAMES[pid])})
            s['img_name'] = 'step%02d.png' % n
            renders.append({'img': s['img_name'], 'title': 'Step %d — %s' % (n, s['title']), 'view': list(s['view']),
                            'fit': s.get('frame', 'all'), 'fitExtra': s.get('fitExtra', []), 'zoom': s.get('zoom', 0.92),
                            'hide': [nm for pid in s.get('hide', []) for nm in I(pid)],
                            'ctx': list(installed) if s.get('install') else [],
                            'add': [{'names': g['names'], 'ex': g['ex']} for g in s['add']], 'labels': labels})
        if s.get('install'):
            for g in s.get('add', []):
                installed += [nm for nm in g['names'] if nm not in installed]
    renders.append({'img': 'cover.png', 'title': '', 'view': [-0.55, -0.8, 0.3], 'fit': 'all', 'fitExtra': [], 'ctx': [],
                    'add': [{'names': list(NODES), 'ex': [0, 0, 0]}], 'labels': []})
    return renders


def short(name):
    name = re.sub(r'\s*\(.*?\)', '', name)
    name = name.replace(', kit 63.5 × 63.5', '').replace(' ISO 4762', '').replace(' ISO 10642', '').replace(' DIN 7984', '')
    return name if len(name) <= 26 else name[:25].rstrip() + '…'


def step_rows(s):
    rows, seen = [], {}
    for g in s.get('add', []):
        if g['row']:
            rows.append(('—', g['row'], '', ''))
            continue
        for nm in g['names']:
            pid = nm.rsplit('_', 1)[0]
            seen[pid] = seen.get(pid, 0) + 1
    for pid, k in seen.items():
        rows.append((pid, NAMES[pid], str(k), '[STEP](../models/step/%s.step) · [STL](../models/stl/%s.stl)' % (FILES[pid], FILES[pid])))
    return rows


# =====================================================================================
# document: one list of blocks, written out as Markdown and as HTML (for the PDF)
# =====================================================================================
def doc_blocks():
    B = []
    h = lambda lvl, t, anchor=None: B.append(('h', lvl, t, anchor))
    p = lambda t: B.append(('p', t))
    ul = lambda items: B.append(('ul', items))
    ol = lambda items: B.append(('ol', items))
    tbl = lambda head, rows: B.append(('table', head, rows))
    img = lambda src, alt: B.append(('img', src, alt))
    note = lambda kind, title, t: B.append(('note', kind, title, t))
    brk = lambda: B.append(('break',))

    h(1, 'MagPress M4 — Assembly manual (Rev E)')
    p('How to build the MagPress M4 photo-magnet press from its parts, in 19 steps: frame and die table, ram and crown, toggle drive, universal die, a size kit, then set-up and tests. '
      'Every picture comes from the 3D model in [`models/`](../models/): the parts added in a step are in colour and pulled apart along the way they go in; parts already fitted are grey. '
      'Labels give the part number; the parts table under each picture gives the name, quantity and 3D file.')
    img('assembly/img/cover.png', 'MagPress M4, assembled')
    h(2, 'Before you start')
    ul(['**Parts.** Made parts (MP-xxx) are made to the drawing set in [`release/RevE/`](../release/RevE/); bought parts (BUY-xx) are in the BOM and in [`models/parts.csv`](../models/parts.csv). Lay every step\'s parts out and check them off before you start the step.',
        '**Directions.** Front is the operator side (the base tongue). Left and right are as seen from the front. Station A (pickup) is the left station on the die table, station B (crimp) the right. Pushing the table to the right puts station A under the ram.',
        '**Bushings.** The pin bushings are PTFE-composite and run dry: no grease, never ream them after pressing. Press them with a stepped mandrel, never with a hammer.',
        '**Lubrication.** Columns and the graphite-plugged ram bushings run dry: wipe them clean. Light oil on the rails only. No oil on the dies.',
        '**Threadlocker.** Clean threads with solvent before Loctite. The torque table below lists every joint.',
        '**Safety.** The press weighs about 48 kg: lift it with two people. The pinch points are between the dies and between the table and the stop blocks. Wear gloves when handling tin blanks: the cut edges are sharp.'])
    note('check', 'Rev E',
         'Rev E makes sharp-cornered magnets with the photo carried round and folded twice, flat, onto the back (a two-layer hem: a printed border with the cut tin edge hidden), like bought tin photo magnets, and fixes the points found in an independent design review. '
         'The 3D check was repeated for Rev E at six handle angles and with a round kit fitted: nothing clashes. The changes, and the steps they touch:')
    tbl(['Part', 'Change', 'Step'], [(a_, b_, str(c_)) for (a_, b_, c_) in CHANGES])
    note('check', 'Rev D',
         'Rev D adds four round size kits: Ø44, Ø50, Ø56 and Ø58 (drawings MP-223 to MP-229). They are prepared and fitted like the square kits in steps 17 and 18, with two differences: '
         'the round plug hangs on the inner holes of the die body (dowels in D2, stud in K2, the same locking pin), and round pedestals and anvils have no Ø4 anti-rotation pin. '
         'The 3D check was repeated with round kit D58 fitted in place of kit 6363: nothing clashes.')
    h(2, 'Tools and materials')
    ul(TOOLS)
    h(2, 'Torque and thread-locker table')
    tbl(['Joint', 'Fastener', 'Torque', 'Thread lock'], TORQUE)
    p('Values marked * are standard values for property class 8.8 screws; the others are from the drawings and the build pack.')

    cur = None
    for s in STEPS:
        brk()
        if s['part'] != cur:
            cur = s['part']
            h(2, PARTS_TITLE[cur])
        h(3, 'Step %d — %s' % (s['no'], s['title']), 'step-%d' % s['no'])
        if s.get('img', True):
            img('assembly/img/' + s['img_name'], 'Step %d' % s['no'])
            rows = step_rows(s)
            tbl(['Part', 'Name', 'Qty', '3D model'], rows)
        p('**Tools:** ' + s['tools'])
        ol(s['do'])
        note('check', 'Check', s['check'])
        if s['part'] == 'F':
            tbl(['Test', 'How', 'Pass'], TESTS)

    brk()
    h(2, 'Changing the size kit')
    ol(['Rest the handle up on its stop and push the table to the right (station A under the ram).',
        'Upper: hold the upper ring, loosen its two thumb screws and lower it out. Pull the detent pin out to the left by its ring, and lower the plug off its dowels.',
        'Fit the new plug (it only fits one way: square plugs on the outer holes D and K, round plugs on the inner holes D2 and K2) and push the pin home. Push the new upper ring up so its key slots meet the pins, and tighten the thumb screws.',
        'Lower: screw the M5 T-handle puller into each pedestal or anvil and lift it out, then lift the ring out by its opening. Drop in the new ring A and pickup pedestal on the left, and ring B and crimp anvil on the right.',
        'One slow dry stroke on each station, then two test magnets. Check the corners (or, on a round magnet, the whole edge) and the crimp before running a batch.'])
    h(2, 'Maintenance')
    tbl(['When', 'Task'], [
        ('Each shift', 'Wipe the die table, rails and dies. Blow shell chips out of the rings. No oil on the dies.'),
        ('Weekly or 5,000 strokes', 'Check the thumb screws, the die lock screw and the handle-stop setting. Light oil on the rails only.'),
        ('25,000 strokes', 'Check handle play (≤ 1 mm at the grip) and the column nut torque. Clean tin pick-up from the die edges with a brass brush.'),
        ('100,000 strokes', 'Replace the eight red upper die springs (they work to 29% of their length).'),
        ('250,000 strokes', 'Replace the lower die springs and the return springs. Inspect the bushings and pins. Dye-penetrant check the die corners.')])
    p('If a shell jams, follow the un-jam procedure in [`docs/research/failure-review.md`](research/failure-review.md#un-jam-procedure).')
    return B


def inline_html(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[`?([^\]`]+)`?\]\(([^)]+)\)', lambda m: '<span class="ref">%s</span>' % m.group(1), t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t


def to_md(B):
    out = []
    for b in B:
        k = b[0]
        if k == 'h':
            out.append('%s %s\n' % ('#' * b[1], b[2]))
        elif k == 'p':
            out.append(b[1] + '\n')
        elif k in ('ul', 'ol'):
            out.append('\n'.join(('- ' if k == 'ul' else '%d. ' % (i + 1)) + x for i, x in enumerate(b[1])) + '\n')
        elif k == 'table':
            out.append('| ' + ' | '.join(b[1]) + ' |\n|' + '---|' * len(b[1]) + '\n' +
                       '\n'.join('| ' + ' | '.join(c.replace('|', '\\|') if not c.startswith('[STEP]') else c for c in r) + ' |' for r in b[2]) + '\n')
        elif k == 'img':
            out.append('![%s](%s)\n' % (b[2], b[1]))
        elif k == 'note':
            out.append('> %s **%s.** %s\n' % ('⚠️' if b[1] == 'warn' else '✅', b[2], b[3]))
    return '\n'.join(out)


CSS = '''
@page { size: A4; margin: 14mm 13mm 16mm 13mm; }
body { font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 10pt; color: #1b1d21; line-height: 1.4; }
h1 { font-size: 22pt; margin: 0 0 6pt; } h2 { font-size: 15pt; margin: 14pt 0 6pt; border-bottom: 2px solid #c0392b; padding-bottom: 2pt; }
h3 { font-size: 12.5pt; margin: 12pt 0 4pt; break-after: avoid; }
img { display: block; width: 88%; margin: 0 auto 4pt; border: 1px solid #e3e5e8; break-inside: avoid; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 8pt; font-size: 8.8pt; break-inside: avoid; }
td:first-child { white-space: nowrap; } td code { font-size: 7.4pt; word-break: break-all; }
th, td { border: 1px solid #d6d9de; padding: 2.5pt 5pt; text-align: left; vertical-align: top; } th { background: #f1f2f4; }
tr { break-inside: avoid; }
ol, ul { margin: 4pt 0 6pt; padding-left: 18pt; } li { margin: 2pt 0; }
.note { border-left: 4px solid #2e7d32; background: #f2f8f2; padding: 5pt 8pt; margin: 6pt 0; break-inside: avoid; }
.note.warn { border-color: #c0392b; background: #fbf0ee; }
code { font-family: Consolas, monospace; font-size: 9pt; } .ref { color: #444; font-style: italic; }
.step { break-inside: avoid-page; } .pb { break-before: page; }
'''


def to_html(B, imgdir):
    out = ['<!doctype html><html><head><meta charset="utf-8"><title>MagPress M4 assembly manual</title><style>%s</style></head><body>' % CSS]
    for b in B:
        k = b[0]
        if k == 'h':
            out.append('<h%d>%s</h%d>' % (b[1], inline_html(b[2]), b[1]))
        elif k == 'p':
            out.append('<p>%s</p>' % inline_html(b[1]))
        elif k in ('ul', 'ol'):
            out.append('<%s>%s</%s>' % (k, ''.join('<li>%s</li>' % inline_html(x) for x in b[1]), k))
        elif k == 'table':
            head = ''.join('<th>%s</th>' % inline_html(c) for c in b[1])
            rows = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % (inline_html(c) if not c.startswith('[STEP]') else '<code>%s</code> .step / .stl' % html.escape(FILES[r[0]])) for c in r) for r in b[2])
            out.append('<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (head, rows))
        elif k == 'img':
            out.append('<img src="file://%s" alt="%s">' % (os.path.join(imgdir, os.path.basename(b[1])), html.escape(b[2])))
        elif k == 'note':
            out.append('<div class="note%s"><b>%s.</b> %s</div>' % (' warn' if b[1] == 'warn' else '', inline_html(b[2]), inline_html(b[3])))
        elif k == 'break':
            out.append('<div class="pb"></div>')
    out.append('</body></html>')
    return '\n'.join(out)


PDF_JS = r'''
const { chromium } = require('playwright');
(async () => {
  const [src, dst] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src, { waitUntil: 'load' });
  await p.pdf({ path: dst, format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="font-size:8px;width:100%;padding:0 13mm;color:#666;display:flex;justify-content:space-between"><span>MagPress M4 · Assembly manual · Rev E</span><span class="pageNumber"></span></div>',
    margin: { top: '14mm', bottom: '16mm', left: '13mm', right: '13mm' } });
  await b.close();
})();
'''


def main():
    os.makedirs(IMG, exist_ok=True)
    renders = build()
    tmp = os.environ.get('MANUAL_TMP', os.path.join(HERE, '_build'))
    os.makedirs(tmp, exist_ok=True)
    spec = os.path.join(tmp, 'steps.json')
    with open(spec, 'w') as f:
        json.dump(renders, f)
    if '--no-render' not in sys.argv:
        subprocess.run(['node', os.path.join(HERE, 'render_steps.js'), GLB, spec, IMG], check=True)
    B = doc_blocks()
    with open(MD_OUT, 'w') as f:
        f.write(to_md(B))
    src = os.path.join(tmp, 'manual.html')
    with open(src, 'w') as f:
        f.write(to_html(B, IMG))
    js = os.path.join(tmp, 'pdf.js')
    with open(js, 'w') as f:
        f.write(PDF_JS)
    os.makedirs(os.path.dirname(PDF_OUT), exist_ok=True)
    subprocess.run(['node', js, src, PDF_OUT], check=True)
    print('wrote', MD_OUT, 'and', PDF_OUT)


if __name__ == '__main__':
    main()
