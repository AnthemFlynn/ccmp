# Asset Validation Reference

Validate and debug 3D assets before deployment.

## Validation Tools

### gltf-validator (Official Khronos)

```bash
# Install
npm install -g gltf-validator

# Validate
npx gltf-validator model.glb

# Output JSON report
npx gltf-validator model.glb --output report.json

# Strict mode (all warnings)
npx gltf-validator model.glb --ignore 0
```

**Common issues detected:**
- Invalid JSON structure
- Missing required properties
- Out-of-bounds indices
- Unused data
- Extension compliance

### gltf.report (Web Tool)

https://gltf.report

**Features:**
- Drag-and-drop validation
- Visual preview
- Memory analysis
- Texture inspection
- Animation playback

### gltf-transform inspect

```bash
# File structure overview
gltf-transform inspect model.glb

# Output includes:
# - Mesh count and sizes
# - Texture count and sizes
# - Animation info
# - Extension usage
# - Total file breakdown
```

## Pre-Flight Checklist

### File Structure

- [ ] GLB format (single file, binary)
- [ ] File size within budget
- [ ] No external references
- [ ] Valid JSON structure

### Geometry

- [ ] Triangle count within budget
- [ ] No degenerate triangles
- [ ] Correct winding order
- [ ] Normals present and valid
- [ ] UVs present (if textured)
- [ ] No overlapping UVs (for AO baking)

### Materials

- [ ] Using glTF PBR metallic-roughness
- [ ] Textures embedded or referenced correctly
- [ ] Correct color space (sRGB for color, Linear for data)
- [ ] Power-of-2 texture dimensions

### Animations

- [ ] Named appropriately
- [ ] Smooth playback
- [ ] No jitter from quantization
- [ ] Loop points correct

### Transforms

- [ ] Applied transforms (no scale != 1)
- [ ] Correct up axis (Y-up for web)
- [ ] Appropriate world-space scale

## Automated Validation Script

```bash
#!/bin/bash
# validate-assets.sh

for file in assets/*.glb; do
  echo "Validating: $file"

  # Check file size
  size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
  if [ $size -gt 10485760 ]; then
    echo "  WARNING: File larger than 10MB ($size bytes)"
  fi

  # Run validator
  npx gltf-validator "$file" --output "${file%.glb}-report.json"

  # Check for errors
  if grep -q '"severity": 0' "${file%.glb}-report.json"; then
    echo "  ERROR: Validation failed"
  else
    echo "  OK: Validation passed"
  fi

  # Inspect structure
  gltf-transform inspect "$file"

  echo ""
done
```

## Common Validation Errors

### Invalid Accessor

```
ACCESSOR_INDEX_OOB
Accessor index is out of bounds
```

**Fix:** Re-export from Blender, check for corrupt geometry

### Missing Attributes

```
MESH_PRIMITIVE_NO_POSITION
Mesh primitive has no POSITION attribute
```

**Fix:** Mesh has no vertices, remove or re-create

### Texture Issues

```
IMAGE_MIME_TYPE_INVALID
Image MIME type is invalid
```

**Fix:** Convert textures to supported format (PNG/JPEG/WebP)

### Index Out of Bounds

```
BUFFER_VIEW_TARGET_OOB
Buffer view target is out of bounds
```

**Fix:** Corrupt file, re-export from source

## Debugging in Three.js

### Log Model Structure

```javascript
loader.load('/model.glb', (gltf) => {
  console.log('Scene:', gltf.scene)
  console.log('Animations:', gltf.animations)
  console.log('Cameras:', gltf.cameras)

  // Traverse all objects
  gltf.scene.traverse((child) => {
    console.log(child.type, child.name)
    if (child.isMesh) {
      console.log('  Geometry:', child.geometry)
      console.log('  Material:', child.material)
    }
  })
})
```

### Check Bounding Box

```javascript
loader.load('/model.glb', (gltf) => {
  const box = new THREE.Box3().setFromObject(gltf.scene)
  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())

  console.log('Model size:', size)
  console.log('Model center:', center)

  // Auto-center
  gltf.scene.position.sub(center)

  // Auto-scale to unit size
  const maxDim = Math.max(size.x, size.y, size.z)
  gltf.scene.scale.setScalar(1 / maxDim)
})
```

### Visualize Normals

```javascript
import { VertexNormalsHelper } from 'three/addons/helpers/VertexNormalsHelper.js'

gltf.scene.traverse((child) => {
  if (child.isMesh) {
    const helper = new VertexNormalsHelper(child, 0.1, 0xff0000)
    scene.add(helper)
  }
})
```

### Check UV Mapping

```javascript
gltf.scene.traverse((child) => {
  if (child.isMesh) {
    const uvAttr = child.geometry.getAttribute('uv')
    if (!uvAttr) {
      console.warn('Missing UVs:', child.name)
    } else {
      // Check UV range
      for (let i = 0; i < uvAttr.count; i++) {
        const u = uvAttr.getX(i)
        const v = uvAttr.getY(i)
        if (u < 0 || u > 1 || v < 0 || v > 1) {
          console.warn('UV out of 0-1 range:', child.name, u, v)
          break
        }
      }
    }
  }
})
```

## Memory Analysis

### GPU Memory Estimation

```javascript
function estimateMemory(gltf) {
  let geometryBytes = 0
  let textureBytes = 0

  gltf.scene.traverse((child) => {
    if (child.isMesh) {
      const geo = child.geometry

      // Positions (Float32 = 4 bytes * 3 components)
      const posAttr = geo.getAttribute('position')
      if (posAttr) geometryBytes += posAttr.count * 3 * 4

      // Normals
      const normAttr = geo.getAttribute('normal')
      if (normAttr) geometryBytes += normAttr.count * 3 * 4

      // UVs
      const uvAttr = geo.getAttribute('uv')
      if (uvAttr) geometryBytes += uvAttr.count * 2 * 4

      // Indices (Uint16 or Uint32)
      const index = geo.index
      if (index) geometryBytes += index.count * (index.array.BYTES_PER_ELEMENT)
    }

    if (child.material) {
      const mat = child.material
      const textures = [mat.map, mat.normalMap, mat.roughnessMap, mat.metalnessMap, mat.aoMap]

      textures.forEach(tex => {
        if (tex && tex.image) {
          // Uncompressed: width * height * 4 (RGBA)
          textureBytes += tex.image.width * tex.image.height * 4
        }
      })
    }
  })

  return {
    geometry: geometryBytes,
    textures: textureBytes,
    total: geometryBytes + textureBytes,
    formatted: {
      geometry: (geometryBytes / 1024 / 1024).toFixed(2) + ' MB',
      textures: (textureBytes / 1024 / 1024).toFixed(2) + ' MB',
      total: ((geometryBytes + textureBytes) / 1024 / 1024).toFixed(2) + ' MB'
    }
  }
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Validate 3D Assets

on:
  push:
    paths:
      - 'public/models/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install validator
        run: npm install -g gltf-validator @gltf-transform/cli

      - name: Validate GLB files
        run: |
          for file in public/models/*.glb; do
            echo "Validating $file..."
            npx gltf-validator "$file" --max-issues 0
          done

      - name: Check file sizes
        run: |
          for file in public/models/*.glb; do
            size=$(stat -c%s "$file")
            if [ $size -gt 5242880 ]; then
              echo "ERROR: $file is larger than 5MB"
              exit 1
            fi
          done
```

## Quality Checklist

### Before Commit

- [ ] Passes gltf-validator with no errors
- [ ] File size within budget
- [ ] Preview renders correctly
- [ ] Textures at appropriate resolution
- [ ] Animations play correctly

### Before Production

- [ ] Compressed with Meshopt/Draco
- [ ] Textures compressed (KTX2/WebP)
- [ ] LODs generated if needed
- [ ] Loading time acceptable
- [ ] Memory usage within budget
