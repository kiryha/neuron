import React, { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, useFBO, useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import './App.css'

const HERO_URL = '/geometry/material_hero/sculpted-rubber-toy.glb'
const CAMERA_URL = '/cameras/material_hero/cam_001.json'
const ORBIT_TARGET = [0, 0, 0]
const PASSES = {
  N: 0,
  P: 1,
  V: 2,
}
const COVERAGE_PASS = 3

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
  varying vec3 vWorldPosition;

  void main() {
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vec3 viewNormal = normalize(normalMatrix * normal);
    vWorldNormal = normalize(uCameraWorldRotation * viewNormal);
    vWorldPosition = worldPosition.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPosition;
  }
`

const fragmentShader = /* glsl */ `
  uniform bool uEncodeForDisplay;
  uniform int uPass;
  varying vec3 vWorldNormal;
  varying vec3 vWorldPosition;

  void main() {
    vec3 rawValue;

    if (uPass == 3) {
      rawValue = vec3(1.0);
    } else if (uPass == 1) {
      rawValue = vWorldPosition;
    } else if (uPass == 2) {
      rawValue = normalize(cameraPosition - vWorldPosition);
    } else {
      rawValue = normalize(vWorldNormal);
    }

    vec3 outputValue = rawValue;
    if (uEncodeForDisplay) {
      outputValue = rawValue * 0.5 + 0.5;
    }

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

function packReadback(source, width, height, channels) {
  const packed = new Float32Array(width * height * channels)
  for (let y = 0; y < height; y += 1) {
    const sourceY = height - 1 - y
    for (let x = 0; x < width; x += 1) {
      const sourceOffset = (sourceY * width + x) * 4
      const targetOffset = (y * width + x) * channels
      for (let channel = 0; channel < channels; channel += 1) {
        packed[targetOffset + channel] = source[sourceOffset + channel]
      }
    }
  }
  return packed
}

function GeometryBufferCapture({ bufferApi, cameraConfig, material }) {
  const { camera, gl, scene } = useThree()
  const geometryTarget = useFBO(cameraConfig.resolution[0], cameraConfig.resolution[1], {
    depthBuffer: true,
    format: THREE.RGBAFormat,
    minFilter: THREE.NearestFilter,
    magFilter: THREE.NearestFilter,
    samples: 4,
    stencilBuffer: false,
    type: THREE.FloatType,
  })

  useEffect(() => {
    geometryTarget.texture.colorSpace = THREE.NoColorSpace
    geometryTarget.texture.name = 'material-hero-geometry-capture'
  }, [geometryTarget])

  useFrame(() => {
    material.uniforms.uCameraWorldRotation.value.setFromMatrix4(camera.matrixWorld)
  }, -1)

  useEffect(() => {
    const api = {
      capture() {
        const width = cameraConfig.resolution[0]
        const height = cameraConfig.resolution[1]
        const readback = new Float32Array(width * height * 4)
        const buffers = {}
        const previousTarget = gl.getRenderTarget()
        const previousAspect = camera.aspect
        const previousPass = material.uniforms.uPass.value
        const previousDisplay = material.uniforms.uEncodeForDisplay.value
        const previousClearColor = gl.getClearColor(new THREE.Color()).clone()
        const previousClearAlpha = gl.getClearAlpha()

        camera.aspect = cameraConfig.aspect
        camera.updateProjectionMatrix()
        camera.updateMatrixWorld(true)
        material.uniforms.uCameraWorldRotation.value.setFromMatrix4(camera.matrixWorld)
        material.uniforms.uEncodeForDisplay.value = false
        gl.setClearColor(0x000000, 0)

        try {
          for (const [name, passValue, channels] of [
            ['position', PASSES.P, 3],
            ['normal', PASSES.N, 3],
            ['view', PASSES.V, 3],
            ['coverage', COVERAGE_PASS, 1],
          ]) {
            material.uniforms.uPass.value = passValue
            gl.setRenderTarget(geometryTarget)
            gl.clear(true, true, true)
            gl.render(scene, camera)
            gl.readRenderTargetPixels(geometryTarget, 0, 0, width, height, readback)
            buffers[name] = packReadback(readback, width, height, channels)
          }
        } finally {
          gl.setRenderTarget(previousTarget)
          gl.setClearColor(previousClearColor, previousClearAlpha)
          camera.aspect = previousAspect
          camera.updateProjectionMatrix()
          material.uniforms.uPass.value = previousPass
          material.uniforms.uEncodeForDisplay.value = previousDisplay
        }

        return { ...buffers, width, height }
      },
    }
    bufferApi.current = api
    return () => {
      if (bufferApi.current === api) bufferApi.current = null
    }
  }, [bufferApi, camera, cameraConfig, geometryTarget, gl, material, scene])

  return null
}

function Scene({ bufferApi, cameraApi, cameraConfig, onInteractionEnd, onInteractionStart }) {
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
          uPass: { value: PASSES.N },
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
        enableDamping={false}
        minDistance={0.1}
        maxDistance={12}
        onEnd={onInteractionEnd}
        onStart={onInteractionStart}
        target={ORBIT_TARGET}
      />

      <GeometryBufferCapture
        bufferApi={bufferApi}
        cameraConfig={cameraConfig}
        material={normalMaterial}
      />
    </>
  )
}

export default function App() {
  const bufferApi = useRef(null)
  const cameraApi = useRef(null)
  const renderAbort = useRef(null)
  const resultUrl = useRef(null)
  const [prompt, setPrompt] = useState('gold polished clean')
  const [cameraConfig, setCameraConfig] = useState(null)
  const [cameraError, setCameraError] = useState('')
  const [interacting, setInteracting] = useState(false)
  const [renderError, setRenderError] = useState('')
  const [rendering, setRendering] = useState(false)
  const [result, setResult] = useState(null)
  const [showResult, setShowResult] = useState(false)

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

  useEffect(
    () => () => {
      renderAbort.current?.abort()
      if (resultUrl.current) URL.revokeObjectURL(resultUrl.current)
    },
    [],
  )

  const renderMaterial = useCallback(async () => {
      if (!bufferApi.current || !prompt.trim()) return

      renderAbort.current?.abort()
      const controller = new AbortController()
      renderAbort.current = controller
      setRendering(true)
      setRenderError('')
      setShowResult(false)

      try {
        await new Promise((resolve) => requestAnimationFrame(resolve))
        const buffers = bufferApi.current.capture()
        const form = new FormData()
        form.set('prompt', prompt.trim())
        form.set('width', String(buffers.width))
        form.set('height', String(buffers.height))
        for (const name of ['position', 'normal', 'view', 'coverage']) {
          form.set(
            name,
            new Blob([buffers[name].buffer], { type: 'application/octet-stream' }),
            `${name}.f32`,
          )
        }

        const response = await fetch('/api/render', {
          method: 'POST',
          body: form,
          signal: controller.signal,
        })
        if (!response.ok) {
          const payload = await response.json().catch(() => null)
          throw new Error(payload?.detail || `Render failed (${response.status}).`)
        }

        const blob = await response.blob()
        if (resultUrl.current) URL.revokeObjectURL(resultUrl.current)
        resultUrl.current = URL.createObjectURL(blob)
        setResult({
          prompt: response.headers.get('X-Normalized-Prompt') || prompt.trim(),
          url: resultUrl.current,
        })
        setShowResult(true)
      } catch (error) {
        if (error.name !== 'AbortError') setRenderError(error.message)
      } finally {
        if (renderAbort.current === controller) {
          renderAbort.current = null
          setRendering(false)
        }
      }
    }, [prompt])

  const submitPrompt = useCallback(
    (event) => {
      event.preventDefault()
      renderMaterial()
    },
    [renderMaterial],
  )

  const startCameraInteraction = useCallback(() => {
    renderAbort.current?.abort()
    setInteracting(true)
    setRendering(false)
    setShowResult(false)
  }, [])

  const endCameraInteraction = useCallback(() => {
    setInteracting(false)
    renderMaterial()
  }, [renderMaterial])

  const resetCamera = useCallback(() => {
    startCameraInteraction()
    cameraApi.current?.reset()
    requestAnimationFrame(() => {
      setInteracting(false)
      renderMaterial()
    })
  }, [renderMaterial, startCameraInteraction])

  return (
    <main className="app-shell">
      <header className="brand">NEURON // LATENT ENGINE</header>

      <div className="viewport-controls">
        <button
          className="reset-camera"
          type="button"
          disabled={!cameraConfig}
          onClick={resetCamera}
        >
          Reset Camera
        </button>
      </div>

      <form className="prompt-dock" onSubmit={submitPrompt}>
        <p className="prompt-help">
          Material · optional color · finish · condition
          <span>Example: car paint red polished clean</span>
        </p>
        <div className="prompt-row">
        <input
          aria-label="Material prompt"
          className="prompt-input"
          onChange={(event) => setPrompt(event.target.value)}
          disabled={rendering}
          placeholder="gold polished clean"
          spellCheck="false"
          type="text"
          value={prompt}
        />
          <button
            className="render-button"
            disabled={rendering || !cameraConfig}
            type="submit"
          >
            {rendering ? 'Rendering…' : 'Render'}
          </button>
        </div>
        {renderError && <p className="render-message error">{renderError}</p>}
        {!renderError && result && <p className="render-message">{result.prompt}</p>}
      </form>

      {cameraError && <div className="camera-status">Camera error: {cameraError}</div>}

      {!cameraError && !cameraConfig && <div className="camera-status">Loading camera…</div>}

      {showResult && result && !interacting && (
        <div className="result-layer">
          <img alt={`Material Hero result: ${result.prompt}`} src={result.url} />
        </div>
      )}

      {!result && !rendering && !interacting && (
        <div className="camera-status">Enter a supported material prompt and render.</div>
      )}

      {rendering && <div className="camera-status">Rendering Material Hero v0…</div>}

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
          <Scene
            bufferApi={bufferApi}
            cameraApi={cameraApi}
            cameraConfig={cameraConfig}
            onInteractionEnd={endCameraInteraction}
            onInteractionStart={startCameraInteraction}
          />
        </Canvas>
      )}
    </main>
  )
}

useGLTF.preload(HERO_URL)
