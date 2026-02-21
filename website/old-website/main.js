import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// setup scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x222222);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(10, 10, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// rotatable controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// lights
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 10, 7.5);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));;

// test data
const size = 5;
const totalBlocks = size * size * size;


function renderVoxels(voxelData, scene) {
    // 1x1x1 Cube
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshStandardMaterial({ color: 0x7daa42 }); 

    const count = voxelData.length;
    const instancedMesh = new THREE.InstancedMesh(geometry, material, count);
    
    const dummy = new THREE.Object3D();

    voxelData.forEach((pos, i) => {
        // Set the dummy to the coordinates from our data
        dummy.position.set(pos.x, pos.y, pos.z);
        
        // Essential: Update the math and save it to the instance
        dummy.updateMatrix();
        instancedMesh.setMatrixAt(i, dummy.matrix);
    });

    scene.add(instancedMesh);
    return instancedMesh; // Return it so you can remove/update it later
}


// simulates what a .schem parser would return
function getTestData(size = 5) {
    const data = [];
    for (let x = 0; x < size; x++) {
        for (let y = 0; y < size; y++) {
            for (let z = 0; z < size; z++) {
                // Only "build" a simple hollow shell or a shape to test
                if (x === 0 || x === size - 1 || z === 0 || z === size - 1 || y === 0) {
                    data.push({ x, y, z });
                }
            }
        }
    }
    return data;
}
const instancedMesh = renderVoxels(getTestData(5), scene);




function animate() {
    requestAnimationFrame(animate);
    controls.update(); // Only needed if enableDamping is true
    renderer.render(scene, camera);
}

animate();


// handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});