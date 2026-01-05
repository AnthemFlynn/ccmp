# 3D Format Reference

Comparison and conversion between 3D file formats.

## Format Comparison

### Mesh Formats

| Format | Extension | Features | Best For |
|--------|-----------|----------|----------|
| GLTF/GLB | .gltf/.glb | Full PBR, animation, scene | Web delivery |
| FBX | .fbx | Animation, rigging | Game engines, DCC exchange |
| OBJ | .obj | Mesh + materials | Simple static meshes |
| USD | .usd/.usda/.usdc | Composition, variants | Film/VFX pipelines |
| Alembic | .abc | Baked animation, simulation | VFX, cached animation |
| STL | .stl | Mesh only | 3D printing |
| PLY | .ply | Point clouds, scans | Photogrammetry |

### GLTF vs FBX

| Aspect | GLTF | FBX |
|--------|------|-----|
| Openness | Open standard | Autodesk proprietary |
| Web support | Native | Requires conversion |
| File size | Smaller (binary GLB) | Larger |
| PBR materials | Full support | Partial |
| Compression | Draco, Meshopt, KTX2 | None standard |
| Animation | Skeletal, morph, keyframe | Full suite |
| Scene hierarchy | Yes | Yes |
| Cameras/Lights | Yes | Yes |

**Recommendation**: Use GLTF for web. Convert FBX to GLTF for delivery.

## Conversion Tools

### Blender (Universal Converter)

Import/export most formats. Best for manual cleanup.

```
Import: FBX, OBJ, DAE, USD, Alembic, STL, PLY, GLTF
Export: GLTF, FBX, OBJ, USD, Alembic, STL
```

### Command Line Tools

```bash
# FBX to GLTF (FBX2glTF)
FBX2glTF -i model.fbx -o model.glb

# OBJ to GLTF (obj2gltf)
npx obj2gltf -i model.obj -o model.glb

# DAE (Collada) to GLTF (COLLADA2GLTF)
COLLADA2GLTF -i model.dae -o model.gltf

# Any to GLTF via Assimp
assimp export model.fbx model.gltf
```

### Online Converters

- **gltf.report**: Validate and inspect GLTF
- **Sketchfab**: Upload any format, download as GLTF
- **Gestaltor**: GLTF editor and converter

## GLTF Extensions

### Core Extensions

| Extension | Purpose | Support |
|-----------|---------|---------|
| KHR_draco_mesh_compression | Geometry compression | Widespread |
| KHR_mesh_quantization | Reduce precision | Widespread |
| KHR_texture_basisu | GPU texture compression | Growing |
| KHR_materials_unlit | Unlit materials | Widespread |
| KHR_lights_punctual | Point/spot/directional lights | Widespread |
| KHR_texture_transform | UV offset/scale/rotation | Widespread |

### Material Extensions

| Extension | Purpose |
|-----------|---------|
| KHR_materials_transmission | Glass/liquid transparency |
| KHR_materials_volume | Refraction, absorption |
| KHR_materials_ior | Index of refraction |
| KHR_materials_clearcoat | Car paint, lacquer |
| KHR_materials_sheen | Fabric, velvet |
| KHR_materials_specular | Specular workflow |
| KHR_materials_iridescence | Soap bubbles, oil slicks |
| KHR_materials_anisotropy | Brushed metal |
| KHR_materials_emissive_strength | HDR emissive |

### Checking Extension Support

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const loader = new GLTFLoader()
loader.load('/model.glb', (gltf) => {
  console.log('Extensions used:', gltf.parser.json.extensionsUsed)
  console.log('Extensions required:', gltf.parser.json.extensionsRequired)
})
```

## Texture Formats

### Image Formats

| Format | Compression | Alpha | HDR | Use Case |
|--------|-------------|-------|-----|----------|
| PNG | Lossless | Yes | No | UI, masks, normals |
| JPEG | Lossy | No | No | Photos, diffuse |
| WebP | Both | Yes | No | General web |
| AVIF | Lossy | Yes | Yes | Best compression |
| EXR | Lossless | Yes | Yes | HDR, compositing |
| HDR | None | No | Yes | Environment maps |

### GPU Compressed (KTX2/Basis)

| Mode | Quality | Size | Decode Speed |
|------|---------|------|--------------|
| ETC1S | Lower | Smallest | Fastest |
| UASTC | Higher | Larger | Fast |

```bash
# Create KTX2 with UASTC (quality priority)
basisu -uastc -uastc_level 2 input.png -output_file output.ktx2

# Create KTX2 with ETC1S (size priority)
basisu -comp_level 2 input.png -output_file output.ktx2

# Via gltf-transform
gltf-transform ktx model.glb model_ktx.glb --compress uastc
```

### Format Selection Guide

```
Is it a normal map?
  → PNG or KTX2 (UASTC)
  
Is it a photo/diffuse?
  → WebP (quality 80-85) or KTX2 (ETC1S)
  
Does it need alpha?
  → WebP or PNG
  
Is it an environment/HDR?
  → HDR or EXR (convert to cubemap)
  
Is GPU decompression important?
  → KTX2/Basis
```

## Animation Formats

### Keyframe Animation

Standard in GLTF, FBX, USD. Stores transforms per keyframe.

```
Pros: Precise control, editability
Cons: File size scales with duration and complexity
```

### Baked Animation (Alembic)

Stores vertex positions per frame. For cloth, fluid, destruction.

```
Pros: Any deformation possible
Cons: Large files, no runtime blending
```

### Morph Targets (Blend Shapes)

Store mesh deltas. For facial animation, corrective shapes.

```
Pros: Blendable, compact
Cons: Memory for vertex deltas
```

## Validation

### GLTF Validator

```bash
# Online
https://github.khronos.org/glTF-Validator/

# CLI
npm install -g gltf-validator
gltf-validator model.glb

# Programmatic
import { validateBytes } from 'gltf-validator'
const report = await validateBytes(new Uint8Array(buffer))
console.log(report.issues)
```

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| ACCESSOR_TOTAL_OFFSET_ALIGNMENT | Buffer alignment | Re-export or use gltf-transform |
| MESH_PRIMITIVE_UNEQUAL_ACCESSOR_COUNT | Mismatched attributes | Check geometry in Blender |
| TEXTURE_INVALID_IMAGE | Corrupted/unsupported image | Convert to PNG/JPEG |
| ANIMATION_SAMPLER_INPUT_ACCESSOR_WITHOUT_BOUNDS | Missing min/max | Re-export animation |

### Three.js GLTF Inspection

```javascript
loader.load('/model.glb', (gltf) => {
  // Log structure
  console.log('Scene:', gltf.scene)
  console.log('Animations:', gltf.animations)
  console.log('Cameras:', gltf.cameras)
  console.log('Asset:', gltf.asset)
  
  // Traverse meshes
  gltf.scene.traverse((child) => {
    if (child.isMesh) {
      console.log('Mesh:', child.name)
      console.log('  Geometry:', child.geometry)
      console.log('  Material:', child.material)
      console.log('  Vertices:', child.geometry.attributes.position.count)
    }
  })
})
```

## File Size Reference

### Typical Sizes (Compressed GLB)

| Asset Type | Uncompressed | Draco | Meshopt |
|------------|--------------|-------|---------|
| Simple prop (1K tris) | 50-100KB | 20-40KB | 25-50KB |
| Character (10K tris) | 500KB-1MB | 150-300KB | 200-400KB |
| Vehicle (50K tris) | 2-5MB | 500KB-1MB | 700KB-1.5MB |
| Environment (100K tris) | 5-10MB | 1-2MB | 1.5-3MB |

### Texture Size Impact

| Resolution | PNG (RGBA) | JPEG (q85) | WebP (q80) | KTX2 (UASTC) |
|------------|------------|------------|------------|--------------|
| 512×512 | 1MB | 50KB | 40KB | 350KB |
| 1024×1024 | 4MB | 150KB | 120KB | 1.3MB |
| 2048×2048 | 16MB | 500KB | 400KB | 5MB |
| 4096×4096 | 64MB | 1.5MB | 1.2MB | 21MB |

Note: KTX2 is larger but decompresses faster on GPU and uses less VRAM.
