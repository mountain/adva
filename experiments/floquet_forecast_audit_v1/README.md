# Floquet check of the frozen current ctcal12 model

The first ideal method's conditional periodic homogeneous-linear claim is retained.
This checks the currently published parameters, not a fitted replacement model.

## Public reproduction

Download and unpack floquet-review.zip outside the Adva repository. Obtain the
already public frozen model (the checker verifies its declared SHA-256):

```sh
curl -fL https://climatetensor.io/research/native-background-l12-v1/model.npz -o model.npz
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 verify.py --root . --model model.npz
```

Python 3.11.15 / NumPy 2.4.6 were used. The independent checker uses column
coordinates, numpy eigenvalues, matrix_power and direct SVD. It reproduces all
four principal spectral/gain values and the six direct-versus-iterated differences.
It has 60 seconds wall, 40 CPU and 3 GiB address-space limits, with no training.
Dependencies are installed separately, not included in the ZIP.

The complete original diagnostic additionally uses the locally frozen L12
projection and forecast arrays specified in contract.json, plus SciPy 1.17.1 and
Matplotlib 3.11.2. They are NOT in this archive. Missing full inputs means
Unavailable for the complete historical-innovation calculation, not a pass.

Executed full diagnostic command in its original outside-repository directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /home/ubuntu/climatetensor-env/bin/python run.py
```

Its single launch is spent; retain launch-ledger.json. Do not reset a ledger to
repeat or widen experiments. The public read-only verify.py is the runnable
reproduction command for the main operator findings.

## Reading the numbers

Use row coordinates x=(c-climatology[month])/scale, z=x V. Direct forecasts are
z R_h. The declared homogeneous one-step extension uses B=R_1 V and annual
z -> z B^12. Column monodromy is (B^12)^T. Current R_h are independent of month;
seasonal climatology is not a seasonally varying transition operator.

The direct maps fail the composition test. Thus the annual spectrum belongs to
the explicitly defined one-step extension, not to the entire published direct
family. This failure is not a forecast-skill score or evidence that direct
regression is invalid. Gains use fixed normalized coefficient/EOF Euclidean
norms, not atmospheric physical energy. The actual atmosphere's stability and
forecast skill are not established.

Historical innovation decomposition is ex-post, uses realized subsequent states,
and may cross training/selection/development split boundaries. It is not a
12-month operational hindcast. Residuals include omitted state, bias, nonlinear,
stochastic and measurement effects; their separate causes are not identified.

The first audit stopped at a NumPy datetime64-versus-string mask comparison;
attempt-1 retains source, contract and failure. The successor changed only to
explicit datetime constants under a one-launch continuation. The original model,
thresholds and tested family were unchanged. The first independent verification
invocation stopped before numerical work because contract.json and report.json
were not co-located; the corrected invocation and its two-invocation cap are
recorded in verification-contract.json. No further automatic retry.

Authored by Codex (OpenAI), original contribution under Unknown v0.3, through
Mingli Yuan's authorized account proxy. Not his technical endorsement. No raw
meteorological data, model array, third-party paper, dependency or map image is
included. The aggregate SVG contains original geometry and text nodes, no font
program. Data-source authentication concerns from the frozen review remain open.
