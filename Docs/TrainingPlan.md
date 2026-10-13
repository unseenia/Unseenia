---
title: Training Program
---
RTX 5080: runs the full model (parameters + optimizer states + activations)

RTX 5070 Ti: acts as a data‑parallel worker or offload device depending on your training strategy

CPU RAM (192 GB DDR5‑6400): holds dataset, tokenized batches, prefetch queues, and quantization buffers.

The 5070 Ti holds:

A full copy of the model (same 16 GB footprint)

Its own activations

Its own gradients

Then:

Gradients are all‑reduced between 5080 ↔ 5070 Ti over PCIe 4.0 x4

Step time improves because you double your effective batch size

This is the simplest and most stable configuration.

Your system RAM becomes the staging area for everything that doesn’t need to be on GPU:

Stored in CPU RAM
Full training dataset (text + images if doing VLM distillation)

Tokenized sequences

Batch prefetch queues

Augmented vision embeddings (if precomputed)

Quantization buffers (TurboQuant uses CPU‑side quantization passes)

Checkpoints before GPU upload

Teacher logits (if cached)

Why 192 GB helps
TurboQuant pipelines often require:

Large prefetch windows

Mixed‑precision CPU‑side quantization

