# Advanced Three.js

Post-processing, VR/AR, and advanced optimization techniques.

## Post-Processing

### EffectComposer Setup

```javascript
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const composer = new EffectComposer(renderer);

// Base scene render
composer.addPass(new RenderPass(scene, camera));

// Bloom effect
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5,   // strength
  0.4,   // radius
  0.85   // threshold
);
composer.addPass(bloomPass);

// Required for correct color output
composer.addPass(new OutputPass());

// In animation loop, replace renderer.render() with:
composer.render();
```

### Common Post-Processing Passes

```javascript
// Ambient Occlusion
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';
const ssaoPass = new SSAOPass(scene, camera, width, height);
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;

// Anti-aliasing
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
const smaaPass = new SMAAPass(width, height);

// Depth of Field
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
const bokehPass = new BokehPass(scene, camera, {
  focus: 10,
  aperture: 0.025,
  maxblur: 0.01,
});

// Film Grain
import { FilmPass } from 'three/addons/postprocessing/FilmPass.js';
const filmPass = new FilmPass(0.35, false);

// Outline
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';
const outlinePass = new OutlinePass(
  new THREE.Vector2(width, height), scene, camera
);
outlinePass.selectedObjects = [selectedMesh];
```

### Custom ShaderPass

```javascript
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

const customShader = {
  uniforms: {
    tDiffuse: { value: null },
    uTime: { value: 0 },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float uTime;
    varying vec2 vUv;
    
    void main() {
      vec2 uv = vUv;
      uv.x += sin(uv.y * 10.0 + uTime) * 0.01;
      gl_FragColor = texture2D(tDiffuse, uv);
    }
  `,
};

const customPass = new ShaderPass(customShader);
composer.addPass(customPass);

// Update in animate loop:
customPass.uniforms.uTime.value = elapsed;
```

## VR/AR (WebXR)

### VR Setup

```javascript
import { VRButton } from 'three/addons/webxr/VRButton.js';

renderer.xr.enabled = true;
document.body.appendChild(VRButton.createButton(renderer));

// Replace requestAnimationFrame with XR-compatible loop
renderer.setAnimationLoop(animate);

function animate() {
  // Your animation code
  renderer.render(scene, camera);
}
```

### AR Setup

```javascript
import { ARButton } from 'three/addons/webxr/ARButton.js';

renderer.xr.enabled = true;
document.body.appendChild(ARButton.createButton(renderer, {
  requiredFeatures: ['hit-test'],
}));

// For AR, typically use transparent background
renderer.setClearColor(0x000000, 0);
scene.background = null;

// Hit testing for placing objects
let hitTestSource = null;
let hitTestSourceRequested = false;

renderer.setAnimationLoop((timestamp, frame) => {
  if (frame) {
    const referenceSpace = renderer.xr.getReferenceSpace();
    const session = renderer.xr.getSession();
    
    if (!hitTestSourceRequested) {
      session.requestReferenceSpace('viewer').then((refSpace) => {
        session.requestHitTestSource({ space: refSpace }).then((source) => {
          hitTestSource = source;
        });
      });
      hitTestSourceRequested = true;
    }
    
    if (hitTestSource) {
      const hitTestResults = frame.getHitTestResults(hitTestSource);
      if (hitTestResults.length > 0) {
        const hit = hitTestResults[0];
        const pose = hit.getPose(referenceSpace);
        // Use pose.transform.position for placement
      }
    }
  }
  renderer.render(scene, camera);
});
```

### XR Controllers

```javascript
const controller1 = renderer.xr.getController(0);
controller1.addEventListener('selectstart', onSelectStart);
controller1.addEventListener('selectend', onSelectEnd);
scene.add(controller1);

// Controller model
import { XRControllerModelFactory } from 'three/addons/webxr/XRControllerModelFactory.js';
const controllerModelFactory = new XRControllerModelFactory();
const controllerGrip1 = renderer.xr.getControllerGrip(0);
controllerGrip1.add(controllerModelFactory.createControllerModel(controllerGrip1));
scene.add(controllerGrip1);
```

## Advanced Optimization

### GPU Instancing with Custom Attributes

```javascript
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial();
const count = 10000;
const mesh = new THREE.InstancedMesh(geometry, material, count);

// Per-instance colors
const colors = new Float32Array(count * 3);
for (let i = 0; i < count; i++) {
  colors[i * 3] = Math.random();
  colors[i * 3 + 1] = Math.random();
  colors[i * 3 + 2] = Math.random();
}
geometry.setAttribute('instanceColor', new THREE.InstancedBufferAttribute(colors, 3));

// Enable vertex colors in material
material.vertexColors = true;
```

### Texture Optimization

```javascript
// Compressed textures (KTX2)
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
const ktx2Loader = new KTX2Loader()
  .setTranscoderPath('path/to/basis/')
  .detectSupport(renderer);

ktx2Loader.load('texture.ktx2', (texture) => {
  material.map = texture;
  material.needsUpdate = true;
});

// Texture atlas
const texture = new THREE.TextureLoader().load('atlas.png');
texture.repeat.set(0.25, 0.25);  // 4x4 atlas
texture.offset.set(0.25, 0.5);   // select specific tile
```

### Level of Detail (LOD)

```javascript
const lod = new THREE.LOD();

// High detail (close)
lod.addLevel(highDetailMesh, 0);
// Medium detail
lod.addLevel(mediumDetailMesh, 50);
// Low detail (far)
lod.addLevel(lowDetailMesh, 100);

scene.add(lod);

// In animate loop:
lod.update(camera);
```

### Object Pooling

```javascript
class ObjectPool {
  constructor(createFn, size = 100) {
    this.pool = Array.from({ length: size }, createFn);
    this.active = new Set();
  }
  
  acquire() {
    const obj = this.pool.pop();
    if (obj) {
      this.active.add(obj);
      obj.visible = true;
    }
    return obj;
  }
  
  release(obj) {
    if (this.active.has(obj)) {
      this.active.delete(obj);
      obj.visible = false;
      this.pool.push(obj);
    }
  }
}

const bulletPool = new ObjectPool(() => {
  const mesh = new THREE.Mesh(bulletGeometry, bulletMaterial);
  mesh.visible = false;
  scene.add(mesh);
  return mesh;
}, 200);
```

### Frustum Culling & Occlusion

```javascript
// Manual frustum check
const frustum = new THREE.Frustum();
const projScreenMatrix = new THREE.Matrix4();

function updateFrustum() {
  projScreenMatrix.multiplyMatrices(
    camera.projectionMatrix,
    camera.matrixWorldInverse
  );
  frustum.setFromProjectionMatrix(projScreenMatrix);
}

function isVisible(object) {
  return frustum.intersectsObject(object);
}

// Disable auto-update for static objects
staticMesh.matrixAutoUpdate = false;
staticMesh.updateMatrix();  // Call once after positioning
```

### Memory Management

```javascript
// Dispose pattern
function disposeObject(obj) {
  if (obj.geometry) obj.geometry.dispose();
  if (obj.material) {
    if (Array.isArray(obj.material)) {
      obj.material.forEach(m => disposeMaterial(m));
    } else {
      disposeMaterial(obj.material);
    }
  }
}

function disposeMaterial(material) {
  material.dispose();
  for (const key of Object.keys(material)) {
    const value = material[key];
    if (value && typeof value.dispose === 'function') {
      value.dispose();  // Disposes textures
    }
  }
}

// Clean up scene
function clearScene() {
  while (scene.children.length > 0) {
    const child = scene.children[0];
    disposeObject(child);
    scene.remove(child);
  }
}
```

## Environment & Lighting

### HDR Environment Maps

```javascript
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

new RGBELoader().load('environment.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.background = texture;
  scene.environment = texture;  // PBR materials use this for reflections
});
```

### Light Probes

```javascript
import { LightProbeGenerator } from 'three/addons/lights/LightProbeGenerator.js';

// From cube render target
const cubeCamera = new THREE.CubeCamera(0.1, 1000, 256);
cubeCamera.update(renderer, scene);
const lightProbe = LightProbeGenerator.fromCubeRenderTarget(renderer, cubeCamera.renderTarget);
scene.add(lightProbe);
```
