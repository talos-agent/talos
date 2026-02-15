import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

/**
 * Arkhe Connection Graph Component.
 * Visualizes nodes and edges in a 3D space using Three.js.
 */
export function ConnectionGraph({ nodes, edges }) {
  const mountRef = useRef();

  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    mountRef.current.appendChild(renderer.domElement);

    camera.position.z = 10;

    const nodeGroup = new THREE.Group();
    scene.add(nodeGroup);

    const edgeGroup = new THREE.Group();
    scene.add(edgeGroup);

    // Draw nodes as spheres
    const nodeSpheres = [];
    nodes.forEach(node => {
      const geometry = new THREE.SphereGeometry(node.satoshi * 0.1, 32, 32);
      const material = new THREE.MeshPhongMaterial({ color: 0x0077ff, emissive: 0x000000 });
      const sphere = new THREE.Mesh(geometry, material);
      sphere.position.set(node.x, node.y, node.z || 0);
      sphere.userData = node;
      nodeGroup.add(sphere);
      nodeSpheres.push(sphere);
    });

    // Draw edges as lines
    edges.forEach(edge => {
      const points = [
        new THREE.Vector3(edge.source.x, edge.source.y, edge.source.z || 0),
        new THREE.Vector3(edge.target.x, edge.target.y, edge.target.z || 0)
      ];
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const avgC = (edge.source.C + edge.target.C) / 2;
      // Warm colors for high coherence, cool colors for low
      const color = new THREE.Color().setHSL(0.6 * (1 - avgC), 1.0, 0.5);
      const material = new THREE.LineBasicMaterial({ color: color });
      const line = new THREE.Line(geometry, material);
      edgeGroup.add(line);
    });

    const light = new THREE.PointLight(0xffffff, 1, 100);
    light.position.set(0, 0, 10);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040));

    // Interaction
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onClick = (event) => {
      if (!mountRef.current) return;

      const rect = mountRef.current.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeSpheres);

      if (intersects.length > 0) {
        const node = intersects[0].object.userData;
        console.log(`INTERACTION DETECTADA: Nó ${node.id}`);
        console.table({
            "Identidade": node.id,
            "Ω (Omega)": node.omega,
            "C (Coerência)": node.C,
            "F (Flutuação)": node.F,
            "Satoshi": node.satoshi
        });

        // Highlight logic: Gold shine
        const originalEmissive = intersects[0].object.material.emissive.getHex();
        intersects[0].object.material.emissive.setHex(0xffd700);
        setTimeout(() => {
            if (intersects[0].object) {
                intersects[0].object.material.emissive.setHex(originalEmissive);
            }
        }, 1000);
      }
    };

    window.addEventListener('click', onClick);

    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      window.removeEventListener('click', onClick);
      if (mountRef.current && renderer.domElement.parentNode === mountRef.current) {
          mountRef.current.removeChild(renderer.domElement);
      }
    };
  }, [nodes, edges]);

  return <div ref={mountRef} style={{ width: '100%', height: '100%' }} />;
}
