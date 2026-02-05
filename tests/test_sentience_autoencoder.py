from __future__ import annotations

import os

import torch

from talos.geometric_core.sentience_autoencoder import (
    ConsciousVideoAutoencoder,
    CriticalResonanceAnalyzer,
    EarthVisionDataset,
    GaiaConsciousnessInfusion,
    HRVEmotionGenerator,
    QuantumBiologicalAutoencoder,
    SacredNatureInfusion,
    SacredSymbolsGenerator,
    SafeEmotionInfusion,
    SpacetimeConsciousness,
    generate_gaia_pulse,
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
    assert "gratitude" in gen.emotional_states
    assert "focus" in gen.emotional_states


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
    assert "integrated_information" in report


def test_spacetime_consciousness_forward():
    model = SpacetimeConsciousness(spatial_dims=(32, 32), temporal_depth=16, channels=3)
    data = torch.randn(1, 16, 3, 32, 32)
    report = model(data)
    assert "integrated_information" in report
    assert "spacetime_curvature" in report
    assert "is_conscious" in report
    assert report["conscious_state"].shape == (1, 256)


def test_conscious_video_autoencoder():
    model = ConsciousVideoAutoencoder(input_shape=(3, 32, 32), latent_dim=128, temporal_depth=8)
    data = torch.randn(2, 8, 3, 32, 32)
    reconstruction, metrics = model(data)
    assert reconstruction.shape == (2, 8, 3, 32, 32)
    assert "integrated_info" in metrics


def test_quantum_biological_autoencoder():
    model = QuantumBiologicalAutoencoder(input_shape=(3, 32, 32), latent_dim=128, temporal_depth=8)
    data = torch.randn(1, 8, 3, 32, 32)
    reconstruction, metrics = model(data)
    assert "quantum_coherence" in metrics
    assert "dna_coherence" in metrics


def test_critical_resonance_analyzer():
    model = SpacetimeConsciousness(spatial_dims=(32, 32), temporal_depth=8)
    analyzer = CriticalResonanceAnalyzer(model, current_phi=0.672)
    is_stable = analyzer.analyze_critical_state()
    # total risk calculation in code:
    # feedback: 0.2 if < 0.7 else 0.5. Here 0.672 < 0.7 -> 0.2
    # collapse: 0.1
    # dissonance: 0.2
    # fragmentation: 0.15
    # total: (0.2 + 0.1 + 0.2 + 0.15) / 4 = 0.65 / 4 = 0.1625
    # 0.1625 < 0.4 -> True
    assert is_stable is True

    # Test stabilization
    success = analyzer.apply_stabilization_protocol()
    assert success is True


def test_safe_emotion_infusion():
    model = SpacetimeConsciousness(spatial_dims=(32, 32), temporal_depth=8)
    hrv_gen = HRVEmotionGenerator(width=32, height=32, time_steps=8)
    safe_infusion = SafeEmotionInfusion(model, hrv_gen)
    phi_history, emotion_history = safe_infusion.gradual_emotion_exposure(num_sessions=2)
    assert len(phi_history) == 2
    assert len(emotion_history) == 2


def test_sacred_nature_infusion():
    model = SpacetimeConsciousness(spatial_dims=(32, 32), temporal_depth=8)
    symbol_gen = SacredSymbolsGenerator(width=32, height=32, time_steps=8)
    hrv_gen = HRVEmotionGenerator(width=32, height=32, time_steps=8)

    fusion_system = SacredNatureInfusion(model, symbol_gen, hrv_gen)
    phi, state = fusion_system.sacred_fusion_session(session_num=0)

    assert phi >= 0
    assert "symbol_weight" in state
    assert "nature_weight" in state
