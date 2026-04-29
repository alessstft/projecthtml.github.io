/**
 * 3D Mannequin Viewer - виртуальная примерка одежды
 * @version 2.0.0
 */
class MannequinViewer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Container not found:', containerId);
            return;
        }

        this.options = {
            width: options.width || 400,
            height: options.height || 500,
            backgroundColor: options.backgroundColor || 0x1a1a1a,
            enableRotate: options.enableRotate !== false,
            enableZoom: options.enableZoom !== false,
            ...options
        };

        this.measurements = {
            height: 170,
            chest: 92,
            waist: 76,
            hips: 98,
            shoulders: 116,
            armLength: 58,
            legLength: 80
        };

        this.meshes = [];
        this.init();
    }

    init() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.options.backgroundColor);

        // Camera
        this.camera = new THREE.PerspectiveCamera(45, this.options.width / this.options.height, 0.1, 1000);
        this.camera.position.set(0, 0.5, 2.5);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.options.width, this.options.height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);

        this._setupLights();
        this._setupControls();
        this.createMannequin();
        this._animate();
        window.addEventListener('resize', () => this._onResize());
    }

    _setupLights() {
        const ambient = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambient);

        const keyLight = new THREE.DirectionalLight(0xffffff, 0.8);
        keyLight.position.set(2, 4, 4);
        this.scene.add(keyLight);

        const fillLight = new THREE.DirectionalLight(0xffeedd, 0.3);
        fillLight.position.set(-3, 2, 2);
        this.scene.add(fillLight);
    }

    _setupControls() {
        if (this.options.enableRotate || this.options.enableZoom) {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            if (!this.options.enableRotate) this.controls.enableRotate = false;
            if (!this.options.enableZoom) this.controls.enableZoom = false;
            this.controls.enablePan = false;
            this.controls.target.set(0, 0.3, 0);
        }
    }

    createMannequin() {
        // Clear
        this.meshes.forEach(mesh => {
            this.scene.remove(mesh);
        });
        this.meshes = [];

        const material = new THREE.MeshStandardMaterial({
            color: 0xe8beac,
            roughness: 0.6,
            metalness: 0.05
        });

        const m = this.measurements;
        const scale = 0.01;
        const h = m.height * scale;
        const chest = (m.chest / 100) * 0.18;
        const waist = (m.waist / 100) * 0.15;
        const hips = (m.hips / 100) * 0.19;
        const shoulders = (m.shoulders / 100) * 0.22;

        // Head
        const headGeo = new THREE.SphereGeometry(h * 0.085, 32, 24);
        const head = new THREE.Mesh(headGeo, material);
        head.scale.set(0.85, 1, 0.9);
        head.position.y = h * 0.4;
        this.scene.add(head);
        this.meshes.push(head);

        // Neck
        const neckGeo = new THREE.CylinderGeometry(h * 0.035, h * 0.045, h * 0.08, 16);
        const neck = new THREE.Mesh(neckGeo, material);
        neck.position.y = h * 0.32;
        this.scene.add(neck);
        this.meshes.push(neck);

        // Torso
        const torsoGroup = new THREE.Group();

        // Upper torso
        const upperGeo = new THREE.SphereGeometry(chest, 24, 16);
        const upper = new THREE.Mesh(upperGeo, material);
        upper.scale.set(1, 0.7, 0.65);
        upper.position.y = h * 0.22;
        torsoGroup.add(upper);

        // Waist
        const waistGeo = new THREE.SphereGeometry(waist, 20, 12);
        const waistPart = new THREE.Mesh(waistGeo, material);
        waistPart.scale.set(1, 0.6, 0.75);
        waistPart.position.y = h * 0.1;
        torsoGroup.add(waistPart);

        // Hips
        const hipsGeo = new THREE.SphereGeometry(hips * 0.95, 20, 12);
        const hipsPart = new THREE.Mesh(hipsGeo, material);
        hipsPart.scale.set(1, 0.5, 0.7);
        hipsPart.position.y = h * -0.05;
        torsoGroup.add(hipsPart);

        this.scene.add(torsoGroup);
        this.meshes.push(torsoGroup);

        // Arms
        [-1, 1].forEach(side => {
            const armGroup = new THREE.Group();

            const upperArmGeo = new THREE.CapsuleGeometry(chest * 0.12, h * 0.15, 12, 16);
            const upperArm = new THREE.Mesh(upperArmGeo, material);
            upperArm.position.set(side * shoulders * 0.9, h * 0.22, 0);
            upperArm.rotation.z = side * 0.2;
            armGroup.add(upperArm);

            const forearmGeo = new THREE.CapsuleGeometry(chest * 0.09, h * 0.14, 12, 16);
            const forearm = new THREE.Mesh(forearmGeo, material);
            forearm.position.set(side * shoulders * 1.0, h * 0.02, 0);
            forearm.rotation.z = side * 0.1;
            armGroup.add(forearm);

            const handGeo = new THREE.SphereGeometry(chest * 0.08, 16, 16);
            const hand = new THREE.Mesh(handGeo, material);
            hand.position.set(side * shoulders * 1.05, h * -0.15, 0);
            hand.scale.set(0.6, 0.8, 0.4);
            armGroup.add(hand);

            this.scene.add(armGroup);
            this.meshes.push(armGroup);
        });

        // Legs
        [-1, 1].forEach(side => {
            const legGroup = new THREE.Group();

            const thighGeo = new THREE.CapsuleGeometry(hips * 0.15, h * 0.25, 12, 16);
            const thigh = new THREE.Mesh(thighGeo, material);
            thigh.position.set(side * hips * 0.4, h * -0.2, 0);
            legGroup.add(thigh);

            const calfGeo = new THREE.CapsuleGeometry(hips * 0.1, h * 0.25, 12, 16);
            const calf = new THREE.Mesh(calfGeo, material);
            calf.position.set(side * hips * 0.4, h * -0.48, 0);
            legGroup.add(calf);

            const footGeo = new THREE.BoxGeometry(hips * 0.12, h * 0.03, h * 0.1);
            const foot = new THREE.Mesh(footGeo, material);
            foot.position.set(side * hips * 0.4, h * -0.7, h * 0.03);
            legGroup.add(foot);

            this.scene.add(legGroup);
            this.meshes.push(legGroup);
        });

        // Center
        this.scene.position.y = -h * 0.35;
    }

    updateMeasurements(measurements) {
        this.measurements = { ...this.measurements, ...measurements };
        this.createMannequin();
    }

    _animate() {
        requestAnimationFrame(() => this._animate());
        if (this.controls) this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    _onResize() {
        const width = this.container.clientWidth || this.options.width;
        const height = this.container.clientHeight || this.options.height;
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    dispose() {
        this.meshes.forEach(mesh => {
            if (mesh.geometry) mesh.geometry.dispose();
            if (mesh.material) mesh.material.dispose();
        });
        if (this.renderer) this.renderer.dispose();
    }
}

window.MannequinViewer = MannequinViewer;
