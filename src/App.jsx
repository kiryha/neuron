import React, { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Center, Grid, OrbitControls, useFBO, useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import './App.css'

const HERO_URL = '/geometry/material_hero/sculpted-rubber-toy.glb'
const NORMAL_SIZE = 1024
const REFERENCE_POSITION = [3, 2.6, 3.8]
const REFERENCE_TARGET = [0, 0.8, 0]
const REFERENCE_FOV = 50

const vertexShader = /* glsl */ `
  uniform mat3 uCameraWorldRotation;
  varying vec3 vWorldNormal;

  void main() {
    vec3 viewNormal = normalize(normalMatrix * normal);
    vWorldNormal = normalize(uCameraWorldRotation * viewNormal);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`

const fragmentShader = /* glsl */ `
  uniform bool uEncodeForDisplay;
  varying vec3 vWorldNormal;

  void main() {
    vec3 worldNormal = normalize(vWorldNormal);
    vec3 outputValue = uEncodeForDisplay
      ? worldNormal * 0.5 + 0.5
      : worldNormal;
    gl_FragColor = vec4(outputValue, 1.0);
  }
`

function Hero({ material }) {
  const { scene } = useGLTF(HERO_URL)

  const hero = useMemo(() => {
    const clone = scene.clone(true)
    clone.traverse((child) => {
      if (child.isMesh) {
        child.material = material
      }
    })
    return clone
  }, [material, scene])

  return (
    <Center top>
      <primitive object={hero} dispose={null} />
    </Center>
  )
}

function NormalBufferCapture({ gridRef, material }) {
  const { camera, gl, scene } = useThree()
  const normalTarget = useFBO(NORMAL_SIZE, NORMAL_SIZE, {
    depthBuffer: true,
    format: THREE.RGBAFormat,
    minFilter: THREE.NearestFilter,
    magFilter: THREE.NearestFilter,
    stencilBuffer: false,
    type: THREE.HalfFloatType,
  })

  useEffect(() => {
    normalTarget.texture.colorSpace = THREE.NoColorSpace
    normalTarget.texture.name = 'material-hero-world-normal'
  }, [normalTarget])

  useFrame(() => {
    material.uniforms.uCameraWorldRotation.value.setFromMatrix4(camera.matrixWorld)

    const previousTarget = gl.getRenderTarget()
    const previousAspect = camera.aspect
    const gridWasVisible = gridRef.current?.visible ?? false

    try {
      if (gridRef.current) gridRef.current.visible = false
      material.uniforms.uEncodeForDisplay.value = false
      camera.aspect = 1
      camera.updateProjectionMatrix()
      gl.setRenderTarget(normalTarget)
      gl.clear()
      gl.render(scene, camera)
    } finally {
      gl.setRenderTarget(previousTarget)
      camera.aspect = previousAspect
      camera.updateProjectionMatrix()
      material.uniforms.uEncodeForDisplay.value = true
      if (gridRef.current) gridRef.current.visible = gridWasVisible
    }
  }, -1)

  return null
}

function Scene({ cameraApi }) {
  const controlsRef = useRef(null)
  const gridRef = useRef(null)
  const { camera } = useThree()

  const normalMaterial = useMemo(
    () =>
      new THREE.ShaderMaterial({
        fragmentShader,
        toneMapped: false,
        uniforms: {
          uCameraWorldRotation: { value: new THREE.Matrix3() },
          uEncodeForDisplay: { value: true },
        },
        vertexShader,
      }),
    [],
  )

  const resetCamera = useCallback(() => {
    camera.position.set(...REFERENCE_POSITION)
    camera.fov = REFERENCE_FOV
    camera.near = 0.1
    camera.far = 100
    camera.up.set(0, 1, 0)
    camera.updateProjectionMatrix()

    if (controlsRef.current) {
      controlsRef.current.target.set(...REFERENCE_TARGET)
      controlsRef.current.update()
    } else {
      camera.lookAt(...REFERENCE_TARGET)
    }
  }, [camera])

  useEffect(() => {
    const api = { reset: resetCamera }
    cameraApi.current = api
    resetCamera()

    return () => {
      if (cameraApi.current === api) cameraApi.current = null
    }
  }, [cameraApi, resetCamera])

  return (
    <>
      <color attach="background" args={['#050505']} />

      <Suspense fallback={null}>
        <Hero material={normalMaterial} />
      </Suspense>

      <Grid
        ref={gridRef}
        infiniteGrid
        fadeDistance={50}
        fadeStrength={1}
        sectionColor="#111111"
        cellColor="#090909"
      />

      <OrbitControls
        ref={controlsRef}
        makeDefault
        enableDamping
        dampingFactor={0.08}
        minDistance={2.25}
        maxDistance={12}
        target={REFERENCE_TARGET}
      />

      <NormalBufferCapture gridRef={gridRef} material={normalMaterial} />
    </>
  )
}

export default function App() {
  const cameraApi = useRef(null)
  const [prompt, setPrompt] = useState('')

  return (
    <main className="app-shell">
      <header className="brand">NEURON // LATENT ENGINE</header>

      <button
        className="reset-camera"
        type="button"
        onClick={() => cameraApi.current?.reset()}
      >
        Reset Camera
      </button>

      <div className="prompt-dock">
        <input
          aria-label="Material prompt"
          className="prompt-input"
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="Describe a material..."
          spellCheck="false"
          type="text"
          value={prompt}
        />
      </div>

      <Canvas
        camera={{
          far: 100,
          fov: REFERENCE_FOV,
          near: 0.1,
          position: REFERENCE_POSITION,
        }}
        dpr={[1, 2]}
        gl={{ antialias: true, toneMapping: THREE.NoToneMapping }}
      >
        <Scene cameraApi={cameraApi} />
      </Canvas>
    </main>
  )
}

useGLTF.preload(HERO_URL)
