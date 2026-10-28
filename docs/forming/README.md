# How the MagPress M4 forms a magnet

Stills from section 02 of the build pack (`web/magpress-m4.html`), where they are animated. The section runs through one edge of the dies at true size, about 25 times enlarged.
The dimensions come from the die drawings MP-203 to MP-209 (square and rectangular kits); the round kits (MP-223 to MP-229) roll the edge instead, see the end. Remake these images with `node web/tools/forming_stills.js web/magpress-m4.html docs/forming`.

## The finished magnet

Rev E: sharp corners, photo and film wrapped round the edge, the edge folded twice, flat, under the back plate (a flattened version of the Rev D rolled edge, with the cut edge of the tin hidden inside), 2.4 mm thick, with a 2.8 mm flat border of the photo on the back, mitred at the corners (size 63.5 × 63.5 shown). Print a date, a name or a brand on that border with the Magnet Studio (`web/magnet-studio.html`).

| Front | Back | Edge, cut open |
|---|---|---|
| ![Front](magnet_face.png) | ![Back](magnet_back.png) | ![Edge, cut open](magnet_edge.png) |

## Stroke by stroke

### 1. Load station A

![Load station A](stage01.png)

Station A is outside the press. A flat tinplate blank lies in the 0.6 mm recess on top of pickup ring A, with the printed photo and the mylar film over it, all cut 6 mm bigger than the face on every side with the corners clipped at 45°.

### 2. Stroke 1: the dies close

![Stroke 1: the dies close](stage02.png)

The upper die comes down. The upper ring’s opening is the shell size plus 0.35 mm, and the plug sits 5.5 mm up inside it. At 26 mm of ram travel the upper ring lands on ring A, over the blank and the photo.

### 3. Fold 1: tin, photo and film fold down together

![Fold 1: tin, photo and film fold down together](stage03.png)

The upper ring pushes ring A down 8 mm against its light springs. After 2.4 mm the blank meets the pedestal, which then pushes its middle up into the upper ring: the tin, photo and film fold down round the pedestal’s R0.8 edge into a 5.6 mm wall. At each corner the spare tin and paper fold into a small flat gusset; the corner reliefs make room for it. The upper die springs hold the ring down while the tin folds.

### 4. The plug sets the face

![The plug sets the face](stage04.png)

Ring A reaches its stop just as the plug meets the face. The carrier gives 0.1 mm and the plug presses the film and photo flat on the face. The plug’s R1 lip cradles the rounded edge.

### 5. Pickup: the shell rides up in the ring

![Pickup: the shell rides up in the ring](stage05.png)

On the way up the folded shell stays in the upper ring: the tin springs back against the bore, and four ball plungers hold it. Its walls are 5.6 mm deep and stand a little below the ring; the photo and film end with the tin, so there are no loose tails.

### 6. Slide to station B

![Slide to station B](stage06.png)

Push the table to the left: station B comes under the ram. A back plate went onto the crimp anvil’s platform while the station was outside.

### 7. Stroke 2: onto the crimp ring

![Stroke 2: onto the crimp ring](stage07.png)

The upper ring lands on crimp ring B and pushes it down to its stop. Ring B’s 30° lead-in centres the wrapped shell over the anvil, and the bottom of the skirt reaches the cove at the anvil’s edge.

### 8. The plug comes down

![The plug comes down](stage08.png)

The upper ring is blocked on ring B. Its carrier gives way and the plug comes down onto the face.

### 9. The crimp: the edge folds twice, flat

![The crimp: the edge folds twice, flat](stage09.png)

The plug pushes the shell 4.8 mm out of the upper ring. The skirt runs down ring B’s bore into the R0.7 cove at the anvil’s edge, turns inward along the floor, meets the wall at the edge of the back-plate platform, turns up and folds back outward under the back plate. The stroke ends when the shell face bottoms on the back plate: the edge lies in two flat layers, the photo outside on the back and the cut edge of the tin hidden inside.

### 10. Finished magnet

![Finished magnet](stage10.png)

The ram lifts and ring B springs back up round the finished magnet: photo and film wrapped round the edge, the skirt folded twice and flat under the back plate, 2.4 mm thick, with a 2.8 mm flat border of the photo on the back. Lift it out and stick the magnet sheet on the back plate, inside the border.

## At the corners

The tin blank, the photo and the film are all cut 6 mm over the face, with their corners clipped at 45° on the line |x| + |y| = W/2 + H/2 + 1.7. Folded down the side, along the back and back on themselves, the edges at a corner meet in a diagonal mitre on the back. Where the side walls meet, about two layers overlap in a small gusset; the upper ring and ring B have a Ø1.2 relief in each corner to make room for it. If the corners tear or wrinkle onto the face, the paper is too thick: use 90–120 g/m² paper.

## Round magnets (Rev D rolled edge)

Round kits keep the Rev D design: a drawn round cup, and a roll channel in the anvil that rolls the edge under the back plate with the photo and film inside the roll. A round edge cannot be folded flat without wrinkling, so nothing of the print shows on the back. Size Ø58 shown: photo cut Ø70.

| Front | Back | Edge, cut open |
|---|---|---|
| ![Round magnet, front](round_face.png) | ![Round magnet, back](round_back.png) | ![Round magnet, edge cut open](round_edge.png) |
