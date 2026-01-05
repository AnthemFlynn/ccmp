---
name: graphics-troubleshooting
description: Debug and fix common issues in Three.js, React Three Fiber, and 3D asset pipelines. Use when encountering visual bugs, performance problems, loading failures, or unexpected behavior. Covers black screens, Z-fighting, memory leaks, shader errors, and physics glitches.
---

# Graphics Troubleshooting

Diagnose and fix 3D web graphics issues fast. Organized by **symptom** (what you see) for rapid diagnosis.

> **Library Versions (2026)**
> - Three.js: r171+
> - React Three Fiber: v9.5+
> - @react-three/drei: v9.116+
> - @react-three/rapier: v2+

## Quick Diagnosis

### Nothing Renders (Black/Empty Screen)

| Check | Command/Action |
|-------|----------------|
| Camera position | Is camera inside object? Move to `[0, 0, 5]` |
| Camera target | Is camera looking at scene? Check `lookAt` |
| Object scale | Is object too small/large? Check scale isn't `0` |
| Lights | Are there any lights? Add `<ambientLight />` |
| Material | Using `MeshStandardMaterial` without lights? |
| Render loop | Is `animate()` being called? |
| Canvas size | Is container height `0`? Check CSS |
| WebGPU support | Browser support? Check console for errors |

**R3F Minimum Visible Scene:**
```jsx
<Canvas>
  <ambientLight intensity={0.5} />
  <directionalLight position={[5, 5, 5]} />
  <mesh position={[0, 0, 0]}>
    <boxGeometry />
    <meshStandardMaterial color="red" />
  </mesh>
</Canvas>
```

**Vanilla Three.js Minimum Scene:**
```javascript
import * as THREE from 'three/webgpu'

const scene = new THREE.Scene()
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
camera.position.z = 5

const renderer = new THREE.WebGPURenderer({ antialias: true })
await renderer.init()
renderer.setSize(window.innerWidth, window.innerHeight)
document.body.appendChild(renderer.domElement)

// Add light - required for Standard materials
scene.add(new THREE.AmbientLight(0xffffff, 0.5))
scene.add(new THREE.DirectionalLight(0xffffff, 1))

// Add visible object
const mesh = new THREE.Mesh(
  new THREE.BoxGeometry(),
  new THREE.MeshStandardMaterial({ color: 'red' })
)
scene.add(mesh)

function animate() {
  renderer.render(scene, camera)
}
renderer.setAnimationLoop(animate)
```

### Object Renders But Looks Wrong

| Symptom | Cause | Fix |
|---------|-------|-----|
| All black | No lights | Add ambient + directional light |
| Flickering faces | Z-fighting | Increase camera `near`, offset overlapping geometry |
| Inside-out | Inverted normals | `material.side = THREE.DoubleSide` or fix in Blender |
| Pixelated edges | Low DPR | `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))` |
| Washed out colors | No tone mapping | `renderer.toneMapping = THREE.ACESFilmicToneMapping` |
| Colors look wrong | Color space | `renderer.outputColorSpace = THREE.SRGBColorSpace` |
| Texture blurry | Filtering | `texture.minFilter = THREE.LinearMipmapLinearFilter` |
| Texture stretched | Wrong UVs | Check UV mapping in Blender, use `texture.repeat` |

### Performance Issues

| Symptom | Diagnosis | Target | Fix |
|---------|-----------|--------|-----|
| Low FPS (<30) | Check `renderer.info.render.calls` | <100 draw calls | Use InstancedMesh, merge geometries |
| Stuttering/hitching | GC pauses | Avoid allocations | Object pooling, reuse Vector3s |
| Memory growing | Check `renderer.info.memory` | Stable | Call `.dispose()` on removal |
| Slow initial load | Large assets | <5MB total | Compress with Meshopt, resize textures |
| Slow on mobile | Too many triangles | <100K | Simplify geometry, use LOD |

**Quick Performance Check:**
```javascript
// Add to console or scene
console.log('Draw calls:', renderer.info.render.calls)
console.log('Triangles:', renderer.info.render.triangles)
console.log('Geometries:', renderer.info.memory.geometries)
console.log('Textures:', renderer.info.memory.textures)
```

See [references/performance.md](references/performance.md) for detailed profiling.

### Loading Failures

| Error | Cause | Fix |
|-------|-------|-----|
| 404 Not Found | Wrong path | Check file exists, use absolute path from public |
| CORS error | Cross-origin | Serve from same origin or configure CORS headers |
| "Unexpected token" | Wrong file format | Ensure file is valid GLTF/GLB |
| Draco decode error | Missing decoder | Set `dracoLoader.setDecoderPath('/draco/')` |
| KTX2 decode error | Missing transcoder | Set `ktx2Loader.setTranscoderPath('/basis/')` |
| "Invalid glTF" | Corrupted file | Validate at https://gltf.report |
| Model invisible | Wrong scale | Check scale (Blender default: 1 unit = 1 meter) |

**Loader Setup Pattern:**
```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js'
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js'
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'

const loader = new GLTFLoader()

// Draco (for Draco-compressed models)
const dracoLoader = new DRACOLoader()
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.6/')
loader.setDRACOLoader(dracoLoader)

// Meshopt (for Meshopt-compressed models)
loader.setMeshoptDecoder(MeshoptDecoder)

// KTX2 (for Basis Universal textures)
const ktx2Loader = new KTX2Loader()
ktx2Loader.setTranscoderPath('https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/libs/basis/')
ktx2Loader.detectSupport(renderer)
loader.setKTX2Loader(ktx2Loader)
```

See [references/loading.md](references/loading.md) for more patterns.

### Physics Issues (@react-three/rapier)

| Symptom | Cause | Fix |
|---------|-------|-----|
| Objects fall through floor | Missing collider | Add `<RigidBody type="fixed">` to ground |
| Objects stuck in air | Wrong body type | Use `type="dynamic"` for moving objects |
| Jittery movement | High velocity + low mass | Increase mass or reduce forces |
| Tunneling (fast objects pass through) | CCD disabled | Enable `ccd={true}` on fast bodies |
| Collider wrong shape | Auto-collider mismatch | Use explicit `<CuboidCollider>` etc. |
| Physics not updating | Wrong loop | Check `updateLoop` prop on `<Physics>` |

**Minimum Physics Setup:**
```jsx
import { Physics, RigidBody } from '@react-three/rapier'

<Physics gravity={[0, -9.81, 0]} debug>
  {/* Ground - fixed, doesn't move */}
  <RigidBody type="fixed">
    <mesh position={[0, -1, 0]}>
      <boxGeometry args={[10, 0.5, 10]} />
      <meshStandardMaterial />
    </mesh>
  </RigidBody>

  {/* Falling object - dynamic */}
  <RigidBody type="dynamic">
    <mesh>
      <sphereGeometry />
      <meshStandardMaterial />
    </mesh>
  </RigidBody>
</Physics>
```

### Shader/Material Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "X is not defined" in shader | Missing uniform/varying | Declare all variables |
| Black material | Shader compile error | Check console for GLSL/WGSL errors |
| Material not updating | Missing `needsUpdate` | Set `material.needsUpdate = true` |
| TSL error | Wrong import | Use `import { x } from 'three/tsl'` |
| NodeMaterial black | Missing colorNode | Set `material.colorNode = ...` |

**TSL Debug Pattern:**
```javascript
import { color, uniform } from 'three/tsl'

// Start simple, add complexity
const material = new THREE.MeshBasicNodeMaterial()
material.colorNode = color(0xff0000) // Should be red

// If this works, add your custom logic incrementally
```

## Related Skills

| When you need... | Use skill |
|------------------|-----------|
| Optimize assets before loading | **asset-pipeline-3d** |
| Build scenes with vanilla Three.js | **threejs** |
| Build scenes with React | **react-three-fiber** |

## Reference Files

- [references/visual-bugs.md](references/visual-bugs.md) - Z-fighting, clipping, shadow artifacts, transparency issues
- [references/performance.md](references/performance.md) - Profiling, optimization, memory management
- [references/loading.md](references/loading.md) - Asset loading, decoder setup, CORS, caching
