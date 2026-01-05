# Compression Reference

Detailed comparison of 3D asset compression methods.

## Geometry Compression

### Meshopt vs Draco

| Feature | Meshopt | Draco |
|---------|---------|-------|
| Decode speed | **Faster** (2-3x) | Slower |
| File size | Slightly larger | **Smaller** (10-20%) |
| Animation support | **Excellent** | Good |
| Morph targets | **Excellent** | Good |
| Browser WASM | Yes | Yes |
| Streaming decode | Yes | No |
| Quantization | 16-bit default | Configurable |

### Recommendation

**Use Meshopt** for most projects (2026 default):
- Faster decode = faster time-to-interactive
- Better animation fidelity
- Streaming support

**Use Draco** when:
- Bandwidth is critical (slow connections)
- File size matters more than decode time
- Static meshes only (no animation)

### Meshopt Commands

```bash
# gltf-transform
gltf-transform meshopt input.glb output.glb

# gltfpack (meshoptimizer CLI)
gltfpack -i input.glb -o output.glb -cc

# With quantization settings
gltfpack -i input.glb -o output.glb -cc -vp 14 -vt 12 -vn 8
# -vp: position bits (default 14)
# -vt: texcoord bits (default 12)
# -vn: normal bits (default 8)
```

### Draco Commands

```bash
# gltf-transform
gltf-transform draco input.glb output.glb

# With settings
gltf-transform draco input.glb output.glb \
  --quantize-position 14 \
  --quantize-normal 10 \
  --quantize-texcoord 12
```

## Texture Compression

### Format Comparison

| Format | File Size | GPU Memory | Decode | Alpha | Quality |
|--------|-----------|------------|--------|-------|---------|
| PNG | Large | Uncompressed | Fast | Yes | Lossless |
| JPEG | Small | Uncompressed | Fast | No | Lossy |
| WebP | **Smaller** | Uncompressed | Fast | Yes | Both |
| AVIF | **Smallest** | Uncompressed | Medium | Yes | Lossy |
| KTX2 UASTC | Medium | **Compressed** | **Native** | Yes | High |
| KTX2 ETC1S | **Small** | **Compressed** | **Native** | Yes | Medium |

### KTX2/Basis Universal

**GPU-compressed textures** stay compressed in video memory:

```bash
# UASTC (high quality)
basisu -uastc -uastc_level 2 input.png -output_file output.ktx2

# ETC1S (smaller, lower quality)
basisu input.png -output_file output.ktx2

# Via gltf-transform
gltf-transform ktx input.glb output.glb --compress uastc
gltf-transform ktx input.glb output.glb --compress etc1s
```

**UASTC** - Use for:
- Hero textures
- Normal maps (quality sensitive)
- Albedo on main characters

**ETC1S** - Use for:
- Background textures
- Large texture counts
- Mobile optimization

### WebP

Good balance of size and compatibility:

```bash
# Convert to WebP
cwebp -q 80 input.png -o output.webp

# Via gltf-transform
gltf-transform optimize input.glb output.glb --texture-compress webp

# With quality setting
gltf-transform webp input.glb output.glb --quality 85
```

## Complete Pipeline Examples

### Production Web (Recommended)

```bash
# Full optimization: Meshopt + KTX2
gltf-transform optimize input.glb output.glb \
  --compress meshopt \
  --texture-compress ktx2 \
  --texture-size 1024

# Result: Fast decode, GPU-compressed textures, good file size
```

### Maximum Compression (Bandwidth Limited)

```bash
# Smallest file size: Draco + WebP
gltf-transform optimize input.glb output.glb \
  --compress draco \
  --texture-compress webp \
  --texture-size 512

# Result: Smallest download, slower decode
```

### High Quality (Desktop/High-end)

```bash
# Best quality: Meshopt + UASTC 2048px
gltf-transform optimize input.glb output.glb \
  --compress meshopt \
  --texture-compress ktx2 \
  --texture-size 2048

# Result: High fidelity, fast rendering
```

### Mobile Optimized

```bash
# Mobile: Meshopt + ETC1S + Small textures
gltf-transform optimize input.glb output.glb \
  --compress meshopt

# Then compress textures separately for smaller ETC1S
basisu -linear -mipmap input/*.png
```

## Simplification (LOD)

Reduce triangle count for distant objects:

```bash
# Simplify to 50% triangles
gltf-transform simplify input.glb output.glb --ratio 0.5

# With error threshold
gltf-transform simplify input.glb output.glb --ratio 0.5 --error 0.001

# gltfpack simplification
gltfpack -i input.glb -o output.glb -si 0.5
```

### LOD Levels

| LOD | Distance | Triangle Ratio | Use Case |
|-----|----------|----------------|----------|
| LOD0 | 0-10m | 100% | Close-up |
| LOD1 | 10-30m | 50% | Medium |
| LOD2 | 30-100m | 25% | Far |
| LOD3 | 100m+ | 10% | Very far |

## Decoder Setup (Three.js)

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js'
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js'

const loader = new GLTFLoader()

// Meshopt (recommended)
loader.setMeshoptDecoder(MeshoptDecoder)

// Draco (if used)
const dracoLoader = new DRACOLoader()
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/')
loader.setDRACOLoader(dracoLoader)

// KTX2 (requires renderer)
const ktx2Loader = new KTX2Loader()
ktx2Loader.setTranscoderPath('https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/libs/basis/')
ktx2Loader.detectSupport(renderer)
loader.setKTX2Loader(ktx2Loader)
```

## Size Budgets

| Platform | Model (GLB) | Total Textures | Per Texture |
|----------|-------------|----------------|-------------|
| Mobile | <3MB | <10MB | 512-1024px |
| Desktop | <10MB | <50MB | 1024-2048px |
| High-end | <30MB | <100MB | 2048-4096px |

## Measuring Results

```bash
# Check file sizes
ls -lh *.glb

# Inspect GLTF structure
gltf-transform inspect model.glb

# Validate compression
npx gltf-validator model.glb
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Blurry textures | Over-compression | Increase quality/size |
| Blocky normals | Low quantization | Use higher bit depth |
| Animation jitter | Quantization | Use meshopt for animations |
| Long load time | Large textures | Reduce size, use KTX2 |
| Missing details | Over-simplification | Reduce simplify ratio |
