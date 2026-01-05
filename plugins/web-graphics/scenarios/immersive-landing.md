# Immersive Landing Page Scenario

Scroll-driven 3D experiences for marketing sites, portfolios, or storytelling.

## Tech Stack

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| Framework | React + R3F | Vanilla Three.js + GSAP |
| Scroll control | ScrollControls (Drei) | react-scroll-motion |
| Animation | useScroll hook | GSAP ScrollTrigger |
| Text | Html component | CSS overlays |
| Performance | demand frameloop | intersection observer |

## Core Pattern

```jsx
import { Canvas } from '@react-three/fiber'
import { ScrollControls, Scroll, useScroll, Html } from '@react-three/drei'
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

export default function ImmersiveLanding() {
  return (
    <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
      <color attach="background" args={['#000']} />

      <ScrollControls pages={5} damping={0.1}>
        {/* 3D content that animates with scroll */}
        <Scene />

        {/* HTML content that scrolls */}
        <Scroll html>
          <HtmlContent />
        </Scroll>
      </ScrollControls>
    </Canvas>
  )
}

function Scene() {
  const scroll = useScroll()
  const groupRef = useRef()

  useFrame(() => {
    const offset = scroll.offset // 0 to 1

    // Animate based on scroll position
    groupRef.current.rotation.y = offset * Math.PI * 2
    groupRef.current.position.y = offset * -10
  })

  return (
    <group ref={groupRef}>
      <HeroSection />
      <FeaturesSection />
      <CTASection />
    </group>
  )
}
```

## Scroll-Driven Animations

```jsx
import { useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'

function ScrollAnimatedObject() {
  const scroll = useScroll()
  const meshRef = useRef()

  useFrame(() => {
    const offset = scroll.offset

    // Animate in range (0.2 to 0.4 of scroll)
    const range = scroll.range(0.2, 0.2) // start, length

    // Scale up as user scrolls into view
    meshRef.current.scale.setScalar(THREE.MathUtils.lerp(0.5, 1.5, range))

    // Rotate continuously
    meshRef.current.rotation.y = offset * Math.PI * 4

    // Fade in
    meshRef.current.material.opacity = range
  })

  return (
    <mesh ref={meshRef} position={[0, -5, 0]}>
      <torusKnotGeometry args={[1, 0.3, 128, 16]} />
      <meshStandardMaterial color="#ff6b6b" transparent />
    </mesh>
  )
}

// Curve-based camera path
function CameraPath() {
  const scroll = useScroll()

  // Define camera path
  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 0, 10),
    new THREE.Vector3(5, 2, 5),
    new THREE.Vector3(0, 5, 0),
    new THREE.Vector3(-5, 2, 5),
    new THREE.Vector3(0, 0, 10),
  ])

  useFrame((state) => {
    const offset = scroll.offset

    // Move camera along curve
    const point = curve.getPointAt(offset)
    state.camera.position.copy(point)

    // Look at center
    state.camera.lookAt(0, 0, 0)
  })

  return null
}
```

## Section-Based Layout

```jsx
function SectionsLayout() {
  return (
    <>
      {/* Section 1: Hero (scroll 0-0.2) */}
      <Section start={0} end={0.2}>
        <HeroContent />
      </Section>

      {/* Section 2: Features (scroll 0.2-0.5) */}
      <Section start={0.2} end={0.5}>
        <FeaturesContent />
      </Section>

      {/* Section 3: Testimonials (scroll 0.5-0.8) */}
      <Section start={0.5} end={0.8}>
        <TestimonialsContent />
      </Section>

      {/* Section 4: CTA (scroll 0.8-1.0) */}
      <Section start={0.8} end={1}>
        <CTAContent />
      </Section>
    </>
  )
}

function Section({ start, end, children }) {
  const scroll = useScroll()
  const groupRef = useRef()

  useFrame(() => {
    const visible = scroll.visible(start, end - start)
    const range = scroll.range(start, end - start)

    // Fade in/out
    groupRef.current.visible = visible > 0

    // Position based on section
    const sectionY = start * -50 // Each section is 50 units apart
    groupRef.current.position.y = sectionY

    // Scale animation
    const scale = THREE.MathUtils.lerp(0.8, 1, range)
    groupRef.current.scale.setScalar(scale)
  })

  return <group ref={groupRef}>{children}</group>
}
```

## HTML Overlay Content

```jsx
function HtmlContent() {
  return (
    <>
      {/* Hero section */}
      <div className="section hero" style={{ height: '100vh' }}>
        <h1>Welcome to the Future</h1>
        <p>Scroll to explore</p>
      </div>

      {/* Features section */}
      <div className="section features" style={{ height: '150vh', marginTop: '50vh' }}>
        <div className="feature">
          <h2>Feature One</h2>
          <p>Description of this amazing feature.</p>
        </div>
      </div>

      {/* CTA section */}
      <div className="section cta" style={{ height: '100vh' }}>
        <h2>Ready to Start?</h2>
        <button>Get Started</button>
      </div>
    </>
  )
}

// CSS
const styles = `
.section {
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  pointer-events: none;
}

.section button {
  pointer-events: auto;
}
`
```

## Parallax Effects

```jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useScroll, Stars } from '@react-three/drei'

function ParallaxLayers() {
  const scroll = useScroll()
  const layer1 = useRef()
  const layer2 = useRef()
  const layer3 = useRef()

  useFrame(() => {
    const offset = scroll.offset

    // Different scroll speeds create parallax
    layer1.current.position.y = offset * -10  // Slow
    layer2.current.position.y = offset * -20  // Medium
    layer3.current.position.y = offset * -40  // Fast
  })

  return (
    <>
      {/* Background layer (slow) */}
      <group ref={layer1}>
        <Stars radius={100} depth={50} count={5000} factor={4} />
      </group>

      {/* Mid layer (medium) */}
      <group ref={layer2}>
        <FloatingParticles count={100} />
      </group>

      {/* Foreground layer (fast) */}
      <group ref={layer3}>
        <MainContent />
      </group>
    </>
  )
}
```

## Entrance Animations

```jsx
import { useSpring, animated } from '@react-spring/three'
import { useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useState } from 'react'

function AnimatedSection({ scrollStart }) {
  const scroll = useScroll()
  const [visible, setVisible] = useState(false)

  useFrame(() => {
    const inView = scroll.offset >= scrollStart
    if (inView !== visible) setVisible(inView)
  })

  const { scale, opacity } = useSpring({
    scale: visible ? 1 : 0,
    opacity: visible ? 1 : 0,
    config: { mass: 1, tension: 200, friction: 30 }
  })

  return (
    <animated.mesh scale={scale}>
      <boxGeometry />
      <animated.meshStandardMaterial transparent opacity={opacity} />
    </animated.mesh>
  )
}
```

## Performance Optimizations

```jsx
// Only render when scrolling
function OptimizedCanvas() {
  const [scrolling, setScrolling] = useState(false)
  const timeoutRef = useRef()

  useEffect(() => {
    const handleScroll = () => {
      setScrolling(true)
      clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(() => setScrolling(false), 150)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <Canvas frameloop={scrolling ? 'always' : 'demand'}>
      {/* ... */}
    </Canvas>
  )
}

// Lazy load heavy sections
function LazySection({ scrollThreshold, children }) {
  const [loaded, setLoaded] = useState(false)
  const scroll = useScroll()

  useFrame(() => {
    if (!loaded && scroll.offset > scrollThreshold - 0.1) {
      setLoaded(true)
    }
  })

  if (!loaded) return null
  return children
}
```

## Mobile Considerations

```jsx
function ResponsiveScene() {
  const { viewport } = useThree()
  const isMobile = viewport.width < 5 // Approximate mobile breakpoint

  return (
    <>
      {/* Adjust complexity for mobile */}
      <Stars count={isMobile ? 1000 : 5000} />

      {/* Adjust positions for viewport */}
      <mesh position={[viewport.width / 4, 0, 0]}>
        {/* ... */}
      </mesh>
    </>
  )
}

// Touch-friendly scroll
<ScrollControls
  pages={5}
  damping={0.1}
  // Better touch scrolling
  touch={1} // 1 = 100% touch sensitivity
/>
```

## Complete Example

```jsx
import { Canvas } from '@react-three/fiber'
import { ScrollControls, Scroll, useScroll, Stars, Float, Text } from '@react-three/drei'
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export default function LandingPage() {
  return (
    <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
      <color attach="background" args={['#0a0a0a']} />
      <fog attach="fog" args={['#0a0a0a', 5, 30]} />

      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />

      <ScrollControls pages={4} damping={0.1}>
        <Stars radius={50} depth={50} count={3000} factor={4} />

        <AnimatedContent />

        <Scroll html>
          <LandingContent />
        </Scroll>
      </ScrollControls>
    </Canvas>
  )
}

function AnimatedContent() {
  const scroll = useScroll()
  const torusRef = useRef()
  const sphereRef = useRef()

  useFrame((state) => {
    const offset = scroll.offset

    // Hero torus
    torusRef.current.rotation.x = offset * Math.PI
    torusRef.current.rotation.y = offset * Math.PI * 2
    torusRef.current.position.y = -offset * 30

    // Feature sphere
    const featureRange = scroll.range(0.25, 0.25)
    sphereRef.current.scale.setScalar(featureRange * 2)
    sphereRef.current.position.y = -15 + (1 - featureRange) * 5
  })

  return (
    <>
      <Float speed={2} rotationIntensity={0.5}>
        <mesh ref={torusRef}>
          <torusKnotGeometry args={[1.5, 0.5, 128, 16]} />
          <meshStandardMaterial color="#ff6b6b" metalness={0.8} roughness={0.2} />
        </mesh>
      </Float>

      <mesh ref={sphereRef} position={[3, -15, 0]}>
        <icosahedronGeometry args={[1, 1]} />
        <meshStandardMaterial color="#4dabf7" wireframe />
      </mesh>
    </>
  )
}
```

## Checklist

- [ ] Scroll feel is smooth and responsive
- [ ] 3D animations sync with scroll position
- [ ] HTML content is readable and accessible
- [ ] Performance is good on scroll (no jank)
- [ ] Mobile touch scroll works well
- [ ] Sections transition smoothly
- [ ] Loading states handle heavy assets
- [ ] Reduced motion preference respected
