---
name: threejs
description: Create 3D graphics, visualizations, and interactive experiences using Three.js. Use this skill when the user asks to build 3D scenes, WebGL/WebGPU applications, 3D data visualizations, interactive 3D components, games, or any browser-based 3D content. Covers scene setup, geometries, materials, lighting, cameras, animations, controls, shaders (TSL), and performance optimization.
---

# Three.js Development

Create 3D browser experiences with Three.js. This skill covers scene construction, rendering pipelines, and interactive 3D applications.

> **Library Versions (2026)**
> - Three.js: r171+
> - Uses WebGPU by default with WebGL2 fallback
> - TSL (Three.js Shading Language) for custom shaders

## Decision Frameworks

### When to Use Which Renderer

```
Need WebGPU features (compute shaders, TSL, better performance)?
  → WebGPURenderer (recommended for 2026)

Need maximum browser compatibility (Safari < 18, older devices)?
  → WebGLRenderer

Unsure?
  → WebGPURenderer (automatically falls back to WebGL2)
```

### When to Use Which Material

```
Is it unlit (UI, wireframe, stylized, full bright)?
  → MeshBasicNodeMaterial

Is it realistic/PBR (default for most 3D)?
  ├─ Standard roughness/metalness → MeshStandardNodeMaterial
  ├─ Need glass/transmission/refraction? → MeshPhysicalNodeMaterial
  ├─ Need clearcoat (car paint, lacquer)? → MeshPhysicalNodeMaterial
  └─ Need subsurface scattering? → MeshPhysicalNodeMaterial

Is it custom/procedural?
  → TSL + NodeMaterial (see references/tsl-shaders.md)

Performance critical (thousands of objects)?
  → MeshLambertNodeMaterial (diffuse only, fast)
```

### When to Use Which Camera

```
3D scene with depth/perspective?
  → PerspectiveCamera (most common)

2D game, UI overlay, isometric view?
  → OrthographicCamera

VR/AR application?
  → WebXR handles cameras automatically
```

### When to Use Which Controls

```
Inspect/view 3D model from all angles?
  → OrbitControls

First-person exploration/game?
  → PointerLockControls

Flight simulator, free camera?
  → FlyControls

Touch-friendly product viewer?
  → OrbitControls with touch enabled

Scroll-driven animation?
  → Custom (or use R3F ScrollControls)
```

## Core Setup (2026 - WebGPU)

```javascript
import * as THREE from 'three/webgpu'

// Scene
const scene = new THREE.Scene()

// Camera
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
)
camera.position.z = 5

// Renderer (WebGPU with automatic WebGL2 fallback)
const renderer = new THREE.WebGPURenderer({ antialias: true })
await renderer.init() // Required for WebGPU
renderer.setSize(window.innerWidth, window.innerHeight)
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.toneMapping = THREE.ACESFilmicToneMapping
renderer.outputColorSpace = THREE.SRGBColorSpace
document.body.appendChild(renderer.domElement)

// Animation loop (use setAnimationLoop for WebGPU/WebXR)
function animate() {
  renderer.render(scene, camera)
}
renderer.setAnimationLoop(animate)

// Resize handling
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
})
```

## Essential Components

### Geometries
- **Primitives**: `BoxGeometry`, `SphereGeometry`, `PlaneGeometry`, `CylinderGeometry`, `TorusGeometry`, `ConeGeometry`
- **Complex**: `TorusKnotGeometry`, `IcosahedronGeometry`, `OctahedronGeometry`
- **Custom**: `BufferGeometry` with `Float32Array` attributes for vertices, normals, UVs
- **Text**: `TextGeometry` (requires FontLoader)

### Materials (NodeMaterial for WebGPU compatibility)

| Material | Use Case |
|----------|----------|
| `MeshBasicNodeMaterial` | Unlit, UI, wireframes |
| `MeshStandardNodeMaterial` | PBR, realistic surfaces (default) |
| `MeshPhysicalNodeMaterial` | Glass, clearcoat, transmission |
| `MeshLambertNodeMaterial` | Performance, diffuse only |
| `SpriteNodeMaterial` | Billboards, particles |

```javascript
// Standard PBR material
const material = new THREE.MeshStandardNodeMaterial({
  color: 0x00ff00,
  roughness: 0.5,
  metalness: 0.5
})

// Physical material with transmission (glass)
const glass = new THREE.MeshPhysicalNodeMaterial({
  transmission: 1,
  roughness: 0,
  ior: 1.5,
  thickness: 0.5
})
```

### Lights
- `AmbientLight` - uniform fill light, no shadows
- `DirectionalLight` - sun-like parallel rays, supports shadows
- `PointLight` - omnidirectional from a point
- `SpotLight` - cone-shaped with falloff
- `HemisphereLight` - sky/ground gradient
- `RectAreaLight` - rectangular area light

```javascript
// Typical lighting setup
scene.add(new THREE.AmbientLight(0xffffff, 0.4))

const sun = new THREE.DirectionalLight(0xffffff, 1)
sun.position.set(5, 10, 5)
sun.castShadow = true
sun.shadow.mapSize.setScalar(2048)
scene.add(sun)
```

### Shadows

```javascript
renderer.shadowMap.enabled = true
renderer.shadowMap.type = THREE.PCFSoftShadowMap

light.castShadow = true
light.shadow.mapSize.width = 2048
light.shadow.mapSize.height = 2048
light.shadow.camera.near = 0.5
light.shadow.camera.far = 50

mesh.castShadow = true
groundMesh.receiveShadow = true
```

## Common Imports

```javascript
// Controls
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js'

// Loaders
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js'
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js'
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js'

// Compression decoders
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'

// TSL for custom shaders
import { color, uniform, uv, sin, time, mix } from 'three/tsl'
```

## Animation Patterns

### Clock-based Animation

```javascript
const clock = new THREE.Clock()

function animate() {
  const delta = clock.getDelta()
  const elapsed = clock.getElapsedTime()

  mesh.rotation.y += delta * 0.5
  mesh.position.y = Math.sin(elapsed) * 0.5

  renderer.render(scene, camera)
}
renderer.setAnimationLoop(animate)
```

### GLTF Animation

```javascript
let mixer
const loader = new GLTFLoader()

loader.load('/character.glb', (gltf) => {
  scene.add(gltf.scene)
  mixer = new THREE.AnimationMixer(gltf.scene)

  // Play all animations
  gltf.animations.forEach((clip) => {
    mixer.clipAction(clip).play()
  })
})

// In animate loop
function animate() {
  const delta = clock.getDelta()
  if (mixer) mixer.update(delta)
  renderer.render(scene, camera)
}
```

## Interaction & Raycasting

```javascript
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()

window.addEventListener('pointermove', (event) => {
  pointer.x = (event.clientX / window.innerWidth) * 2 - 1
  pointer.y = -(event.clientY / window.innerHeight) * 2 + 1
})

function checkIntersections() {
  raycaster.setFromCamera(pointer, camera)
  const intersects = raycaster.intersectObjects(scene.children, true)

  if (intersects.length > 0) {
    const hit = intersects[0]
    console.log('Hit:', hit.object.name, 'at', hit.point)
  }
}
```

## Performance Guidelines

| Technique | When to Use | Impact |
|-----------|-------------|--------|
| `InstancedMesh` | Many identical objects | Reduces draw calls 100x+ |
| `LOD` | Large scenes with distant objects | Reduces triangles |
| Geometry merging | Static scenes | Reduces draw calls |
| Texture atlases | Many materials | Reduces draw calls |
| Object pooling | Frequently created/destroyed objects | Reduces GC |
| `.dispose()` | Removing objects | Prevents memory leaks |

```javascript
// Instanced rendering (1 draw call for 1000 objects)
const count = 1000
const mesh = new THREE.InstancedMesh(geometry, material, count)

const dummy = new THREE.Object3D()
for (let i = 0; i < count; i++) {
  dummy.position.randomDirection().multiplyScalar(Math.random() * 50)
  dummy.updateMatrix()
  mesh.setMatrixAt(i, dummy.matrix)
}
scene.add(mesh)
```

## CDN Usage (Browser)

For HTML artifacts or quick prototypes:

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.webgpu.min.js",
    "three/webgpu": "https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.webgpu.min.js",
    "three/tsl": "https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.tsl.min.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/"
  }
}
</script>
<script type="module">
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
</script>
```

## Related Skills

| When you need... | Use skill |
|------------------|-----------|
| React integration | → **react-three-fiber** |
| Optimize assets before loading | → **asset-pipeline-3d** |
| Debug visual/performance issues | → **graphics-troubleshooting** |

## Reference Files

- [references/webgpu.md](references/webgpu.md) - WebGPU setup, feature detection, fallbacks
- [references/tsl-shaders.md](references/tsl-shaders.md) - TSL custom shaders (replaces GLSL)
- [references/materials.md](references/materials.md) - NodeMaterial patterns and customization
- [references/physics.md](references/physics.md) - Rapier physics integration
- [references/advanced.md](references/advanced.md) - Post-processing, VR/AR, optimization
