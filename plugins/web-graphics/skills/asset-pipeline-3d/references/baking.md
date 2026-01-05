# Texture Baking

Bake complex effects into textures for real-time performance.

## Baking in Blender

### Setup

1. Create UV map for target (low-poly) mesh
2. Create image texture node in material (bake target)
3. Select image node (make it active)
4. Set bake settings in Render Properties → Bake

### Bake Types

| Type | Description | Use Case |
|------|-------------|----------|
| Diffuse | Base color without lighting | Texture atlases |
| Roughness | Surface roughness | PBR workflows |
| Normal | Surface detail as normal map | High-to-low poly |
| Ambient Occlusion | Soft shadows in crevices | PBR enhancement |
| Combined | Full lighting baked | Static scenes |
| Emit | Emissive channel | Light maps |
| Shadow | Shadow information | Static shadows |

### High-to-Low Poly Baking

Transfer detail from high-poly sculpt to low-poly game mesh.

```
1. Create low-poly mesh with good UVs
2. Keep high-poly mesh (sculpt or subdivided)
3. Select high-poly, then Shift+select low-poly
4. In Bake settings:
   - Selected to Active: ✓
   - Ray Distance: 0.1 (adjust based on mesh)
   - Cage: optionally create cage mesh
5. Bake Normal map
6. Bake Ambient Occlusion
7. Bake Curvature (for edge wear)
```

### Blender Bake Settings

```
Render Properties → Bake:

Bake Type: Normal
  Space: Tangent (for game engines)
  R: +X, G: +Y, B: +Z (OpenGL standard)

Selected to Active: ✓ (for high-to-low)
  Ray Distance: 0.1
  
Margin:
  Size: 16px (prevents seam artifacts)
  Type: Adjacent Faces

Output:
  Target: Image Textures
  Clear Image: ✓
```

### Normal Map Baking

```python
# Blender Python script for batch normal baking
import bpy

def bake_normal_map(high_poly, low_poly, output_path, resolution=2048):
    # Create bake image
    bake_image = bpy.data.images.new(
        name="NormalBake",
        width=resolution,
        height=resolution,
        float_buffer=True
    )
    
    # Setup material with image node
    mat = low_poly.active_material
    nodes = mat.node_tree.nodes
    
    img_node = nodes.new('ShaderNodeTexImage')
    img_node.image = bake_image
    nodes.active = img_node
    
    # Set bake settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.bake_type = 'NORMAL'
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.cage_extrusion = 0.1
    bpy.context.scene.render.bake.margin = 16
    
    # Select objects
    bpy.ops.object.select_all(action='DESELECT')
    high_poly.select_set(True)
    low_poly.select_set(True)
    bpy.context.view_layer.objects.active = low_poly
    
    # Bake
    bpy.ops.object.bake(type='NORMAL')
    
    # Save image
    bake_image.filepath_raw = output_path
    bake_image.file_format = 'PNG'
    bake_image.save()
```

## Ambient Occlusion Baking

### Blender AO Bake

```
Bake Type: Ambient Occlusion

Samples: 128+ (higher = smoother)
Distance: 1.0 (world units, affects AO spread)

For clean results:
- Use 32-bit float image
- Post-process with levels/curves
```

### Combining AO with Albedo

```javascript
// In shader or material
uniform sampler2D albedoMap;
uniform sampler2D aoMap;
uniform float aoIntensity;

vec3 albedo = texture2D(albedoMap, vUv).rgb;
float ao = texture2D(aoMap, vUv).r;
vec3 finalColor = albedo * mix(1.0, ao, aoIntensity);
```

## Lightmap Baking

Bake static lighting for better performance.

### Blender Lightmap Bake

```
1. Create second UV channel for lightmaps:
   - Object Data Properties → UV Maps → Add
   - Name it "Lightmap"
   
2. Unwrap with margin:
   - Smart UV Project with Island Margin 0.02
   - Or use Lightmap Pack
   
3. Set up lights in scene

4. Bake:
   - Bake Type: Combined or Diffuse
   - Contributions: Direct + Indirect
   - Color: unchecked (for pure light info)
```

### Three.js Lightmap Usage

```javascript
const lightmapTexture = new THREE.TextureLoader().load('/lightmap.jpg')
lightmapTexture.flipY = false
lightmapTexture.channel = 1  // Second UV set

const material = new THREE.MeshStandardMaterial({
  map: albedoTexture,
  lightMap: lightmapTexture,
  lightMapIntensity: 1.0,
})

// Mesh must have second UV set
geometry.setAttribute('uv2', geometry.getAttribute('uv').clone())
// Or load from GLTF which includes uv2
```

## Curvature Baking

Edge highlights and cavity shadows for stylized looks.

### Blender Curvature via Geometry Nodes

```
1. Add Geometry Nodes modifier
2. Create node setup:
   Position → Separate XYZ
   Normal → Separate XYZ
   Math: Subtract position derivatives
   Map Range to 0-1
   Store Named Attribute: "curvature"
   
3. Bake to vertex colors or texture
```

### Post-Process Curvature from Normal Map

```javascript
// Fragment shader to extract curvature from normal map
vec3 normal = texture2D(normalMap, vUv).rgb * 2.0 - 1.0;
vec3 dx = dFdx(normal);
vec3 dy = dFdy(normal);
float curvature = length(dx) + length(dy);
```

## Texture Atlas Generation

Combine multiple textures into single atlas.

### Blender Atlas Workflow

```
1. Select all objects to atlas
2. UV → Pack Islands
3. Or use add-on: "UV Packer" or "Texel Density Checker"
4. Bake all maps to single texture set
```

### Atlas Considerations

- **Consistent texel density**: Same pixels per unit across all objects
- **Padding**: 2-4px between islands to prevent bleeding
- **Power of 2**: Final atlas should be 1024, 2048, 4096
- **Channel packing**: Combine grayscale maps into RGBA

## Baking Checklist

1. **UVs**
   - [ ] No overlapping (except for symmetry)
   - [ ] Consistent texel density
   - [ ] Sufficient margin between islands
   - [ ] Correct UV channel selected

2. **Geometry**
   - [ ] Applied transforms
   - [ ] Clean normals
   - [ ] No non-manifold geometry
   - [ ] Cage mesh if needed (high-to-low)

3. **Materials**
   - [ ] Active image texture node selected
   - [ ] Correct image resolution
   - [ ] 16/32-bit for normals/displacement

4. **Settings**
   - [ ] Appropriate ray distance
   - [ ] Sufficient samples (AO, Combined)
   - [ ] Correct normal space (Tangent for games)
   - [ ] Margin set (16px minimum)

5. **Post-Process**
   - [ ] Fix seams if visible
   - [ ] Adjust levels/contrast
   - [ ] Convert to correct format (PNG for normals, JPEG/WebP for colors)
   - [ ] Check file size and compress if needed
