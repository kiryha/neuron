import React from 'react'
import { Canvas } from '@react-three/fiber'
import { Center, Text3D, OrbitControls, Grid } from '@react-three/drei'

function Scene() {
  return (
    <>
      <color attach="background" args={['#050505']} />
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      
      <Center top>
        {/* You'll need a JSON font file in your public folder for Text3D, 
            or just use standard <Text> for now */}
        <mesh>
          <sphereGeometry args={[0.5, 32, 32]} />
          <meshStandardMaterial color="#00f2ff" emissive="#00f2ff" emissiveIntensity={2} />
        </mesh>
      </Center>

      <Grid infiniteGrid fadeDistance={50} sectionColor="#111" cellColor="#222" />
      <OrbitControls makeDefault />
    </>
  )
}

export default function App() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <div style={{ 
        position: 'absolute', top: 20, left: 20, zIndex: 1, 
        color: 'white', fontFamily: 'monospace', letterSpacing: '4px' 
      }}>
        NEURON // LATENT ENGINE
      </div>
      <Canvas camera={{ position: [3, 3, 3], fov: 50 }}>
        <Scene />
      </Canvas>
    </div>
  )
}