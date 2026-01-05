# TSL Shaders Reference

TSL (Three.js Shading Language) is the modern way to write custom shaders in Three.js. It compiles to both WGSL (WebGPU) and GLSL (WebGL).

## Why TSL?

- **Cross-platform**: Same code works on WebGPU and WebGL
- **Type-safe**: JavaScript-based, better error messages
- **Composable**: Build shaders from reusable nodes
- **Integrated**: Works with Three.js material system

## Basic Setup

```javascript
import * as THREE from 'three/webgpu'
import {
  color, uniform, uv, time,
  sin, cos, mix, vec3, vec4, float,
  positionLocal, normalLocal
} from 'three/tsl'

// Create material and customize with nodes
const material = new THREE.MeshBasicNodeMaterial()
material.colorNode = color(0xff0000) // Red
```

## Core Concepts

### Nodes

Everything in TSL is a node. Nodes can be combined to create complex effects:

```javascript
// Literal values
const red = color(0xff0000)
const half = float(0.5)
const pos = vec3(1, 2, 3)

// Built-in inputs
const uvCoord = uv()           // UV coordinates
const t = time                  // Elapsed time
const pos = positionLocal       // Vertex position
const norm = normalLocal        // Vertex normal

// Operations
const result = sin(time.mul(2)) // sin(time * 2)
const mixed = mix(red, blue, half) // lerp
```

### Material Nodes

Each material has customizable nodes:

```javascript
const material = new THREE.MeshStandardNodeMaterial()

// Available nodes:
material.colorNode = ...        // Base color
material.opacityNode = ...      // Alpha
material.normalNode = ...       // Normal map
material.roughnessNode = ...    // Roughness
material.metalnessNode = ...    // Metalness
material.emissiveNode = ...     // Emission
material.positionNode = ...     // Vertex position (vertex shader)
```

## Common Patterns

### Animated Color

```javascript
import { color, time, sin, mix } from 'three/tsl'

const material = new THREE.MeshBasicNodeMaterial()

// Oscillate between red and blue
const red = color(0xff0000)
const blue = color(0x0000ff)
const t = sin(time).mul(0.5).add(0.5) // 0 to 1
material.colorNode = mix(red, blue, t)
```

### UV-Based Gradient

```javascript
import { uv, vec3 } from 'three/tsl'

const material = new THREE.MeshBasicNodeMaterial()

// Horizontal gradient
material.colorNode = vec3(uv().x, 0, 1.0.sub(uv().x))
```

### Procedural Noise Pattern

```javascript
import { uv, time, sin, cos, vec3 } from 'three/tsl'

const material = new THREE.MeshBasicNodeMaterial()

// Simple wave pattern
const wave = sin(uv().x.mul(20).add(time))
           .add(sin(uv().y.mul(20).add(time)))
           .mul(0.5).add(0.5)

material.colorNode = vec3(wave, wave.mul(0.5), 1.0.sub(wave))
```

### Fresnel Effect

```javascript
import { normalView, cameraPosition, positionWorld, dot, pow, vec3, float } from 'three/tsl'

const material = new THREE.MeshStandardNodeMaterial()

// View direction
const viewDir = cameraPosition.sub(positionWorld).normalize()
const fresnel = pow(float(1).sub(dot(normalView, viewDir).max(0)), 2)

// Apply fresnel to emission
material.emissiveNode = vec3(fresnel, fresnel.mul(0.5), 1).mul(fresnel)
```

### Vertex Displacement

```javascript
import { positionLocal, normalLocal, sin, time, float } from 'three/tsl'

const material = new THREE.MeshStandardNodeMaterial()

// Displace vertices along normal
const displacement = sin(positionLocal.y.mul(10).add(time)).mul(0.1)
material.positionNode = positionLocal.add(normalLocal.mul(displacement))
```

### Dissolve Effect

```javascript
import { uv, uniform, texture, step, mix, color, float } from 'three/tsl'

const noiseTexture = new THREE.TextureLoader().load('/noise.png')
const threshold = uniform(0.5) // Control via JS

const material = new THREE.MeshStandardNodeMaterial()

const noise = texture(noiseTexture, uv())
const alpha = step(threshold, noise.r)

material.opacityNode = alpha
material.transparent = true
material.alphaTest = 0.01
```

## Uniforms

Pass values from JavaScript to shaders:

```javascript
import { uniform, color, float, vec2, vec3 } from 'three/tsl'

// Create uniforms
const uColor = uniform(color(0xff0000))
const uIntensity = uniform(float(1.0))
const uMouse = uniform(vec2(0, 0))

const material = new THREE.MeshBasicNodeMaterial()
material.colorNode = uColor.mul(uIntensity)

// Update in render loop
function animate() {
  uIntensity.value = Math.sin(Date.now() * 0.001) * 0.5 + 0.5
  uMouse.value.set(mouseX, mouseY)
}
```

## Textures

```javascript
import { texture, uv, time, vec2 } from 'three/tsl'

const tex = new THREE.TextureLoader().load('/texture.jpg')

const material = new THREE.MeshBasicNodeMaterial()

// Simple texture
material.colorNode = texture(tex)

// Scrolling texture
const scrolledUV = uv().add(vec2(time.mul(0.1), 0))
material.colorNode = texture(tex, scrolledUV)

// Texture with tint
material.colorNode = texture(tex).mul(color(0xff8800))
```

## Math Functions

```javascript
import {
  sin, cos, tan, asin, acos, atan,  // Trigonometry
  abs, sign, floor, ceil, fract,     // Rounding
  min, max, clamp, saturate,         // Clamping
  mix, smoothstep, step,             // Interpolation
  pow, sqrt, log, exp,               // Power
  length, distance, dot, cross,      // Vector
  normalize, reflect, refract        // Vector operations
} from 'three/tsl'
```

## Examples

### Hologram Effect

```javascript
import { color, normalView, cameraPosition, positionWorld, time, sin, pow, float, vec3 } from 'three/tsl'

const material = new THREE.MeshBasicNodeMaterial()

// Fresnel
const viewDir = cameraPosition.sub(positionWorld).normalize()
const fresnel = pow(float(1).sub(dot(normalView, viewDir).max(0)), 3)

// Scanlines
const scanline = sin(positionWorld.y.mul(50).add(time.mul(5))).mul(0.5).add(0.5)

// Combine
const holoColor = vec3(0.2, 0.8, 1.0)
material.colorNode = holoColor.mul(fresnel.add(0.2)).mul(scanline.mul(0.5).add(0.5))
material.opacityNode = fresnel.mul(0.8).add(0.2)
material.transparent = true
```

### Energy Shield

```javascript
import { color, uv, time, normalView, positionWorld, cameraPosition, sin, pow, vec3, float } from 'three/tsl'

const material = new THREE.MeshBasicNodeMaterial()

// Hexagon pattern (simplified)
const hex = sin(uv().x.mul(20)).mul(sin(uv().y.mul(20)))

// Fresnel
const viewDir = cameraPosition.sub(positionWorld).normalize()
const fresnel = pow(float(1).sub(dot(normalView, viewDir).max(0)), 2)

// Pulse
const pulse = sin(time.mul(3)).mul(0.3).add(0.7)

// Shield color
const shieldColor = vec3(0.3, 0.6, 1.0)
material.colorNode = shieldColor.mul(fresnel.add(hex.mul(0.2))).mul(pulse)
material.opacityNode = fresnel.mul(0.9)
material.transparent = true
material.side = THREE.DoubleSide
```

### Toon Shading

```javascript
import { normalWorld, vec3, step, mix, color } from 'three/tsl'

const material = new THREE.MeshBasicNodeMaterial()

// Light direction
const lightDir = vec3(1, 1, 1).normalize()
const NdotL = dot(normalWorld, lightDir).max(0)

// Toon bands
const shadow = color(0x333366)
const mid = color(0x6666aa)
const lit = color(0xaaaaff)

const toon = mix(shadow, mid, step(0.3, NdotL))
material.colorNode = mix(toon, lit, step(0.7, NdotL))
```

## Debugging

```javascript
// Visualize UVs
material.colorNode = vec3(uv().x, uv().y, 0)

// Visualize normals
material.colorNode = normalLocal.mul(0.5).add(0.5)

// Visualize position
material.colorNode = positionLocal.mul(0.5).add(0.5)

// Visualize any value as grayscale
const value = sin(time)
material.colorNode = vec3(value, value, value)
```

## Migration from GLSL

| GLSL | TSL |
|------|-----|
| `vec3(1, 0, 0)` | `vec3(1, 0, 0)` |
| `a * b` | `a.mul(b)` |
| `a + b` | `a.add(b)` |
| `sin(x)` | `sin(x)` |
| `mix(a, b, t)` | `mix(a, b, t)` |
| `texture2D(tex, uv)` | `texture(tex, uv)` |
| `uniform float time;` | `const t = time` |
| `gl_Position` | `material.positionNode` |
| `gl_FragColor` | `material.colorNode` |
