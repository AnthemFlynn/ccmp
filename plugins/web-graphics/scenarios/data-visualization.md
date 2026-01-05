# Data Visualization Scenario

3D data visualization for dashboards, analytics, or interactive charts.

## Tech Stack

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| Framework | React + R3F | Vanilla Three.js |
| Data binding | Zustand | React Context |
| Animation | Spring (react-spring) | useFrame |
| Camera | OrthographicCamera | PerspectiveCamera |
| Instancing | InstancedMesh | Individual meshes |

## When to Use 3D

3D visualization is valuable when:
- Data has natural 3D structure (geographic, network graphs)
- Showing relationships between many variables
- Interactive exploration adds insight
- Visual impact matters (presentations, marketing)

Don't use 3D when:
- 2D charts would be clearer
- Data is simple (bar chart, line graph)
- Performance is critical on low-end devices
- Accessibility is paramount

## Starter Code (R3F)

```jsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Html, Line } from '@react-three/drei'
import { useMemo, useRef, useState } from 'react'
import { useSpring, animated } from '@react-spring/three'

// 3D Bar Chart
function BarChart({ data, maxValue }) {
  const bars = useMemo(() => {
    return data.map((d, i) => ({
      ...d,
      x: (i - data.length / 2) * 1.5,
      height: (d.value / maxValue) * 5
    }))
  }, [data, maxValue])

  return (
    <group>
      {bars.map((bar, i) => (
        <Bar key={bar.id || i} data={bar} />
      ))}
      <gridHelper args={[20, 20, '#ccc', '#eee']} rotation={[0, 0, 0]} />
    </group>
  )
}

function Bar({ data }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)

  const { scale } = useSpring({
    scale: hovered ? 1.1 : 1,
    config: { tension: 300, friction: 10 }
  })

  const { height } = useSpring({
    height: data.height,
    config: { tension: 120, friction: 14 }
  })

  return (
    <animated.mesh
      ref={meshRef}
      position-x={data.x}
      scale-y={height}
      scale-x={scale}
      scale-z={scale}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial
        color={hovered ? '#ff6b6b' : data.color || '#4dabf7'}
      />
      {hovered && (
        <Html position={[0, 0.6, 0]} center>
          <div className="tooltip">
            <strong>{data.label}</strong>
            <span>{data.value}</span>
          </div>
        </Html>
      )}
    </animated.mesh>
  )
}

export default function DataViz3D({ data }) {
  const maxValue = Math.max(...data.map(d => d.value))

  return (
    <Canvas camera={{ position: [10, 10, 10], fov: 50 }}>
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 10, 5]} intensity={0.8} />

      <BarChart data={data} maxValue={maxValue} />

      <OrbitControls
        enablePan={true}
        maxPolarAngle={Math.PI / 2.1}
      />
    </Canvas>
  )
}
```

## Instanced Visualization (Large Datasets)

```jsx
import { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

function ScatterPlot3D({ points }) {
  const meshRef = useRef()
  const count = points.length

  const { matrices, colors } = useMemo(() => {
    const matrices = new Float32Array(count * 16)
    const colors = new Float32Array(count * 3)
    const dummy = new THREE.Object3D()
    const color = new THREE.Color()

    points.forEach((point, i) => {
      dummy.position.set(point.x, point.y, point.z)
      dummy.scale.setScalar(point.size || 0.1)
      dummy.updateMatrix()
      dummy.matrix.toArray(matrices, i * 16)

      color.set(point.color || '#4dabf7')
      color.toArray(colors, i * 3)
    })

    return { matrices, colors }
  }, [points, count])

  useEffect(() => {
    if (meshRef.current) {
      const mesh = meshRef.current

      // Set instance matrices
      for (let i = 0; i < count; i++) {
        const matrix = new THREE.Matrix4()
        matrix.fromArray(matrices, i * 16)
        mesh.setMatrixAt(i, matrix)
      }
      mesh.instanceMatrix.needsUpdate = true

      // Set instance colors
      mesh.geometry.setAttribute(
        'color',
        new THREE.InstancedBufferAttribute(colors, 3)
      )
    }
  }, [matrices, colors, count])

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <sphereGeometry args={[1, 16, 16]} />
      <meshStandardMaterial vertexColors />
    </instancedMesh>
  )
}
```

## Network Graph

```jsx
import { Line, Sphere } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo, useRef, useState } from 'react'

function NetworkGraph({ nodes, edges }) {
  return (
    <group>
      {/* Edges */}
      {edges.map((edge, i) => {
        const start = nodes.find(n => n.id === edge.source)
        const end = nodes.find(n => n.id === edge.target)
        return (
          <Line
            key={i}
            points={[[start.x, start.y, start.z], [end.x, end.y, end.z]]}
            color="#aaa"
            lineWidth={1}
          />
        )
      })}

      {/* Nodes */}
      {nodes.map((node) => (
        <NetworkNode key={node.id} node={node} />
      ))}
    </group>
  )
}

function NetworkNode({ node }) {
  const [hovered, setHovered] = useState(false)
  const meshRef = useRef()

  useFrame((state) => {
    // Subtle floating animation
    meshRef.current.position.y = node.y + Math.sin(state.clock.elapsedTime + node.id) * 0.1
  })

  return (
    <Sphere
      ref={meshRef}
      args={[node.size || 0.5, 32, 32]}
      position={[node.x, node.y, node.z]}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <meshStandardMaterial
        color={hovered ? '#ff6b6b' : node.color || '#4dabf7'}
        emissive={hovered ? '#ff6b6b' : '#000'}
        emissiveIntensity={hovered ? 0.3 : 0}
      />
      {hovered && (
        <Html center>
          <div className="node-tooltip">{node.label}</div>
        </Html>
      )}
    </Sphere>
  )
}
```

## Animated Transitions

```jsx
import { useSpring, animated } from '@react-spring/three'
import { useEffect, useState } from 'react'

function AnimatedDataPoint({ targetPosition, targetColor }) {
  const { position, color } = useSpring({
    position: targetPosition,
    color: targetColor,
    config: { mass: 1, tension: 170, friction: 26 }
  })

  return (
    <animated.mesh position={position}>
      <sphereGeometry args={[0.2]} />
      <animated.meshStandardMaterial color={color} />
    </animated.mesh>
  )
}

// Usage with data updates
function LiveChart({ data }) {
  return (
    <>
      {data.map((d, i) => (
        <AnimatedDataPoint
          key={d.id}
          targetPosition={[d.x, d.y, d.z]}
          targetColor={d.color}
        />
      ))}
    </>
  )
}
```

## Performance Tips

1. **Instancing**: Use InstancedMesh for >100 identical objects
2. **LOD**: Reduce geometry detail for distant points
3. **Culling**: Only render visible data points
4. **Aggregation**: Group nearby points at zoom-out levels
5. **Web Workers**: Process large datasets off main thread

```jsx
// Efficient large dataset handling
function LargeDataset({ data }) {
  // Only render visible subset
  const visibleData = useMemo(() => {
    return data.filter(d => d.visible).slice(0, 10000)
  }, [data])

  return <ScatterPlot3D points={visibleData} />
}
```

## Data Binding with Zustand

```jsx
import { create } from 'zustand'

const useDataStore = create((set, get) => ({
  data: [],
  selectedId: null,
  filters: {},

  setData: (data) => set({ data }),
  selectPoint: (id) => set({ selectedId: id }),
  setFilter: (key, value) => set((state) => ({
    filters: { ...state.filters, [key]: value }
  })),

  // Computed
  get filteredData() {
    const { data, filters } = get()
    return data.filter(d => {
      return Object.entries(filters).every(([key, value]) => {
        if (!value) return true
        return d[key] === value
      })
    })
  }
}))

// In component
function DataPoints() {
  const filteredData = useDataStore((s) => s.filteredData)
  const selectPoint = useDataStore((s) => s.selectPoint)

  return filteredData.map(d => (
    <DataPoint
      key={d.id}
      data={d}
      onClick={() => selectPoint(d.id)}
    />
  ))
}
```

## Checklist

- [ ] Data loads and displays correctly
- [ ] Interactions (hover, click) provide feedback
- [ ] Tooltips show relevant information
- [ ] Transitions animate smoothly on data change
- [ ] Performance handles expected data volume
- [ ] Camera controls allow exploration
- [ ] Legend/axis labels aid understanding
- [ ] Color scheme is accessible
