// 3D Size Model JavaScript
class SizeModel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.human = null;
        this.controls = null;

        this.init();
        this.createHuman();
        this.setupEventListeners();
        this.animate();
    }

    init() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf5f5f5);

        this.camera = new THREE.PerspectiveCamera(50, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
        this.camera.position.set(0, 0.5, 3.5);
        this.camera.lookAt(0, 0, 0);

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);

        this.container.style.cursor = 'grab';

        this.setupLighting();
        this.createGround();
        this.setupInteraction();

        window.addEventListener('resize', () => this.onWindowResize());
    }

    setupLighting() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
        this.scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
        dirLight.position.set(3, 5, 4);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 20;
        dirLight.shadow.camera.left = -3;
        dirLight.shadow.camera.right = 3;
        dirLight.shadow.camera.top = 3;
        dirLight.shadow.camera.bottom = -3;
        this.scene.add(dirLight);

        const fillLight = new THREE.DirectionalLight(0xaaccff, 0.3);
        fillLight.position.set(-3, 3, -2);
        this.scene.add(fillLight);

        const rimLight = new THREE.DirectionalLight(0xffffff, 0.4);
        rimLight.position.set(0, 2, -5);
        this.scene.add(rimLight);
    }

    createGround() {
        const groundGeometry = new THREE.CircleGeometry(2, 32);
        const groundMaterial = new THREE.MeshLambertMaterial({ color: 0xe8e8e8 });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -0.75;
        ground.receiveShadow = true;
        this.scene.add(ground);
    }

    setupInteraction() {
        this.controls = {
            isDragging: false,
            previousMouseX: 0,
            previousMouseY: 0,
            rotationY: 0,
            rotationX: 0.1,
            zoom: 3.5,
            autoRotate: true,
            autoRotateSpeed: 0.003,
            lastInteraction: 0
        };

        const container = this.container;
        const canvas = this.renderer.domElement;

        const startDrag = (x, y) => {
            this.controls.isDragging = true;
            this.controls.previousMouseX = x;
            this.controls.previousMouseY = y;
            this.controls.lastInteraction = Date.now();
            container.style.cursor = 'grabbing';
        };

        const moveDrag = (x, y) => {
            if (!this.controls.isDragging) return;
            const deltaX = x - this.controls.previousMouseX;
            const deltaY = y - this.controls.previousMouseY;
            this.controls.rotationY += deltaX * 0.008;
            this.controls.rotationX += deltaY * 0.005;
            this.controls.rotationX = Math.max(-0.5, Math.min(0.8, this.controls.rotationX));
            this.controls.previousMouseX = x;
            this.controls.previousMouseY = y;
            this.controls.lastInteraction = Date.now();
        };

        const endDrag = () => {
            this.controls.isDragging = false;
            this.controls.lastInteraction = Date.now();
            container.style.cursor = 'grab';
        };

        canvas.addEventListener('mousedown', (e) => {
            e.preventDefault();
            startDrag(e.clientX, e.clientY);
        });

        window.addEventListener('mousemove', (e) => {
            moveDrag(e.clientX, e.clientY);
        });

        window.addEventListener('mouseup', endDrag);

        canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.controls.zoom += e.deltaY * 0.003;
            this.controls.zoom = Math.max(1.5, Math.min(7, this.controls.zoom));
            this.controls.lastInteraction = Date.now();
        }, { passive: false });

        canvas.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                e.preventDefault();
                startDrag(e.touches[0].clientX, e.touches[0].clientY);
            }
        }, { passive: false });

        canvas.addEventListener('touchmove', (e) => {
            if (e.touches.length === 1) {
                e.preventDefault();
                moveDrag(e.touches[0].clientX, e.touches[0].clientY);
            }
        }, { passive: false });

        canvas.addEventListener('touchend', endDrag);
    }

    createHuman() {
        this.human = new THREE.Group();
        this.materials = {};

        const skinMaterial = new THREE.MeshLambertMaterial({ color: 0xF5DEB3 });
        const torsoMaterial = new THREE.MeshLambertMaterial({ color: 0x4169E1 });
        const legsMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });

        this.materials = { skin: skinMaterial, torso: torsoMaterial, legs: legsMaterial };

        const headGeometry = new THREE.SphereGeometry(0.1, 16, 16);
        this.head = new THREE.Mesh(headGeometry, skinMaterial);
        this.head.position.y = 0.15;
        this.head.castShadow = true;
        this.human.add(this.head);

        const neckGeometry = new THREE.CylinderGeometry(0.04, 0.045, 0.06, 8);
        this.neck = new THREE.Mesh(neckGeometry, skinMaterial);
        this.neck.position.y = 0.04;
        this.neck.castShadow = true;
        this.human.add(this.neck);

        const torsoGeometry = new THREE.CylinderGeometry(0.1, 0.08, 0.35, 8);
        this.torso = new THREE.Mesh(torsoGeometry, torsoMaterial);
        this.torso.position.y = -0.15;
        this.torso.castShadow = true;
        this.human.add(this.torso);

        const shoulderGeometry = new THREE.SphereGeometry(0.03, 8, 8);
        this.leftShoulder = new THREE.Mesh(shoulderGeometry, torsoMaterial);
        this.leftShoulder.position.set(-0.12, -0.02, 0);
        this.leftShoulder.castShadow = true;
        this.human.add(this.leftShoulder);

        this.rightShoulder = new THREE.Mesh(shoulderGeometry, torsoMaterial);
        this.rightShoulder.position.set(0.12, -0.02, 0);
        this.rightShoulder.castShadow = true;
        this.human.add(this.rightShoulder);

        const upperArmGeometry = new THREE.CylinderGeometry(0.025, 0.022, 0.2, 8);
        this.leftUpperArm = new THREE.Mesh(upperArmGeometry, skinMaterial);
        this.leftUpperArm.position.set(-0.15, -0.12, 0);
        this.leftUpperArm.castShadow = true;
        this.human.add(this.leftUpperArm);

        this.rightUpperArm = new THREE.Mesh(upperArmGeometry, skinMaterial);
        this.rightUpperArm.position.set(0.15, -0.12, 0);
        this.rightUpperArm.castShadow = true;
        this.human.add(this.rightUpperArm);

        const forearmGeometry = new THREE.CylinderGeometry(0.022, 0.018, 0.18, 8);
        this.leftForearm = new THREE.Mesh(forearmGeometry, skinMaterial);
        this.leftForearm.position.set(-0.15, -0.25, 0);
        this.leftForearm.castShadow = true;
        this.human.add(this.leftForearm);

        this.rightForearm = new THREE.Mesh(forearmGeometry, skinMaterial);
        this.rightForearm.position.set(0.15, -0.25, 0);
        this.rightForearm.castShadow = true;
        this.human.add(this.rightForearm);

        const hipGeometry = new THREE.CylinderGeometry(0.09, 0.085, 0.08, 8);
        this.hip = new THREE.Mesh(hipGeometry, legsMaterial);
        this.hip.position.y = -0.36;
        this.hip.castShadow = true;
        this.human.add(this.hip);

        const upperLegGeometry = new THREE.CylinderGeometry(0.04, 0.035, 0.25, 8);
        this.leftUpperLeg = new THREE.Mesh(upperLegGeometry, legsMaterial);
        this.leftUpperLeg.position.set(-0.05, -0.5, 0);
        this.leftUpperLeg.castShadow = true;
        this.human.add(this.leftUpperLeg);

        this.rightUpperLeg = new THREE.Mesh(upperLegGeometry, legsMaterial);
        this.rightUpperLeg.position.set(0.05, -0.5, 0);
        this.rightUpperLeg.castShadow = true;
        this.human.add(this.rightUpperLeg);

        const lowerLegGeometry = new THREE.CylinderGeometry(0.03, 0.025, 0.25, 8);
        this.leftLowerLeg = new THREE.Mesh(lowerLegGeometry, legsMaterial);
        this.leftLowerLeg.position.set(-0.05, -0.65, 0);
        this.leftLowerLeg.castShadow = true;
        this.human.add(this.leftLowerLeg);

        this.rightLowerLeg = new THREE.Mesh(lowerLegGeometry, legsMaterial);
        this.rightLowerLeg.position.set(0.05, -0.65, 0);
        this.rightLowerLeg.castShadow = true;
        this.human.add(this.rightLowerLeg);

        const footGeometry = new THREE.BoxGeometry(0.05, 0.03, 0.1);
        this.leftFoot = new THREE.Mesh(footGeometry, legsMaterial);
        this.leftFoot.position.set(-0.05, -0.79, 0.02);
        this.leftFoot.castShadow = true;
        this.human.add(this.leftFoot);

        this.rightFoot = new THREE.Mesh(footGeometry, legsMaterial);
        this.rightFoot.position.set(0.05, -0.79, 0.02);
        this.rightFoot.castShadow = true;
        this.human.add(this.rightFoot);

        this.scene.add(this.human);

        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    }

    updateHumanSize(params) {
        if (!this.human) return;

        const heightScale = params.height / 175;
        const chestScale = params.chest / 90;
        const waistScale = params.waist / 75;
        const hipsScale = params.hips / 95;
        const shoulderScale = params.shoulders / 42;

        this.head.scale.setScalar(chestScale * 0.5 + 0.5);
        this.neck.scale.set(chestScale * 0.5 + 0.5, heightScale, chestScale * 0.5 + 0.5);

        this.torso.scale.set(chestScale, heightScale * 0.5 + waistScale * 0.5, chestScale * 0.8 + waistScale * 0.2);

        this.leftShoulder.position.x = -0.12 * shoulderScale;
        this.rightShoulder.position.x = 0.12 * shoulderScale;
        this.leftShoulder.scale.setScalar(shoulderScale);
        this.rightShoulder.scale.setScalar(shoulderScale);

        this.leftUpperArm.position.x = -0.15 * shoulderScale;
        this.rightUpperArm.position.x = 0.15 * shoulderScale;
        this.leftForearm.position.x = -0.15 * shoulderScale;
        this.rightForearm.position.x = 0.15 * shoulderScale;

        this.hip.scale.set(hipsScale, 1, hipsScale);

        this.leftUpperLeg.position.x = -0.05 * hipsScale;
        this.rightUpperLeg.position.x = 0.05 * hipsScale;
        this.leftLowerLeg.position.x = -0.05 * hipsScale;
        this.rightLowerLeg.position.x = 0.05 * hipsScale;
        this.leftFoot.position.x = -0.05 * hipsScale;
        this.rightFoot.position.x = 0.05 * hipsScale;

        this.human.scale.setScalar(heightScale);
        this.human.position.y = -(1 - heightScale) * 0.75;
    }

    setupEventListeners() {
        const fields = ['height', 'weight', 'chest', 'waist', 'hips', 'shoulders'];

        fields.forEach(id => {
            const rangeInput = document.getElementById(id);
            const valueDisplay = document.getElementById(id + 'Value');

            const syncInputs = (value) => {
                value = Number(value);
                const min = Number(rangeInput.min);
                const max = Number(rangeInput.max);
                value = Math.max(min, Math.min(max, value));
                rangeInput.value = value;
                valueDisplay.textContent = value;
                this.onParamsChanged();
            };

            rangeInput.addEventListener('input', (e) => syncInputs(e.target.value));
        });

        document.querySelectorAll('.param-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const field = btn.dataset.field;
                const dir = parseInt(btn.dataset.dir);
                const rangeInput = document.getElementById(field);
                const step = field === 'weight' ? 1 : 1;
                const newValue = Number(rangeInput.value) + dir * step;
                const min = Number(rangeInput.min);
                const max = Number(rangeInput.max);
                const clamped = Math.max(min, Math.min(max, newValue));
                rangeInput.value = clamped;
                document.getElementById(field + 'Value').textContent = clamped;
                this.onParamsChanged();
            });
        });

        document.getElementById('rotateBtn')?.addEventListener('click', () => {
            this.controls.autoRotate = !this.controls.autoRotate;
            const btn = document.getElementById('rotateBtn');
            btn.textContent = this.controls.autoRotate ? 'Остановить' : 'Вращать';
            btn.classList.toggle('active', this.controls.autoRotate);
        });

        document.getElementById('resetViewBtn')?.addEventListener('click', () => {
            this.controls.zoom = 3.5;
            this.controls.rotationY = 0;
            this.controls.rotationX = 0.1;
        });

        document.getElementById('saveSizeBtn')?.addEventListener('click', () => {
            const params = this.getCurrentParams();
            localStorage.setItem('userSizeParams', JSON.stringify(params));
            alert('Параметры сохранены!');
        });

        document.getElementById('resetSizeBtn')?.addEventListener('click', () => {
            this.resetToDefaults();
        });

        const rotateBtn = document.getElementById('rotateBtn');
        if (rotateBtn) rotateBtn.classList.add('active');

        this.loadSavedParams();
    }

    onParamsChanged() {
        const params = this.getCurrentParams();
        this.updateHumanSize(params);
        this.updateSizeOutput(params);
    }

    getCurrentParams() {
        return {
            height: Number(document.getElementById('height').value),
            weight: Number(document.getElementById('weight').value),
            chest: Number(document.getElementById('chest').value),
            waist: Number(document.getElementById('waist').value),
            hips: Number(document.getElementById('hips').value),
            shoulders: Number(document.getElementById('shoulders').value)
        };
    }

    resetToDefaults() {
        const defaults = { height: 175, weight: 70, chest: 90, waist: 75, hips: 95, shoulders: 42 };
        Object.keys(defaults).forEach(key => {
            const rangeInput = document.getElementById(key);
            const value = defaults[key];
            const unit = key === 'weight' ? 'кг' : 'см';
            rangeInput.value = value;
            document.getElementById(key + 'Value').textContent = value;
        });
        this.updateHumanSize(defaults);
        this.updateSizeOutput(defaults);
    }

    loadSavedParams() {
        const saved = localStorage.getItem('userSizeParams');
        if (saved) {
            try {
                const params = JSON.parse(saved);
                Object.keys(params).forEach(key => {
                    const value = params[key];
                    document.getElementById(key).value = value;
                    document.getElementById(key + 'Value').textContent = value;
                });
                this.updateHumanSize(params);
                this.updateSizeOutput(params);
            } catch (e) {
                console.error('Error loading saved parameters:', e);
            }
        } else {
            this.updateSizeOutput(this.getCurrentParams());
        }
    }

    computeRecommendedSize(params) {
        const { chest, waist, hips, height } = params;
        const ideal = Math.round((chest + hips + waist) / 3);

        const sizes = [
            { label: 'XS', ru: '42-44', eu: 'XS', us: 'XS', max: 86 },
            { label: 'S', ru: '44-46', eu: 'S', us: 'S', max: 94 },
            { label: 'M', ru: '46-48', eu: 'M', us: 'M', max: 102 },
            { label: 'L', ru: '48-50', eu: 'L', us: 'L', max: 110 },
            { label: 'XL', ru: '50-52', eu: 'XL', us: 'XL', max: 118 },
            { label: 'XXL', ru: '52-54', eu: 'XXL', us: 'XXL', max: 999 }
        ];

        let result = sizes[sizes.length - 1];
        for (const size of sizes) {
            if (ideal <= size.max) { result = size; break; }
        }

        if (height < 160 && result.label === 'XL') { result = sizes[3]; }
        return result;
    }

    updateSizeOutput(params) {
        const sizeInfo = this.computeRecommendedSize(params);
        const sizeElement = document.getElementById('recommendedSize');
        const detailsElement = document.getElementById('sizeDetails');
        if (sizeElement) sizeElement.textContent = sizeInfo.label;
        if (detailsElement) detailsElement.textContent = `RU ${sizeInfo.ru}, EU ${sizeInfo.eu}, US ${sizeInfo.us}`;
    }

    onWindowResize() {
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const now = Date.now();
        if (this.controls.autoRotate && !this.controls.isDragging && now - this.controls.lastInteraction > 3000) {
            this.controls.rotationY += this.controls.autoRotateSpeed;
        }

        this.camera.position.x = Math.sin(this.controls.rotationY) * this.controls.zoom;
        this.camera.position.z = Math.cos(this.controls.rotationY) * this.controls.zoom;
        this.camera.position.y = this.controls.rotationX * 2;
        this.camera.lookAt(0, -0.1, 0);

        this.renderer.render(this.scene, this.camera);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('modelContainer')) {
        new SizeModel('modelContainer');
    }
});
