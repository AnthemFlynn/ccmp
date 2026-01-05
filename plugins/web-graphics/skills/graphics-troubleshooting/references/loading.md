# Loading Troubleshooting

Fix asset loading issues in Three.js and React Three Fiber applications.

## Common Loading Errors

### 404 Not Found

**Cause:** File path is incorrect.

**Fixes:**

1. **Check file location**
   - Vite/React: Files in `public/` are served at root
   - Next.js: Files in `public/` are served at root
   - Use absolute paths from root: `/models/character.glb`

2. **Check file name case sensitivity**
   - Linux/macOS servers are case-sensitive
   - `Model.glb` !== `model.glb`

3. **Verify file exists**
   ```bash
   ls -la public/models/
   ```

### CORS Errors

**Symptom:** `Access-Control-Allow-Origin` error in console.

**Cause:** Loading assets from different domain without CORS headers.

**Fixes:**

1. **Serve from same origin** (recommended)
   - Move assets to your `public/` folder

2. **Configure CORS on asset server**
   ```
   Access-Control-Allow-Origin: *
   ```

3. **Use a CORS proxy** (development only)
   ```javascript
   // Not for production!
   const corsProxy = 'https://cors-anywhere.herokuapp.com/'
   loader.load(corsProxy + assetUrl, onLoad)
   ```

4. **CDN with CORS**
   - jsDelivr, unpkg, and Cloudflare R2 have CORS enabled

### Decoder Not Found (Draco/KTX2)

**Symptom:** Draco or KTX2 decoder errors.

**Fix:** Configure decoder paths correctly.

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js'
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js'
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'

const loader = new GLTFLoader()

// Draco decoder - use CDN or copy to public/
const dracoLoader = new DRACOLoader()
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.6/')
// Or local: dracoLoader.setDecoderPath('/draco/')
loader.setDRACOLoader(dracoLoader)

// Meshopt decoder - import directly
loader.setMeshoptDecoder(MeshoptDecoder)

// KTX2 transcoder
const ktx2Loader = new KTX2Loader()
ktx2Loader.setTranscoderPath('https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/libs/basis/')
ktx2Loader.detectSupport(renderer) // Required!
loader.setKTX2Loader(ktx2Loader)
```

**R3F with Drei:** Draco is handled automatically by `useGLTF`.

### Invalid GLTF

**Symptom:** "Unexpected token" or parsing errors.

**Fixes:**

1. **Validate the file**
   - Online: https://gltf.report
   - CLI: `npx gltf-validator model.glb`

2. **Re-export from Blender**
   - Use GLB format (binary, single file)
   - Check export settings

3. **Check file isn't corrupted**
   - Re-download or re-export

### Model Loads But Is Invisible

**Causes and fixes:**

| Cause | Diagnosis | Fix |
|-------|-----------|-----|
| Wrong scale | Check in console | Scale up/down in loader or Blender |
| Wrong position | Log `gltf.scene.position` | Move camera or model |
| No lights | Model is black | Add lights |
| Material issue | Check materials in console | Use standard materials |
| Camera inside model | Model is huge | Move camera back |

```javascript
loader.load('/model.glb', (gltf) => {
  // Debug: Log bounding box
  const box = new THREE.Box3().setFromObject(gltf.scene)
  console.log('Model size:', box.getSize(new THREE.Vector3()))
  console.log('Model center:', box.getCenter(new THREE.Vector3()))

  // Auto-scale to fit view
  const size = box.getSize(new THREE.Vector3()).length()
  const scale = 5 / size // Target size of 5 units
  gltf.scene.scale.setScalar(scale)

  // Center the model
  const center = box.getCenter(new THREE.Vector3())
  gltf.scene.position.sub(center.multiplyScalar(scale))

  scene.add(gltf.scene)
})
```

## Loading Patterns

### Basic GLTF Loading

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const loader = new GLTFLoader()

loader.load(
  '/model.glb',
  // onLoad
  (gltf) => {
    scene.add(gltf.scene)
  },
  // onProgress
  (xhr) => {
    console.log((xhr.loaded / xhr.total * 100) + '% loaded')
  },
  // onError
  (error) => {
    console.error('Loading error:', error)
  }
)
```

### Async/Await Pattern

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

async function loadModel(url) {
  const loader = new GLTFLoader()

  try {
    const gltf = await loader.loadAsync(url)
    return gltf.scene
  } catch (error) {
    console.error('Failed to load model:', error)
    throw error
  }
}

// Usage
const model = await loadModel('/character.glb')
scene.add(model)
```

### R3F Loading with useGLTF

```jsx
import { useGLTF, Preload } from '@react-three/drei'
import { Suspense } from 'react'

// Preload during idle time
useGLTF.preload('/model.glb')

function Model({ url }) {
  const { scene, nodes, materials, animations } = useGLTF(url)
  return <primitive object={scene} />
}

function App() {
  return (
    <Canvas>
      <Suspense fallback={<LoadingIndicator />}>
        <Model url="/model.glb" />
      </Suspense>
      <Preload all /> {/* Preload all suspended assets */}
    </Canvas>
  )
}
```

### Loading Multiple Assets

```javascript
import { LoadingManager } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { TextureLoader } from 'three'

const manager = new LoadingManager()

manager.onStart = (url, loaded, total) => {
  console.log(`Started loading: ${url}`)
}

manager.onProgress = (url, loaded, total) => {
  console.log(`Loading: ${loaded}/${total}`)
}

manager.onLoad = () => {
  console.log('All assets loaded!')
  startGame()
}

manager.onError = (url) => {
  console.error(`Error loading: ${url}`)
}

const gltfLoader = new GLTFLoader(manager)
const textureLoader = new TextureLoader(manager)

// Load all assets
gltfLoader.load('/character.glb', (gltf) => { /* ... */ })
gltfLoader.load('/environment.glb', (gltf) => { /* ... */ })
textureLoader.load('/skybox.jpg', (texture) => { /* ... */ })
```

### Caching Loaded Assets

```javascript
const assetCache = new Map()

async function loadCached(url) {
  if (assetCache.has(url)) {
    return assetCache.get(url).clone()
  }

  const gltf = await loader.loadAsync(url)
  assetCache.set(url, gltf.scene)
  return gltf.scene.clone()
}
```

## Texture Loading

### Basic Texture

```javascript
import { TextureLoader } from 'three'

const textureLoader = new TextureLoader()
const texture = textureLoader.load('/texture.jpg')

// Set correct color space for color textures
texture.colorSpace = THREE.SRGBColorSpace

// Apply to material
material.map = texture
```

### Multiple Textures (PBR)

```javascript
const [colorMap, normalMap, roughnessMap] = await Promise.all([
  textureLoader.loadAsync('/color.jpg'),
  textureLoader.loadAsync('/normal.jpg'),
  textureLoader.loadAsync('/roughness.jpg')
])

colorMap.colorSpace = THREE.SRGBColorSpace
// Normal and roughness stay linear

const material = new THREE.MeshStandardNodeMaterial({
  map: colorMap,
  normalMap: normalMap,
  roughnessMap: roughnessMap
})
```

### R3F Texture Loading

```jsx
import { useTexture } from '@react-three/drei'

function TexturedMesh() {
  const [colorMap, normalMap] = useTexture([
    '/color.jpg',
    '/normal.jpg'
  ])

  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial map={colorMap} normalMap={normalMap} />
    </mesh>
  )
}
```

## Environment Maps

### HDR Environment

```javascript
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js'

const rgbeLoader = new RGBELoader()
rgbeLoader.load('/environment.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping
  scene.background = texture
  scene.environment = texture // For PBR reflections
})
```

### R3F Environment

```jsx
import { Environment } from '@react-three/drei'

// Using preset
<Environment preset="sunset" background />

// Using custom HDR
<Environment files="/environment.hdr" background />

// Using cube map
<Environment files={['px.jpg', 'nx.jpg', 'py.jpg', 'ny.jpg', 'pz.jpg', 'nz.jpg']} path="/cubemap/" />
```

## Loading Progress UI

### HTML Overlay

```javascript
const loadingOverlay = document.getElementById('loading')
const progressBar = document.getElementById('progress')

manager.onProgress = (url, loaded, total) => {
  const progress = (loaded / total) * 100
  progressBar.style.width = progress + '%'
}

manager.onLoad = () => {
  loadingOverlay.style.display = 'none'
}
```

### R3F with Html

```jsx
import { Html, useProgress } from '@react-three/drei'

function Loader() {
  const { progress } = useProgress()
  return <Html center>{progress.toFixed(0)}% loaded</Html>
}

<Canvas>
  <Suspense fallback={<Loader />}>
    <Scene />
  </Suspense>
</Canvas>
```

## Debug Checklist

When assets fail to load:

1. [ ] Check browser console for errors
2. [ ] Verify file path (case-sensitive)
3. [ ] Check file exists in public folder
4. [ ] Check for CORS issues (cross-origin)
5. [ ] Validate GLTF at gltf.report
6. [ ] Check decoder paths (Draco/KTX2)
7. [ ] Check file size (large files may timeout)
8. [ ] Try loading a known-working model
9. [ ] Check network tab for actual request
