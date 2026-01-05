# Shader Patterns

Custom shaders for advanced visual effects in Three.js.

## ShaderMaterial Structure

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
    uTexture: { value: texture },
    uColor: { value: new THREE.Color(0xff0000) },
  },
  vertexShader: `...`,
  fragmentShader: `...`,
  transparent: true,
  side: THREE.DoubleSide,
});

// Update in animation loop
material.uniforms.uTime.value = clock.getElapsedTime();
```

## Basic Vertex Shader

```glsl
uniform float uTime;
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);
  vPosition = position;
  
  vec3 pos = position;
  // Apply vertex displacement here
  pos.z += sin(pos.x * 10.0 + uTime) * 0.1;
  
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
```

## Basic Fragment Shader

```glsl
uniform float uTime;
uniform vec3 uColor;
uniform sampler2D uTexture;
varying vec2 vUv;
varying vec3 vNormal;

void main() {
  vec4 texColor = texture2D(uTexture, vUv);
  
  // Fresnel effect
  vec3 viewDirection = normalize(cameraPosition - vPosition);
  float fresnel = pow(1.0 - dot(viewDirection, vNormal), 3.0);
  
  gl_FragColor = vec4(uColor * fresnel + texColor.rgb, 1.0);
}
```

## Common Shader Patterns

### Gradient
```glsl
vec3 color = mix(colorA, colorB, vUv.y);
```

### Noise (simplex/perlin)
Use `glsl-noise` or inline noise functions for procedural patterns.

### Pulse Effect
```glsl
float pulse = sin(uTime * 2.0) * 0.5 + 0.5;
gl_FragColor = vec4(uColor * pulse, 1.0);
```

### Rim Lighting
```glsl
float rim = 1.0 - max(0.0, dot(vNormal, viewDirection));
rim = pow(rim, 3.0);
```

### UV Distortion
```glsl
vec2 distortedUv = vUv;
distortedUv.x += sin(vUv.y * 10.0 + uTime) * 0.1;
```

## GLSL Built-in Functions

- `mix(a, b, t)` - linear interpolation
- `smoothstep(edge0, edge1, x)` - smooth Hermite interpolation
- `clamp(x, min, max)` - constrain value
- `fract(x)` - fractional part
- `mod(x, y)` - modulo
- `step(edge, x)` - returns 0.0 if x < edge, else 1.0
- `length(v)` - vector magnitude
- `normalize(v)` - unit vector
- `dot(a, b)` - dot product
- `cross(a, b)` - cross product
- `reflect(I, N)` - reflection vector

## RawShaderMaterial

For complete control (no Three.js uniforms injected):

```javascript
const material = new THREE.RawShaderMaterial({
  uniforms: { ... },
  vertexShader: `
    precision highp float;
    uniform mat4 projectionMatrix;
    uniform mat4 modelViewMatrix;
    attribute vec3 position;
    attribute vec2 uv;
    varying vec2 vUv;
    
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    precision highp float;
    varying vec2 vUv;
    
    void main() {
      gl_FragColor = vec4(vUv, 1.0, 1.0);
    }
  `,
});
```

## onBeforeCompile Hook

Modify built-in materials without full custom shaders:

```javascript
const material = new THREE.MeshStandardMaterial();
material.onBeforeCompile = (shader) => {
  shader.uniforms.uTime = { value: 0 };
  
  shader.vertexShader = shader.vertexShader.replace(
    '#include <begin_vertex>',
    `
    #include <begin_vertex>
    transformed.z += sin(transformed.x * 5.0 + uTime) * 0.2;
    `
  );
  
  // Store reference to update uniform
  material.userData.shader = shader;
};

// In animate loop:
if (material.userData.shader) {
  material.userData.shader.uniforms.uTime.value = elapsed;
}
```
