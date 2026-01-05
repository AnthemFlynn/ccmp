# Materials Reference

NodeMaterial patterns and customization for Three.js WebGPU.

## Material Types

| Material | Use Case | Performance |
|----------|----------|-------------|
| `MeshBasicNodeMaterial` | Unlit, UI, wireframes, fullbright | Fastest |
| `MeshLambertNodeMaterial` | Diffuse only, stylized | Fast |
| `MeshPhongNodeMaterial` | Specular highlights, legacy | Medium |
| `MeshStandardNodeMaterial` | PBR, realistic (default) | Medium |
| `MeshPhysicalNodeMaterial` | Glass, clearcoat, SSS | Slow |
| `SpriteNodeMaterial` | Billboards, particles | Fast |
| `LineBasicNodeMaterial` | Lines, wireframes | Fast |
| `PointsNodeMaterial` | Point clouds | Fast |

## MeshStandardNodeMaterial (PBR)

The default choice for realistic rendering:

```javascript
import * as THREE from 'three/webgpu'

const material = new THREE.MeshStandardNodeMaterial({
  color: 0xff0000,           // Base color
  roughness: 0.5,            // 0 = mirror, 1 = matte
  metalness: 0.5,            // 0 = dielectric, 1 = metal
  map: colorTexture,         // Color texture
  normalMap: normalTexture,  // Normal map
  roughnessMap: roughTexture,// Roughness texture
  metalnessMap: metalTexture,// Metalness texture
  aoMap: aoTexture,          // Ambient occlusion
  emissive: 0x000000,        // Emission color
  emissiveIntensity: 1,      // Emission strength
  envMapIntensity: 1,        // Environment reflection
})
```

### Customizing with Nodes

```javascript
import { color, uv, texture, uniform, float, mix } from 'three/tsl'

const material = new THREE.MeshStandardNodeMaterial()

// Dynamic color
const baseColor = uniform(color(0xff0000))
material.colorNode = baseColor

// Animated roughness
const roughnessValue = uniform(float(0.5))
material.roughnessNode = roughnessValue

// Texture blending
const tex1 = texture(texture1)
const tex2 = texture(texture2)
const blendFactor = uniform(float(0.5))
material.colorNode = mix(tex1, tex2, blendFactor)
```

## MeshPhysicalNodeMaterial (Advanced PBR)

For glass, car paint, skin, and other complex materials:

```javascript
// Glass
const glass = new THREE.MeshPhysicalNodeMaterial({
  transmission: 1,        // 1 = fully transparent
  roughness: 0,           // Smooth surface
  thickness: 0.5,         // Refraction depth
  ior: 1.5,               // Index of refraction (glass = 1.5)
  attenuationColor: new THREE.Color(0.8, 0.9, 1.0),
  attenuationDistance: 0.5
})

// Car Paint (clearcoat)
const carPaint = new THREE.MeshPhysicalNodeMaterial({
  color: 0xff0000,
  metalness: 0.9,
  roughness: 0.5,
  clearcoat: 1,           // Clear lacquer layer
  clearcoatRoughness: 0.1
})

// Iridescent (angle-dependent color)
const iridescent = new THREE.MeshPhysicalNodeMaterial({
  iridescence: 1,
  iridescenceIOR: 1.3,
  iridescenceThicknessRange: [100, 400]
})

// Sheen (fabric-like)
const velvet = new THREE.MeshPhysicalNodeMaterial({
  color: 0x880000,
  sheen: 1,
  sheenRoughness: 0.8,
  sheenColor: new THREE.Color(1, 0.5, 0.5)
})

// Subsurface Scattering (skin, wax)
const skin = new THREE.MeshPhysicalNodeMaterial({
  color: 0xffdbac,
  roughness: 0.5,
  transmission: 0,
  thickness: 1,
  // SSS approximation through transmission
})
```

## Common Material Properties

```javascript
// All materials share these properties
material.transparent = true        // Enable transparency
material.opacity = 0.5             // Global opacity
material.alphaTest = 0.5           // Alpha cutoff
material.side = THREE.DoubleSide   // Render both sides
material.depthWrite = true         // Write to depth buffer
material.depthTest = true          // Read depth buffer
material.blending = THREE.NormalBlending
material.visible = true
```

## Texture Setup

```javascript
const textureLoader = new THREE.TextureLoader()

// Color texture (sRGB)
const colorMap = textureLoader.load('/color.jpg')
colorMap.colorSpace = THREE.SRGBColorSpace

// Normal map (Linear)
const normalMap = textureLoader.load('/normal.jpg')
normalMap.colorSpace = THREE.LinearSRGBColorSpace

// Data textures (roughness, metalness, AO) - Linear
const roughnessMap = textureLoader.load('/roughness.jpg')
roughnessMap.colorSpace = THREE.LinearSRGBColorSpace

// Texture settings
colorMap.wrapS = THREE.RepeatWrapping
colorMap.wrapT = THREE.RepeatWrapping
colorMap.repeat.set(2, 2)
colorMap.anisotropy = renderer.capabilities.getMaxAnisotropy()
```

## ORM Packed Textures

Pack Occlusion, Roughness, Metalness into RGB channels:

```javascript
const ormMap = textureLoader.load('/orm.jpg')
ormMap.colorSpace = THREE.LinearSRGBColorSpace

const material = new THREE.MeshStandardNodeMaterial({
  aoMap: ormMap,
  roughnessMap: ormMap,
  metalnessMap: ormMap,
  // Three.js reads:
  // R channel → AO
  // G channel → Roughness
  // B channel → Metalness
})
```

## Dynamic Material Updates

```javascript
// Update uniforms (fast)
const colorUniform = uniform(color(0xff0000))
material.colorNode = colorUniform

function update() {
  colorUniform.value.setHex(0x00ff00) // Just update value
}

// Update properties (triggers recompile)
material.roughness = 0.8 // Avoid in render loop

// Update textures
material.map = newTexture
material.needsUpdate = true
```

## Material Cloning

```javascript
// Clone material for variants
const baseMaterial = new THREE.MeshStandardNodeMaterial({
  roughness: 0.5,
  metalness: 0.5
})

// Clone and modify
const redVariant = baseMaterial.clone()
redVariant.color.setHex(0xff0000)

const blueVariant = baseMaterial.clone()
blueVariant.color.setHex(0x0000ff)
```

## Custom Node Materials

Build materials entirely from nodes:

```javascript
import * as THREE from 'three/webgpu'
import { color, uv, texture, normalMap, time, sin, mix } from 'three/tsl'

const material = new THREE.MeshStandardNodeMaterial()

// Base color from texture with tint
const baseTexture = texture(colorMap)
const tint = uniform(color(0xffffff))
material.colorNode = baseTexture.mul(tint)

// Normal from texture
material.normalNode = normalMap(texture(normalMapTex))

// Animated roughness
material.roughnessNode = sin(time).mul(0.25).add(0.5)

// Animated emission
const emissionStrength = uniform(float(0))
material.emissiveNode = color(0x00ffff).mul(emissionStrength)
```

## Performance Tips

1. **Reuse materials**: Share materials between meshes when possible
2. **Avoid needsUpdate**: Cache uniform nodes instead of changing properties
3. **Use simpler materials**: Lambert instead of Standard when lighting isn't critical
4. **Limit transparency**: Transparent objects are expensive (sorting, overdraw)
5. **Texture atlases**: Fewer unique materials = fewer draw calls

```javascript
// Good: Shared material with uniform variation
const sharedMaterial = new THREE.MeshStandardNodeMaterial()
const colorUniform = uniform(color(0xffffff))
sharedMaterial.colorNode = colorUniform

// Each mesh can update colorUniform.value differently
meshes.forEach((mesh, i) => {
  // Use instance color or update uniform per draw
})
```

## Environment Mapping

```javascript
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js'

const rgbeLoader = new RGBELoader()
rgbeLoader.load('/environment.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping

  // Apply to scene (affects all PBR materials)
  scene.environment = texture

  // Optional: Also use as background
  scene.background = texture
})

// Per-material environment intensity
material.envMapIntensity = 1.5
```

## Debugging Materials

```javascript
// Visualize specific channels
material.colorNode = texture(normalMapTex) // See normal map as color
material.colorNode = texture(roughnessMap) // See roughness as grayscale

// Override to solid color
material.colorNode = color(0xff00ff) // Magenta = material applied

// Check UV mapping
material.colorNode = vec3(uv().x, uv().y, 0)
```
