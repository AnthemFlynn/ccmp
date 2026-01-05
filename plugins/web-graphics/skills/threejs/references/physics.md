# Physics Integration

Integrate physics engines with Three.js for realistic simulations.

## Rapier (Recommended)

Modern, WASM-based physics engine. Excellent performance and API.

```javascript
import RAPIER from '@dimforge/rapier3d-compat';

await RAPIER.init();
const gravity = { x: 0, y: -9.81, z: 0 };
const world = new RAPIER.World(gravity);

// Create rigid body
const rigidBodyDesc = RAPIER.RigidBodyDesc.dynamic()
  .setTranslation(0, 5, 0);
const rigidBody = world.createRigidBody(rigidBodyDesc);

// Create collider (attach to rigid body)
const colliderDesc = RAPIER.ColliderDesc.cuboid(0.5, 0.5, 0.5);
world.createCollider(colliderDesc, rigidBody);

// In animation loop:
world.step();
const position = rigidBody.translation();
const rotation = rigidBody.rotation();
mesh.position.set(position.x, position.y, position.z);
mesh.quaternion.set(rotation.x, rotation.y, rotation.z, rotation.w);
```

### Rapier Collider Shapes

```javascript
RAPIER.ColliderDesc.ball(radius)
RAPIER.ColliderDesc.cuboid(hx, hy, hz)  // half-extents
RAPIER.ColliderDesc.capsule(halfHeight, radius)
RAPIER.ColliderDesc.cylinder(halfHeight, radius)
RAPIER.ColliderDesc.cone(halfHeight, radius)
RAPIER.ColliderDesc.trimesh(vertices, indices)  // for complex meshes
RAPIER.ColliderDesc.convexHull(points)
```

### Rapier Body Types

```javascript
RAPIER.RigidBodyDesc.dynamic()      // affected by forces
RAPIER.RigidBodyDesc.fixed()        // static, immovable
RAPIER.RigidBodyDesc.kinematicPositionBased()  // moved programmatically
RAPIER.RigidBodyDesc.kinematicVelocityBased()
```

## Cannon.js / Cannon-es

Classic physics engine, easier setup but less performant.

```javascript
import * as CANNON from 'cannon-es';

const world = new CANNON.World();
world.gravity.set(0, -9.82, 0);

// Ground
const groundBody = new CANNON.Body({
  type: CANNON.Body.STATIC,
  shape: new CANNON.Plane(),
});
groundBody.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
world.addBody(groundBody);

// Dynamic body
const sphereBody = new CANNON.Body({
  mass: 5,
  shape: new CANNON.Sphere(1),
  position: new CANNON.Vec3(0, 10, 0),
});
world.addBody(sphereBody);

// In animation loop:
world.step(1 / 60, delta, 3);
sphereMesh.position.copy(sphereBody.position);
sphereMesh.quaternion.copy(sphereBody.quaternion);
```

### Cannon Shapes

```javascript
new CANNON.Sphere(radius)
new CANNON.Box(new CANNON.Vec3(hx, hy, hz))
new CANNON.Cylinder(radiusTop, radiusBottom, height, numSegments)
new CANNON.Plane()  // infinite plane
new CANNON.Trimesh(vertices, indices)
new CANNON.ConvexPolyhedron({ vertices, faces })
```

## Physics Synchronization Pattern

```javascript
// Map Three.js meshes to physics bodies
const physicsObjects = [];

function createPhysicsBox(size, position) {
  // Three.js mesh
  const geometry = new THREE.BoxGeometry(size.x, size.y, size.z);
  const material = new THREE.MeshStandardMaterial();
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
  
  // Physics body
  const body = world.createRigidBody(
    RAPIER.RigidBodyDesc.dynamic().setTranslation(position.x, position.y, position.z)
  );
  world.createCollider(
    RAPIER.ColliderDesc.cuboid(size.x / 2, size.y / 2, size.z / 2),
    body
  );
  
  physicsObjects.push({ mesh, body });
  return { mesh, body };
}

function updatePhysics() {
  world.step();
  
  for (const { mesh, body } of physicsObjects) {
    const pos = body.translation();
    const rot = body.rotation();
    mesh.position.set(pos.x, pos.y, pos.z);
    mesh.quaternion.set(rot.x, rot.y, rot.z, rot.w);
  }
}
```

## Constraints & Joints

### Rapier Joints
```javascript
// Fixed joint (weld)
const jointParams = RAPIER.JointData.fixed(
  { x: 0, y: 0, z: 0 },  // anchor in body1
  { w: 1, x: 0, y: 0, z: 0 },  // frame rotation body1
  { x: 0, y: 0, z: 0 },  // anchor in body2
  { w: 1, x: 0, y: 0, z: 0 }   // frame rotation body2
);
world.createImpulseJoint(jointParams, body1, body2, true);

// Revolute (hinge)
RAPIER.JointData.revolute(anchor1, anchor2, axis)

// Spherical (ball socket)
RAPIER.JointData.spherical(anchor1, anchor2)

// Prismatic (slider)
RAPIER.JointData.prismatic(anchor1, anchor2, axis)
```

## Performance Tips

1. Use simple collider shapes (spheres, boxes) when possible
2. Disable collision detection for distant objects
3. Use fixed timestep: `world.step(1/60)` not `world.step(delta)`
4. Group static objects into compound colliders
5. Set appropriate solver iterations based on precision needs
6. Use collision groups/masks to filter unnecessary collision checks
