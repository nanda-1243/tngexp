# Study: one stepped die for every size

**Question.** Could a single die serve all four sizes as steps, like stairs, with supports underneath for the larger sheets, instead of one die set per size?

**Answer.** Not as one stepped part. Rev C keeps the goal (one die for every size) by making the die universal and swapping only the thin forming parts.

## 1. The four sizes don't stack

A step can only sit inside a bigger step, so the sizes would have to nest. Long side across, all centred:

| Size | X (long) | Z (short) |
|---|---|---|
| 65 × 90 | 90 | 65 |
| 53 × 80 | 80 | 53 |
| 63.5 × 63.5 | 63.5 | 63.5 |
| 50 × 50 | 50 | 50 |

- 50 × 50 fits inside 53 × 80, which fits inside 65 × 90.
- 63.5 × 63.5 fits inside 65 × 90.
- But 63.5 × 63.5 is 10.5 mm taller than 53 × 80 (63.5 against 53), and 53 × 80 is 16.5 mm longer than the square (80 against 63.5). Neither fits inside the other, so they can't both be steps of one die.

## 2. The walls between steps would be too thin

Where sizes do nest, the wall between two forming edges is half the difference of the two openings:

- 50 × 50 inside 53 × 80: about 1.5 mm in Z, for example (53.45 − 50.45) / 2 for the crimp openings and (53.3 − 50.35) / 2 between a 53 × 80 plug and a 50 × 50 grip opening.
- 63.5 square inside 65 × 90: (65.35 − 63.85) / 2 = 0.75 mm in Z.

That is hardened steel 0.75–1.5 mm thick carrying the crimp. Thin hardened walls are what crack (failure mode 6 in [failure-review.md](failure-review.md)).

## 3. The steps get in the way of the forming

- **Crimp.** The edge of a big shell has to roll inward under its back plate. A smaller size's step forms a ledge exactly where that edge has to go, so the big magnet can't be crimped.
- **Plug.** A stepped plug is made of nested pieces. The joint between them would press a visible line across the bigger magnet's photo.
- **Fits.** Every forming edge needs its own 0.35–0.45 mm fit all round its own shell. One stepped part can't give every size its fit at the same time.

## 4. What Rev C keeps from the idea

- **One die does the work for every size.** The universal die (body, carriers, station bases, all springs) is made once and never changes.
- **Support from below for every size.** Each lower carrier has a ledge that carries any size ring; this is the "support underneath" from the idea.
- **Only thin "steps" change.** A size kit is six hardened parts (plug, upper ring, pickup ring and pedestal, crimp ring and anvil). Every ring has the same 106 × 81 outside, so any size, or any new shape up to 90 × 65, drops into the same pockets.

## 5. Rev B (one full die set per size) against Rev C (universal die + kits)

Masses are from [`calc/results.txt`](../../calc/results.txt).

| | Rev B: one full set per size | Rev C: universal die + kits |
|---|---|---|
| Die steel for all four sizes | ≈ 35 kg (4 sets of ≈ 8.8 kg) | ≈ 20.5 kg (7.6 kg die + 4 kits of 3.1–3.4 kg) |
| Cost of an extra size | a whole die set | six small parts |
| Size change | 2–3 min, swap whole sets | about 1 min, no tools |
| Die springs | a set per size | one set shared by every size |
| Alignment | fewer fits, a little more forgiving | one extra precision fit (ring in carrier, +0.01/0 and −0.01/−0.02) |
| Loose parts | none | kit parts to store (kit case) |

**Choice: Rev C.** It suits a press sold to people who make two or more sizes, which is most buyers. A machine that will only ever make one size gains little from it. Either way the crimp anvil and the corrected springs are needed: Rev B without them would not crimp reliably.

## 6. Why the Rev C die isn't one heavy block

The die is not light: the universal die plus one kit is about 11 kg of steel. It is plates and rings instead of thick blocks because:

- **The frame takes the load.** The crimp force (under 5 kN) goes straight down through the anvil, station base and die table into the 15 mm steel base. That is about 1 MPa on the anvil, so extra die thickness would add no strength.
- **Hardened tool steel.** A2 at 58–60 HRC is several times stronger and more wear-resistant than soft or cast die material, so it needs no bulk.
- **The springs live in the universal carriers.** An all-in-one die needs spring room inside every set, which makes each set tall and heavy.

Market dies were not weighed or measured for this comparison.

## 7. Output and life (estimates)

- **Output:** 2–4 magnets a minute by hand, about 1,000–2,000 per 8-hour shift. Each magnet takes 2 strokes, and the operator sets the pace.
- **Service interval:** about 250,000 strokes (about 125,000 magnets), then replace the upper die springs. The lower die springs are good for about 1 million strokes.
- **Kit life:** the hardened, chromed kit edges should last hundreds of thousands of magnets before a re-polish, and PVD-coated kits 1 million or more. These are targets until a 10,000-stroke prototype test confirms them.
- **For comparison,** one vendor guide reports cheap die sets cracking or warping after a few hundred uses. No verified life data was found for better-quality brands.
