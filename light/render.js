// Renders the MagPress L1 assembly GLBs to PNG for the drawing set (cover and assembly sheets).
// Usage: node light/render.js <assembly dir> <out dir>
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');

const VIEWS = [
  // [glb, png, view direction (from the target toward the camera), fit: null = whole model, or [cx, cy, cz, radius]]
  // glTF frame: Y up, +Z toward the front of the press (assembly -Y), X to the right.
  ['MagPress-L1_assembly.glb', 'render_assembled.png', [0.62, 0.42, 0.66], null],
  ['MagPress-L1_exploded.glb', 'render_exploded.png', [0.62, 0.30, 0.72], null],
  ['MagPress-L1_assembly.glb', 'render_dies.png', [-0.42, 0.30, 0.86], [0, 80, 0, 175]],
];

(async () => {
  const [,, asmDir, outDir] = process.argv;
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  for (const [glb, png, dir, fit] of VIEWS) {
    const page = await browser.newPage({ viewport: { width: 1400, height: 1400 }, deviceScaleFactor: 1 });
    const b64 = fs.readFileSync(path.join(asmDir, glb)).toString('base64');
    const html = `<!doctype html><html><head><meta charset="utf-8">
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<style>html,body{margin:0;background:#fff}</style></head><body>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const r = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
r.setSize(1400, 1400); r.setClearColor(0xffffff, 1); r.outputColorSpace = THREE.SRGBColorSpace;
r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.05;
document.body.appendChild(r.domElement);
const scene = new THREE.Scene();
const pm = new THREE.PMREMGenerator(r);
scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
const sun = new THREE.DirectionalLight(0xffffff, 1.4); sun.position.set(500, 900, 600); scene.add(sun);
scene.add(new THREE.AmbientLight(0xffffff, 0.35));
const cam = new THREE.PerspectiveCamera(22, 1, 10, 20000);
const DIR = new THREE.Vector3(${dir.join(',')}).normalize(); const FIT = ${JSON.stringify(fit)};
const bin = Uint8Array.from(atob('${b64}'), c => c.charCodeAt(0)).buffer;
new GLTFLoader().parse(bin, '', g => {
  g.scene.traverse(o => { if (o.isMesh) { o.material.side = THREE.DoubleSide; } });
  scene.add(g.scene);
  const edges = new THREE.Group();
  g.scene.traverse(o => { if (o.isMesh) { const e = new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry, 30), new THREE.LineBasicMaterial({ color: 0x222222, transparent: true, opacity: 0.35 })); o.updateWorldMatrix(true, false); e.applyMatrix4(o.matrixWorld); edges.add(e); } });
  scene.add(edges);
  let c, rad;
  if (FIT) { c = new THREE.Vector3(FIT[0], FIT[1], FIT[2]); rad = FIT[3]; }
  else { const s = new THREE.Box3().setFromObject(g.scene).getBoundingSphere(new THREE.Sphere()); c = s.center; rad = s.radius; }
  const dist = rad / Math.sin(THREE.MathUtils.degToRad(11)) * 0.98;
  cam.position.copy(c).addScaledVector(DIR, dist); cam.lookAt(c); cam.updateProjectionMatrix();
  r.render(scene, cam); window.DONE = true;
}, e => { document.title = 'ERR ' + e; window.DONE = true; });
</script></body></html>`;
    const tmp = path.join(outDir, '_render.html');
    fs.writeFileSync(tmp, html);
    await page.goto('file://' + tmp);
    await page.waitForFunction(() => window.DONE === true, null, { timeout: 120000 });
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(outDir, png) });
    console.log('wrote', png, await page.title());
    await page.close();
    fs.unlinkSync(tmp);
  }
  await browser.close();
})();
