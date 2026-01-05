# Visual Bugs Reference

Detailed fixes for common visual artifacts and rendering issues.

> **Note:** Examples assume `import * as THREE from 'three/webgpu'` or `'three'`.

## Z-Fighting (Flickering Overlapping Surfaces)

**Symptom:** Two surfaces at nearly the same depth flicker between each other.

**Causes:**
- Overlapping geometry at same Z-depth
- Camera near/far ratio too large
- Precision loss in depth buffer

**Fixes (in order of preference):**

1. **Offset geometry slightly**
   ```javascript
   // Move one surface by tiny amount
   plane2.position.z += 0.001
   ```

2. **Adjust camera near plane**
   ```javascript
   // Increase near (default 0.1 is often too small)
   camera.near = 0.5  // or even 1.0 for large scenes
   camera.updateProjectionMatrix()
   ```

3. **Use logarithmic depth buffer** (performance cost)
   ```javascript
   const renderer = new THREE.WebGPURenderer({
     logarithmicDepthBuffer: true
   })
   ```

4. **Use polygon offset** on decals/overlays
   ```javascript
   material.polygonOffset = true
   material.polygonOffsetFactor = -1
   material.polygonOffsetUnits = -1
   ```

## Clipping (Objects Cut Off)

**Symptom:** Parts of objects disappear, especially at edges of view.

### Near Plane Clipping
Objects close to camera get cut off.

```javascript
camera.near = 0.01  // Decrease for close objects
camera.updateProjectionMatrix()
```

### Far Plane Clipping
Distant objects disappear.

```javascript
camera.far = 10000  // Increase for distant objects
camera.updateProjectionMatrix()
```

### Frustum Culling
Object disappears when partially off-screen.

```javascript
// Check bounding sphere is correct
mesh.geometry.computeBoundingSphere()

// Or disable culling for this object
mesh.frustumCulled = false
```

## Shadow Artifacts

### Shadow Acne (Striping on Lit Surfaces)

**Cause:** Surface self-shadows due to depth precision.

```javascript
// Increase bias (start small, increase until acne gone)
directionalLight.shadow.bias = -0.0001

// Or use normal bias (often better)
directionalLight.shadow.normalBias = 0.02
```

### Peter Panning (Shadow Detached from Object)

**Cause:** Bias too high pushes shadow away.

```javascript
// Reduce bias
directionalLight.shadow.bias = -0.00005

// Prefer normalBias over bias
directionalLight.shadow.normalBias = 0.01
directionalLight.shadow.bias = 0
```

### Blocky/Pixelated Shadows

**Cause:** Shadow map resolution too low.

```javascript
directionalLight.shadow.mapSize.width = 2048
directionalLight.shadow.mapSize.height = 2048

// For very large scenes, may need 4096
// But watch GPU memory usage
```

### Missing Shadows

**Checklist:**
```javascript
// 1. Enable on renderer
renderer.shadowMap.enabled = true
renderer.shadowMap.type = THREE.PCFSoftShadowMap

// 2. Light must cast shadows
directionalLight.castShadow = true

// 3. Objects must cast
mesh.castShadow = true

// 4. Ground must receive
ground.receiveShadow = true

// 5. Check shadow camera frustum
directionalLight.shadow.camera.left = -10
directionalLight.shadow.camera.right = 10
directionalLight.shadow.camera.top = 10
directionalLight.shadow.camera.bottom = -10
directionalLight.shadow.camera.near = 0.1
directionalLight.shadow.camera.far = 50

// 6. Visualize shadow camera
const helper = new THREE.CameraHelper(directionalLight.shadow.camera)
scene.add(helper)
```

## Transparency Issues

### Wrong Draw Order (Transparent Objects Overlapping Incorrectly)

**Cause:** WebGL draws transparent objects back-to-front based on object center.

**Fixes:**

1. **Manual render order**
   ```javascript
   transparentMesh.renderOrder = 1  // Higher = drawn later
   ```

2. **Depth write off** (for particles, UI)
   ```javascript
   material.depthWrite = false
   ```

3. **Alpha test** (for cutout textures)
   ```javascript
   material.alphaTest = 0.5  // Discard pixels below threshold
   ```

4. **Use transmission** (for glass-like materials)
   ```javascript
   const material = new THREE.MeshPhysicalNodeMaterial({
     transmission: 1,
     roughness: 0,
     thickness: 0.5
   })
   ```

### Transparent Object Shows Black Background

**Cause:** No background or environment set.

```javascript
// Set scene background
scene.background = new THREE.Color(0x000000)

// Or use environment for reflections
scene.environment = envTexture
```

## Color Issues

### Colors Look Wrong/Washed Out

```javascript
// Enable correct color space
renderer.outputColorSpace = THREE.SRGBColorSpace

// Enable tone mapping for HDR
renderer.toneMapping = THREE.ACESFilmicToneMapping
renderer.toneMappingExposure = 1.0
```

### Textures Look Different Than Source

```javascript
// Ensure texture uses correct color space
texture.colorSpace = THREE.SRGBColorSpace  // For color textures

// Normal/roughness/metalness should be Linear
normalMap.colorSpace = THREE.LinearSRGBColorSpace
```

## WebGPU-Specific Issues

### "WebGPU not supported"

```javascript
// Check support before creating renderer
if (!navigator.gpu) {
  console.warn('WebGPU not supported, falling back to WebGL')
  // WebGPURenderer automatically falls back
}
```

### Shader Compilation Errors

WebGPU uses WGSL, not GLSL. Use TSL to write cross-compatible shaders:

```javascript
// Wrong: Raw GLSL
const material = new THREE.ShaderMaterial({
  fragmentShader: `void main() { gl_FragColor = vec4(1,0,0,1); }`
})

// Right: TSL (compiles to both WGSL and GLSL)
import { color } from 'three/tsl'
const material = new THREE.MeshBasicNodeMaterial()
material.colorNode = color(0xff0000)
```

## Debug Helpers

```javascript
// Axes helper (red=X, green=Y, blue=Z)
scene.add(new THREE.AxesHelper(5))

// Grid helper
scene.add(new THREE.GridHelper(10, 10))

// Box helper around object
scene.add(new THREE.BoxHelper(mesh, 0xffff00))

// Skeleton helper for animated characters
scene.add(new THREE.SkeletonHelper(character))

// Light helpers
scene.add(new THREE.DirectionalLightHelper(light))
scene.add(new THREE.SpotLightHelper(spotlight))
scene.add(new THREE.PointLightHelper(pointLight))

// Camera helper (for shadow camera debugging)
scene.add(new THREE.CameraHelper(light.shadow.camera))
```
