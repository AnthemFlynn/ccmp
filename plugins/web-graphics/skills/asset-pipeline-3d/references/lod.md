# Level of Detail (LOD)

Strategies for rendering appropriate detail based on distance.

## LOD Generation

### gltf-transform Simplification

```bash
# Single simplification pass
gltf-transform simplify input.glb output.glb --ratio 0.5

# Options
--ratio 0.5         # Target 50% of original triangles
--error 0.001       # Max geometric error (0.001 = 0.1%)
--lock-border       # Preserve mesh boundaries

# Generate multiple LODs manually
gltf-transform simplify input.glb lod0.glb --ratio 1.0    # Original
gltf-transform simplify input.glb lod1.glb --ratio 0.5    # 50%
gltf-transform simplify input.glb lod2.glb --ratio 0.25   # 25%
gltf-transform simplify input.glb lod3.glb --ratio 0.1    # 10%
```

### Blender Decimate Modifier

1. Add Decimate modifier to mesh
2. Set ratio (0.5 = 50% reduction)
3. Mode options:
   - **Collapse**: Best quality, general use
   - **Un-Subdivide**: Good for subdivided meshes
   - **Planar**: Removes flat areas
4. Apply modifier
5. Export as separate LOD file

### meshoptimizer / gltfpack

```bash
# Generate with simplification
gltfpack -i input.glb -o output.glb -si 0.5

# Multiple LODs
gltfpack -i input.glb -o lod1.glb -si 0.75
gltfpack -i input.glb -o lod2.glb -si 0.5
gltfpack -i input.glb -o lod3.glb -si 0.25
```

## Three.js LOD Implementation

### Basic LOD

```javascript
import * as THREE from 'three'

const lod = new THREE.LOD()

// Add levels (mesh, distance threshold)
lod.addLevel(highDetailMesh, 0)     // < 10 units
lod.addLevel(mediumDetailMesh, 10)  // 10-50 units
lod.addLevel(lowDetailMesh, 50)     // 50-100 units
lod.addLevel(billboardMesh, 100)    // > 100 units

scene.add(lod)

// Update in animation loop
function animate() {
  lod.update(camera)
  renderer.render(scene, camera)
}
```

### Loading Multiple LODs

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const loader = new GLTFLoader()
const lod = new THREE.LOD()

const lodFiles = [
  { file: '/model_lod0.glb', distance: 0 },
  { file: '/model_lod1.glb', distance: 20 },
  { file: '/model_lod2.glb', distance: 50 },
]

Promise.all(lodFiles.map(({ file, distance }) => 
  new Promise((resolve) => {
    loader.load(file, (gltf) => {
      resolve({ mesh: gltf.scene, distance })
    })
  })
)).then((levels) => {
  levels.forEach(({ mesh, distance }) => {
    lod.addLevel(mesh, distance)
  })
  scene.add(lod)
})
```

### React Three Fiber with Drei

```jsx
import { Detailed, useGLTF } from '@react-three/drei'

function Model() {
  const lod0 = useGLTF('/model_lod0.glb')
  const lod1 = useGLTF('/model_lod1.glb')
  const lod2 = useGLTF('/model_lod2.glb')
  
  return (
    <Detailed distances={[0, 20, 50]}>
      <primitive object={lod0.scene.clone()} />
      <primitive object={lod1.scene.clone()} />
      <primitive object={lod2.scene.clone()} />
    </Detailed>
  )
}

// Preload all LODs
useGLTF.preload('/model_lod0.glb')
useGLTF.preload('/model_lod1.glb')
useGLTF.preload('/model_lod2.glb')
```

## LOD Strategies

### Distance-Based (Standard)

Switch based on camera distance. Good for most cases.

```javascript
// Calculate distances based on screen coverage
const objectSize = 2  // meters
const screenCoverage = [0.5, 0.2, 0.05]  // % of screen height

screenCoverage.forEach((coverage, i) => {
  const distance = objectSize / (2 * Math.tan(camera.fov / 2 * Math.PI / 180) * coverage)
  lod.addLevel(meshes[i], distance)
})
```

### Screen-Space Error

Switch based on geometric error in pixels. More accurate.

```javascript
function calculateScreenSpaceError(geometricError, distance, fov, screenHeight) {
  const pixelsPerRadian = screenHeight / (2 * Math.tan(fov / 2 * Math.PI / 180))
  return (geometricError / distance) * pixelsPerRadian
}

// Switch when error > threshold (e.g., 2 pixels)
const threshold = 2
```

### Hybrid LOD + Imposters

Use billboards for very distant objects.

```javascript
// Create imposter from render
function createImposter(mesh, resolution = 256) {
  const renderTarget = new THREE.WebGLRenderTarget(resolution, resolution)
  const imposterCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10)
  
  // Render mesh to texture
  renderer.setRenderTarget(renderTarget)
  renderer.render(imposterScene, imposterCamera)
  renderer.setRenderTarget(null)
  
  // Create billboard
  const imposter = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: renderTarget.texture })
  )
  return imposter
}
```

## HLOD (Hierarchical LOD)

For large scenes with many objects.

```javascript
// Group nearby objects at distance
class HLODNode {
  constructor(objects, bounds) {
    this.objects = objects
    this.bounds = bounds
    this.mergedMesh = null
    this.children = []
  }
  
  createMergedMesh() {
    // Merge all child geometries
    const geometries = this.objects.map(obj => obj.geometry.clone())
    this.mergedMesh = BufferGeometryUtils.mergeGeometries(geometries)
  }
}

// At distance, show merged mesh instead of individual objects
function updateHLOD(camera) {
  const distance = camera.position.distanceTo(hlodNode.bounds.center)
  
  if (distance > threshold) {
    // Show merged mesh
    hlodNode.objects.forEach(obj => obj.visible = false)
    hlodNode.mergedMesh.visible = true
  } else {
    // Show individual objects
    hlodNode.objects.forEach(obj => obj.visible = true)
    hlodNode.mergedMesh.visible = false
  }
}
```

## Performance Considerations

### Triangle Budgets per LOD

| LOD Level | Distance | Triangle % | Use Case |
|-----------|----------|------------|----------|
| LOD0 | 0-10m | 100% | Full detail |
| LOD1 | 10-30m | 50% | Medium detail |
| LOD2 | 30-60m | 25% | Low detail |
| LOD3 | 60-100m | 10% | Minimal |
| Imposter | 100m+ | Billboard | 2 triangles |

### Texture LODs (Mipmaps)

Three.js generates mipmaps automatically for power-of-2 textures.

```javascript
texture.generateMipmaps = true
texture.minFilter = THREE.LinearMipmapLinearFilter

// Manual mipmap control
texture.mipmaps = [level0Image, level1Image, level2Image]
texture.generateMipmaps = false
```

### LOD Hysteresis

Prevent popping by using different switch distances for approaching vs receding.

```javascript
class HysteresisLOD extends THREE.LOD {
  constructor() {
    super()
    this.hysteresis = 0.1  // 10% buffer
    this.lastLevel = 0
  }
  
  update(camera) {
    const distance = camera.position.distanceTo(this.position)
    
    // Find appropriate level with hysteresis
    let targetLevel = 0
    for (let i = 0; i < this.levels.length; i++) {
      let threshold = this.levels[i].distance
      
      // Add buffer when switching away from current level
      if (i > this.lastLevel) {
        threshold *= (1 + this.hysteresis)
      } else if (i < this.lastLevel) {
        threshold *= (1 - this.hysteresis)
      }
      
      if (distance >= threshold) {
        targetLevel = i
      }
    }
    
    if (targetLevel !== this.lastLevel) {
      this.lastLevel = targetLevel
      // Switch visibility
    }
  }
}
```
