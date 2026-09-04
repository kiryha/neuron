import React, { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, useFBO, useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import './App.css'

const HERO_URL = '/geometry/material_hero/sculpted-rubber-toy.glb'
const CAMERA_URL = '/cameras/material_hero/cam_001.json'
const ORBIT_TARGET = [0, 0, 0]

function createCameraConfig(data) {
  const requiredVectors = ['position', 'target', 'up', 'resolution']
  const vectorsAreValid = requiredVectors.every(
    (key) => Array.isArray(data[key]) && data[key].length >= 2 && data[key].every(Number.isFinite),
  )

  if (
    !vectorsAreValid ||
    data.position.length !== 3 ||
    data.target.length !== 3 ||
    data.up.length !== 3 ||
    !Number.isFinite(data.focal_length_mm) ||
    !Number.isFinite(data.horizontal_aperture_mm) ||
    data.focal_length_mm <= 0 ||
    data.horizontal_aperture_mm <= 0 ||
    data.resolution[0] <= 0 ||
    data.resolution[1] <= 0
  ) {
    throw new Error('Camera JSON contains invalid or missing values.')
  }

  const aspect = data.resolution[0] / data.resolution[1]
  const verticalAperture = data.horizontal_aperture_mm / aspect
  const fov = THREE.MathUtils.radToDeg(
    2 * Math.atan(verticalAperture / (2 * data.focal_length_mm)),
  )

  return {
    ...data,
    aspect,
    fov,
  }
}

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

  return <primitive object={hero} dispose={null} />
}

function NormalBufferCapture({ cameraConfig, material }) {
  const { camera, gl, scene } = useThree()
  const normalTarget = useFBO(cameraConfig.resolution[0], cameraConfig.resolution[1], {
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
    try {
      material.uniforms.uEncodeForDisplay.value = false
      camera.aspect = cameraConfig.aspect
      camera.updateProjectionMatrix()
      gl.setRenderTarget(normalTarget)
      gl.clear()
      gl.render(scene, camera)
    } finally {
      gl.setRenderTarget(previousTarget)
      camera.aspect = previousAspect
      camera.updateProjectionMatrix()
      material.uniforms.uEncodeForDisplay.value = true
    }
  }, -1)

  return null
}

function Scene({ cameraApi, cameraConfig }) {
  const controlsRef = useRef(null)
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
    camera.position.set(...cameraConfig.position)
    camera.fov = cameraConfig.fov
    camera.near = 0.1
    camera.far = 100
    camera.up.set(...cameraConfig.up).normalize()
    camera.updateProjectionMatrix()

    if (controlsRef.current) {
      controlsRef.current.target.set(...ORBIT_TARGET)
      controlsRef.current.update()
    } else {
      camera.lookAt(...ORBIT_TARGET)
    }
  }, [camera, cameraConfig])

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

      <OrbitControls
        ref={controlsRef}
        makeDefault
        enableDamping
        dampingFactor={0.08}
        minDistance={0.1}
        maxDistance={12}
        target={ORBIT_TARGET}
      />

      <NormalBufferCapture cameraConfig={cameraConfig} material={normalMaterial} />
    </>
  )
}

export default function App() {
  const cameraApi = useRef(null)
  const [prompt, setPrompt] = useState('')
  const [cameraConfig, setCameraConfig] = useState(null)
  const [cameraError, setCameraError] = useState('')

  useEffect(() => {
    let active = true

    fetch(CAMERA_URL)
      .then((response) => {
        if (!response.ok) throw new Error(`Camera request failed (${response.status}).`)
        return response.json()
      })
      .then((data) => {
        if (active) setCameraConfig(createCameraConfig(data))
      })
      .catch((error) => {
        if (active) setCameraError(error.message)
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <main className="app-shell">
      <header className="brand">NEURON // LATENT ENGINE</header>

      <button
        className="reset-camera"
        type="button"
        disabled={!cameraConfig}
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

      {cameraError && <div className="camera-status">Camera error: {cameraError}</div>}

      {!cameraError && !cameraConfig && <div className="camera-status">Loading camera…</div>}

      {cameraConfig && (
        <Canvas
          camera={{
            far: 100,
            fov: cameraConfig.fov,
            near: 0.1,
            position: cameraConfig.position,
            up: cameraConfig.up,
          }}
          dpr={[1, 2]}
          gl={{ antialias: true, toneMapping: THREE.NoToneMapping }}
        >
          <Scene cameraApi={cameraApi} cameraConfig={cameraConfig} />
        </Canvas>
      )}
    </main>
  )
}

useGLTF.preload(HERO_URL)
