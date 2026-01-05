# WebGPU Reference

Three.js WebGPU renderer and modern graphics API patterns for 2026.

## WebGPU vs WebGL

| Feature | WebGPU | WebGL2 |
|---------|--------|--------|
| Compute shaders | Yes | No |
| Better multi-threading | Yes | Limited |
| Lower CPU overhead | Yes | No |
| TSL shaders | Native | Transpiled |
| Browser support | Chrome, Edge, Firefox, Safari 18+ | Universal |

## Feature Detection

```javascript
// Check WebGPU support
if (navigator.gpu) {
  console.log('WebGPU supported')
} else {
  console.log('WebGPU not supported, will fall back to WebGL')
}

// Three.js handles fallback automatically
import * as THREE from 'three/webgpu'

const renderer = new THREE.WebGPURenderer({ antialias: true })
// Falls back to WebGL2 if WebGPU unavailable
```

## Basic Setup

```javascript
import * as THREE from 'three/webgpu'

// Scene and camera
const scene = new THREE.Scene()
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
camera.position.z = 5

// WebGPU Renderer (async initialization required)
const renderer = new THREE.WebGPURenderer({ antialias: true })
await renderer.init() // REQUIRED for WebGPU

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
```

## Import Patterns

```javascript
// WebGPU build (recommended for 2026)
import * as THREE from 'three/webgpu'

// Includes WebGPURenderer + NodeMaterial system
// Automatically falls back to WebGL2

// TSL (Three.js Shading Language)
import { color, uniform, uv, sin, time, mix, vec3, float } from 'three/tsl'

// Addons work the same way
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
```

## NodeMaterial System

WebGPU uses NodeMaterial instead of ShaderMaterial:

```javascript
import * as THREE from 'three/webgpu'

// Standard materials have Node variants
const material = new THREE.MeshStandardNodeMaterial({
  color: 0x00ff00,
  roughness: 0.5,
  metalness: 0.5
})

// Available NodeMaterials:
// - MeshBasicNodeMaterial
// - MeshStandardNodeMaterial
// - MeshPhysicalNodeMaterial
// - MeshLambertNodeMaterial
// - MeshPhongNodeMaterial
// - PointsNodeMaterial
// - LineBasicNodeMaterial
// - SpriteNodeMaterial
```

## Compute Shaders

WebGPU enables compute shaders for parallel GPU computation:

```javascript
import * as THREE from 'three/webgpu'
import { storageBuffer, instanceIndex, float } from 'three/tsl'

// Create storage buffer for compute
const count = 1000
const positionArray = new Float32Array(count * 3)
const positionBuffer = new THREE.StorageBufferAttribute(positionArray, 3)

// Compute function
const computePositions = () => {
  const position = storageBuffer(positionBuffer)
  const i = float(instanceIndex)

  // Parallel computation for each particle
  position.x = sin(i.mul(0.1).add(time))
  position.y = cos(i.mul(0.1).add(time))
  position.z = i.mul(0.01)

  return position
}

// Create compute node
const computeNode = computePositions().compute(count)

// Run compute in render loop
function animate() {
  renderer.compute(computeNode)
  renderer.render(scene, camera)
}
```

## Renderer Capabilities

```javascript
// Check renderer backend
console.log('Backend:', renderer.backend.name) // 'webgpu' or 'webgl'

// WebGPU-specific features
if (renderer.backend.name === 'webgpu') {
  // Can use compute shaders
  // Better performance for complex scenes
  // Native TSL compilation
}

// Get GPU info
const adapter = await navigator.gpu?.requestAdapter()
if (adapter) {
  console.log('GPU:', adapter.name)
  console.log('Limits:', adapter.limits)
}
```

## Performance Benefits

### Reduced CPU Overhead

```javascript
// WebGPU batches draw calls more efficiently
// Less JavaScript → GPU communication overhead

// Instanced rendering is even faster on WebGPU
const count = 10000
const mesh = new THREE.InstancedMesh(geometry, material, count)
// WebGPU handles this with minimal CPU cost
```

### Compute for Physics/Particles

```javascript
// Move physics calculations to GPU
const particleCompute = () => {
  const velocity = storageBuffer(velocityBuffer)
  const position = storageBuffer(positionBuffer)

  // Physics on GPU (parallel for all particles)
  velocity.y = velocity.y.sub(float(9.8).mul(deltaTime))
  position.addAssign(velocity.mul(deltaTime))

  return position
}
```

## Migration from WebGL

### Renderer

```javascript
// Before (WebGL)
import * as THREE from 'three'
const renderer = new THREE.WebGLRenderer({ antialias: true })

// After (WebGPU)
import * as THREE from 'three/webgpu'
const renderer = new THREE.WebGPURenderer({ antialias: true })
await renderer.init() // Add this line
```

### Materials

```javascript
// Before (WebGL)
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 })

// After (WebGPU) - works the same, but use Node variant for customization
const material = new THREE.MeshStandardNodeMaterial({ color: 0xff0000 })
```

### Custom Shaders

```javascript
// Before (GLSL ShaderMaterial)
const material = new THREE.ShaderMaterial({
  vertexShader: `...`,
  fragmentShader: `...`
})

// After (TSL NodeMaterial) - see tsl-shaders.md
import { color, uv, sin, time } from 'three/tsl'
const material = new THREE.MeshBasicNodeMaterial()
material.colorNode = color(0xff0000).mul(sin(time))
```

## Browser Support (2026)

| Browser | WebGPU | Notes |
|---------|--------|-------|
| Chrome 113+ | Yes | Full support |
| Edge 113+ | Yes | Full support |
| Firefox 128+ | Yes | Full support |
| Safari 18+ | Yes | macOS/iOS |
| Safari < 18 | No | Falls back to WebGL |
| Mobile Chrome | Yes | Android 13+ |
| Mobile Safari | Yes | iOS 18+ |

## Debugging

```javascript
// Enable WebGPU validation
const renderer = new THREE.WebGPURenderer({
  antialias: true,
  // Enable validation layer (dev only)
})

// Chrome DevTools → Application → GPU
// Shows WebGPU adapter info and errors

// Console errors are more detailed in WebGPU
```

## Best Practices

1. **Always await init()**: WebGPU requires async initialization
2. **Use setAnimationLoop**: Required for WebXR, recommended for WebGPU
3. **Prefer NodeMaterial**: Use Node variants for WebGPU optimization
4. **Use TSL for custom shaders**: Compiles to both WGSL and GLSL
5. **Test fallback**: Verify your app works on WebGL2 fallback
6. **Leverage compute**: Move parallel work to compute shaders
