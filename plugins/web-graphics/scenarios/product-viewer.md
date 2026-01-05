# Product Viewer Scenario

Interactive 3D product viewer for e-commerce, portfolios, or marketing sites.

## Tech Stack

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| Framework | React + R3F | Vanilla Three.js |
| Controls | OrbitControls | CameraControls |
| Lighting | Environment (HDR) | Three-point setup |
| Shadows | ContactShadows | Shadow maps |
| Post-processing | Optional bloom | None |

## Starter Code (R3F)

```jsx
import { Canvas } from '@react-three/fiber'
import {
  OrbitControls,
  Environment,
  ContactShadows,
  useGLTF,
  PresentationControls,
  Html
} from '@react-three/drei'
import { Suspense, useState, useEffect } from 'react'
import { useThree } from '@react-three/fiber'

function Product({ url }) {
  const { scene } = useGLTF(url)
  return <primitive object={scene} />
}

function Annotations({ annotations }) {
  return annotations.map((a, i) => (
    <Html key={i} position={a.position} center>
      <div className="annotation">{a.label}</div>
    </Html>
  ))
}

export default function ProductViewer({ modelUrl, annotations = [] }) {
  return (
    <Canvas
      camera={{ position: [0, 0, 4], fov: 45 }}
      gl={{ antialias: true, preserveDrawingBuffer: true }}
      dpr={[1, 2]}
    >
      <Suspense fallback={null}>
        {/* Lighting */}
        <Environment preset="studio" />
        <ambientLight intensity={0.2} />

        {/* Product with rotation controls */}
        <PresentationControls
          global
          rotation={[0, 0, 0]}
          polar={[-Math.PI / 4, Math.PI / 4]}
          azimuth={[-Math.PI / 4, Math.PI / 4]}
        >
          <Product url={modelUrl} />
          <Annotations annotations={annotations} />
        </PresentationControls>

        {/* Ground shadow */}
        <ContactShadows
          position={[0, -1, 0]}
          opacity={0.5}
          scale={10}
          blur={2}
          far={4}
        />
      </Suspense>

      {/* Fallback controls */}
      <OrbitControls
        enablePan={false}
        minDistance={2}
        maxDistance={8}
        minPolarAngle={Math.PI / 6}
        maxPolarAngle={Math.PI / 2}
      />
    </Canvas>
  )
}

// Preload model
useGLTF.preload('/product.glb')
```

## Vanilla Three.js Version

```javascript
import * as THREE from 'three/webgpu'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js'

// Setup
const scene = new THREE.Scene()
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100)
camera.position.set(0, 0, 4)

const renderer = new THREE.WebGPURenderer({ antialias: true })
await renderer.init()
renderer.setSize(window.innerWidth, window.innerHeight)
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.toneMapping = THREE.ACESFilmicToneMapping
renderer.outputColorSpace = THREE.SRGBColorSpace
document.body.appendChild(renderer.domElement)

// Environment
const rgbeLoader = new RGBELoader()
rgbeLoader.load('/studio.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping
  scene.environment = texture
  scene.background = new THREE.Color(0xffffff)
})

// Controls
const controls = new OrbitControls(camera, renderer.domElement)
controls.enablePan = false
controls.minDistance = 2
controls.maxDistance = 8
controls.enableDamping = true

// Load product
const loader = new GLTFLoader()
loader.load('/product.glb', (gltf) => {
  scene.add(gltf.scene)
})

// Animation
function animate() {
  controls.update()
  renderer.render(scene, camera)
}
renderer.setAnimationLoop(animate)
```

## Common Features

### Color/Material Variants

```jsx
function ProductWithVariants({ variants }) {
  const [variant, setVariant] = useState(0)
  const { scene, materials } = useGLTF('/product.glb')

  useEffect(() => {
    const mat = materials['Body']
    if (mat) {
      mat.color.set(variants[variant].color)
    }
  }, [variant, materials, variants])

  return (
    <>
      <primitive object={scene} />
      <Html position={[0, -1.5, 0]}>
        <div className="variants">
          {variants.map((v, i) => (
            <button
              key={i}
              onClick={() => setVariant(i)}
              style={{ background: v.color }}
            />
          ))}
        </div>
      </Html>
    </>
  )
}
```

### Hotspot Annotations

```jsx
const hotspots = [
  { position: [0.5, 0.3, 0.2], label: 'Premium leather', detail: 'Hand-stitched Italian leather' },
  { position: [-0.3, 0.5, 0.4], label: 'Metal clasp', detail: 'Solid brass with gold finish' }
]

function Hotspots({ spots }) {
  const [active, setActive] = useState(null)

  return spots.map((spot, i) => (
    <Html key={i} position={spot.position}>
      <div
        className={`hotspot ${active === i ? 'active' : ''}`}
        onClick={() => setActive(active === i ? null : i)}
      >
        <div className="dot" />
        {active === i && (
          <div className="tooltip">
            <h4>{spot.label}</h4>
            <p>{spot.detail}</p>
          </div>
        )}
      </div>
    </Html>
  ))
}
```

### Screenshot/Share

```jsx
function ScreenshotButton() {
  const { gl, scene, camera } = useThree()

  const takeScreenshot = () => {
    gl.render(scene, camera)
    const dataUrl = gl.domElement.toDataURL('image/png')

    // Download
    const link = document.createElement('a')
    link.download = 'product.png'
    link.href = dataUrl
    link.click()
  }

  return (
    <Html position={[0, 2, 0]}>
      <button onClick={takeScreenshot}>Download Image</button>
    </Html>
  )
}
```

## Performance Tips

1. **Single model**: Keep to one hero product, avoid multiple complex models
2. **Texture size**: 1024px max for mobile, 2048px for desktop
3. **LOD not needed**: Single viewing distance, full detail OK
4. **Demand rendering**: Use `frameloop="demand"` with OrbitControls onChange
5. **Preload**: Always preload the model for instant display

## Asset Requirements

| Asset | Format | Size | Notes |
|-------|--------|------|-------|
| Model | GLB | <3MB | Meshopt compressed |
| Textures | KTX2/WebP | 1024-2048px | Embedded in GLB |
| Environment | HDR | 512px | For reflections |

## Checklist

- [ ] Model loads and displays correctly
- [ ] Controls have sensible limits (min/max zoom, rotation)
- [ ] Environment lighting looks good
- [ ] Shadows add depth without performance cost
- [ ] Mobile touch controls work
- [ ] Loading indicator shows during load
- [ ] Screenshot feature works (if needed)
- [ ] Variants switch correctly (if applicable)
