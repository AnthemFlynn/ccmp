# Performance Troubleshooting

Diagnose and fix performance issues in Three.js and React Three Fiber applications.

## Profiling Setup

### Stats.js (FPS Monitor)

```javascript
import Stats from 'stats.js'

const stats = new Stats()
stats.showPanel(0) // 0: fps, 1: ms, 2: mb
document.body.appendChild(stats.dom)

function animate() {
  stats.begin()
  renderer.render(scene, camera)
  stats.end()
  requestAnimationFrame(animate)
}
```

### Renderer Info

```javascript
// Call after render to get accurate counts
function logRenderInfo() {
  const info = renderer.info
  console.log({
    drawCalls: info.render.calls,
    triangles: info.render.triangles,
    points: info.render.points,
    lines: info.render.lines,
    geometries: info.memory.geometries,
    textures: info.memory.textures
  })
}
```

### R3F Performance Monitor

```jsx
import { PerformanceMonitor } from '@react-three/drei'

<Canvas>
  <PerformanceMonitor
    onIncline={() => console.log('Performance good, can increase quality')}
    onDecline={() => console.log('Performance dropping, reduce quality')}
    onFallback={() => console.log('Performance critical')}
  >
    <Scene />
  </PerformanceMonitor>
</Canvas>
```

## Performance Targets

| Platform | Target FPS | Max Draw Calls | Max Triangles | Max Texture Memory |
|----------|------------|----------------|---------------|-------------------|
| Desktop | 60 | 200 | 2M | 500MB |
| Laptop | 60 | 100 | 500K | 200MB |
| Mobile | 30-60 | 50 | 100K | 50MB |
| Low-end | 30 | 25 | 50K | 25MB |

## Common Performance Issues

### Too Many Draw Calls

**Symptom:** Low FPS despite low triangle count.

**Diagnosis:**
```javascript
console.log('Draw calls:', renderer.info.render.calls)
// Target: <100 for mobile, <200 for desktop
```

**Fixes:**

1. **Use InstancedMesh** for repeated objects
   ```javascript
   // Instead of 1000 separate meshes
   const count = 1000
   const mesh = new THREE.InstancedMesh(geometry, material, count)

   const dummy = new THREE.Object3D()
   for (let i = 0; i < count; i++) {
     dummy.position.set(Math.random() * 100, 0, Math.random() * 100)
     dummy.updateMatrix()
     mesh.setMatrixAt(i, dummy.matrix)
   }
   scene.add(mesh) // 1 draw call instead of 1000
   ```

2. **Merge static geometries**
   ```javascript
   import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js'

   const geometries = meshes.map(m => m.geometry.clone().applyMatrix4(m.matrixWorld))
   const merged = mergeGeometries(geometries)
   const singleMesh = new THREE.Mesh(merged, sharedMaterial)
   ```

3. **Use texture atlases** to share materials

4. **R3F: Use Merged component**
   ```jsx
   import { Merged } from '@react-three/drei'

   <Merged meshes={[mesh1, mesh2, mesh3]}>
     {(Mesh1, Mesh2, Mesh3) => (
       <>
         <Mesh1 position={[0, 0, 0]} />
         <Mesh1 position={[1, 0, 0]} />
         <Mesh2 position={[2, 0, 0]} />
       </>
     )}
   </Merged>
   ```

### Too Many Triangles

**Symptom:** Low FPS, high GPU usage.

**Diagnosis:**
```javascript
console.log('Triangles:', renderer.info.render.triangles)
```

**Fixes:**

1. **Use LOD (Level of Detail)**
   ```javascript
   const lod = new THREE.LOD()
   lod.addLevel(highDetailMesh, 0)    // Within 0-50 units
   lod.addLevel(mediumDetailMesh, 50) // 50-150 units
   lod.addLevel(lowDetailMesh, 150)   // Beyond 150 units
   scene.add(lod)

   // Update in render loop
   lod.update(camera)
   ```

2. **R3F LOD**
   ```jsx
   import { Detailed } from '@react-three/drei'

   <Detailed distances={[0, 50, 150]}>
     <HighDetailModel />
     <MediumDetailModel />
     <LowDetailModel />
   </Detailed>
   ```

3. **Simplify models** in Blender or with gltf-transform
   ```bash
   gltf-transform simplify input.glb output.glb --ratio 0.5
   ```

### Memory Leaks

**Symptom:** Memory grows over time, eventual crash.

**Diagnosis:**
```javascript
// Log periodically
setInterval(() => {
  console.log({
    geometries: renderer.info.memory.geometries,
    textures: renderer.info.memory.textures
  })
}, 5000)
```

**Fixes:**

1. **Dispose on removal**
   ```javascript
   function removeObject(obj) {
     scene.remove(obj)

     if (obj.geometry) obj.geometry.dispose()
     if (obj.material) {
       if (Array.isArray(obj.material)) {
         obj.material.forEach(m => disposeMaterial(m))
       } else {
         disposeMaterial(obj.material)
       }
     }
   }

   function disposeMaterial(material) {
     material.dispose()
     // Dispose textures
     for (const key of Object.keys(material)) {
       const value = material[key]
       if (value && typeof value.dispose === 'function') {
         value.dispose()
       }
     }
   }
   ```

2. **R3F handles disposal automatically** when components unmount, but watch for:
   - Textures loaded outside components
   - Manually created geometries
   - Refs to objects that persist

3. **Use object pools** for frequently created/destroyed objects
   ```javascript
   class Pool {
     constructor(factory, initialSize = 10) {
       this.factory = factory
       this.available = Array.from({ length: initialSize }, factory)
       this.inUse = new Set()
     }

     acquire() {
       const obj = this.available.pop() || this.factory()
       this.inUse.add(obj)
       obj.visible = true
       return obj
     }

     release(obj) {
       if (this.inUse.delete(obj)) {
         obj.visible = false
         this.available.push(obj)
       }
     }
   }
   ```

### GC Stuttering (Frame Hitches)

**Symptom:** Periodic stutters every few seconds.

**Cause:** Creating objects in render loop triggers garbage collection.

**Fixes:**

1. **Reuse vectors and matrices**
   ```javascript
   // Bad: Creates new Vector3 every frame
   function animate() {
     mesh.position.add(new THREE.Vector3(0.1, 0, 0))
   }

   // Good: Reuse pre-allocated vector
   const velocity = new THREE.Vector3(0.1, 0, 0)
   function animate() {
     mesh.position.add(velocity)
   }
   ```

2. **Avoid array methods that allocate**
   ```javascript
   // Bad: map/filter create new arrays
   const visible = objects.filter(o => o.visible).map(o => o.position)

   // Good: Reuse array, use for loop
   const positions = []
   for (let i = 0; i < objects.length; i++) {
     if (objects[i].visible) {
       positions.push(objects[i].position)
     }
   }
   positions.length = 0 // Reuse next frame
   ```

3. **Pre-allocate in setup, not in loop**

### Texture Memory Issues

**Symptom:** GPU memory full, textures not loading.

**Fixes:**

1. **Use power-of-2 dimensions** (256, 512, 1024, 2048)
2. **Compress textures** with KTX2/Basis
3. **Resize large textures**
   ```bash
   gltf-transform resize model.glb output.glb --width 1024 --height 1024
   ```
4. **Share textures** between materials
5. **Dispose unused textures**
   ```javascript
   texture.dispose()
   ```

## R3F-Specific Optimizations

### Demand Rendering

Only re-render when something changes:

```jsx
<Canvas frameloop="demand">
  {/* Scene only re-renders when invalidate() is called */}
</Canvas>

function Controls() {
  const { invalidate } = useThree()
  return <OrbitControls onChange={invalidate} />
}
```

### Adaptive DPR

Reduce resolution under load:

```jsx
import { AdaptiveDpr } from '@react-three/drei'

<Canvas>
  <AdaptiveDpr pixelated />
</Canvas>
```

### GPU Tier Detection

Adjust quality based on hardware:

```jsx
import { useDetectGPU } from '@react-three/drei'

function Scene() {
  const gpu = useDetectGPU()

  // gpu.tier: 0 (low), 1 (medium), 2 (high), 3 (very high)
  const quality = gpu.tier >= 2 ? 'high' : gpu.tier >= 1 ? 'medium' : 'low'

  return <Model quality={quality} />
}
```

### BVH for Raycasting

Speed up raycasting with BVH:

```jsx
import { Bvh } from '@react-three/drei'

<Bvh firstHitOnly>
  <ComplexModel />
</Bvh>
```

## Profiling Tools

| Tool | Use For |
|------|---------|
| Stats.js | Real-time FPS monitoring |
| Chrome DevTools Performance | Frame timing, JS profiling |
| Chrome DevTools Memory | Memory snapshots, leak detection |
| Spector.js | WebGL call inspection |
| RenderDoc | GPU debugging (desktop) |
| `renderer.info` | Draw calls, memory counts |
