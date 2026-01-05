# Product Configurator Scenario

Interactive 3D configurators for customizable products (furniture, vehicles, apparel).

## Tech Stack

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| Framework | React + R3F | Vanilla Three.js |
| State | Zustand | React Context |
| UI Controls | Custom React | dat.gui |
| Materials | Dynamic MeshStandardMaterial | Pre-baked variants |
| Environment | HDR preset | Custom lighting |

## Core Architecture

```jsx
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Configuration state
const useConfigStore = create(
  persist(
    (set, get) => ({
      // Selected options
      options: {
        color: '#ff0000',
        material: 'leather',
        size: 'medium',
        accessories: []
      },

      // Pricing
      basePrice: 299,

      // Actions
      setOption: (key, value) => set((state) => ({
        options: { ...state.options, [key]: value }
      })),

      toggleAccessory: (id) => set((state) => {
        const accessories = state.options.accessories.includes(id)
          ? state.options.accessories.filter(a => a !== id)
          : [...state.options.accessories, id]
        return { options: { ...state.options, accessories } }
      }),

      // Computed
      get totalPrice() {
        const { options, basePrice } = get()
        let price = basePrice

        // Material pricing
        const materialPrices = { leather: 100, fabric: 0, suede: 50 }
        price += materialPrices[options.material] || 0

        // Size pricing
        const sizePrices = { small: -20, medium: 0, large: 30 }
        price += sizePrices[options.size] || 0

        // Accessories
        const accessoryPrices = { armrest: 49, wheels: 79, headrest: 39 }
        options.accessories.forEach(a => {
          price += accessoryPrices[a] || 0
        })

        return price
      },

      reset: () => set({
        options: {
          color: '#ff0000',
          material: 'leather',
          size: 'medium',
          accessories: []
        }
      })
    }),
    { name: 'product-config' }
  )
)
```

## Configurable 3D Model

```jsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment, useGLTF, ContactShadows } from '@react-three/drei'
import { useEffect, useMemo } from 'react'
import * as THREE from 'three'

function ConfigurableProduct() {
  const { scene, nodes, materials } = useGLTF('/chair.glb')
  const options = useConfigStore((s) => s.options)

  // Apply color
  useEffect(() => {
    if (materials.Body) {
      materials.Body.color.set(options.color)
    }
  }, [options.color, materials])

  // Apply material type
  useEffect(() => {
    if (materials.Body) {
      switch (options.material) {
        case 'leather':
          materials.Body.roughness = 0.4
          materials.Body.metalness = 0
          break
        case 'fabric':
          materials.Body.roughness = 0.8
          materials.Body.metalness = 0
          break
        case 'suede':
          materials.Body.roughness = 0.9
          materials.Body.metalness = 0
          break
      }
    }
  }, [options.material, materials])

  // Scale based on size
  const scale = useMemo(() => {
    const scales = { small: 0.9, medium: 1, large: 1.1 }
    return scales[options.size] || 1
  }, [options.size])

  return (
    <group scale={scale}>
      <primitive object={scene} />

      {/* Conditional accessories */}
      {options.accessories.includes('armrest') && (
        <Armrest />
      )}
      {options.accessories.includes('headrest') && (
        <Headrest />
      )}
      {options.accessories.includes('wheels') && (
        <Wheels />
      )}
    </group>
  )
}

// Accessory components
function Armrest() {
  const { scene } = useGLTF('/armrest.glb')
  return <primitive object={scene} />
}

function Headrest() {
  const { scene } = useGLTF('/headrest.glb')
  return <primitive object={scene} />
}

function Wheels() {
  const { scene } = useGLTF('/wheels.glb')
  return <primitive object={scene} />
}

// Preload all models
useGLTF.preload('/chair.glb')
useGLTF.preload('/armrest.glb')
useGLTF.preload('/headrest.glb')
useGLTF.preload('/wheels.glb')
```

## Configuration UI

```jsx
function ConfiguratorUI() {
  const { options, setOption, toggleAccessory, totalPrice, reset } = useConfigStore()

  return (
    <div className="configurator-panel">
      {/* Color picker */}
      <section>
        <h3>Color</h3>
        <div className="color-options">
          {['#ff0000', '#0066ff', '#222222', '#ffffff', '#8b4513'].map(color => (
            <button
              key={color}
              className={`color-swatch ${options.color === color ? 'active' : ''}`}
              style={{ backgroundColor: color }}
              onClick={() => setOption('color', color)}
            />
          ))}
          <input
            type="color"
            value={options.color}
            onChange={(e) => setOption('color', e.target.value)}
          />
        </div>
      </section>

      {/* Material selector */}
      <section>
        <h3>Material</h3>
        <div className="material-options">
          {[
            { id: 'leather', label: 'Leather', price: '+$100' },
            { id: 'fabric', label: 'Fabric', price: 'Included' },
            { id: 'suede', label: 'Suede', price: '+$50' }
          ].map(mat => (
            <button
              key={mat.id}
              className={`option-btn ${options.material === mat.id ? 'active' : ''}`}
              onClick={() => setOption('material', mat.id)}
            >
              <span>{mat.label}</span>
              <span className="price">{mat.price}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Size selector */}
      <section>
        <h3>Size</h3>
        <div className="size-options">
          {[
            { id: 'small', label: 'Small', price: '-$20' },
            { id: 'medium', label: 'Medium', price: 'Standard' },
            { id: 'large', label: 'Large', price: '+$30' }
          ].map(size => (
            <button
              key={size.id}
              className={`option-btn ${options.size === size.id ? 'active' : ''}`}
              onClick={() => setOption('size', size.id)}
            >
              <span>{size.label}</span>
              <span className="price">{size.price}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Accessories */}
      <section>
        <h3>Accessories</h3>
        <div className="accessory-options">
          {[
            { id: 'armrest', label: 'Armrests', price: '$49' },
            { id: 'headrest', label: 'Headrest', price: '$39' },
            { id: 'wheels', label: 'Premium Wheels', price: '$79' }
          ].map(acc => (
            <label key={acc.id} className="checkbox-option">
              <input
                type="checkbox"
                checked={options.accessories.includes(acc.id)}
                onChange={() => toggleAccessory(acc.id)}
              />
              <span>{acc.label}</span>
              <span className="price">+{acc.price}</span>
            </label>
          ))}
        </div>
      </section>

      {/* Price and actions */}
      <div className="configurator-footer">
        <div className="total-price">
          <span>Total:</span>
          <strong>${totalPrice}</strong>
        </div>
        <div className="actions">
          <button onClick={reset}>Reset</button>
          <button className="primary">Add to Cart</button>
        </div>
      </div>
    </div>
  )
}
```

## Complete Configurator

```jsx
export default function ProductConfigurator() {
  return (
    <div className="configurator-container">
      <div className="canvas-container">
        <Canvas
          camera={{ position: [3, 2, 5], fov: 50 }}
          gl={{ antialias: true, preserveDrawingBuffer: true }}
          dpr={[1, 2]}
        >
          <Suspense fallback={null}>
            <Environment preset="studio" />
            <ambientLight intensity={0.3} />

            <ConfigurableProduct />

            <ContactShadows
              position={[0, -1, 0]}
              opacity={0.4}
              scale={10}
              blur={2}
            />
          </Suspense>

          <OrbitControls
            enablePan={false}
            minDistance={3}
            maxDistance={10}
            minPolarAngle={Math.PI / 6}
            maxPolarAngle={Math.PI / 2}
          />
        </Canvas>

        {/* Screenshot button */}
        <ScreenshotButton />
      </div>

      <ConfiguratorUI />
    </div>
  )
}
```

## Material Swapping (Pre-loaded)

```jsx
import { useMemo, useEffect } from 'react'
import { useGLTF, useTexture } from '@react-three/drei'
import * as THREE from 'three'

// For complex materials, pre-load textures
function ConfigurableWithTextures() {
  const { nodes } = useGLTF('/chair.glb')
  const options = useConfigStore((s) => s.options)

  // Pre-load all material textures
  const textures = useTexture({
    leather: '/textures/leather_diff.jpg',
    leatherNormal: '/textures/leather_norm.jpg',
    fabric: '/textures/fabric_diff.jpg',
    fabricNormal: '/textures/fabric_norm.jpg',
    suede: '/textures/suede_diff.jpg',
    suedeNormal: '/textures/suede_norm.jpg',
  })

  // Create materials
  const materials = useMemo(() => ({
    leather: new THREE.MeshStandardMaterial({
      map: textures.leather,
      normalMap: textures.leatherNormal,
      roughness: 0.4
    }),
    fabric: new THREE.MeshStandardMaterial({
      map: textures.fabric,
      normalMap: textures.fabricNormal,
      roughness: 0.8
    }),
    suede: new THREE.MeshStandardMaterial({
      map: textures.suede,
      normalMap: textures.suedeNormal,
      roughness: 0.9
    })
  }), [textures])

  // Apply color tint
  useEffect(() => {
    const mat = materials[options.material]
    if (mat) {
      mat.color.set(options.color)
    }
  }, [options.color, options.material, materials])

  return (
    <mesh geometry={nodes.Body.geometry} material={materials[options.material]} />
  )
}
```

## AR Preview (Optional)

```jsx
import { ARButton, XR, Interactive } from '@react-three/xr'

function ARConfigurator() {
  return (
    <>
      <ARButton />
      <Canvas>
        <XR>
          <ambientLight intensity={0.5} />
          <Interactive onSelect={() => console.log('placed')}>
            <ConfigurableProduct />
          </Interactive>
        </XR>
      </Canvas>
    </>
  )
}
```

## Save/Share Configuration

```jsx
// Generate shareable URL
function useShareableConfig() {
  const options = useConfigStore((s) => s.options)

  const generateShareUrl = () => {
    const params = new URLSearchParams({
      color: options.color,
      material: options.material,
      size: options.size,
      acc: options.accessories.join(',')
    })
    return `${window.location.origin}${window.location.pathname}?${params}`
  }

  const loadFromUrl = () => {
    const params = new URLSearchParams(window.location.search)
    const setOption = useConfigStore.getState().setOption

    if (params.get('color')) setOption('color', params.get('color'))
    if (params.get('material')) setOption('material', params.get('material'))
    if (params.get('size')) setOption('size', params.get('size'))
    if (params.get('acc')) {
      params.get('acc').split(',').forEach(acc => {
        useConfigStore.getState().toggleAccessory(acc)
      })
    }
  }

  return { generateShareUrl, loadFromUrl }
}

// Load config from URL on mount
useEffect(() => {
  loadFromUrl()
}, [])
```

## Screenshot/Export

```jsx
import { useThree } from '@react-three/fiber'

function ScreenshotButton() {
  const { gl, scene, camera } = useThree()

  const takeScreenshot = () => {
    gl.render(scene, camera)
    const dataUrl = gl.domElement.toDataURL('image/png')

    // Create download link
    const link = document.createElement('a')
    link.download = 'my-custom-chair.png'
    link.href = dataUrl
    link.click()
  }

  return (
    <button className="screenshot-btn" onClick={takeScreenshot}>
      Save Image
    </button>
  )
}
```

## Performance Tips

1. **Preload variants**: Load all accessory models on initial load
2. **Reuse materials**: Clone and modify rather than create new
3. **Texture atlases**: Combine color swatches into single texture
4. **Demand rendering**: Only render on option change
5. **LOD**: Lower poly for thumbnail/gallery views

## Checklist

- [ ] All configuration options work correctly
- [ ] 3D model updates in real-time
- [ ] Price updates with each selection
- [ ] Configuration persists across page reloads
- [ ] Share URL captures full configuration
- [ ] Screenshot captures current state
- [ ] Mobile touch controls work
- [ ] Loading states for model/texture swaps
- [ ] Reset returns to default state
- [ ] Add to cart captures configuration
