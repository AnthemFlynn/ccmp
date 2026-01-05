# Web Graphics Plugin

Production-ready 3D web graphics toolkit for Claude Code. Build interactive 3D experiences with modern WebGPU rendering, React integration, optimized asset pipelines, and expert troubleshooting.

## Skills

### Three.js (`threejs`)

Create 3D browser experiences with Three.js and WebGPU.

- **WebGPU-first rendering** with automatic WebGL2 fallback
- **TSL shaders** (Three.js Shading Language) for cross-platform custom materials
- **NodeMaterial system** for advanced material customization
- Scene setup, cameras, lighting, shadows
- Animation patterns, interaction, raycasting
- Performance optimization

**Triggers**: 3D scenes, WebGL/WebGPU applications, visualizations, games, browser 3D content.

### React Three Fiber (`react-three-fiber`)

Build 3D applications with React's declarative paradigm.

- Declarative JSX for 3D objects
- React hooks (`useFrame`, `useThree`, `useLoader`)
- Drei helpers (OrbitControls, Environment, useGLTF, Text, Html)
- Zustand state management patterns
- Performance optimization (instancing, memoization, demand rendering)
- Physics with @react-three/rapier

**Triggers**: React-based 3D, R3F, Drei, declarative 3D, React state + 3D.

### Asset Pipeline (`asset-pipeline-3d`)

Optimize and prepare 3D assets for performant web delivery.

- GLTF/GLB workflows
- Meshopt and Draco geometry compression
- KTX2/Basis Universal GPU-compressed textures
- Blender export settings
- LOD generation and simplification
- Performance budgets and validation

**Triggers**: GLTF optimization, 3D compression, texture optimization, Blender export.

### Graphics Troubleshooting (`graphics-troubleshooting`)

Debug and fix 3D graphics issues fast.

- **Symptom-first diagnosis**: Black screen, wrong rendering, performance issues
- Visual bugs: Z-fighting, clipping, shadow artifacts, transparency
- Loading failures: CORS, decoder setup, validation
- Physics debugging for @react-three/rapier
- Shader/material error resolution

**Triggers**: 3D bugs, rendering issues, performance problems, loading errors.

## Scenarios

Ready-to-use patterns for common use cases:

| Scenario | Description |
|----------|-------------|
| [Product Viewer](scenarios/product-viewer.md) | Interactive 3D product showcase |
| [Data Visualization](scenarios/data-visualization.md) | 3D charts and data exploration |
| [Simple Game](scenarios/simple-game.md) | Browser-based 3D games with physics |
| [Immersive Landing](scenarios/immersive-landing.md) | Scroll-driven 3D marketing pages |
| [Configurator](scenarios/configurator.md) | Product customization interfaces |

## Installation

```bash
claude plugin install web-graphics@ccmp
```

## Quick Start

### Vanilla Three.js (WebGPU)

```javascript
import * as THREE from 'three/webgpu'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

const scene = new THREE.Scene()
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
camera.position.z = 5

const renderer = new THREE.WebGPURenderer({ antialias: true })
await renderer.init()
renderer.setSize(window.innerWidth, window.innerHeight)
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.toneMapping = THREE.ACESFilmicToneMapping
renderer.outputColorSpace = THREE.SRGBColorSpace
document.body.appendChild(renderer.domElement)

scene.add(new THREE.AmbientLight(0xffffff, 0.4))
const sun = new THREE.DirectionalLight(0xffffff, 1)
sun.position.set(5, 10, 5)
scene.add(sun)

const mesh = new THREE.Mesh(
  new THREE.BoxGeometry(),
  new THREE.MeshStandardNodeMaterial({ color: 0x00ff00 })
)
scene.add(mesh)

const controls = new OrbitControls(camera, renderer.domElement)

function animate() {
  mesh.rotation.y += 0.01
  controls.update()
  renderer.render(scene, camera)
}
renderer.setAnimationLoop(animate)
```

### React Three Fiber

```jsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment } from '@react-three/drei'

function App() {
  return (
    <Canvas camera={{ position: [0, 0, 5] }} shadows>
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 10, 5]} castShadow />
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="green" />
      </mesh>
      <OrbitControls />
      <Environment preset="studio" />
    </Canvas>
  )
}
```

### CDN Usage (No Bundler)

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
```

## Library Versions (2026)

- **Three.js**: r171+ (WebGPU default)
- **React Three Fiber**: v9.5+
- **@react-three/drei**: v9.116+
- **@react-three/rapier**: v2+
- **gltf-transform**: v4+

## License

MIT
