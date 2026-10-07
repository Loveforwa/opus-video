// 博弈论 · 60s — deterministic three.js film. Every visual is a pure function of time t (seconds),
// so the same code drives live preview (?play) and frame-exact rendering (scripts/render.mjs).
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const Q = new URLSearchParams(location.search);
const W = 1080, H = 1920, DUR = 60;
const RS = parseFloat(Q.get('rs') || '1');            // 3D render scale (text layer is always full res)
const RW = Math.round(W * RS), RH = Math.round(H * RS);

// ───────────────────────────── math / timing ─────────────────────────────
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, x) => a + (b - a) * x;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const eOutExpo = x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x);
const eInExpo = x => x <= 0 ? 0 : Math.pow(2, 10 * x - 10);
const eInOut = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const eOutBack = x => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const eInCubic = x => x * x * x;
const eOutCubic = x => 1 - Math.pow(1 - x, 3);
const eOutElastic = x => x <= 0 ? 0 : x >= 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - .75) * (2 * Math.PI) / 3) + 1;
const TAU = Math.PI * 2;
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const nz = x => Math.sin(x * 12.9898) * .5 + Math.sin(x * 7.13 + 1.3) * .3 + Math.sin(x * 3.1 + 4.0) * .2;

const AUDIO = await (await fetch('./assets/audio/beats.json')).json();
const BT = AUDIO.beats.slice();
while (BT.length < 130) BT.push(BT[BT.length - 1] + 60 / AUDIO.tempo);
const B = n => BT[n];
const beatIdx = t => { let i = -1; for (let k = 0; k < BT.length; k++) { if (BT[k] <= t) i = k; else break; } return i; };
const hit = (t, tb, d = 8) => t < tb ? 0 : Math.exp(-(t - tb) * d);
const kick = t => { const i = beatIdx(t); return i < 0 ? 0 : hit(t, BT[i], 9); };
// stepped counter: each beat in [n0,n1) adds a snappy 0→1 — the "卡点" motion primitive
const bstep = (t, n0, n1, dur = .32) => { let s = 0; for (let k = n0; k < n1; k++) s += eOutExpo(clamp((t - BT[k]) / dur)); return s; };
const low = t => AUDIO.low[Math.min(AUDIO.low.length - 1, Math.max(0, Math.round(t * 30)))] || 0;

// ───────────────────────────── palette ─────────────────────────────
const P = { ink: '#07080B', paper: '#F3EFE6', clay: '#E07A55', blue: '#6EA4E8', gold: '#EDC46E', red: '#F0504A', mute: '#8D919B' };
const col = (hex, k = 1) => new THREE.Color(hex).multiplyScalar(k);

// ───────────────────────────── renderer / pipeline ─────────────────────────────
const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.domElement.id = 'film';
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const pm = new THREE.PMREMGenerator(renderer);
scene.environment = pm.fromScene(new RoomEnvironment(), .04).texture;
scene.environmentIntensity = .5;
const camera = new THREE.PerspectiveCamera(38, W / H, .05, 200);

const key = new THREE.DirectionalLight(0xfff1e0, 1.6); key.position.set(3, 5, 4); scene.add(key);
const rimA = new THREE.PointLight(0xff7a4a, 30, 30); rimA.position.set(-4, 2, -2); scene.add(rimA);
const rimB = new THREE.PointLight(0x5a9cff, 30, 30); rimB.position.set(4, -1, -2); scene.add(rimB);

const rt = new THREE.WebGLRenderTarget(RW, RH, { type: THREE.HalfFloatType, samples: 4 });
const composer = new EffectComposer(renderer, rt);
composer.renderToScreen = false;
composer.setPixelRatio(1);
composer.setSize(RW, RH);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(RW, RH), .16, .35, 1.6);
composer.addPass(bloom);

// text layer: full-res 2D canvas composited in the final pass (gets the same RGB split / flash as 3D)
const tcv = document.createElement('canvas'); tcv.width = W; tcv.height = H;
const g = tcv.getContext('2d');
const textTex = new THREE.CanvasTexture(tcv);
textTex.minFilter = THREE.LinearFilter; textTex.generateMipmaps = false;

const finalMat = new THREE.ShaderMaterial({
  uniforms: {
    tScene: { value: null }, tText: { value: textTex }, uTime: { value: 0 }, uRGB: { value: 0 }, uZoom: { value: 0 },
    uDir: { value: new THREE.Vector2() }, uFlash: { value: 0 }, uFade: { value: 0 }, uSat: { value: 1 }, uVig: { value: 1 },
    uGrain: { value: .06 }, uExpo: { value: 1 }, uN: { value: 1 }, uTint: { value: new THREE.Vector3(0, 0, 0) },
  },
  vertexShader: `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy,0.,1.); }`,
  fragmentShader: `
    uniform sampler2D tScene, tText; uniform float uTime,uRGB,uZoom,uFlash,uFade,uSat,uVig,uGrain,uExpo; uniform int uN;
    uniform vec2 uDir; uniform vec3 uTint; varying vec2 vUv;
    vec3 aces(vec3 x){ return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.); }
    vec3 samp(vec2 uv){ vec2 d=(uv-.5)*uRGB*.012; return vec3(texture2D(tScene,uv-d).r,texture2D(tScene,uv).g,texture2D(tScene,uv+d).b); }
    float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
    void main(){
      vec2 uv=vUv; vec3 c=vec3(0.);
      if(uN<=1){ c=samp(uv); }
      else { for(int i=0;i<16;i++){ if(i>=uN) break; float f=float(i)/float(uN-1);
        vec2 s=mix(uv,vec2(.5),uZoom*f*.22)+uDir*(f-.5); c+=samp(s);} c/=float(uN); }
      c*=uExpo; c=aces(c*.9); c=pow(c,vec3(1./2.2));
      vec2 td=(uv-.5)*uRGB*.006;
      vec4 tm=texture2D(tText,uv);
      float ar=texture2D(tText,uv-td).a, ab=texture2D(tText,uv+td).a;
      vec3 tc=vec3(texture2D(tText,uv-td).r*ar, tm.g*tm.a, texture2D(tText,uv+td).b*ab);
      float ta=max(tm.a,max(ar,ab));
      c=c*(1.-ta)+tc;
      c+=uTint;
      float l=dot(c,vec3(.299,.587,.114)); c=mix(vec3(l),c,uSat);
      vec2 q=uv-.5; q.x*=.5625; c*=mix(1.,smoothstep(.95,.18,length(q)*1.25),uVig);
      c+=(h(uv*vec2(1080.,1920.)+fract(uTime*7.31)*100.)-.5)*uGrain;
      c=mix(c,vec3(1.,.97,.92),clamp(uFlash,0.,1.));
      c*=1.-uFade;
      gl_FragColor=vec4(c,1.);
    }`,
  depthTest: false, depthWrite: false,
});
const finalScene = new THREE.Scene();
finalScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), finalMat));
const orthoCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

// ───────────────────────────── shared pieces ─────────────────────────────
const SPH = new THREE.SphereGeometry(1, 64, 40);
const D = new THREE.Object3D();
const UP = new THREE.Vector3(0, 1, 0);
const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);

const phys = (hex, o = {}) => new THREE.MeshPhysicalMaterial(Object.assign({
  color: hex, metalness: .35, roughness: .16, clearcoat: 1, clearcoatRoughness: .08,
  iridescence: .55, iridescenceIOR: 1.5, emissive: hex, emissiveIntensity: .1,
}, o));
// instanced meshes: per-instance color also scales emissive, so instance colors > 1 bloom
function glowify(mat) {
  mat.onBeforeCompile = sh => {
    sh.fragmentShader = sh.fragmentShader.replace('#include <emissivemap_fragment>',
      '#include <emissivemap_fragment>\n#ifdef USE_COLOR\n totalEmissiveRadiance *= vColor.rgb;\n#endif');
  };
  return mat;
}
const addMat = (c, o = .4) => new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: o, blending: THREE.AdditiveBlending, depthWrite: false });

function mkTrail(n, color) {
  const m = new THREE.InstancedMesh(SPH, addMat(color, .25), n); m.frustumCulled = false; return m;
}
function setTrail(m, fn, t, dt, r0) {
  for (let i = 0; i < m.count; i++) {
    D.position.copy(fn(t - i * dt)); D.rotation.set(0, 0, 0);
    D.scale.setScalar(Math.max(1e-4, r0 * Math.pow(1 - i / m.count, 1.3))); D.updateMatrix(); m.setMatrixAt(i, D.matrix);
  }
  m.instanceMatrix.needsUpdate = true;
}

class Burst {
  constructor(n, size, seed, colors, vmin = 1.5, vmax = 6) {
    const r = rng(seed);
    this.m = new THREE.InstancedMesh(new THREE.TetrahedronGeometry(size),
      glowify(new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: .55, roughness: .2, emissive: 0xffffff, emissiveIntensity: .12, flatShading: true })), n);
    this.m.frustumCulled = false;
    this.dir = []; this.v = []; this.ax = []; this.spin = []; this.sc = []; this.rr = [];
    for (let i = 0; i < n; i++) {
      const u = r() * 2 - 1, a = r() * TAU, s = Math.sqrt(1 - u * u);
      this.dir.push(V(s * Math.cos(a), u, s * Math.sin(a)));
      this.v.push(lerp(vmin, vmax, Math.pow(r(), .7)));
      this.ax.push(V(r() - .5, r() - .5, r() - .5).normalize());
      this.spin.push(lerp(2, 9, r()));
      this.sc.push(lerp(.5, 1.6, r()));
      this.rr.push([r(), r(), r()]);
      this.m.setColorAt(i, col(colors[i % colors.length], lerp(.8, 1.1, r())));
    }
    this.m.instanceColor.needsUpdate = true;
  }
  burstPos(i, dt, out, k = 2.4) { return out.copy(this.dir[i]).multiplyScalar(this.v[i] * (1 - Math.exp(-k * Math.max(0, dt))) / k); }
  put(i, pos, angle, scale) {
    D.position.copy(pos); D.quaternion.setFromAxisAngle(this.ax[i], angle); D.scale.setScalar(Math.max(1e-4, scale));
    D.updateMatrix(); this.m.setMatrixAt(i, D.matrix);
  }
  done() { this.m.instanceMatrix.needsUpdate = true; }
}

// metallic gyroscope: nested rings that spin on different axes (structure instead of glow)
function mkGyro(r0, n, hex, thick = .014) {
  const grp = new THREE.Group(), rings = [];
  for (let i = 0; i < n; i++) {
    const m = new THREE.Mesh(new THREE.TorusGeometry(r0 * (1 + i * .16), thick * (1 + i * .3), 12, 160),
      new THREE.MeshPhysicalMaterial({ color: hex, metalness: 1, roughness: .18, clearcoat: .6 }));
    grp.add(m); rings.push(m);
  }
  grp.userData.spin = (t, snaps) => rings.forEach((m, i) => {
    const d = i % 2 ? -1 : 1;
    m.rotation.set(d * (t * .5 + i * .7) + snaps * Math.PI / 2 * (i % 3 === 0 ? 1 : 0), d * t * (.3 + i * .12) + snaps * Math.PI / 2 * (i % 3 === 1 ? 1 : 0), i * .4 + snaps * Math.PI / 2 * (i % 3 === 2 ? 1 : 0));
  });
  return grp;
}
// nested wire polyhedra with metal nodes on the vertices
function mkLattice(hex) {
  const grp = new THREE.Group(), layers = [];
  [[new THREE.IcosahedronGeometry(1.15, 0), .9], [new THREE.DodecahedronGeometry(1.55, 0), .55], [new THREE.OctahedronGeometry(.75, 0), .8]].forEach(([geo, k]) => {
    const l = new THREE.Group();
    l.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: col(hex, k), transparent: true })));
    const pos = geo.attributes.position, seen = new Map();
    for (let i = 0; i < pos.count; i++) { const v = V().fromBufferAttribute(pos, i); seen.set(v.toArray().map(x => x.toFixed(3)).join(), v); }
    const nodes = new THREE.InstancedMesh(SPH, new THREE.MeshPhysicalMaterial({ color: hex, metalness: 1, roughness: .2 }), seen.size);
    [...seen.values()].forEach((v, i) => { D.position.copy(v); D.rotation.set(0, 0, 0); D.scale.setScalar(.035); D.updateMatrix(); nodes.setMatrixAt(i, D.matrix); });
    l.add(nodes); grp.add(l); layers.push(l);
  });
  grp.userData.layers = layers;
  return grp;
}

// glowing grid surface (flat or gravity well)
function mkGrid(size, seg, cIn, cOut, N) {
  const geo = new THREE.PlaneGeometry(size, size, seg, seg); geo.rotateX(-Math.PI / 2);
  const mat = new THREE.ShaderMaterial({
    uniforms: { uDepth: { value: 0 }, uA: { value: .9 }, uRip: { value: 0 }, uRipT: { value: 0 }, uN: { value: N },
      cIn: { value: col(cIn) }, cOut: { value: col(cOut) }, uAlpha: { value: 1 }, uMaxR: { value: size / 2 }, uHot: { value: 1 } },
    vertexShader: `uniform float uDepth,uA,uRip,uRipT; varying vec2 vUv; varying float vR;
      void main(){ vec3 p=position; float r=length(p.xz);
        p.y += -uDepth*uA*uA/(r*r+uA*uA) + uRip*sin(r*4.-uRipT*14.)*exp(-uRipT*2.5)*exp(-r*.25)*.25;
        vR=r; vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.); }`,
    fragmentShader: `uniform vec3 cIn,cOut; uniform float uN,uAlpha,uMaxR,uHot; varying vec2 vUv; varying float vR;
      void main(){ vec2 gg=vUv*uN; vec2 f=abs(fract(gg-.5)-.5)/fwidth(gg); float l=1.-min(min(f.x,f.y),1.);
        vec3 c=mix(cIn,cOut,smoothstep(0.,uMaxR*.55,vR)); float fade=1.-smoothstep(uMaxR*.45,uMaxR,vR);
        gl_FragColor=vec4(c*(l*.45+.01)*uAlpha*fade*(1.+uHot*.6*exp(-vR*1.2)),1.); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide,
  });
  return new THREE.Mesh(geo, mat);
}

// soft additive points
function mkPoints(n) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  geo.setAttribute('size', new THREE.BufferAttribute(new Float32Array(n), 1));
  const mat = new THREE.ShaderMaterial({
    uniforms: { uScale: { value: RH / 1920 }, uAlpha: { value: 1 } },
    vertexShader: `attribute float size; attribute vec3 color; varying vec3 vC; uniform float uScale;
      void main(){ vC=color; vec4 mv=modelViewMatrix*vec4(position,1.); gl_PointSize=size*uScale*(380./-mv.z); gl_Position=projectionMatrix*mv; }`,
    fragmentShader: `varying vec3 vC; uniform float uAlpha; void main(){ float d=length(gl_PointCoord-.5); float a=smoothstep(.5,0.,d); gl_FragColor=vec4(vC*a*a*uAlpha,1.); }`,
    transparent: true, blending: THREE.AdditiveBlending, depthWrite: false,
  });
  const p = new THREE.Points(geo, mat); p.frustumCulled = false; return p;
}

// backdrop sphere (follows camera)
const backMat = new THREE.ShaderMaterial({
  uniforms: { cTop: { value: col('#0b0e16') }, cBot: { value: col('#030305') }, cGlow: { value: col('#3a1c12') }, gDir: { value: V(0, .3, -1).normalize() }, uT: { value: 0 } },
  vertexShader: `varying vec3 vD; void main(){ vD=normalize(position); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader: `uniform vec3 cTop,cBot,cGlow,gDir; uniform float uT; varying vec3 vD;
    void main(){ vec3 d=normalize(vD); vec3 c=mix(cBot,cTop,smoothstep(-.7,.8,d.y));
      c+=cGlow*pow(max(dot(d,gDir),0.),6.)*1.3 + cGlow*.35*pow(max(dot(d,-gDir),0.),10.);
      gl_FragColor=vec4(c,1.); }`,
  side: THREE.BackSide, depthWrite: false,
});
const back = new THREE.Mesh(new THREE.SphereGeometry(80, 32, 16), backMat); back.renderOrder = -10; scene.add(back);
function setBack(top, bot, glow, gx = 0, gy = .3, gz = -1) {
  backMat.uniforms.cTop.value.set(top); backMat.uniforms.cBot.value.set(bot); backMat.uniforms.cGlow.value.set(glow);
  backMat.uniforms.gDir.value.set(gx, gy, gz).normalize();
}

// floating dust everywhere
const dust = mkPoints(900);
{ const r = rng(7), p = dust.geometry.attributes.position.array, c = dust.geometry.attributes.color.array, s = dust.geometry.attributes.size.array;
  dust.userData.base = [];
  for (let i = 0; i < 900; i++) { dust.userData.base.push([(r() - .5) * 26, (r() - .5) * 26, (r() - .5) * 26, r()]); const k = lerp(.08, .3, r()); c[i * 3] = k; c[i * 3 + 1] = k * .95; c[i * 3 + 2] = k * .9; s[i] = lerp(.6, 1.6, r()); }
  dust.geometry.attributes.color.needsUpdate = true; dust.geometry.attributes.size.needsUpdate = true; }
scene.add(dust);
function updDust(t, center) {
  const p = dust.geometry.attributes.position.array;
  dust.userData.base.forEach((b, i) => {
    p[i * 3] = center.x + ((b[0] + Math.sin(t * .2 + b[3] * 9) * .6 + 13) % 26 + 26) % 26 - 13;
    p[i * 3 + 1] = center.y + ((b[1] + t * .25 * (0.3 + b[3]) + 13) % 26 + 26) % 26 - 13;
    p[i * 3 + 2] = center.z + ((b[2] + 13) % 26 + 26) % 26 - 13;
  });
  dust.geometry.attributes.position.needsUpdate = true;
}

// ───────────────────────────── text system ─────────────────────────────
const FF = { serif: '"GTSerif"', sans: '"GTSans"', mono: '"GTMono","GTSans"' };
const TX = [];
// tx(t0, t1, text, opts) — {braces} mark highlighted words
const tx = (t0, t1, text, o = {}) => TX.push(Object.assign({ t0, t1, text, x: W / 2, y: 960, size: 80, font: 'serif', weight: 900,
  color: P.paper, hl: P.clay, anim: 'drop', stagger: .045, ls: 0, align: 'center', out: .22, alpha: 1 }, o));
function parse(text, c, hl) { const out = []; let cur = c; for (const ch of text) { if (ch === '{') { cur = hl; continue; } if (ch === '}') { cur = c; continue; } out.push({ ch, c: cur }); } return out; }
function drawText(t, o) {
  if (t < o.t0 || t > o.t1) return;
  const chars = parse(o.text, o.color, o.hl);
  g.font = `${o.weight} ${o.size}px ${FF[o.font]}`;
  const ws = chars.map(c => g.measureText(c.ch).width + o.ls);
  const total = ws.reduce((a, b) => a + b, 0) - o.ls;
  let x0 = o.align === 'center' ? o.x - total / 2 : o.align === 'right' ? o.x - total : o.x;
  const outA = o.t1 >= DUR ? 1 : clamp((o.t1 - t) / o.out);
  const outBlur = (1 - outA) * 14, outDy = -(1 - outA) * o.size * .25;
  const lt = t - o.t0;
  // group slam scale about text centre
  let gs = 1, gA = 1;
  if (o.anim === 'slam') { const p = clamp(lt / .3); gs = 1 + (1 - eOutExpo(p)) * .9; gA = clamp(lt / .05); }
  const cx = x0 + total / 2;
  const sh = o.shake ? o.shake * hit(t, o.t0, 6) : 0;
  let x = x0;
  chars.forEach((c, i) => {
    const w = ws[i];
    let a = gA, dy = 0, blur = 0, sc = 1;
    const li = lt - (o.anim === 'slam' || o.anim === 'fade' ? 0 : i * o.stagger);
    if (o.anim === 'drop') { const p = clamp(li / .42); dy = -(1 - eOutExpo(p)) * o.size * .55; a = clamp(li / .12); blur = (1 - eOutCubic(p)) * 12; }
    else if (o.anim === 'rise') { const p = clamp(li / .5); dy = (1 - eOutExpo(p)) * o.size * .6; a = clamp(li / .15); blur = (1 - eOutCubic(p)) * 10; }
    else if (o.anim === 'pop') { const p = clamp(li / .35); sc = eOutBack(p); a = clamp(li / .08); }
    else if (o.anim === 'type') { a = li >= 0 ? 1 : 0; }
    else if (o.anim === 'fade') { const p = clamp(li / (o.fin || .9)); a = eInOut(p); blur = (1 - p) * 16; }
    a *= outA * o.alpha;
    if (a > .003 && c.ch !== ' ') {
      g.save();
      g.globalAlpha = a;
      const b = blur + outBlur; if (b > .4) g.filter = `blur(${b.toFixed(1)}px)`;
      const px = cx + (x + w / 2 - cx) * gs + nz(t * 40 + i) * sh * 18, py = o.y + dy + outDy + nz(t * 37 + 3 + i) * sh * 18;
      g.translate(px, py); g.scale(gs * sc, gs * sc);
      
      g.fillStyle = c.c; g.textAlign = 'center'; g.textBaseline = 'middle';
      g.fillText(c.ch, 0, 0);
      g.restore();
    }
    x += w;
  });
  if (o.anim === 'type' && o.cursor && lt < (chars.length * o.stagger + .6)) {
    const n = Math.min(chars.length, Math.floor(lt / o.stagger));
    const cxp = x0 + ws.slice(0, n).reduce((a, b) => a + b, 0);
    if (Math.floor(t * 6) % 2 === 0) { g.fillStyle = o.color; g.fillRect(cxp + 4, o.y - o.size * .45, o.size * .5, o.size * .9); }
  }
}
// projected labels pushed by scenes each frame
let LBL = [];
const proj = v => { const p = v.clone().project(camera); return { x: (p.x + 1) / 2 * W, y: (1 - p.y) / 2 * H, z: p.z }; };
function label(v3, text, o = {}) { const p = proj(v3); if (p.z > 1) return; LBL.push(Object.assign({ x: p.x, y: p.y + (o.dy || 0), text, size: 30, font: 'sans', weight: 700, color: P.paper, hl: P.gold, alpha: 1 }, o)); }
function drawLabel(o) {
  const chars = parse(o.text, o.color, o.hl);
  g.font = `${o.weight} ${o.size}px ${FF[o.font]}`;
  const ws = chars.map(c => g.measureText(c.ch).width);
  const total = ws.reduce((a, b) => a + b, 0);
  let x = o.x - total / 2;
  g.save(); g.globalAlpha = clamp(o.alpha); g.textBaseline = 'middle'; g.textAlign = 'left';
  if (o.box) { g.fillStyle = 'rgba(7,8,11,.62)'; g.fillRect(x - 14, o.y - o.size * .72, total + 28, o.size * 1.44); g.strokeStyle = 'rgba(243,239,230,.22)'; g.lineWidth = 1.5; g.strokeRect(x - 14, o.y - o.size * .72, total + 28, o.size * 1.44); }
  chars.forEach((c, i) => { g.fillStyle = c.c; g.fillText(c.ch, x, o.y); x += ws[i]; });
  g.restore();
}

// ───────────────────────────── 2D line layer (3Blue1Brown-style) ─────────────────────────────
// Flat scenes push draw closures into D2; they run on the text canvas before the type, after a beat "punch".
let D2 = [];
function flatBack() { setBack('#0c0d11', '#0a0b0e', '#000000'); fx.flat = true; look(0, 0, 8, 0, 0, 0, 38); }
function paper(t, t0) {
  g.save(); g.strokeStyle = P.paper; g.globalAlpha = .045 * clamp((t - t0) / .5); g.lineWidth = 1; g.beginPath();
  for (let x = 0; x <= W; x += 90) { g.moveTo(x + .5, 0); g.lineTo(x + .5, H); }
  for (let y = 30; y <= H; y += 90) { g.moveTo(0, y + .5); g.lineTo(W, y + .5); }
  g.stroke(); g.restore();
}
const ePen = (t, b, d = .45) => eOutCubic(clamp((t - b) / d));
function pen(c, w = 4, a = 1, dash = null) { g.strokeStyle = c; g.lineWidth = w; g.globalAlpha = clamp(a); g.lineCap = 'round'; g.lineJoin = 'round'; g.setLineDash(dash || []); }
// stroke a polyline up to fraction p of its length; returns the pen tip for arrowheads
function poly(pts, p = 1) {
  if (p <= 0 || pts.length < 2) return null;
  const L = [0]; for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const tgt = L[L.length - 1] * clamp(p);
  g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); let end = pts[0], dir = [1, 0];
  for (let i = 1; i < pts.length; i++) {
    const [x0, y0] = pts[i - 1], [x1, y1] = pts[i]; dir = [x1 - x0, y1 - y0];
    if (L[i] >= tgt) { const f = (tgt - L[i - 1]) / Math.max(1e-6, L[i] - L[i - 1]); end = [x0 + (x1 - x0) * f, y0 + (y1 - y0) * f]; g.lineTo(end[0], end[1]); break; }
    g.lineTo(x1, y1); end = pts[i];
  }
  g.stroke(); return { end, dir };
}
function arc(cx, cy, r, p = 1, a0 = -Math.PI / 2) { if (p <= 0) return; g.beginPath(); g.arc(cx, cy, Math.max(.1, r), a0, a0 + TAU * clamp(p)); g.stroke(); }
function disc(cx, cy, r, c, a) { g.save(); g.globalAlpha = clamp(a); g.fillStyle = c; g.beginPath(); g.arc(cx, cy, Math.max(.1, r), 0, TAU); g.fill(); g.restore(); }
function bez(a, b, bend, n = 48) {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1;
  const cx = mx - dy / l * bend, cy = my + dx / l * bend, pts = [];
  for (let i = 0; i <= n; i++) { const u = i / n; pts.push([(1 - u) * (1 - u) * a[0] + 2 * (1 - u) * u * cx + u * u * b[0], (1 - u) * (1 - u) * a[1] + 2 * (1 - u) * u * cy + u * u * b[1]]); }
  return pts;
}
function arrow(pts, p, c, w = 4, a = 1) {
  pen(c, w, a); const r = poly(pts, p); if (!r || p < .05) return;
  const ang = Math.atan2(r.dir[1], r.dir[0]), sz = 14 + w * 2; g.setLineDash([]);
  g.beginPath(); g.moveTo(r.end[0] - Math.cos(ang - .45) * sz, r.end[1] - Math.sin(ang - .45) * sz); g.lineTo(r.end[0], r.end[1]);
  g.lineTo(r.end[0] - Math.cos(ang + .45) * sz, r.end[1] - Math.sin(ang + .45) * sz); g.stroke();
}
function write(x, y, str, o = {}) {
  g.save(); g.globalAlpha = clamp(o.a ?? 1); g.translate(x, y); if (o.rot) g.rotate(o.rot); if (o.s !== undefined) g.scale(Math.max(1e-3, o.s), Math.max(1e-3, o.s));
  g.font = `${o.weight || 900} ${o.size || 40}px ${FF[o.font || 'serif']}`; g.fillStyle = o.c || P.paper; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(str, 0, 0); g.restore();
}

// ───────────────────────────── HUD ─────────────────────────────
const CHAP = [[0, '00', 'INTRO'], [B(16), '01', '囚徒困境'], [B(32), '02', '纳什均衡'], [B(48), '03', '重复博弈'], [B(64), '04', '零和 / 正和'], [B(80), '05', '生活中的博弈'], [B(96), '06', '结论']];
function drawHUD(t) {
  const a = .62 * clamp(t / .4) * (1 - clamp((t - 58.9) / .6));
  if (a <= 0) return;
  g.save(); g.globalAlpha = a; g.fillStyle = P.paper; g.strokeStyle = P.paper; g.lineWidth = 2;
  const m = 56, L = 34;
  [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]].forEach(([x, y, sx, sy]) => { g.beginPath(); g.moveTo(x, y + sy * L); g.lineTo(x, y); g.lineTo(x + sx * L, y); g.stroke(); });
  g.font = `500 22px ${FF.mono}`; g.textBaseline = 'middle';
  g.textAlign = 'left'; g.fillText('GAME THEORY', 96, 104); g.globalAlpha = a * .7; g.fillText('博弈论 · 60s', 96, 136);
  g.globalAlpha = a; g.textAlign = 'right';
  const s = Math.floor(t), f = Math.floor((t - s) * 30);
  g.fillText(`00:${String(s).padStart(2, '0')}:${String(f).padStart(2, '0')}`, W - 96, 104);
  g.globalAlpha = a * .7; g.fillText(`♩ ${AUDIO.tempo.toFixed(1)}  BEAT ${String(Math.max(0, beatIdx(t)) + 1).padStart(3, '0')}`, W - 96, 136);
  // chapter + progress
  let ci = 0; CHAP.forEach((c, i) => { if (t >= c[0]) ci = i; });
  g.globalAlpha = a; g.textAlign = 'left'; g.fillText(`${CHAP[ci][1]} — ${CHAP[ci][2]}`, 96, H - 150);
  const x0 = 96, x1 = W - 96, gap = 10, n = CHAP.length, sw = (x1 - x0 - gap * (n - 1)) / n;
  CHAP.forEach((c, i) => {
    const e = i + 1 < n ? CHAP[i + 1][0] : DUR, p = clamp((t - c[0]) / (e - c[0]));
    const xx = x0 + i * (sw + gap);
    g.globalAlpha = a * .25; g.fillRect(xx, H - 116, sw, 4);
    g.globalAlpha = a * .95; g.fillRect(xx, H - 116, sw * p, 4);
  });
  // beat tick
  g.globalAlpha = a * kick(t); g.beginPath(); g.arc(W - 104, H - 150, 7, 0, TAU); g.fill();
  g.restore();
}

// ───────────────────────────── scenes ─────────────────────────────
const SC = [];
function mkScene(t0, t1, update) { const grp = new THREE.Group(); grp.visible = false; scene.add(grp); const s = { t0, t1, g: grp, update }; SC.push(s); return s; }
let fx;
function look(px, py, pz, tx_, ty, tz, fov = 38, roll = 0) {
  camera.position.set(px, py, pz); camera.up.set(Math.sin(roll), Math.cos(roll), 0); camera.lookAt(tx_, ty, tz); camera.fov = fov;
}
function shake(amp, t) { if (amp <= 0) return; camera.position.x += nz(t * 31) * amp; camera.position.y += nz(t * 27 + 5) * amp; }

// ═══ S1 · HOOK ═══════════════════════════════════════════════════════════
{
  const TI = B(6);
  const s = mkScene(0, B(16), null);
  const A = new THREE.Mesh(SPH, phys(P.clay)), Bm = new THREE.Mesh(SPH, phys(P.blue));
  const trA = mkTrail(26, col(P.clay, .5)), trB = mkTrail(26, col(P.blue, .5));
  const shock = new THREE.Mesh(new THREE.TorusGeometry(1, .012, 8, 160), addMat(col('#ffe2c8', 1), .7));
  const shards = new Burst(420, .085, 11, [P.clay, P.blue, P.clay, P.blue, '#ffffff']);
  const orbit = new THREE.Group(); orbit.rotation.x = .32;
  orbit.add(A, Bm, trA, trB); s.g.add(orbit, shock, shards.m);
  const lat = mkLattice('#d9cfc0'); s.g.add(lat);
  const ringTilt = new THREE.Euler(1.18, 0, .22); const ringQ = new THREE.Quaternion().setFromEuler(ringTilt);
  const rr = rng(5); const ringR = [...Array(420)].map(() => [2.0 + (rr() - .5) * .45, (rr() - .5) * .1]);
  const orbPos = (t, sgn) => {
    const p = clamp(t / TI), rho = .55 + 1.0 * (1 - eInCubic(p)), th = -.5 + TAU * 1.15 * Math.pow(p, 2.2) + (sgn < 0 ? Math.PI : 0);
    return V(rho * Math.cos(th), .15 * Math.sin(th * 2) * (1 - p), rho * Math.sin(th));
  };
  const tmp = V();
  s.update = (t) => {
    setBack('#0b0d14', '#020203', t < TI ? '#2a140c' : '#3a1a10', 0, .2, -1);
    const pre = t < TI;
    A.visible = Bm.visible = trA.visible = trB.visible = pre;
    if (pre) {
      const pulse = 1 + .14 * kick(t);
      A.position.copy(orbPos(t, 1)); Bm.position.copy(orbPos(t, -1));
      A.scale.setScalar(.55 * pulse); Bm.scale.setScalar(.55 * pulse);
      A.rotation.y = t * 3; Bm.rotation.y = -t * 3;
      A.material.emissiveIntensity = Bm.material.emissiveIntensity = .05 + .15 * kick(t) + .4 * eInExpo(inv(TI - .6, TI, t));
      setTrail(trA, x => orbPos(x, 1), t, .022, .5); setTrail(trB, x => orbPos(x, -1), t, .022, .5);
    }
    // shock wave + shards
    const dt = t - TI;
    shock.visible = dt > 0 && dt < .9;
    if (shock.visible) { shock.scale.setScalar(.3 + 5.5 * eOutExpo(dt / .9)); shock.material.opacity = 1 - dt / .9; shock.rotation.set(Math.PI / 2 - .3, 0, 0); }
    shards.m.visible = dt > 0;
    if (dt > 0) {
      const m = eOutExpo(clamp((t - B(8)) / .7));
      const rot = .45 * Math.max(0, t - B(8)) + .55 * bstep(t, 8, 15) + 7 * eInExpo(inv(B(14), B(16), t));
      for (let i = 0; i < 420; i++) {
        shards.burstPos(i, dt, tmp);
        const [R, hy] = ringR[i]; const ph = TAU * i / 420 + rot;
        const ring = V(R * Math.cos(ph), hy, R * Math.sin(ph)).applyQuaternion(ringQ);
        tmp.lerp(ring, m);
        shards.put(i, tmp, shards.spin[i] * dt, shards.sc[i] * (1 + .5 * kick(t) * m));
      }
      shards.done();
    }
    // title lattice: each layer flips 90° on alternating beats
    lat.visible = t >= B(8);
    if (lat.visible) {
      const e = eOutBack(clamp((t - B(8)) / .5)), sn = bstep(t, 8, 16, .3);
      lat.scale.setScalar(e * (1 + .04 * kick(t)) * (1 + 2.5 * eInExpo(inv(B(14), B(16), t))));
      lat.userData.layers.forEach((l, i) => l.rotation.set(
        (i === 0 ? 1 : 0) * Math.PI / 2 * Math.ceil(sn / 1) * .5 + t * .15 * (i + 1), (i === 1 ? -1 : 1) * (t * .3 + Math.PI / 2 * sn * (i === 1 ? .5 : .25)), (i === 2 ? 1 : 0) * Math.PI / 2 * sn * .5));
    }
    // camera
    const p = clamp(t / TI);
    const dive = eInExpo(inv(B(14), B(16), t));
    const az = pre ? -.25 + .25 * p : .12 * Math.sin((t - TI) * .6);
    const dist = (pre ? 8.6 - 2.2 * eInCubic(p) : 7.6) - 6.4 * dive;
    look(Math.sin(az) * dist, .5 * (1 - dive), Math.cos(az) * dist, 0, 0, 0, 38 - 3 * kick(t) + 20 * dive, .06 * Math.sin(t * .7));
    shake(.32 * hit(t, TI, 3.5) + .05 * kick(t), t);
    fx.flash += .85 * hit(t, TI, 9);
    fx.rgb += 2.2 * hit(t, TI, 3) + .9 * (hit(t, B(8), 6) + hit(t, B(9), 6) + hit(t, B(10), 6));
    fx.zoom += 1.3 * dive + .9 * hit(t, TI, 4);
  };
  tx(.07, B(6) - .05, '两个聪明人', { y: 470, size: 104 });
  tx(B(2), B(6) - .05, '各自做出了{最理性}的选择', { y: 600, size: 58, font: 'sans', weight: 700 });
  tx(B(4), B(6) - .05, '结果——', { y: 1500, size: 124, anim: 'slam' });
  tx(B(6), B(8) - .02, '两个人，{一起输了}。', { y: 560, size: 96, anim: 'slam', hl: P.red, shake: 1.2 });
  tx(B(8), B(16), '博', { x: W / 2 - 250, y: 930, size: 250, anim: 'slam', glow: 30, out: .3 });
  tx(B(9), B(16), '弈', { x: W / 2, y: 930, size: 250, anim: 'slam', glow: 30, out: .3 });
  tx(B(10), B(16), '论', { x: W / 2 + 250, y: 930, size: 250, anim: 'slam', glow: 30, out: .3 });
  tx(B(11), B(16), 'GAME  THEORY', { y: 1110, size: 40, font: 'mono', weight: 500, anim: 'type', stagger: .03, ls: 14, cursor: true });
  tx(B(12), B(16), '一门关于「{我猜你猜我猜}」的学问', { y: 1260, size: 46, font: 'sans', weight: 500, hl: P.gold });
}

// ═══ S2 · PRISONER'S DILEMMA — flat line drawing ═══════════════════════════
{
  const s = mkScene(B(16), B(32), null);
  const MX = 190, MY = 770, CS = 350;
  const YRS = [[[1, 1], [10, 0]], [[0, 10], [5, 5]]];       // [A row][B col] → [A yrs, B yrs]
  const yr = y => y === 0 ? '释放' : `${y}年`;
  s.update = (t) => {
    flatBack();
    D2.push(() => {
      paper(t, B(16));
      if (t < B(20)) {
        [[330, P.clay, 'A', 16], [750, P.blue, 'B', 17]].forEach(([x, c, n, b]) => {
          const p = ePen(t, B(b)), r = 118 * (1 + .04 * kick(t));
          disc(x, 960, r, c, .1 * p); pen(c, 5); arc(x, 960, r, p);
          write(x, 960, n, { size: 96, c, a: clamp((t - B(b) - .15) / .2) });
        });
        pen(P.paper, 3, .6, [16, 14]); poly([[540, 740], [540, 1180]], ePen(t, B(17) + .25, .5));
        arrow([[462, 920], [526, 920]], ePen(t, B(18), .35), P.clay, 3, .8);
        arrow([[618, 1000], [554, 1000]], ePen(t, B(19), .35), P.blue, 3, .8);
        return;
      }
      const fr = ePen(t, B(20), .5), slow = eInOut(inv(B(30), B(32), t));
      pen(P.paper, 3, .9);
      poly([[MX, MY], [MX + 2 * CS, MY], [MX + 2 * CS, MY + 2 * CS], [MX, MY + 2 * CS], [MX, MY]], fr);
      poly([[MX + CS, MY - 24], [MX + CS, MY + 2 * CS + 24]], fr); poly([[MX - 24, MY + CS], [MX + 2 * CS + 24, MY + CS]], fr);
      ['沉默', '背叛'].forEach((w, i) => {
        write(MX + CS * (i + .5), MY - 48, `B ${w}`, { size: 36, c: P.blue, font: 'sans', weight: 700, a: fr });
        write(MX - 52, MY + CS * (i + .5), `A ${w}`, { size: 36, c: P.clay, font: 'sans', weight: 700, a: fr, rot: -Math.PI / 2 });
      });
      // the trap: red hatch + outline on (betray, betray), built slowly in the pre-drop breath
      const ddx = MX + CS, ddy = MY + CS;
      g.save(); g.beginPath(); g.rect(ddx + 3, ddy + 3, CS - 6, CS - 6); g.clip();
      for (let k = 0; k < 16; k++) { pen(P.red, 3, .32); poly([[ddx - 40 + k * 46, ddy + CS + 20], [ddx - 40 + k * 46 + CS + 60, ddy - 40]], clamp(slow * 2.2 - k / 16)); }
      g.restore();
      pen(P.red, 6, 1); poly([[ddx, ddy], [ddx + CS, ddy], [ddx + CS, ddy + CS], [ddx, ddy + CS], [ddx, ddy]], ePen(t, B(28) + .25, .6));
      for (let r = 0; r < 2; r++) for (let c = 0; c < 2; c++) {
        const e = clamp((t - B(20 + r * 2 + c)) / .35), cx = MX + CS * (c + .5), cy = MY + CS * (r + .5);
        const dim = r === 1 && c === 1 ? 1 : 1 - .7 * slow, [ya, yb] = YRS[r][c];
        pen(P.paper, 2, .22 * dim); poly([[cx + 70, cy - 120], [cx - 70, cy + 120]], e);
        write(cx - 72, cy - 58, yr(ya), { size: ya ? 76 : 52, c: P.clay, s: eOutBack(e), a: clamp(e * 4) * dim });
        write(cx + 72, cy + 66, yr(yb), { size: yb ? 76 : 52, c: P.blue, s: eOutBack(e), a: clamp(e * 4) * dim });
      }
      // A's reasoning (switch row), then B's (switch column)
      [25, 26].forEach((bt, c) => { const x = MX + CS * (c + .5) - 72; arrow(bez([x - 6, MY + CS * .5 - 10], [x - 6, MY + CS * 1.5 - 112], 80), ePen(t, B(bt), .4), P.clay, 4, 1 - .6 * slow); });
      [28, 29].forEach((bt, r) => { const y = MY + CS * (r + .5) + 66; arrow(bez([MX + CS * .5 + 130, y + 8], [MX + CS * 1.5 + 10, y + 8], 70), ePen(t, B(bt), .4), P.blue, 4, 1 - .6 * slow); });
    });
  };
  tx(B(16), B(20) - .03, '两个嫌犯', { y: 430, size: 110 });
  tx(B(17), B(20) - .03, '被{分开审问}', { y: 560, size: 64, font: 'sans', weight: 700, hl: P.paper });
  tx(B(18), B(20) - .03, '{合作} = 保持沉默', { y: 1400, size: 48, font: 'sans', weight: 700, hl: P.gold, anim: 'rise' });
  tx(B(19), B(20) - .03, '{背叛} = 出卖对方', { y: 1480, size: 48, font: 'sans', weight: 700, hl: P.red, anim: 'rise' });
  tx(B(20), B(24) - .03, '坐牢年数', { y: 360, size: 84 });
  tx(B(21), B(24) - .03, '{越短越好}  ·  A {橙}  B {蓝}', { y: 460, size: 40, font: 'sans', weight: 500, hl: P.gold });
  tx(B(24), B(28) - .03, '站在 A 的角度：', { y: 340, size: 46, font: 'sans', weight: 700, color: P.clay });
  tx(B(25), B(28) - .03, '无论对方怎么选', { y: 440, size: 88 });
  tx(B(26), B(28) - .03, '{背叛}都更划算', { y: 550, size: 88, hl: P.red });
  tx(B(28), B(30) - .03, 'B 也是这么想的', { y: 440, size: 88, hl: P.blue });
  tx(B(30), B(32) - .02, '于是——', { y: 440, size: 130, anim: 'fade', fin: .9, out: .1 });
}

// ═══ S3 · NASH EQUILIBRIUM (drop) ═════════════════════════════════════════
{
  const s = mkScene(B(32), B(48), null);
  const well = mkGrid(16, 160, '#ff5a3c', '#3550c8', 40); s.g.add(well);
  const NP = 2600, pts = mkPoints(NP); s.g.add(pts);
  const r = rng(21); const PD = [...Array(NP)].map(() => [r(), .04 + .1 * r(), r() * TAU, lerp(.5, 1.4, r())]);
  const core = new THREE.Mesh(SPH, new THREE.MeshBasicMaterial({ color: col('#ff6a3a', 1.2) })); s.g.add(core);
  const A = new THREE.Mesh(SPH, phys(P.clay)), Bm = new THREE.Mesh(SPH, phys(P.blue)); s.g.add(A, Bm);
  const gyro = mkGyro(.85, 5, '#c9a46c', .012); s.g.add(gyro);
  const NM = 36, mono = new THREE.InstancedMesh(new THREE.BoxGeometry(.16, 1, .16).translate(0, .5, 0), new THREE.MeshPhysicalMaterial({ color: 0x23262e, metalness: .9, roughness: .25, clearcoat: .5 }), NM);
  mono.frustumCulled = false; s.g.add(mono);
  const Dp = 3.0, Aa = .9, wy = r_ => -Dp * Aa * Aa / (r_ * r_ + Aa * Aa);
  const cutAz = [0, 1.25, 2.55, 3.9];
  const azAt = t => Math.PI * eOutExpo(clamp((t - B(32)) / .55)) + .12 * (t - B(32))
    + (Math.PI / 4) * [36, 40].reduce((a, b) => a + eOutExpo(clamp((t - B(b)) / .4)), 0);
  s.update = (t) => {
    setBack('#160809', '#040203', '#4a1410', 0, -.2, -1);
    const lt = t - B(32);
    const depth = eOutElastic(clamp(lt / .9));
    well.material.uniforms.uDepth.value = Dp * depth;
    well.material.uniforms.uRip.value = 1; well.material.uniforms.uRipT.value = t - BT[Math.max(32, beatIdx(t))];
    well.material.uniforms.uHot.value = 1 + 1.5 * kick(t);
    // spiral particles
    const pa = pts.geometry.attributes.position.array, pc = pts.geometry.attributes.color.array, ps = pts.geometry.attributes.size.array;
    const hot = col('#ff7a3c', 2.2), cold = col('#5a7cff', 1.2), tc = new THREE.Color();
    for (let i = 0; i < NP; i++) {
      const [s0, rate, a0, sz] = PD[i];
      const ph = (s0 + rate * lt * (1 + 1.5 * eInExpo(inv(B(44), B(48), t)))) % 1;
      const rr_ = .22 + 6.6 * Math.pow(1 - ph, 1.4);
      const ang = a0 + lt * 1.4 / Math.pow(rr_, 1.1) + ph * 3;
      pa[i * 3] = rr_ * Math.cos(ang); pa[i * 3 + 2] = rr_ * Math.sin(ang); pa[i * 3 + 1] = wy(rr_) * depth + .04;
      tc.copy(cold).lerp(hot, clamp(1 - rr_ / 3.5)); const k = clamp(lt * 3) * (.38 + .25 * kick(t));
      pc[i * 3] = tc.r * k; pc[i * 3 + 1] = tc.g * k; pc[i * 3 + 2] = tc.b * k; ps[i] = sz;
    }
    ['position', 'color', 'size'].forEach(n => pts.geometry.attributes[n].needsUpdate = true);
    gyro.position.y = wy(0) * depth + .25; gyro.scale.setScalar(depth); gyro.userData.spin(lt, bstep(t, 32, 48, .3));
    for (let i = 0; i < NM; i++) {
      const a = i / NM * TAU, R = 4.4, bar = 4 * Math.floor(i / 9);                 // each quarter of the ring rises on its own bar
      const up = eOutBack(clamp((t - B(32 + bar) - (i % 9) * .03) / .45));
      D.position.set(Math.cos(a) * R, wy(R) * depth - .05, Math.sin(a) * R); D.rotation.set(0, -a, 0);
      D.scale.set(1, Math.max(1e-3, up * (.5 + 1.6 * ((i * 7) % 5) / 4)), 1); D.updateMatrix(); mono.setMatrixAt(i, D.matrix);
    }
    mono.instanceMatrix.needsUpdate = true;
    core.position.y = wy(0) * depth + .05; core.scale.setScalar(.16 * (1 + .6 * kick(t)));
    // trapped players: try to climb out on B37 / B38, slide back
    const pl = (m, phase, hopBeat) => {
      const hp = clamp((t - B(hopBeat)) / .55), hop = Math.sin(Math.PI * hp) * (hp < 1 ? 1 : 0);
      const rr_ = .48 + 1.45 * hop, ang = 2.6 * lt + phase;
      m.position.set(rr_ * Math.cos(ang), wy(rr_) * depth + .2, rr_ * Math.sin(ang));
      m.scale.setScalar(.2 * (1 + .2 * kick(t))); m.rotation.y = t * 4;
      m.material.emissiveIntensity = .05 + .25 * hop;
    };
    pl(A, 0, 37); pl(Bm, Math.PI, 38);
    // camera: whip on drop, bar snaps, hard cut per beat on B44–B47
    let az = azAt(t), el = .78, dist = 7.4;
    const cutI = beatIdx(t) - 44;
    if (t >= B(44)) { az += 1.1 + cutAz[Math.min(3, cutI)]; el = [.5, 1.05, .35, .9][Math.min(3, cutI)]; dist = [6.2, 7.8, 5.6, 8.4][Math.min(3, cutI)]; }
    const tgtY = -1.25;
    look(Math.sin(az) * dist * Math.cos(el), tgtY + dist * Math.sin(el), Math.cos(az) * dist * Math.cos(el), 0, tgtY, 0,
      40 - 4 * kick(t) + 14 * eInExpo(inv(B(47), B(48), t)), .08 * Math.sin(lt * .8));
    shake(.18 * hit(t, B(32), 3) + .06 * kick(t), t);
    const av = (azAt(t + 1 / 60) - azAt(t)) * 60;
    fx.dir.x += clamp(av * .012, -.09, .09);
    fx.flash += .8 * hit(t, B(32), 9) + .4 * [44, 45, 46, 47].reduce((a, b) => a + hit(t, B(b), 10), 0);
    fx.rgb += 2.5 * hit(t, B(32), 2.5) + 1.2 * [44, 45, 46, 47].reduce((a, b) => a + hit(t, B(b), 7), 0);
    fx.zoom += 1.2 * eInExpo(inv(B(47), B(48), t));
  };
  tx(B(32), B(36) - .03, '纳什均衡', { y: 420, size: 172, anim: 'slam', glow: 40, shake: 1 });
  tx(B(33), B(36) - .03, 'NASH  EQUILIBRIUM', { y: 560, size: 34, font: 'mono', weight: 500, anim: 'type', stagger: .028, ls: 10, cursor: true });
  tx(B(34), B(36) - .03, 'John Nash · 1950', { y: 1460, size: 30, font: 'mono', weight: 500, anim: 'type', stagger: .03, color: P.mute });
  tx(B(36), B(40) - .03, '谁都不愿意', { y: 420, size: 96 });
  tx(B(37), B(40) - .03, '{单独}改变', { y: 540, size: 96 });
  tx(B(38), B(40) - .03, '单方面改变 → 只会更亏', { y: 1460, size: 40, font: 'sans', weight: 500, color: P.mute, anim: 'rise' });
  tx(B(40), B(44) - .03, '每个人都很理性', { y: 420, size: 92 });
  tx(B(42), B(44) - .03, '结局却是{集体最差}', { y: 540, size: 92, hl: P.red });
  ['价格战', '军备竞赛', '内卷', '公地悲剧'].forEach((w, i) => {
    tx(B(44 + i), B(45 + i) - .01, w, { y: 900, size: w.length > 2 ? 170 : 210, anim: 'slam', glow: 36, out: .05, shake: .6 });
    tx(B(44 + i), B(45 + i) - .01, `CASE 0${i + 1} / 04`, { y: 720, size: 30, font: 'mono', weight: 500, anim: 'type', stagger: .02, color: P.red, out: .05 });
  });
}

// ═══ S4 · REPEATED GAME → AXELROD ════════════════════════════════════════
{
  const s = mkScene(B(48), B(64), null);
  const tun = new THREE.Group(); s.g.add(tun);
  const NR = 42, rings = [];
  for (let i = 0; i < NR; i++) {
    const c = i % 2 ? P.gold : P.blue;
    const m = new THREE.Mesh(new THREE.TorusGeometry(1.5, .07, 4, 6), new THREE.MeshPhysicalMaterial({ color: c, metalness: 1, roughness: .22, clearcoat: .6, emissive: c, emissiveIntensity: .04, flatShading: true }));
    m.position.z = -i * 1.3; m.rotation.z = i * .15; tun.add(m); rings.push(m);
  }
  const tunPts = mkPoints(700); tun.add(tunPts);
  { const r = rng(31), p = tunPts.geometry.attributes.position.array, c = tunPts.geometry.attributes.color.array, sz = tunPts.geometry.attributes.size.array;
    for (let i = 0; i < 700; i++) { const a = r() * TAU, rr_ = 1.7 + r() * 2.5; p[i * 3] = Math.cos(a) * rr_; p[i * 3 + 1] = Math.sin(a) * rr_; p[i * 3 + 2] = -r() * 56; const k = .12 + .25 * r(); c[i * 3] = k; c[i * 3 + 1] = k * .85; c[i * 3 + 2] = k * .6; sz[i] = 1.5 + r() * 2.5; }
    ['position', 'color', 'size'].forEach(n => tunPts.geometry.attributes[n].needsUpdate = true); }
  const RA = 2.4, NB = 44, RB = .14, ACX = 540, ACY = 1000, AS = 330 / 2.4;
  const TYPE = [...Array(NB)].map((_, i) => i % 3);           // 0 TFT gold · 1 always-defect red · 2 random violet
  const TCOL = [new THREE.Color(P.gold), new THREE.Color(P.red), new THREE.Color('#a36cf0')];
  const CONV = TYPE.map((ty, i) => ty === 0 ? -1 : B(60 + (i % 3)));
  const sim = { t: -1 };
  const resetSim = () => {
    const r = rng(77); sim.t = B(52); sim.x = []; sim.z = []; sim.vx = []; sim.vz = []; sim.last = Array(NB).fill(-9);
    for (let i = 0; i < NB; i++) {
      let x, z, ok; do { const a = r() * TAU, d = Math.sqrt(r()) * (RA - .3); x = Math.cos(a) * d; z = Math.sin(a) * d; ok = sim.x.every((xx, j) => Math.hypot(xx - x, sim.z[j] - z) > 2.3 * RB); } while (!ok);
      const a = r() * TAU, sp = lerp(1.4, 2.4, r()); sim.x.push(x); sim.z.push(z); sim.vx.push(Math.cos(a) * sp); sim.vz.push(Math.sin(a) * sp);
    }
  };
  const step = dt => {
    const { x, z, vx, vz } = sim;
    for (let i = 0; i < NB; i++) {
      x[i] += vx[i] * dt; z[i] += vz[i] * dt;
      const d = Math.hypot(x[i], z[i]);
      if (d > RA - RB) { const nx = x[i] / d, nz_ = z[i] / d, vn = vx[i] * nx + vz[i] * nz_; if (vn > 0) { vx[i] -= 2 * vn * nx; vz[i] -= 2 * vn * nz_; } x[i] = nx * (RA - RB); z[i] = nz_ * (RA - RB); }
    }
    for (let i = 0; i < NB; i++) for (let j = i + 1; j < NB; j++) {
      const dx = x[j] - x[i], dz = z[j] - z[i], d = Math.hypot(dx, dz);
      if (d < 2 * RB && d > 1e-6) {
        const nx = dx / d, nz_ = dz / d, rv = (vx[j] - vx[i]) * nx + (vz[j] - vz[i]) * nz_;
        if (rv < 0) { vx[i] += rv * nx; vz[i] += rv * nz_; vx[j] -= rv * nx; vz[j] -= rv * nz_; sim.last[i] = sim.last[j] = sim.t; }
        const o = (2 * RB - d) / 2; x[i] -= nx * o; z[i] -= nz_ * o; x[j] += nx * o; z[j] += nz_ * o;
      }
    }
    sim.t += dt;
  };
  const simTo = t => { if (t < sim.t - 1e-6 || sim.t < 0) resetSim(); const dt = 1 / 240; while (sim.t + dt <= t) step(dt); };
  const c_ = new THREE.Color();
  s.update = (t) => {
    const inTun = t < B(52);
    tun.visible = inTun;
    if (inTun) {
      setBack('#060a16', '#020204', '#1c2a4a', 0, 0, -1);
      const warp = eInExpo(inv(B(50), B(52), t));
      const zc = 3.2 - (2.6 * bstep(t, 48, 51, .3) + 44 * warp);
      const sn = bstep(t, 48, 52, .3);
      rings.forEach((m, i) => { m.rotation.z = i * .26 + (i % 2 ? 1 : -1) * (t * .3 + sn * Math.PI / 6); m.rotation.x = .06 * Math.sin(i + t); m.scale.setScalar(1 + .05 * kick(t)); });
      rimA.position.set(-1, 1, zc - 3); rimB.position.set(1, -1, zc - 6);
      look(0, 0, zc, 0, 0, zc - 5, 42 + 30 * warp - 3 * kick(t), .35 * bstep(t, 48, 52, .3) + 2.5 * warp);
      fx.zoom += 1.1 * warp; fx.rgb += 1.6 * warp;
      return;
    }
    flatBack();
    simTo(t);
    D2.push(() => {
      paper(t, B(52));
      pen(P.paper, 3, .85); arc(ACX, ACY, RA * AS + 4, ePen(t, B(52), .6));
      pen(P.paper, 1.5, .18); arc(ACX, ACY, RA * AS * .5, ePen(t, B(52) + .15, .6), Math.PI / 2);
      const appear = clamp((t - B(52) - .2) / .3);
      for (let i = 0; i < NB; i++) {
        const conv = CONV[i] > 0 ? eOutExpo(clamp((t - CONV[i]) / .25)) : 0;
        c_.copy(TCOL[TYPE[i]]).lerp(TCOL[0], conv); const cs = c_.getStyle();
        const x = ACX + sim.x[i] * AS, y = ACY + sim.z[i] * AS, r = RB * AS * (1 + .12 * kick(t)) * appear;
        disc(x, y, r, cs, .85); pen(P.ink, 2, .6); arc(x, y, r, 1);
        const dh = t - sim.last[i]; if (dh >= 0 && dh < .4) { pen(cs, 2, (1 - dh / .4) * .8); arc(x, y, r + 34 * dh / .4, 1); }
        const dc = CONV[i] > 0 ? t - CONV[i] : -1; if (dc >= 0 && dc < .5) { pen(P.gold, 3, 1 - dc / .5); arc(x, y, r + 50 * dc / .5, 1); }
      }
    });
  };
  const roundTxt = [];
  for (let f = Math.floor(B(48) * 30); f < Math.ceil(B(52) * 30); f++) {
    const t = f / 30, warp = eInExpo(inv(B(50), B(52), t));
    const n = t < B(50) ? 1 + Math.floor(bstep(t, 48, 50, .01)) : 3 + Math.floor(197 * warp);
    roundTxt.push([t, n]);
  }
  for (let i = 0; i < roundTxt.length; i++) {
    const [t, n] = roundTxt[i]; const t1 = i + 1 < roundTxt.length ? roundTxt[i + 1][0] : B(52);
    tx(t, t1 - 1e-4, `ROUND ${String(n).padStart(3, '0')}`, { y: 1480, size: 54, font: 'mono', weight: 500, anim: 'type', stagger: 0, out: .001, color: P.gold, ls: 6 });
  }
  tx(B(48), B(52) - .03, '但如果，', { y: 430, size: 104 });
  tx(B(49), B(52) - .03, '游戏{不止一局}呢？', { y: 560, size: 92, hl: P.gold });
  tx(B(52), B(56) - .03, '1980 年', { y: 360, size: 116, anim: 'slam' });
  tx(B(53), B(56) - .03, '阿克塞尔罗德举办了一场', { y: 480, size: 50, font: 'sans', weight: 700 });
  tx(B(54), B(56) - .03, '{策略对战}锦标赛', { y: 550, size: 50, font: 'sans', weight: 700, hl: P.gold });
  tx(B(54), B(56) - .03, 'AXELROD TOURNAMENT · 200 ROUNDS', { y: 1480, size: 28, font: 'mono', weight: 500, anim: 'type', stagger: .02, color: P.mute });
  tx(B(56), B(62) - .03, '冠军，是最简单的那个：', { y: 350, size: 48, font: 'sans', weight: 700 });
  tx(B(57), B(62) - .03, '以牙还牙', { y: 480, size: 150, anim: 'slam', glow: 34, color: P.gold });
  tx(B(57), B(62) - .03, 'TIT  FOR  TAT', { y: 600, size: 32, font: 'mono', weight: 500, anim: 'type', stagger: .03, ls: 8, color: P.gold });
  [['① ', '先{合作}'], ['② ', '被背叛，就{回击}'], ['③ ', '对方回头，就{原谅}'], ['④ ', '规则{简单}，让人看得懂']].forEach(([n, s_], i) => {
    tx(B(58 + i), B(62) - .03, n + s_, { x: 150, align: 'left', y: 1360 + i * 76, size: 44, font: 'sans', weight: 700, hl: P.gold, anim: 'rise' });
  });
  tx(B(62), B(64) - .02, '{合作}，在重复中胜出', { y: 440, size: 88, hl: P.gold, anim: 'slam' });
}

// ═══ S5 · ZERO-SUM vs POSITIVE-SUM — flat ════════════════════════════════
{
  const s = mkScene(B(64), B(80), null);
  const OWN = [[0, 0, 0, 0, 1, 1, 1, 1]];                     // wedge owner per beat: 0 = A, 1 = B
  [[4, 0], [0, 1], [5, 0], [1, 1]].forEach(([w, o]) => { const n = OWN[OWN.length - 1].slice(); n[w] = o; OWN.push(n); });
  const CX = 540, CY = 1010, R0 = 270, sums = [8, 10, 13, 17, 22, 29, 38, 50];
  const rOf = n => R0 * .55 * Math.sqrt(n / 8);
  s.update = (t) => {
    flatBack();
    D2.push(() => {
      paper(t, B(64));
      const merge = eOutExpo(clamp((t - B(70)) / .3));
      if (merge < 1) {                                          // zero-sum: a fixed pie changes hands
        const draw = ePen(t, B(64), .6), split = eOutExpo(clamp((t - B(65)) / .35)) * (1 - merge), bi = clamp(beatIdx(t) - 65, 0, 4);
        for (let k = 0; k < 8; k++) {
          let own = OWN[0][k], prev = own, mv = 1;
          if (t >= B(66)) { own = OWN[bi][k]; prev = OWN[Math.max(0, bi - 1)][k]; mv = eOutExpo(clamp((t - B(65 + bi)) / .3)); }
          const x = CX + lerp(prev ? 1 : -1, own ? 1 : -1, mv) * 70 * split, y = CY - (prev !== own ? Math.sin(Math.PI * mv) * 70 : 0);
          const a0 = Math.PI / 2 + k * TAU / 8, a1 = a0 + TAU / 8, cc = split > .02 ? (own ? P.blue : P.clay) : P.gold, al = 1 - merge;
          g.save(); g.globalAlpha = .22 * draw * al; g.fillStyle = cc; g.beginPath(); g.moveTo(x, y); g.arc(x, y, R0, a0, a1); g.closePath(); g.fill(); g.restore();
          pen(cc, 4, draw * al); g.beginPath(); g.moveTo(x, y); g.arc(x, y, R0, a0, a0 + (a1 - a0) * draw); g.closePath(); g.stroke();
        }
      }
      if (t >= B(70)) {                                         // positive-sum: the whole grows, ring by ring
        const grow = bstep(t, 71, 78, .3), k = Math.min(7, Math.floor(grow)), f = grow - k;
        const out = 1 - clamp((t - B(78)) / .5), burst = eInExpo(clamp((t - B(78)) / .9));
        for (let i = 0; i <= k; i++) { pen(P.gold, 2, .3 * out); arc(CX, CY, rOf(sums[i]) * (1 + burst * (1 + i * .3)), 1); }
        const rr = rOf(lerp(sums[k], sums[Math.min(7, k + 1)], f)) * eOutBack(clamp((t - B(70) - .1) / .4)) * (1 + 2 * burst);
        disc(CX, CY, rr, P.gold, .12 * out); pen(P.gold, 5, out); arc(CX, CY, rr, 1);
        disc(CX - rr, CY, 15, P.clay, out); disc(CX + rr, CY, 15, P.blue, out);
      }
    });
  };
  tx(B(64), B(70) - .03, '零和游戏', { y: 400, size: 140, anim: 'slam' });
  tx(B(65), B(70) - .03, '你多拿一块，我就少一块', { y: 530, size: 50, font: 'sans', weight: 700 });
  [65, 66, 67, 68, 69].forEach((n, i) => {
    const [a, b] = [OWN[i].filter(o => o === 0).length, OWN[i].filter(o => o === 1).length];
    tx(B(n), B(n + 1) - .001, `A {${a}}  :  {${b}} B`, { y: 1440, size: 64, font: 'mono', weight: 500, anim: i ? 'type' : 'rise', stagger: 0, out: .001, color: P.clay, hl: P.paper });
  });
  tx(B(65), B(70) - .03, '总和永远 = 8', { y: 1530, size: 36, font: 'sans', weight: 700, color: P.mute });
  tx(B(70), B(74) - .03, '正和游戏', { y: 400, size: 140, anim: 'slam', color: P.gold, glow: 30 });
  tx(B(71), B(74) - .03, '一起把蛋糕{做大}', { y: 530, size: 54, font: 'sans', weight: 700, hl: P.gold });
  for (let k = 0; k < 8; k++) {
    const n = 70 + k;
    tx(B(n), (k < 7 ? B(n + 1) : B(78)) - .001, `总和 = {${sums[k]}}`, { y: 1460, size: 64, font: 'mono', weight: 500, anim: 'type', stagger: 0, out: .001, hl: P.gold });
  }
  tx(B(74), B(78) - .03, '生活里的大多数游戏', { y: 400, size: 60, font: 'sans', weight: 700 });
  tx(B(75), B(78) - .03, '都{不是零和}', { y: 520, size: 110, hl: P.gold });
  tx(B(78), B(80) - .02, '赢，不一定要别人输', { y: 440, size: 84, anim: 'slam', shake: .6 });
}

// ═══ S6 · LIFE CARDS ═════════════════════════════════════════════════════
{
  const s = mkScene(B(80), B(96), null);
  const cards = [];
  const card = (build) => { const grp = new THREE.Group(); s.g.add(grp); const c = { g: grp, ...build(grp) }; cards.push(c); return c; };
  // 1 谈判
  card(grp => {
    const a = new THREE.Mesh(new THREE.BoxGeometry(.9, .9, .9), phys(P.clay, { metalness: .5 })), b = new THREE.Mesh(new THREE.BoxGeometry(.9, .9, .9), phys(P.blue, { metalness: .5 }));
    const table = new THREE.Mesh(new THREE.BoxGeometry(3.2, .06, 1.4), new THREE.MeshStandardMaterial({ color: 0x1a1d26, metalness: .7, roughness: .3 })); table.position.y = -.5;
    grp.add(a, b, table);
    return { upd: (t, t0) => {
      const walk = eOutExpo(clamp((t - t0 - B(81) + B(80)) / .35));
      a.position.set(-.75 - .9 * walk, 0, -.6 * walk); a.rotation.set(.15, .6 + Math.PI * .75 * walk, 0);
      b.position.set(.75 - .5 * walk, 0, 0); b.rotation.set(.15, -.6 - .4 * walk, 0);
      table.rotation.y = .2;
    } };
  });
  // 2 职场 — compounding coins
  card(grp => {
    const NCN = 30, coins = new THREE.InstancedMesh(new THREE.CylinderGeometry(.55, .55, .075, 48), glowify(new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: .9, roughness: .18, emissive: 0xffffff, emissiveIntensity: .12 })), NCN);
    for (let i = 0; i < NCN; i++) coins.setColorAt(i, col(P.gold, 1));
    coins.frustumCulled = false; grp.add(coins);
    return { upd: (t, t0) => {
      const p = inv(t0, t0 + (B(84) - B(82)) - .1, t), n = 1 + Math.floor(29 * (Math.pow(2, p * 5) - 1) / 31);
      for (let i = 0; i < NCN; i++) {
        const born = t0 + (Math.log2(1 + 31 * (i / 29)) / 5) * ((B(84) - B(82)) - .1), age = t - born;
        D.position.set(Math.sin(i * 1.7) * .04, -1.0 + i * .08 + (1 - eOutExpo(clamp(age / .25))) * 1.5, 0);
        D.rotation.set(.0, i * .3, 0); D.scale.setScalar(i < n ? 1 : 1e-4); D.updateMatrix(); coins.setMatrixAt(i, D.matrix);
      }
      coins.instanceMatrix.needsUpdate = true; grp.rotation.set(.35, t * .8, 0);
    } };
  });
  // 3 冷战 — ice wall shatters
  card(grp => {
    const a = new THREE.Mesh(SPH, phys(P.clay)), b = new THREE.Mesh(SPH, phys(P.blue));
    const ice = new THREE.Mesh(new THREE.BoxGeometry(.1, 1.9, 1.3), new THREE.MeshStandardMaterial({ color: 0x9fd4ff, metalness: .1, roughness: .05, emissive: 0x5aa8ff, emissiveIntensity: .25, transparent: true, opacity: .55 }));
    const br = new Burst(160, .09, 61, ['#cfe9ff', '#9fd4ff', '#ffffff']);
    grp.add(a, b, ice, br.m);
    const tmp = V();
    return { upd: (t, t0) => {
      const tb = t0 + (B(85) - B(84)), dt = t - tb, go = eOutExpo(clamp(dt / .4));
      a.scale.setScalar(.42); b.scale.setScalar(.42);
      a.position.set(-1.0 + .55 * go, 0, 0); b.position.set(1.0 - .3 * go, 0, 0);
      a.rotation.y = t * 2; b.rotation.y = -t * 2;
      ice.visible = dt < 0; br.m.visible = dt >= 0;
      if (dt >= 0) { for (let i = 0; i < 160; i++) { br.burstPos(i, dt, tmp, 3); tmp.x *= .5; tmp.y *= 1.2; br.put(i, tmp, br.spin[i] * dt, br.sc[i]); } br.done(); }
      grp.rotation.set(.1, -.25 + .1 * Math.sin(t), 0);
    } };
  });
  // 4 内卷 — audience stands up in a wave
  card(grp => {
    const C = 7, R = 6, aud = new THREE.InstancedMesh(new THREE.CapsuleGeometry(.11, .26, 4, 10), glowify(new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: .3, roughness: .35, emissive: 0xffffff, emissiveIntensity: .05 })), C * R);
    aud.frustumCulled = false; grp.add(aud);
    const stage = new THREE.Mesh(new THREE.PlaneGeometry(2.6, .9), new THREE.MeshBasicMaterial({ color: col('#ffffff', .55) })); stage.position.set(0, -.25, -2.4); grp.add(stage);
    const c_ = new THREE.Color();
    return { upd: (t, t0) => {
      for (let r = 0; r < R; r++) for (let c = 0; c < C; c++) {
        const i = r * C + c, st = eOutBack(clamp((t - t0 - .12 - (R - 1 - r) * .1 - Math.abs(c - 3) * .03) / .3));
        D.position.set((c - 3) * .38, -.6 + st * .2 + r * .12, (r - 2.5) * .45 - .6); D.rotation.set(0, 0, 0); D.scale.set(1, 1 + .8 * st, 1); D.updateMatrix(); aud.setMatrixAt(i, D.matrix);
        c_.set('#7f8aa3').lerp(new THREE.Color(P.red), st); aud.setColorAt(i, c_);
      }
      aud.instanceMatrix.needsUpdate = true; aud.instanceColor.needsUpdate = true;
      grp.rotation.set(.35, .35 * Math.sin(t * .6), 0);
    } };
  });
  // 5 价格战 — staircase down, 16th-note stutter
  card(grp => {
    const bars = [...Array(8)].map((_, k) => { const m = new THREE.Mesh(new THREE.BoxGeometry(.28, 1, .28).translate(0, .5, 0), new THREE.MeshStandardMaterial({ color: k % 2 ? P.blue : P.clay, metalness: .4, roughness: .3, emissive: k % 2 ? P.blue : P.clay, emissiveIntensity: .4 })); grp.add(m); return m; });
    const red = new THREE.Color(P.red);
    return { upd: (t, t0) => {
      const span = (B(90) - B(88)) - .05;
      bars.forEach((m, k) => {
        const tb = t0 + k * span / 8, e = eOutBack(clamp((t - tb) / .14)), h = lerp(1.9, .18, k / 7);
        m.position.set((k - 3.5) * .36, -.95, 0); m.scale.y = Math.max(1e-3, h * e);
        m.material.emissive.set(k % 2 ? P.blue : P.clay).lerp(red, k / 7); m.material.emissiveIntensity = .15 + .4 * hit(t, tb, 8);
      });
      grp.rotation.set(.18, -.35 + .1 * Math.sin(t), 0);
    } };
  });
  // 6 合作 — rings interlock
  card(grp => {
    const a = new THREE.Mesh(new THREE.TorusGeometry(.62, .12, 32, 120), phys(P.clay, { metalness: .8, roughness: .15 }));
    const b = new THREE.Mesh(new THREE.TorusGeometry(.62, .12, 32, 120), phys(P.blue, { metalness: .8, roughness: .15 }));
    grp.add(a, b);
    return { upd: (t, t0) => {
      const j = eOutBack(clamp((t - t0 - (B(91) - B(90))) / .4));
      a.position.set(lerp(-1.3, -.31, j), 0, 0); b.position.set(lerp(1.3, .31, j), 0, 0);
      a.rotation.set(0, 0, 0); b.rotation.set(Math.PI / 2 * j, 0, 0);
      a.material.emissiveIntensity = b.material.emissiveIntensity = .05 + .3 * hit(t, t0 + (B(91) - B(90)) + .3, 5);
      grp.rotation.set(.3, t * .9, .2);
    } };
  });
  const TINT = ['#121018', '#141006', '#081018', '#180808', '#16080a', '#0a1014'];
  s.update = (t) => {
    const k = clamp(Math.floor((beatIdx(t) - 80) / 2), 0, 6);
    cards.forEach((c, i) => c.g.visible = i === k && k < 6);
    if (k < 6) {
      const t0 = B(80 + 2 * k);
      setBack(TINT[k], '#020203', TINT[k], 0, .5, -1);
      cards[k].upd(t, t0);
      cards[k].g.scale.setScalar([.72, 1, 1, .62, 1, 1][k]); cards[k].g.position.y = [0, 0, 0, -.35, 0, 0][k];
      const lt = t - t0, dirS = k % 2 ? -1 : 1;
      const az = dirS * (.5 * (1 - eOutExpo(clamp(lt / .3)))) + .05 * Math.sin(t);
      look(Math.sin(az) * 6.2, .9, Math.cos(az) * 6.2, 0, -.15, 0, 34 - 3 * kick(t));
      fx.dir.x += dirS * .07 * (1 - clamp(lt / .18));
      fx.flash += .3 * hit(t, t0, 12);
      fx.rgb += 1.2 * hit(t, t0, 7);
    } else {
      flatBack();
      D2.push(() => {
        paper(t, B(92));
        pen(P.gold, 5, 1); poly([[290, 628], [790, 628]], ePen(t, B(94) + .2, .4));
        pen(P.paper, 2, .5);                                    // six small marks — one per life case — tick in on the beat
        for (let i = 0; i < 6; i++) { const x = 315 + i * 90, e = ePen(t, B(92) + i * .09, .3); arc(x, 1000, 22, e); }
        const e2 = ePen(t, B(95), .3); pen(P.gold, 4, 1); for (let i = 0; i < 6; i++) arc(315 + i * 90, 1000, 22, e2);
      });
    }
  };
  const L = [['谈判', '敢{离席}的人，才有筹码'], ['职场', '信誉，像{复利}一样增长'], ['冷战', '先开口的人，在{破局}'], ['内卷', '全场都站起来，{谁也没看得更清}'], ['价格战', '你降我也降，{两败俱伤}'], ['合作', '把一次交易，变成{长期关系}']];
  L.forEach(([h, sub], i) => {
    const t0 = B(80 + 2 * i), t1 = B(82 + 2 * i) - .01;
    tx(t0, t1, `LIFE · 0${i + 1} / 06`, { y: 330, size: 28, font: 'mono', weight: 500, anim: 'type', stagger: .015, out: .05, color: P.gold, ls: 4 });
    tx(t0, t1, h, { y: 470, size: h.length > 2 ? 150 : 170, anim: 'slam', out: .05, glow: 26 });
    tx(t0 + .12, t1, sub, { y: 610, size: 50, font: 'sans', weight: 700, hl: P.gold, out: .05, stagger: .02 });
  });
  tx(B(92), B(96) - .02, '看懂规则的人', { y: 420, size: 100 });
  tx(B(94), B(96) - .02, '才能{改写规则}', { y: 550, size: 100, hl: P.gold });
}

// ═══ S7 · CONCLUSION ═════════════════════════════════════════════════════
{
  const s = mkScene(B(96), DUR + 1, null);
  const A = new THREE.Mesh(SPH, phys(P.clay)), Bm = new THREE.Mesh(SPH, phys(P.blue));
  const trA = mkTrail(70, col(P.gold, .3)), trB = mkTrail(70, col(P.gold, .3));
  const helix = new THREE.Group(); helix.add(A, Bm, trA, trB);
  s.g.add(helix);
  const TF = B(108);
  const pos = (t, sgn) => {
    const th = 1.5 * (t - B(96)) + .7 * bstep(Math.min(t, TF), 96, 108, .4) + (sgn < 0 ? Math.PI : 0);
    const rho = lerp(1.35, .55, eInOut(inv(B(96), TF, t)));
    return V(rho * Math.cos(th), .38 * Math.sin(th * 1.5 + (sgn < 0 ? 1 : 0)), rho * Math.sin(th));
  };
  s.update = (t) => {
    const pre = t < TF;
    helix.visible = pre;
    if (pre) {
      setBack('#07070a', '#010101', '#1a140a', 0, .2, -1);
      A.position.copy(pos(t, 1)); Bm.position.copy(pos(t, -1));
      A.scale.setScalar(.3 * (1 + .15 * kick(t))); Bm.scale.setScalar(.3 * (1 + .15 * kick(t)));
      A.material.emissiveIntensity = Bm.material.emissiveIntensity = .05 + .15 * kick(t) + .3 * eInExpo(inv(TF - .5, TF, t));
      setTrail(trA, x => pos(x, 1), t, .02, .2); setTrail(trB, x => pos(x, -1), t, .02, .2);
      look(0, .9, 6.4 - .6 * inv(B(96), DUR, t), 0, .75, 0, 36 - 2.5 * kick(t));
    } else {                                                    // flat ending: two circles overlap; the overlap is cooperation
      flatBack();
      D2.push(() => {
        paper(t, TF);
        const CX = 540, CY = 1060, R = 200, j = eOutCubic(clamp((t - TF - .25) / .7)), d = lerp(250, 112, j), p = ePen(t, TF, .5);
        g.save(); g.beginPath(); g.arc(CX - d, CY, R, 0, TAU); g.clip(); disc(CX + d, CY, R, P.gold, .55 * j); g.restore();
        pen(P.clay, 5); arc(CX - d, CY, R, p, Math.PI / 2); pen(P.blue, 5); arc(CX + d, CY, R, p, Math.PI / 2);
        write(CX - d - 95, CY, 'A', { size: 72, c: P.clay, a: p }); write(CX + d + 95, CY, 'B', { size: 72, c: P.blue, a: p });
        write(CX, CY, '合作', { size: 54, c: P.paper, a: clamp((j - .6) * 3) });
      });
    }
    fx.flash += .9 * hit(t, TF, 4);
    fx.fade = eInOut(inv(59.25, 59.95, t));
  };
  tx(B(96), B(100) - .03, '博弈论的核心', { y: 400, size: 60, font: 'sans', weight: 700, color: P.mute });
  tx(B(97), B(100) - .03, '只有一句话', { y: 490, size: 60, font: 'sans', weight: 700 });
  tx(B(100), B(104) - .03, '你的最优选择，', { y: 400, size: 100 });
  tx(B(102), B(104) - .03, '取决于{别人}的选择。', { y: 530, size: 100, glow: 0 });
  tx(B(104), B(108) - .03, '所以，别只想赢这一局', { y: 400, size: 62, font: 'sans', weight: 700 });
  tx(B(106), B(108) - .03, '让合作，', { y: 520, size: 112, color: P.paper });
  tx(B(107), B(108) - .03, '成为彼此的{最优解}', { y: 650, size: 100, hl: P.gold });
  tx(TF, DUR, 'GAME  THEORY', { y: 330, size: 34, font: 'mono', weight: 500, anim: 'type', stagger: .03, ls: 10, color: P.gold });
  tx(TF, DUR, '博弈论', { y: 470, size: 170, anim: 'slam', glow: 40 });
  tx(B(109), DUR, '你的最优选择，取决于别人的选择', { y: 1580, size: 44, font: 'sans', weight: 700 });
  tx(B(110), DUR, '让合作，成为彼此的{最优解}', { y: 1660, size: 44, font: 'sans', weight: 700, hl: P.gold });
}

// ───────────────────────────── frame ─────────────────────────────
function renderAt(t) {
  fx = { flash: 0, rgb: .15 * kick(t), zoom: 0, dir: new THREE.Vector2(), sat: 1, vig: 1, fade: 0, grain: .04, flat: false };
  LBL = []; D2 = [];
  rimA.position.set(-4, 2, -2); rimB.position.set(4, -1, -2);
  let active = SC[0];
  SC.forEach(s => { s.g.visible = false; if (t >= s.t0) active = s; });
  active.g.visible = true;
  active.update(t);
  if (active !== SC[0]) { fx.flash += .4 * hit(t, active.t0, 12); fx.rgb += 1.4 * hit(t, active.t0, 5); }
  camera.updateProjectionMatrix();
  back.position.copy(camera.position);
  updDust(t, camera.position);
  dust.material.uniforms.uAlpha.value = fx.flat ? 0 : .8 + .6 * low(t);
  if (fx.flat) { fx.rgb *= .2; fx.flash *= .5; }
  bloom.strength = .16 + .06 * kick(t);

  composer.render();

  g.clearRect(0, 0, W, H);
  const pk = 1 + .012 * kick(t);
  D2.forEach(f => { g.save(); g.translate(W / 2, H / 2); g.scale(pk, pk); g.translate(-W / 2, -H / 2); f(); g.restore(); });
  TX.forEach(o => drawText(t, o));
  LBL.forEach(drawLabel);
  drawHUD(t);
  textTex.needsUpdate = true;

  const u = finalMat.uniforms;
  u.tScene.value = composer.readBuffer.texture;
  u.uTime.value = t; u.uRGB.value = Math.min(.9, fx.rgb * .35); u.uZoom.value = clamp(fx.zoom, 0, 1.6);
  u.uDir.value.set(clamp(fx.dir.x, -.12, .12), clamp(fx.dir.y, -.12, .12));
  u.uN.value = (u.uZoom.value > .01 || u.uDir.value.length() > .002) ? 14 : 1;
  u.uFlash.value = Math.min(.32, fx.flash * .3); u.uFade.value = fx.fade; u.uSat.value = fx.sat; u.uVig.value = fx.vig; u.uGrain.value = fx.grain;
  renderer.setRenderTarget(null);
  renderer.render(finalScene, orthoCam);
}

// ───────────────────────────── boot ─────────────────────────────
const fonts = [['GTSerif', 'NotoSerifSC-900', 900], ['GTSerif', 'NotoSerifSC-700', 700], ['GTSans', 'NotoSansSC-500', 500], ['GTSans', 'NotoSansSC-700', 700], ['GTSans', 'NotoSansSC-900', 900], ['GTMono', 'IBMPlexMono-500', 500]];
await Promise.all(fonts.map(async ([fam, file, w]) => { const f = new FontFace(fam, `url(./assets/fonts/${file}.woff2)`, { weight: String(w) }); await f.load(); document.fonts.add(f); }));

window.renderAt = renderAt;
window.grab = async (q = .95) => {
  const blob = await new Promise(r => renderer.domElement.toBlob(r, 'image/jpeg', q));
  const a = new Uint8Array(await blob.arrayBuffer()); let s = '';
  for (let i = 0; i < a.length; i += 0x8000) s += String.fromCharCode.apply(null, a.subarray(i, i + 0x8000));
  return btoa(s);
};
window.glInfo = () => { const gl = renderer.getContext(); const e = gl.getExtension('WEBGL_debug_renderer_info'); return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); };
window.DURATION = DUR;

// live preview: index.html?play — click to start with music, space = pause, ←/→ = seek 2s, [ ] = seek 1 beat
if (Q.has('play')) {
  const cv = renderer.domElement;
  Object.assign(cv.style, { height: '100vh', width: 'auto', margin: '0 auto' });
  document.body.style.background = '#000';
  const au = new Audio('./assets/audio/bgm60.m4a');
  const hud = document.createElement('div');
  Object.assign(hud.style, { position: 'fixed', left: '12px', bottom: '10px', color: '#aaa', font: '12px monospace' });
  hud.textContent = '点击开始 · space 暂停 · ←/→ 跳 2s · [ ] 跳一拍'; document.body.appendChild(hud);
  let t0 = Q.get('t') ? parseFloat(Q.get('t')) : 0; au.currentTime = t0;
  renderAt(t0);
  const loop = () => { const t = Math.min(DUR - 1e-3, au.currentTime); renderAt(t); hud.textContent = `${t.toFixed(2)}s · beat ${beatIdx(t) + 1}`; requestAnimationFrame(loop); };
  document.addEventListener('click', () => { au.paused ? au.play() : au.pause(); }, { once: false });
  document.addEventListener('keydown', e => {
    if (e.code === 'Space') au.paused ? au.play() : au.pause();
    if (e.code === 'ArrowRight') au.currentTime = Math.min(DUR, au.currentTime + 2);
    if (e.code === 'ArrowLeft') au.currentTime = Math.max(0, au.currentTime - 2);
    if (e.key === ']') { const i = beatIdx(au.currentTime); au.currentTime = BT[i + 1]; }
    if (e.key === '[') { const i = beatIdx(au.currentTime); au.currentTime = BT[Math.max(0, i - 1)]; }
  });
  requestAnimationFrame(loop);
} else if (Q.has('t')) {
  renderAt(parseFloat(Q.get('t')));
}
window.ready = true;
