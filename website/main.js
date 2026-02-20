import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// 1. Setup Scene, Camera, and Renderer
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x222222);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(10, 10, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Allow user to rotate/zoom
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// 2. Lights (Crucial for 3D depth)
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 10, 7.5);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));;

// 3. Simple Test Data (A 5x5x5 solid cube)
const size = 5;
const totalBlocks = size * size * size;

// Minecraft-style geometry and material
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x7daa42 }); // Grass Green

const instancedMesh = new THREE.InstancedMesh(geometry, material, totalBlocks);

// Position the blocks once
const dummy = new THREE.Object3D();
let i = 0;

for (let x = 0; x < size; x++) {
    for (let y = 0; y < size; y++) {
        for (let z = 0; z < size; z++) {
            dummy.position.set(x, y, z);
            dummy.updateMatrix();
            instancedMesh.setMatrixAt(i++, dummy.matrix);
        }
    }
}

scene.add(instancedMesh);

// 4. Standard Render Loop
function animate() {
    requestAnimationFrame(animate);
    controls.update(); // Only needed if enableDamping is true
    renderer.render(scene, camera);
}

animate();

// Handle Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});