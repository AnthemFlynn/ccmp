---
name: asset-pipeline-3d
description: Optimize and prepare 3D assets for web delivery. Use this skill when working with GLTF/GLB files, compressing 3D models, optimizing textures, setting up Blender exports, or preparing assets for Three.js/R3F. Covers GLTF workflows, Draco/meshopt compression, texture optimization, LOD generation, and performance profiling.
---

# 3D Asset Pipeline

Prepare and optimize 3D assets for performant web delivery.

> **Tool Versions (2026)**
> - gltf-transform: v4+
> - Meshoptimizer: v0.21+
> - Basis Universal: v1.16+
> - Blender: 4.2+

## Decision Frameworks

### When to Use Which Compression

```
Geometry Compression:
├─ Need fastest decode time? → Meshopt (recommended)
├─ Need smallest file size? → Draco (10-20% smaller)
├─ Animated models (skinned/morphs)? → Meshopt (better animation support)
├─ Static meshes only? → Either works
└─ Maximum compatibility? → No compression (larger files)

Texture Compression:
├─ GPU-compressed (fastest rendering)? → KTX2/Basis Universal
├─ Good balance (size vs quality)? → WebP
├─ Best quality at cost of size? → PNG (lossless) or AVIF
├─ Need alpha channel? → WebP, PNG, KTX2, or AVIF
└─ Photo textures, no alpha? → JPEG or WebP
```

### When to Use Which Pipeline

```
Single hero model (product viewer)?
  → gltf-transform optimize with high quality settings

Many similar models (e-commerce)?
  → Batch processing script with consistent settings

Game assets (performance critical)?
  → Aggressive compression + LODs + texture atlases

Architectural visualization?
  → High poly + baked lighting + KTX2 textures

Real-time application?
  → Meshopt + KTX2 + LODs + strict budgets
```

### Compression Decision Matrix

| Scenario | Geometry | Textures | LODs |
|----------|----------|----------|------|
| Product viewer | Meshopt | WebP/KTX2 | Optional |
| Game assets | Meshopt | KTX2 | Required |
| Archviz | Meshopt | KTX2 2048px | Per-room |
| Mobile | Meshopt | KTX2 512-1024px | Required |
| E-commerce batch | Draco (smaller) | WebP | Optional |

## GLTF/GLB Overview

GLTF (GL Transmission Format) is the standard for web 3D. GLB is the binary version (single file).

**GLTF supports:**
- Meshes, materials (PBR), textures
- Skeletal animations, morph targets
- Scene hierarchy, cameras, lights
- Extensions for advanced features

**File structure:**
- `.gltf` - JSON with external binary/textures
- `.glb` - Single binary file (preferred for web)

## Compression Tools

### gltf-transform (Recommended)

Node.js CLI for GLTF optimization. Install: `npm install -g @gltf-transform/cli`

```bash
# Meshopt compression (recommended - faster decode)
gltf-transform meshopt input.glb output.glb

# Draco compression (smaller files, slower decode)
gltf-transform draco input.glb output.glb

# Texture compression to KTX2/Basis (GPU-compressed)
gltf-transform ktx input.glb output.glb --compress uastc

# Full optimization pipeline (2026 recommended)
gltf-transform optimize input.glb output.glb \
  --compress meshopt \
  --texture-compress ktx2

# WebP textures (good balance, wider support)
gltf-transform optimize input.glb output.glb \
  --compress meshopt \
  --texture-compress webp

# Resize textures (power of 2)
gltf-transform resize input.glb output.glb --width 1024 --height 1024

# Flatten scene hierarchy (reduces draw calls)
gltf-transform flatten input.glb output.glb

# Merge meshes sharing materials
gltf-transform join input.glb output.glb

# Remove unused data
gltf-transform prune input.glb output.glb

# Deduplicate accessors
gltf-transform dedup input.glb output.glb

# Generate simplified LOD
gltf-transform simplify input.glb output.glb --ratio 0.5 --error 0.001

# Full production pipeline
gltf-transform optimize input.glb output.glb \
  --compress meshopt \
  --texture-compress ktx2 \
  --texture-size 1024
```

### gltfpack

Alternative CLI (part of meshoptimizer). Faster, less flexible.

```bash
# Basic optimization
gltfpack -i input.glb -o output.glb

# With Meshopt compression
gltfpack -i input.glb -o output.glb -cc

# With KTX2 texture compression
gltfpack -i input.glb -o output.glb -tc

# Simplify (50% triangle reduction)
gltfpack -i input.glb -o output.glb -si 0.5

# All optimizations (production ready)
gltfpack -i input.glb -o output.glb -cc -tc -si 0.5
```

## Texture Optimization

### Format Selection

| Format | Use Case | Alpha | Compression | GPU Decode |
|--------|----------|-------|-------------|------------|
| KTX2/Basis | GPU-compressed (best) | Yes | UASTC/ETC1S | Native |
| WebP | General textures | Yes | Lossy/Lossless | CPU |
| AVIF | Best file compression | Yes | Lossy | CPU |
| JPEG | Photos, no alpha | No | Lossy | CPU |
| PNG | UI, sharp edges | Yes | Lossless | CPU |

**KTX2/Basis Universal** is preferred for 2026 - textures stay compressed in GPU memory.

### Size Guidelines

| Texture Type | Mobile | Desktop | Notes |
|--------------|--------|---------|-------|
| Diffuse/Albedo | 512-1024 | 1024-2048 | sRGB color space |
| Normal | 512-1024 | 1024-2048 | Linear, tangent space |
| Roughness/Metal | 256-512 | 512-1024 | Linear, can pack |
| AO | 256-512 | 512-1024 | Linear, can pack |
| Environment | 256-512 | 512-1024 | HDR for reflections |

**Power of 2**: Always use power-of-2 dimensions (256, 512, 1024, 2048) for mipmapping.

### Compression Commands

```bash
# ImageMagick - resize and convert
magick input.png -resize 1024x1024 -quality 85 output.webp

# cwebp (WebP)
cwebp -q 80 input.png -o output.webp

# Basis Universal (KTX2) - high quality UASTC
basisu -uastc -uastc_level 2 input.png -output_file output.ktx2

# Basis Universal - smaller ETC1S (lower quality)
basisu input.png -output_file output.ktx2

# toktx (Khronos tool)
toktx --t2 --uastc 2 output.ktx2 input.png

# Squoosh CLI (WebP/AVIF)
squoosh-cli --webp '{quality:80}' input.png
squoosh-cli --avif '{quality:60}' input.png
```

### Channel Packing (ORM)

Combine grayscale maps into RGBA channels to reduce texture count:

```
R: Ambient Occlusion
G: Roughness
B: Metalness
A: (unused or height)
```

```javascript
// Three.js with packed ORM texture
const ormTexture = textureLoader.load('/orm.png')
ormTexture.colorSpace = THREE.LinearSRGBColorSpace

const material = new THREE.MeshStandardNodeMaterial({
  aoMap: ormTexture,
  roughnessMap: ormTexture,
  metalnessMap: ormTexture,
  // Channel selection happens automatically in ORM workflow
})
```

## Blender Export Settings

### GLTF Export Checklist

1. **Apply transforms**: Ctrl+A → All Transforms
2. **Apply modifiers**: Check "Apply Modifiers" in export
3. **Check scale**: Blender default 1 unit = 1 meter
4. **Clean up**: Remove unused materials, objects, shape keys

### Export Settings (Blender 4.2+)

```
Format: GLB (single file)

Include:
  [x] Selected Objects (if exporting subset)
  [x] Custom Properties
  [x] Cameras (if needed)
  [x] Punctual Lights (if needed)

Transform:
  +Y Up (standard for web)

Data:
  Mesh:
    [x] Apply Modifiers
    [x] UVs
    [x] Normals
    [ ] Tangents (let Three.js compute)
    [ ] Vertex Colors (unless needed)

  Material:
    [x] Materials → Export
    [x] Images → Automatic (embeds in GLB)

  Shape Keys: [x] (if using morph targets)
  Skinning: [x] (if using armatures)
  Armature:
    [x] Export Deformation Bones Only

Animation:
  [x] Animations
  Sampling Rate: 24 or match source

Compression:
  [ ] Draco (prefer post-processing with gltf-transform)
```

### Common Export Issues

| Problem | Solution |
|---------|----------|
| Model too big/small | Apply scale (Ctrl+A) before export |
| Missing textures | Pack textures (File → External Data → Pack) |
| Broken normals | Recalculate normals (Shift+N in Edit mode) |
| Flipped faces | Check normals direction, flip if needed |
| Animation jitter | Increase keyframe sampling rate |
| Materials wrong | Use Principled BSDF, check texture paths |
| Bones missing | Check "Export Deformation Bones Only" |

## Loading in Three.js

### WebGPU Setup (2026)

```javascript
import * as THREE from 'three/webgpu'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js'

const loader = new GLTFLoader()

// Meshopt decoder (recommended)
loader.setMeshoptDecoder(MeshoptDecoder)

// KTX2 textures (requires renderer for format detection)
const ktx2Loader = new KTX2Loader()
ktx2Loader.setTranscoderPath('https://cdn.jsdelivr.net/npm/three@0.171.0/examples/jsm/libs/basis/')
ktx2Loader.detectSupport(renderer) // Required!
loader.setKTX2Loader(ktx2Loader)

// Load
const gltf = await loader.loadAsync('/model.glb')
scene.add(gltf.scene)
```

### Draco Fallback (if needed)

```javascript
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js'

const dracoLoader = new DRACOLoader()
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/')
loader.setDRACOLoader(dracoLoader)
```

### React Three Fiber

```jsx
import { useGLTF } from '@react-three/drei'

// Drei handles Meshopt and Draco automatically
const { scene, nodes, materials, animations } = useGLTF('/model.glb')

// Preload for instant display
useGLTF.preload('/model.glb')
```

## Performance Budgets

### Target Metrics

| Platform | Triangles | Draw Calls | Texture Memory | File Size |
|----------|-----------|------------|----------------|-----------|
| Mobile | <100K | <50 | <50MB | <5MB |
| Desktop | <500K | <100 | <200MB | <20MB |
| High-end | <2M | <200 | <500MB | <50MB |

### Profiling

```javascript
// Three.js render info (call after render)
console.log(renderer.info.render)
// { calls, triangles, points, lines, frame }

console.log(renderer.info.memory)
// { geometries, textures }

// Performance monitor
import Stats from 'stats.js'
const stats = new Stats()
stats.showPanel(0) // 0: fps, 1: ms, 2: mb
document.body.appendChild(stats.dom)

function animate() {
  stats.begin()
  renderer.render(scene, camera)
  stats.end()
}
renderer.setAnimationLoop(animate)
```

### Asset Validation

```bash
# Validate GLTF structure
npx gltf-validator model.glb

# Online validation
# https://gltf.report

# Check file size breakdown
gltf-transform inspect model.glb
```

## Related Skills

| When you need... | Use skill |
|------------------|-----------|
| Build 3D scenes with Three.js | → **threejs** |
| Build 3D scenes with React | → **react-three-fiber** |
| Debug rendering/performance issues | → **graphics-troubleshooting** |

## Reference Files

- [references/compression.md](references/compression.md) - Detailed compression comparisons
- [references/textures.md](references/textures.md) - Texture format deep dive
- [references/validation.md](references/validation.md) - Asset validation and debugging
- [references/lod.md](references/lod.md) - Level-of-detail strategies
- [references/baking.md](references/baking.md) - Texture baking workflows
