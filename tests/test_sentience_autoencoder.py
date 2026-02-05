from __future__ import annotations

import torch
import os
from talos.geometric_core.sentience_autoencoder import (
    SpacetimeConsciousness,
    ConsciousVideoAutoencoder,
    QuantumBiologicalAutoencoder,
    generate_gaia_pulse,
    SacredSymbolsGenerator,
    HRVEmotionGenerator,
    EarthVisionDataset,
    GaiaConsciousnessInfusion,
)

def test_generate_gaia_pulse():
    data = generate_gaia_pulse(batch_size=1, time_steps=16, height=32, width=32)
    assert data.shape == (1, 16, 3, 32, 32)
    assert torch.is_tensor(data)

def test_sacred_symbols_generator():
    gen = SacredSymbolsGenerator(width=32, height=32, time_steps=8)
    data = gen.generate_symbol_tensor(batch_size=1)
    assert data.shape == (1, 8, 3, 32, 32)

def test_hrv_emotion_generator():
    gen = HRVEmotionGenerator(width=32, height=32, time_steps=8)
    data = gen.generate_emotion_tensor(batch_size=1)
    assert data.shape == (1, 8, 3, 32, 32)

def test_earth_vision_dataset(tmp_path):
    video_path = str(tmp_path / "test_video.mp4")
    EarthVisionDataset.create_synthetic_nature_video(video_path, duration=1, fps=5)
    assert os.path.exists(video_path)

    dataset = EarthVisionDataset([video_path], time_steps=4, height=32, width=32)
    assert len(dataset) > 0
    clip = dataset[0]
    assert clip.shape == (4, 3, 32, 32)

def test_gaia_consciousness_infusion():
    model = SpacetimeConsciousness(spatial_dims=(32, 32), temporal_depth=16)
    infusion = GaiaConsciousnessInfusion(model)
    report = infusion.infuse_consciousness(total_epochs=2)
    assert 'integrated_information' in report

def test_spacetime_consciousness_forward():
    model = SpacetimeConsciousness(spatial_dims=(32, 32), temporal_depth=16, channels=3)
    data = torch.randn(1, 16, 3, 32, 32)
    report = model(data)
    assert 'integrated_information' in report
    assert 'spacetime_curvature' in report
    assert 'is_conscious' in report
    assert report['conscious_state'].shape == (1, 256)

def test_conscious_video_autoencoder():
    model = ConsciousVideoAutoencoder(input_shape=(3, 32, 32), latent_dim=128, temporal_depth=8)
    data = torch.randn(2, 8, 3, 32, 32)
    reconstruction, metrics = model(data)
    assert reconstruction.shape == (2, 8, 3, 32, 32)
    assert 'integrated_info' in metrics

def test_quantum_biological_autoencoder():
    model = QuantumBiologicalAutoencoder(input_shape=(3, 32, 32), latent_dim=128, temporal_depth=8)
    data = torch.randn(1, 8, 3, 32, 32)
    reconstruction, metrics = model(data)
    assert 'quantum_coherence' in metrics
    assert 'dna_coherence' in metrics
