// 3D Mannequin Viewer
var MannequinViewer = function(containerId, options) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
        console.error("Container not found: " + containerId);
        return;
    }

    options = options || {};
    this.options = {
        width: options.width || 400,
        height: options.height || 500,
        backgroundColor: options.backgroundColor || 0x1a1a1a
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
};

MannequinViewer.prototype.init = function() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(this.options.backgroundColor);

    this.camera = new THREE.PerspectiveCamera(45, this.options.width / this.options.height, 0.1, 1000);
    this.camera.position.set(0, 0, 3);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(this.options.width, this.options.height);
    this.container.appendChild(this.renderer.domElement);

    this._setupLights();
    this._setupControls();
    this.createMannequin();
    this._animate();
};

MannequinViewer.prototype._setupLights = function() {
    var ambient = new THREE.AmbientLight(0xffffff, 0.5);
    this.scene.add(ambient);

    var keyLight = new THREE.DirectionalLight(0xffffff, 1);
    keyLight.position.set(5, 5, 5);
    this.scene.add(keyLight);

    var fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-5, 0, 5);
    this.scene.add(fillLight);
};

MannequinViewer.prototype._setupControls = function() {
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.target.set(0, 0, 0);
};

MannequinViewer.prototype.createMannequin = function() {
    var i;

    for (i = 0; i < this.meshes.length; i++) {
        this.scene.remove(this.meshes[i]);
    }
    this.meshes = [];

    var material = new THREE.MeshStandardMaterial({
        color: 0xd4a574,
        roughness: 0.7,
        metalness: 0.1
    });

    var shadowMaterial = new THREE.ShadowMaterial({ opacity: 0.3 });

    var scale = 0.01;
    var m = this.measurements;
    var heightScale = m.height * scale;
    var chestScale = (m.chest / 92) * 0.18;
    var waistScale = (m.waist / 76) * 0.15;
    var hipsScale = (m.hips / 98) * 0.18;
    var shoulderScale = (m.shoulders / 116) * 0.22;

    // Torso
    var torsoGeometry = this._createTorsoGeometry(chestScale, waistScale, hipsScale, heightScale);
    var torso = new THREE.Mesh(torsoGeometry, material);
    torso.position.y = heightScale * 0.4;
    this.scene.add(torso);
    this.meshes.push(torso);

    // Head
    var headGeometry = new THREE.SphereGeometry(heightScale * 0.09, 32, 32);
    var head = new THREE.Mesh(headGeometry, material);
    head.position.y = heightScale * 0.88;
    head.scale.set(0.8, 1, 0.85);
    this.scene.add(head);
    this.meshes.push(head);

    // Neck
    var neckGeometry = new THREE.CylinderGeometry(heightScale * 0.04, heightScale * 0.05, heightScale * 0.06, 16);
    var neck = new THREE.Mesh(neckGeometry, material);
    neck.position.y = heightScale * 0.79;
    this.scene.add(neck);
    this.meshes.push(neck);

    // Arms
    var armLength = m.armLength * scale;
    var upperArmGeo = new THREE.CylinderGeometry(chestScale * 0.12, chestScale * 0.1, armLength * 0.35, 16);
    var lowerArmGeo = new THREE.CylinderGeometry(chestScale * 0.1, chestScale * 0.08, armLength * 0.3, 16);
    var handGeo = new THREE.SphereGeometry(chestScale * 0.08, 16, 16);

    // Left arm
    var leftUpperArm = new THREE.Mesh(upperArmGeo, material);
    leftUpperArm.position.set(-shoulderScale * 0.9, heightScale * 0.72, 0);
    leftUpperArm.rotation.z = 0.15;
    this.scene.add(leftUpperArm);
    this.meshes.push(leftUpperArm);

    var leftLowerArm = new THREE.Mesh(lowerArmGeo, material);
    leftLowerArm.position.set(-shoulderScale * 1.1, heightScale * 0.52, 0);
    leftLowerArm.rotation.z = 0.1;
    this.scene.add(leftLowerArm);
    this.meshes.push(leftLowerArm);

    var leftHand = new THREE.Mesh(handGeo, material);
    leftHand.position.set(-shoulderScale * 1.2, heightScale * 0.35, 0);
    leftHand.scale.set(0.6, 0.8, 0.4);
    this.scene.add(leftHand);
    this.meshes.push(leftHand);

    // Right arm
    var rightUpperArm = new THREE.Mesh(upperArmGeo, material);
    rightUpperArm.position.set(shoulderScale * 0.9, heightScale * 0.72, 0);
    rightUpperArm.rotation.z = -0.15;
    this.scene.add(rightUpperArm);
    this.meshes.push(rightUpperArm);

    var rightLowerArm = new THREE.Mesh(lowerArmGeo, material);
    rightLowerArm.position.set(shoulderScale * 1.1, heightScale * 0.52, 0);
    rightLowerArm.rotation.z = -0.1;
    this.scene.add(rightLowerArm);
    this.meshes.push(rightLowerArm);

    var rightHand = new THREE.Mesh(handGeo, material);
    rightHand.position.set(shoulderScale * 1.2, heightScale * 0.35, 0);
    rightHand.scale.set(0.6, 0.8, 0.4);
    this.scene.add(rightHand);
    this.meshes.push(rightHand);

    // Legs
    var legLength = m.legLength * scale;
    var upperLegGeo = new THREE.CylinderGeometry(hipsScale * 0.18, hipsScale * 0.14, legLength * 0.5, 16);
    var lowerLegGeo = new THREE.CylinderGeometry(hipsScale * 0.1, hipsScale * 0.08, legLength * 0.45, 16);
    var footGeo = new THREE.BoxGeometry(hipsScale * 0.12, heightScale * 0.04, heightScale * 0.1);

    // Left leg
    var leftUpperLeg = new THREE.Mesh(upperLegGeo, material);
    leftUpperLeg.position.set(-hipsScale * 0.25, heightScale * 0.22, 0);
    this.scene.add(leftUpperLeg);
    this.meshes.push(leftUpperLeg);

    var leftLowerLeg = new THREE.Mesh(lowerLegGeo, material);
    leftLowerLeg.position.set(-hipsScale * 0.25, heightScale * -0.05, 0);
    this.scene.add(leftLowerLeg);
    this.meshes.push(leftLowerLeg);

    var leftFoot = new THREE.Mesh(footGeo, material);
    leftFoot.position.set(-hipsScale * 0.25, heightScale * -0.23, heightScale * 0.03);
    this.scene.add(leftFoot);
    this.meshes.push(leftFoot);

    // Right leg
    var rightUpperLeg = new THREE.Mesh(upperLegGeo, material);
    rightUpperLeg.position.set(hipsScale * 0.25, heightScale * 0.22, 0);
    this.scene.add(rightUpperLeg);
    this.meshes.push(rightUpperLeg);

    var rightLowerLeg = new THREE.Mesh(lowerLegGeo, material);
    rightLowerLeg.position.set(hipsScale * 0.25, heightScale * -0.05, 0);
    this.scene.add(rightLowerLeg);
    this.meshes.push(rightLowerLeg);

    var rightFoot = new THREE.Mesh(footGeo, material);
    rightFoot.position.set(hipsScale * 0.25, heightScale * -0.23, heightScale * 0.03);
    this.scene.add(rightFoot);
    this.meshes.push(rightFoot);

    // Ground
    var groundGeo = new THREE.PlaneGeometry(2, 2);
    var ground = new THREE.Mesh(groundGeo, shadowMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -heightScale * 0.25;
    this.scene.add(ground);
    this.meshes.push(ground);

    this.scene.position.y = -heightScale * 0.1;
};

MannequinViewer.prototype._createTorsoGeometry = function(chestScale, waistScale, hipsScale, heightScale) {
    var points = [];

    points.push(new THREE.Vector2(hipsScale, 0));
    points.push(new THREE.Vector2(hipsScale * 0.9, heightScale * 0.05));
    points.push(new THREE.Vector2(waistScale, heightScale * 0.15));
    points.push(new THREE.Vector2(waistScale * 1.05, heightScale * 0.22));
    points.push(new THREE.Vector2(chestScale, heightScale * 0.35));
    points.push(new THREE.Vector2(chestScale * 1.1, heightScale * 0.45));
    points.push(new THREE.Vector2(chestScale * 1.15, heightScale * 0.5));
    points.push(new THREE.Vector2(chestScale * 1.2, heightScale * 0.55));
    points.push(new THREE.Vector2(chestScale * 1.15, heightScale * 0.58));
    points.push(new THREE.Vector2(chestScale * 0.5, heightScale * 0.6));

    var shape = new THREE.Shape();
    shape.moveTo(points[0].x, points[0].y);

    for (var i = 1; i < points.length; i++) {
        shape.lineTo(points[i].x, points[i].y);
    }

    for (var i = points.length - 2; i >= 0; i--) {
        shape.lineTo(-points[i].x, points[i].y);
    }

    shape.closePath();

    var extrudeSettings = {
        steps: 1,
        depth: chestScale * 0.6,
        bevelEnabled: true,
        bevelThickness: 0.02,
        bevelSize: 0.02,
        bevelSegments: 3
    };

    var geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    geometry.center();

    return geometry;
};

MannequinViewer.prototype.updateMeasurements = function(measurements) {
    if (measurements.height) this.measurements.height = measurements.height;
    if (measurements.chest) this.measurements.chest = measurements.chest;
    if (measurements.waist) this.measurements.waist = measurements.waist;
    if (measurements.hips) this.measurements.hips = measurements.hips;
    if (measurements.shoulders) this.measurements.shoulders = measurements.shoulders;
    if (measurements.armLength) this.measurements.armLength = measurements.armLength;
    if (measurements.legLength) this.measurements.legLength = measurements.legLength;
    this.createMannequin();
};

MannequinViewer.prototype.getMeasurements = function() {
    return {
        height: this.measurements.height,
        chest: this.measurements.chest,
        waist: this.measurements.waist,
        hips: this.measurements.hips,
        shoulders: this.measurements.shoulders,
        armLength: this.measurements.armLength,
        legLength: this.measurements.legLength
    };
};

MannequinViewer.prototype._animate = function() {
    var self = this;
    function loop() {
        requestAnimationFrame(loop);
        if (self.controls) {
            self.controls.update();
        }
        self.renderer.render(self.scene, self.camera);
    }
    loop();
};

window.MannequinViewer = MannequinViewer;
