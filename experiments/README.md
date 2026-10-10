# Experiments

This directory contains simulations, measurements, and experimental results.

The [ERT observability pilot](ert-observability-pilot/README.md) is implemented. Its [first numerical profiles](ert-observability-pilot/results/2026-10-08/RESULTS.md) are inconclusive, with the full catalog stopped at the accuracy and projected-compute gates. No hardware has been purchased.

Before implementation, an experiment needs an approved protocol defining its hypothesis, baselines, data generation, uncertainty treatment, cost accounting, acceptance criteria, and failure conditions.

When experiments begin, publish the actual protocol, versioned environment, raw inputs, seeds, evaluation procedures, and complete outcomes. Clearly label synthetic data and physical measurements.

Keep private data and local generated outputs out of version control. The initial ignore rules cover `experiments/local/` and `experiments/outputs/`. Choose a documented release location for public artifacts.
