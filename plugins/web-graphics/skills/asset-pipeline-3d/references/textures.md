# Textures Reference

Texture formats, optimization, and best practices for web 3D.

## Texture Types

| Type | Color Space | Compression | Notes |
|------|-------------|-------------|-------|
| Albedo/Diffuse | sRGB | Lossy OK | Base color |
| Normal | Linear | High quality | Direction data |
| Roughness | Linear | Lossy OK | Grayscale |
| Metalness | Linear | Lossy OK | Grayscale |
| AO | Linear | Lossy OK | Grayscale |
| Emission | sRGB | Lossy OK | Glow color |
| Height/Displacement | Linear | Lossless | Precision matters |

## Format Selection

### KTX2/Basis Universal (Recommended 2026)

GPU-compressed textures - stay compressed in video memory.

**Pros:**
- Fastest rendering (native GPU format)
- Lower GPU memory usage
- No decode step

**Cons:**
- Larger file size than WebP
- Quality loss vs PNG

```bash
# High quality (UASTC)
basisu -uastc -uastc_level 2 -mipmap texture.png -output_file texture.ktx2

# Smaller (ETC1S)
basisu -mipmap texture.png -output_file texture.ktx2

# For normal maps (high quality)
basisu -uastc -uastc_level 4 -normal_map normal.png -output_file normal.ktx2

# Via gltf-transform
gltf-transform ktx model.glb output.glb --compress uastc
```

### WebP

Good balance for non-GPU-compressed needs.

```bash
# Lossy (most textures)
cwebp -q 85 texture.png -o texture.webp

# Lossless (when quality critical)
cwebp -lossless texture.png -o texture.webp

# Via gltf-transform
gltf-transform webp model.glb output.glb --quality 85
```

### PNG

Use for source files and when lossless is required.

### JPEG

Legacy, avoid for new projects (no alpha, artifacts on edges).

### AVIF

Best compression ratio, but slower decode and limited support.

```bash
# Convert to AVIF
avifenc -s 6 -q 60 texture.png texture.avif
```

## Size Guidelines

### Resolution by Use Case

| Use Case | Mobile | Desktop | High-end |
|----------|--------|---------|----------|
| Hero/Main model | 1024px | 2048px | 4096px |
| Secondary objects | 512px | 1024px | 2048px |
| Background/Props | 256px | 512px | 1024px |
| UI/Icons | 128px | 256px | 512px |

### Power of Two

**Always use power-of-2 dimensions** for mipmapping:
- 128, 256, 512, 1024, 2048, 4096

Non-power-of-2 textures waste memory and may not mipmap correctly.

## Channel Packing

Combine grayscale maps to reduce texture count:

### ORM (Occlusion-Roughness-Metalness)

```
R: Ambient Occlusion
G: Roughness
B: Metalness
A: (optional - height, mask, etc.)
```

### Creating ORM in Photoshop/GIMP

1. Create new RGB image at target resolution
2. Load AO texture → Copy to Red channel
3. Load Roughness texture → Copy to Green channel
4. Load Metalness texture → Copy to Blue channel
5. Save as PNG (linear color space)

### Using ORM in Three.js

```javascript
const ormTexture = textureLoader.load('/orm.png')
ormTexture.colorSpace = THREE.LinearSRGBColorSpace

const material = new THREE.MeshStandardNodeMaterial({
  aoMap: ormTexture,        // Reads R channel
  roughnessMap: ormTexture, // Reads G channel
  metalnessMap: ormTexture, // Reads B channel
})
```

## Color Space

### sRGB (Color Textures)

- Albedo/Diffuse
- Emission
- Any texture that represents visible color

```javascript
const colorMap = textureLoader.load('/albedo.jpg')
colorMap.colorSpace = THREE.SRGBColorSpace
```

### Linear (Data Textures)

- Normal maps
- Roughness
- Metalness
- AO
- Height/Displacement
- Masks

```javascript
const normalMap = textureLoader.load('/normal.png')
normalMap.colorSpace = THREE.LinearSRGBColorSpace
```

## Normal Maps

### Format

- Use PNG or KTX2 (avoid JPEG - compression artifacts)
- OpenGL format (Y+ up) is Three.js default
- DirectX format (Y- down) needs `material.normalScale.y = -1`

### Quality

- Higher resolution than albedo often needed
- UASTC compression preserves quality
- Avoid heavy lossy compression

```bash
# High quality normal map compression
basisu -uastc -uastc_level 4 -normal_map normal.png -output_file normal.ktx2
```

## Mipmapping

Mipmaps are pre-computed smaller versions for distant rendering.

```javascript
// Enable mipmapping (default)
texture.generateMipmaps = true
texture.minFilter = THREE.LinearMipmapLinearFilter // Trilinear
texture.magFilter = THREE.LinearFilter

// Disable for UI/pixel art
texture.generateMipmaps = false
texture.minFilter = THREE.LinearFilter
```

### Anisotropic Filtering

Improves quality at oblique angles:

```javascript
texture.anisotropy = renderer.capabilities.getMaxAnisotropy()
// Usually 16 on modern GPUs
```

## Texture Loading

### Basic Loading

```javascript
const textureLoader = new THREE.TextureLoader()

const colorMap = textureLoader.load('/color.jpg', (texture) => {
  texture.colorSpace = THREE.SRGBColorSpace
  texture.wrapS = THREE.RepeatWrapping
  texture.wrapT = THREE.RepeatWrapping
})
```

### Async Loading

```javascript
async function loadTextures() {
  const loader = new THREE.TextureLoader()

  const [color, normal, roughness] = await Promise.all([
    loader.loadAsync('/color.jpg'),
    loader.loadAsync('/normal.png'),
    loader.loadAsync('/roughness.jpg')
  ])

  color.colorSpace = THREE.SRGBColorSpace
  // normal and roughness stay linear

  return { color, normal, roughness }
}
```

### KTX2 Loading

```javascript
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js'

const ktx2Loader = new KTX2Loader()
ktx2Loader.setTranscoderPath('https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/libs/basis/')
ktx2Loader.detectSupport(renderer)

const texture = await ktx2Loader.loadAsync('/texture.ktx2')
```

### R3F Loading

```jsx
import { useTexture } from '@react-three/drei'

function TexturedMesh() {
  // Single texture
  const colorMap = useTexture('/color.jpg')

  // Multiple textures
  const [color, normal, roughness] = useTexture([
    '/color.jpg',
    '/normal.png',
    '/roughness.jpg'
  ])

  // With configuration
  const props = useTexture({
    map: '/color.jpg',
    normalMap: '/normal.png',
    roughnessMap: '/roughness.jpg'
  })

  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial {...props} />
    </mesh>
  )
}

// Preload
useTexture.preload('/texture.jpg')
```

## Optimization Checklist

- [ ] All textures are power-of-2
- [ ] Color textures use sRGB color space
- [ ] Data textures use Linear color space
- [ ] Textures sized appropriately for use case
- [ ] Grayscale maps packed into ORM
- [ ] KTX2 used for GPU compression
- [ ] Mipmapping enabled
- [ ] Anisotropic filtering enabled
- [ ] Unused textures disposed

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Colors too dark | Wrong color space | Set sRGB for color maps |
| Colors washed out | sRGB on data texture | Use Linear for normals/roughness |
| Aliasing at distance | No mipmaps | Enable generateMipmaps |
| Blurry at angles | No anisotropic | Set anisotropy to max |
| Memory usage high | Large textures | Resize to appropriate size |
| Slow loading | Many large files | Use KTX2, reduce resolution |
