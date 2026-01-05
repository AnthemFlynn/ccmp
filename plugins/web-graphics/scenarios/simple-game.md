# Simple Game Scenario

Browser-based 3D games: arcade, puzzle, casual games.

## Tech Stack

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| Framework | React + R3F | Vanilla Three.js |
| Physics | @react-three/rapier | cannon-es |
| State | Zustand | Redux |
| Controls | PointerLockControls | Custom |
| Audio | Howler.js | Web Audio API |
| Input | Native events | gamepad API |

## Game Loop Architecture

```jsx
import { create } from 'zustand'

// Game state store
const useGame = create((set, get) => ({
  // State
  phase: 'ready', // ready, playing, paused, ended
  score: 0,
  lives: 3,
  level: 1,

  // Actions
  start: () => set({ phase: 'playing', score: 0, lives: 3 }),
  pause: () => set({ phase: 'paused' }),
  resume: () => set({ phase: 'playing' }),
  end: () => set({ phase: 'ended' }),

  addScore: (points) => set((s) => ({ score: s.score + points })),
  loseLife: () => {
    const lives = get().lives - 1
    if (lives <= 0) {
      set({ lives: 0, phase: 'ended' })
    } else {
      set({ lives })
    }
  },
  nextLevel: () => set((s) => ({ level: s.level + 1 })),

  restart: () => set({ phase: 'ready', score: 0, lives: 3, level: 1 })
}))
```

## Starter Code (R3F + Rapier Physics)

```jsx
import { Canvas } from '@react-three/fiber'
import { Physics, RigidBody, CuboidCollider } from '@react-three/rapier'
import { KeyboardControls, PointerLockControls } from '@react-three/drei'
import { Suspense } from 'react'

const keyMap = [
  { name: 'forward', keys: ['KeyW', 'ArrowUp'] },
  { name: 'backward', keys: ['KeyS', 'ArrowDown'] },
  { name: 'left', keys: ['KeyA', 'ArrowLeft'] },
  { name: 'right', keys: ['KeyD', 'ArrowRight'] },
  { name: 'jump', keys: ['Space'] },
]

export default function Game() {
  return (
    <KeyboardControls map={keyMap}>
      <Canvas shadows camera={{ fov: 75 }}>
        <Suspense fallback={null}>
          <Physics gravity={[0, -30, 0]}>
            <Lights />
            <Player />
            <Level />
          </Physics>
        </Suspense>
        <PointerLockControls />
      </Canvas>
      <UI />
    </KeyboardControls>
  )
}

function Lights() {
  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight
        position={[10, 20, 10]}
        intensity={1}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-far={50}
        shadow-camera-left={-20}
        shadow-camera-right={20}
        shadow-camera-top={20}
        shadow-camera-bottom={-20}
      />
    </>
  )
}

function UI() {
  const { phase, score, lives } = useGame()

  return (
    <div className="game-ui">
      <div className="hud">
        <span>Score: {score}</span>
        <span>Lives: {'❤️'.repeat(lives)}</span>
      </div>

      {phase === 'ready' && (
        <div className="overlay">
          <h1>Click to Start</h1>
        </div>
      )}

      {phase === 'ended' && (
        <div className="overlay">
          <h1>Game Over</h1>
          <p>Final Score: {score}</p>
          <button onClick={() => useGame.getState().restart()}>
            Play Again
          </button>
        </div>
      )}
    </div>
  )
}
```

## Player Controller

```jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { RigidBody, CapsuleCollider } from '@react-three/rapier'
import { useKeyboardControls } from '@react-three/drei'
import * as THREE from 'three'

const SPEED = 5
const JUMP_FORCE = 10

function Player() {
  const rigidBodyRef = useRef()
  const [, getKeys] = useKeyboardControls()

  const canJump = useRef(true)

  useFrame((state, delta) => {
    if (!rigidBodyRef.current) return

    const { forward, backward, left, right, jump } = getKeys()

    // Get camera direction
    const camera = state.camera
    const direction = new THREE.Vector3()
    camera.getWorldDirection(direction)
    direction.y = 0
    direction.normalize()

    const sideways = new THREE.Vector3()
    sideways.crossVectors(camera.up, direction).normalize()

    // Calculate movement
    const impulse = new THREE.Vector3()

    if (forward) impulse.add(direction)
    if (backward) impulse.sub(direction)
    if (left) impulse.add(sideways)
    if (right) impulse.sub(sideways)

    impulse.normalize().multiplyScalar(SPEED * delta * 100)

    // Apply movement
    const vel = rigidBodyRef.current.linvel()
    rigidBodyRef.current.setLinvel({
      x: impulse.x,
      y: vel.y,
      z: impulse.z
    })

    // Jump
    if (jump && canJump.current) {
      rigidBodyRef.current.applyImpulse({ x: 0, y: JUMP_FORCE, z: 0 })
      canJump.current = false
    }

    // Update camera position
    const pos = rigidBodyRef.current.translation()
    camera.position.set(pos.x, pos.y + 1.5, pos.z)
  })

  return (
    <RigidBody
      ref={rigidBodyRef}
      position={[0, 5, 0]}
      enabledRotations={[false, false, false]}
      colliders={false}
      onCollisionEnter={(e) => {
        // Reset jump when landing
        if (e.other.rigidBodyObject?.name === 'ground') {
          canJump.current = true
        }
      }}
    >
      <CapsuleCollider args={[0.5, 0.5]} />
    </RigidBody>
  )
}
```

## Physics Objects

```jsx
import { useState } from 'react'

// Collectible
function Coin({ position, id }) {
  const addScore = useGame((s) => s.addScore)
  const [collected, setCollected] = useState(false)
  const meshRef = useRef()

  useFrame((state) => {
    if (meshRef.current && !collected) {
      meshRef.current.rotation.y += 0.05
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 3) * 0.1
    }
  })

  if (collected) return null

  return (
    <RigidBody
      type="fixed"
      colliders="ball"
      sensor
      onIntersectionEnter={() => {
        setCollected(true)
        addScore(100)
        // Play sound
      }}
    >
      <mesh ref={meshRef} position={position}>
        <cylinderGeometry args={[0.3, 0.3, 0.1, 32]} />
        <meshStandardMaterial color="gold" metalness={0.8} roughness={0.2} />
      </mesh>
    </RigidBody>
  )
}

// Obstacle
function MovingPlatform({ start, end, speed = 2 }) {
  const rigidBodyRef = useRef()
  const progress = useRef(0)

  useFrame((state, delta) => {
    progress.current += delta * speed
    const t = (Math.sin(progress.current) + 1) / 2

    const x = THREE.MathUtils.lerp(start[0], end[0], t)
    const y = THREE.MathUtils.lerp(start[1], end[1], t)
    const z = THREE.MathUtils.lerp(start[2], end[2], t)

    rigidBodyRef.current?.setNextKinematicTranslation({ x, y, z })
  })

  return (
    <RigidBody ref={rigidBodyRef} type="kinematicPosition">
      <mesh castShadow receiveShadow>
        <boxGeometry args={[4, 0.5, 4]} />
        <meshStandardMaterial color="#666" />
      </mesh>
    </RigidBody>
  )
}

// Hazard
function Spike({ position }) {
  const loseLife = useGame((s) => s.loseLife)

  return (
    <RigidBody type="fixed" colliders="hull" sensor>
      <mesh position={position}>
        <coneGeometry args={[0.3, 0.8, 4]} />
        <meshStandardMaterial color="red" />
      </mesh>
      <CuboidCollider
        args={[0.3, 0.4, 0.3]}
        sensor
        onIntersectionEnter={() => loseLife()}
      />
    </RigidBody>
  )
}
```

## Level Design

```jsx
function Level() {
  return (
    <group>
      {/* Ground */}
      <RigidBody type="fixed" name="ground">
        <mesh receiveShadow position={[0, -0.5, 0]}>
          <boxGeometry args={[50, 1, 50]} />
          <meshStandardMaterial color="#8B4513" />
        </mesh>
      </RigidBody>

      {/* Platforms */}
      <Platform position={[5, 2, 0]} size={[3, 0.5, 3]} />
      <Platform position={[10, 4, 0]} size={[3, 0.5, 3]} />
      <MovingPlatform start={[15, 4, 0]} end={[15, 8, 0]} />

      {/* Collectibles */}
      <Coin position={[5, 3, 0]} />
      <Coin position={[10, 5, 0]} />
      <Coin position={[15, 9, 0]} />

      {/* Hazards */}
      <Spike position={[7, 0.4, 0]} />
      <Spike position={[12, 0.4, 0]} />

      {/* Goal */}
      <Goal position={[20, 6, 0]} />
    </group>
  )
}

function Platform({ position, size }) {
  return (
    <RigidBody type="fixed" name="ground">
      <mesh castShadow receiveShadow position={position}>
        <boxGeometry args={size} />
        <meshStandardMaterial color="#666" />
      </mesh>
    </RigidBody>
  )
}
```

## Audio

```jsx
import { Howl } from 'howler'
import { useEffect, useRef } from 'react'

// Sound manager
const sounds = {
  jump: new Howl({ src: ['/sounds/jump.mp3'], volume: 0.5 }),
  coin: new Howl({ src: ['/sounds/coin.mp3'], volume: 0.7 }),
  hurt: new Howl({ src: ['/sounds/hurt.mp3'], volume: 0.6 }),
  music: new Howl({ src: ['/sounds/music.mp3'], loop: true, volume: 0.3 })
}

// Play sounds in response to game events
function useSoundEffects() {
  const prevScore = useRef(0)
  const prevLives = useRef(3)

  const { score, lives, phase } = useGame()

  useEffect(() => {
    if (score > prevScore.current) {
      sounds.coin.play()
    }
    prevScore.current = score
  }, [score])

  useEffect(() => {
    if (lives < prevLives.current) {
      sounds.hurt.play()
    }
    prevLives.current = lives
  }, [lives])

  useEffect(() => {
    if (phase === 'playing') {
      sounds.music.play()
    } else {
      sounds.music.pause()
    }
  }, [phase])
}
```

## Performance Tips

1. **Physics bodies**: Minimize active rigid bodies (<200)
2. **Instancing**: Use for repeated objects (coins, obstacles)
3. **LOD**: Simple geometries for distant objects
4. **Shadow maps**: Limit shadow-casting lights to 1-2
5. **Collision shapes**: Use simple colliders (box, sphere) over mesh

## Checklist

- [ ] Game starts on click/key press
- [ ] Player moves smoothly with WASD/arrows
- [ ] Jumping feels responsive
- [ ] Collectibles register and update score
- [ ] Hazards damage player correctly
- [ ] Lives and score display in UI
- [ ] Game over triggers correctly
- [ ] Restart resets all state
- [ ] Audio plays for key events
- [ ] Performance stays above 30 FPS
