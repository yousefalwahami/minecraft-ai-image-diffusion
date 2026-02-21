import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { MutableRefObject } from 'react';

// ── Scene initialisation ──────────────────────────────────────────────────────
// Call once with the mount <div>. Returns a cleanup function to call on unmount.
export function initScene(
  container: HTMLDivElement,
  sceneRef: MutableRefObject<THREE.Scene | null>,
  controlsRef?: MutableRefObject<OrbitControls | null>
): () => void {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0f172a);
  sceneRef.current = scene;

  const camera = new THREE.PerspectiveCamera(
    75,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
  );
  camera.position.set(10, 10, 10);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  if (controlsRef) controlsRef.current = controls;

  // Lights — strong ambient keeps all faces bright; two opposing dim
  // directional lights add just enough depth cue without dark sides.
  scene.add(new THREE.AmbientLight(0xffffff, 1.0));
  const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.15);
  dirLight1.position.set(5, 10, 7.5);
  scene.add(dirLight1);
  const dirLight2 = new THREE.DirectionalLight(0xffffff, 0.15);
  dirLight2.position.set(-5, -10, -7.5);
  scene.add(dirLight2);

  // Render loop
  let animId: number;
  const animate = () => {
    animId = requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  };
  animate();

  // Resize handler
  const onResize = () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  };
  window.addEventListener('resize', onResize);

  // Cleanup
  return () => {
    cancelAnimationFrame(animId);
    window.removeEventListener('resize', onResize);
    controls.dispose();
    renderer.dispose();
    if (container.contains(renderer.domElement)) {
      container.removeChild(renderer.domElement);
    }
    sceneRef.current = null;
    if (controlsRef) controlsRef.current = null;
  };
}

// ── renderVoxels ──────────────────────────────────────────────────────────────
// Call this whenever you receive voxel data from /generate.
// Renders a vibrant InstancedMesh + a merged LineSegments edge overlay.
export function renderVoxels(
  voxelData: { x: number; y: number; z: number }[],
  scene: THREE.Scene,
  meshRef: MutableRefObject<THREE.InstancedMesh | null>,
  controlsRef?: MutableRefObject<OrbitControls | null>,
  edgesRef?: MutableRefObject<THREE.LineSegments | null>
): void {
  // Remove & dispose previous meshes
  if (meshRef.current) {
    scene.remove(meshRef.current);
    meshRef.current.geometry.dispose();
    (meshRef.current.material as THREE.Material).dispose();
    meshRef.current = null;
  }
  if (edgesRef?.current) {
    scene.remove(edgesRef.current);
    edgesRef.current.geometry.dispose();
    (edgesRef.current.material as THREE.Material).dispose();
    edgesRef.current = null;
  }

  if (voxelData.length === 0) return;

  // Compute centroid so we can centre the model at world origin
  const cx = voxelData.reduce((s, p) => s + p.x, 0) / voxelData.length;
  const cy = voxelData.reduce((s, p) => s + p.y, 0) / voxelData.length;
  const cz = voxelData.reduce((s, p) => s + p.z, 0) / voxelData.length;

  // ── Face mesh ──────────────────────────────────────────────────────────────
  const boxGeo = new THREE.BoxGeometry(1, 1, 1);
  // polygonOffset pushes faces back slightly so edge lines render on top cleanly
  const material = new THREE.MeshLambertMaterial({
    color: 0x4ade80,           // bright vibrant green
    polygonOffset: true,
    polygonOffsetFactor: 1,
    polygonOffsetUnits: 1,
  });
  const mesh = new THREE.InstancedMesh(boxGeo, material, voxelData.length);

  const dummy = new THREE.Object3D();
  voxelData.forEach((pos, i) => {
    dummy.position.set(pos.x - cx, pos.y - cy, pos.z - cz);
    dummy.updateMatrix();
    mesh.setMatrixAt(i, dummy.matrix);
  });
  scene.add(mesh);
  meshRef.current = mesh;

  // ── Edge overlay ───────────────────────────────────────────────────────────
  // Build one merged LineSegments geometry (single draw call) from all voxels.
  // EdgesGeometry gives 12 clean cube edges (24 vertices) with no face diagonals.
  const edgesTemplate = new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1));
  const templatePos = edgesTemplate.attributes.position.array as Float32Array;
  const vertsPerCube = templatePos.length; // 72 floats (24 verts × 3)

  const allEdgePos = new Float32Array(voxelData.length * vertsPerCube);
  voxelData.forEach((pos, i) => {
    const ox = pos.x - cx;
    const oy = pos.y - cy;
    const oz = pos.z - cz;
    for (let j = 0; j < vertsPerCube; j += 3) {
      allEdgePos[i * vertsPerCube + j]     = templatePos[j]     + ox;
      allEdgePos[i * vertsPerCube + j + 1] = templatePos[j + 1] + oy;
      allEdgePos[i * vertsPerCube + j + 2] = templatePos[j + 2] + oz;
    }
  });
  edgesTemplate.dispose();

  const edgesGeo = new THREE.BufferGeometry();
  edgesGeo.setAttribute('position', new THREE.BufferAttribute(allEdgePos, 3));
  const edgeLines = new THREE.LineSegments(
    edgesGeo,
    new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 1 })
  );
  scene.add(edgeLines);
  if (edgesRef) edgesRef.current = edgeLines;

  // Keep OrbitControls pivot at the model centre
  if (controlsRef?.current) {
    controlsRef.current.target.set(0, 0, 0);
    controlsRef.current.update();
  }
}
