# 0231 — Frozen Japan jet review and the scope of Floquet propagation

**Status:** finite physical audit completed for the actual January 2026 URL;
requested December 2026 forecast unavailable. No new forecast, model fitting,
assimilation, native Adva operation or future verification.

Authored by Codex (OpenAI), submitted through Mingli Yuan's GitHub account as
an authorized proxy. Account use is not his authorship, review, endorsement
or correctness guarantee. Original contribution under Unknown v0.3.

## Target and the user's methodological clarification

The user requested a reproducible physical consistency review of a purported
December 2026 500 hPa jet near Japan. The supplied URL was:

<https://climatetensor.io/?model=ctcal12&type=wind500&lines=hgt500#map=1.65/28/128>

A captured browser run resolves this URL to **January 2026**, frame zero of
six, valid label January 15. All frozen published pointers cover January–June;
none contains December 2026. This is a target mismatch, not permission to
relabel January or generate another forecast. December diagnostics remain
Unavailable. The actual linked January field is separately audited below.
No 2026 observations are used as verifying truth. December 2026 is still future.

The user also supplied the first ideal annual-spectrum notebook and emphasized
its conditional claim: for a homogeneous linear approximation with periodic
coefficients, annual Floquet multipliers describe same-season perturbation
propagation; nonlinear and stochastic forcing need separate treatment.
This claim is retained within those assumptions, not rejected because the
experiment is idealized. For

    d eta / dt = A(t) eta, A(t + T) = A(t),
    eta(t0 + T) = M(t0) eta(t0),

the eigenvalues of the annual monodromy M are Floquet multipliers. Their
moduli and arguments describe modal growth/decay and phase advance; arbitrary
norms also depend on mode superposition and possible nonnormal transients.
The notebook's 384 generated monthly samples cover 32 ideal years. Its scalar
0.7788007831 multiplier is an ideal calibration result, not an estimated
atmospheric annual damping rate. Current ctcal12 uses six direct lead maps,
not a verified periodic evolution family or annual monodromy calculation.
The notebook's AR(1) description belongs to an earlier model version.

## Freeze and source contract

The independent freeze contains **592 files, 352,056,990 bytes**, each with
source path, copied path, byte count and SHA-256. It includes the public release,
model/background/forecast, original L12 projections, cached monthly fields,
relevant implementations and captured browser time state. Full inputs remain
outside the public Adva repository; the manifest and original measurements are
admitted. No third-party map screenshot, raw reference array, model coefficient
array, viewer implementation or installed dependency is imported into Adva.

- Product: `ctcal12`, release `native-background-l12-v1-20260924`.
- Source baseline: Adva `610eb6c8dad0d2befe4eae6ea8fce5c7a0851656`, Research 0230.
- Training and monthly means: January 1979–December 2014; 36 samples/month.
- Selection: 2015–2019; exposed development: 2020–2025.
- Input cutoff: December 2025. Container run label: January 1, 2026 00 UTC.
- Actual generation: September 24, 2026 12:39:07 UTC. The container label does
  not establish that this product was available operationally in January.
- Actual mean interval: January 1 inclusive to February 1 exclusive, 2026.
- wind500, hgt500 and prmsl bundle time axes agree exactly.
- Reference: cached NCEP/NCAR Reanalysis 1 monthly means through December 2025.
  u/v in m/s; cached z500 is geopotential Phi in m²/s²; plotted height = Phi/g
  in metres; model MSL pressure in Pa, viewer pressure in hPa.
- Native pressure-level grid: 2.5 degrees; 73 by 144 before excluding exact
  poles, 71 by 144 afterwards. Output: 141 by 288 at 1.25 degrees.
- Learned wind anomalies use vector spherical harmonics L<=12; height uses a
  scalar block. Wind native-grid monthly means are restored; whole-field z500
  remains L12 because its earlier replacement failed the fixed selection gate.

u/v and height have different output blocks but share the 64-dimensional EOF
state and six direct ridge maps. Wind is not diagnosed from height and no
explicit geostrophic constraint is applied. Shared-state statistical coupling
prevents treating their agreement as independent cross-variable evidence.

The user's concern about source authenticity remains explicit. Hash continuity
and internal balance cannot authenticate the original measurements. Reanalysis
shares model and assimilation physics and is not independent raw truth.

## Diagnostics and historical comparison

Review region: 20–60 N, 120 E eastward to 160 W (200 E).
Focus: 25–45 N, 140–180 E. Componentwise anomalies are u-ubar and v-vbar.
The primary baseline is the exact effective model climatology; a second
native-physical baseline isolates static height representation bias.

For geopotential input:

    ug = -(d Phi / d phi) / (f a)
    vg =  (d Phi / d lambda) / (f a cos(phi))
    f = 2 Omega sin(phi), a = 6371000 m, Omega = 7.292115e-5 s^-1.

Angles are radians. Second-order latitude differences use actual descending
coordinates; longitude differences are periodic on the full grid before
regional extraction. Abs(latitude)<10 degrees is excluded. No extra g is
applied to Phi. Weights are exact spherical cell areas clipped to region bounds.
RMS residual = sqrt(area mean((u-ug)^2+(v-vg)^2)), not a forecast error.

Directions are area means of absolute smallest angles. Total/climatology:
actual speed >=20 m/s and both speeds >=5. Anomalies: parent total speed >=20
and both anomaly speeds >=2. Empty support yields null, never a zero angle.

| Region / field | Wind RMS | Geostrophic RMS | Residual RMS | Direction / coverage |
| --- | ---: | ---: | ---: | ---: |
| Focus climatology | 30.536 | 31.906 | 1.853 | 1.531 deg / 91.3% |
| Focus January total | 30.363 | 31.632 | 1.918 | 1.829 deg / 90.4% |
| Focus learned anomaly | 0.644 | 0.689 | 0.262 | null / 0% |
| Review climatology | 22.731 | 24.200 | 2.169 | 1.866 deg / 53.4% |
| Review January total | 22.579 | 24.016 | 2.245 | 2.220 deg / 53.0% |
| Review learned anomaly | 0.700 | 0.747 | 0.296 | null / 0% |

RMS units are m/s. All regional cells have valid support. Historical comparison
uses 11 January and 11 December fields, 2015–2025, each processed through the
same representation/grid/derivative sequence as its forecast counterpart.
For January in the focus region, matched-hybrid total residuals span
1.6875–3.2943 m/s (median 2.3408). The forecast's 1.9185 lies inside that
empirical range. This supports monthly-mean physical compatibility, not truth
accuracy. Anomaly reference residuals span 1.0225–2.2977 (median 1.4821).
Ranges are not confidence intervals. All 568 rows, including native-first
and December reference cases, are retained.

The predicted anomaly residual is small absolutely but **40.71% of anomaly
RMS**, compared with 6.32% for total wind. Historical matched January wind
anomalies have RMS 3.4874–7.0558 m/s (median 5.3140); the predicted anomaly is
0.6443. A deterministic conditional mean can shrink, so this comparison alone
neither proves erroneous damping nor validates learned Floquet decay.

## Where the strong structure comes from

Focus anomaly RMS is 2.122% of total RMS; this is not an additive energy share.
Mean speed changes by -0.1933 m/s. Climatology and forecast maxima are respectively
37.7106 and 37.6912 m/s at the same grid point, 32.5 N / 152.5 E. The median
longitude-by-longitude jet-axis displacement is zero at 1.25-degree precision.
Thus most strong-jet structure is inherited from climatology; the learned change
is small and predominantly weakening. This does not prove zero new information.

For completeness the focus energy terms, in m²/s², are total 921.92986,
climatology 932.44674, anomaly 0.41518 and cross term -10.93206. The sum closes.
The finer output sampling does not establish finer learned forecast resolution.

The requested [combined figure](https://climatetensor.io/research/japan-geostrophic-audit-v1/combined-diagnostic.png)
shows January climatology/total/anomaly, their residual maps, December native
climatology and two explicitly unavailable December forecast panels. The plot
uses unquantized fields and no external basemap. It is published separately
with its reviewed derived inputs, not imported as a raw-data carrier into Adva.

## Representation and display effects

The native geostrophic diagnosis is retained before truncation. Focus January
climatology residual RMS by path:

| Representation | Residual RMS, m/s |
| --- | ---: |
| Native 2.5-degree | 1.9524 |
| Both L12, sampled 2.5-degree | 1.6801 |
| Both L12, sampled 1.25-degree | 1.8076 |
| Production hybrid, sampled 1.25-degree | 1.8532 |

Each historical reference uses exactly its corresponding path. The height
background difference between L12 and remapped native climatology has RMS
5.3342 m, inducing geostrophic wind RMS 1.1686 m/s. Using the native physical
height mean to define the anomaly raises its residual to 1.3093 m/s, because
that definition includes static truncation bias as well as learned change.

A separately declared noncommutation witness fits scalar and vector L12
projections on the same |latitude|>=10 belt and compares G(Ps Phi) with
Pv(G Phi). Focus climatology differences are 0.9596 m/s in January and
0.9601 in December. The scalar/vector Gram condition numbers are 9.584/9.402.
This masked-belt projection differs from production. It demonstrates an
operator-order contribution, not a measurement of atmospheric ageostrophy.
The frozen contract's phrase "constant f field" was imprecise: the executed
code uses the same time-independent, **latitude-varying** f in both orders.
An explicit erratum retains the original contract rather than rewriting it.

Viewer colours are the magnitude of interpolated monthly-mean components,
not the monthly mean of instantaneous speed. Default spatial interpolation
is bilinear; raw nearest-point and legacy Catmull–Rom modes remain selectable.
Particles use visual forward-Euler advection, bilinear texture sampling,
time scaling and random respawn in the decoded monthly vector field; they
are not synoptic trajectory forecasts. Filled frames may blend between months
while particles update on decoded real frames.

Wind components have 1 m/s quantization, heights 8 m. Height contours apply
Gaussian sigma one grid cell at this resolution. Unsmooth quantized-input
geostrophic residual is 2.9477 m/s in the focus region, versus unquantized
1.9185. This is a quantization sensitivity test, not the gradient of the
actual smoothed visible contour. Research 0230 retains the independent legacy
vector interpolation overshoot witness; it was not rerun here.

MSL time axes are checked and corresponding fields retained, but the supplied
URL does not load MSL. The screenshot's continent-high/Pacific-low claim was
not independently established in this audit. MSL is not substituted for Z500.

## Historical forecast skill is a different question

The published 4.22–4.31 m/s values are **global development vector RMSE**:
sqrt(mean over months of the area-weighted sum of component-squared errors),
on the valid nonpolar native grid with 500 hPa surface-pressure screening.
There are 72 target months in 2020–2025 per lead. Leads 1/3/6 score
4.2243/4.2970/4.3078 m/s against native seasonal 4.2756. Corresponding MSE
skills are +2.3848%/-1.0054%/-1.5129%. These are not local Japan error limits.

| Focus development month | Lead 1 RMSE | Lead 3 | Lead 6 | Native seasonal | Samples |
| --- | ---: | ---: | ---: | ---: | --- |
| January | 5.4238 | 5.6144 | 5.5009 | 5.6333 | 6, 2020–2025 |
| December | 7.2277 | 7.4598 | 7.1519 | 7.5130 | 6, 2020–2025 |

Units m/s. These exposed development scores are not an untouched independent
confirmation. No 12-month-lead assessment exists here; no December 2026 error
bound follows. Full wind and height regional results are retained in CSV.

| Review question | Outcome and evidence |
| --- | --- |
| Wind/height compatible? | January monthly total supported by same-process reference range and direction diagnostics; not December evidence. |
| New signal? | Small learned anomalies, with most jet structure already in the monthly mean; usefulness not established by decomposition alone. |
| Predictive skill? | Exposed development scores reported against seasonal baseline; independent historical confirmation **untested**. |
| ENSO attribution? | No causal conclusion; no event-index/composite/confounder evaluation performed. |

## Checks, limits and reproduction

One fixed diagnostic launch completed in 34.985 s wall / 34.873 s CPU,
peak RSS 1,062,020 KiB. Budget: 600 s wall, 540 s CPU, 6 GiB address space,
150 MB output. Persistent ledger, parent process timeout and worker resource
limits enforce the cooperative run boundary. No training occurred.

Analytic spherical derivative control maximum error is 0.024869 m/s at
2.5 degrees, below the predeclared 0.04 bound. Latitude reversal, periodic
longitude roll, Phi/Z unit equivalence, double-g negative control and
linearity passed. Baseline plus stored spectral anomaly reconstructs wind
within 1.91e-6 m/s and geopotential within 0.00196 m²/s². A divide-by-zero
warning in the analytic expected equatorial expression is retained; the
comparison and actual diagnostics exclude that latitude. An initial freeze
path lookup was repaired before any diagnostic launch. Quiver-label overlap
was repaired under a separate presentation contract, preserving original
rendering code and numerical results.

An independent read-only checker uses explicit finite differences and atan2
rather than importing the audit implementation. It reproduces the six main
rows and verifies all 592 frozen input hashes. Its finite bounds are 60 s wall,
40 s CPU and 3 GiB address space. Full original sources and source hashes were
also checked unchanged before publication. Receipts distinguish computational
completion from scientific truth or source authentication.

[Public report and downloads](https://climatetensor.io/research/japan-geostrophic-audit-v1/)
include the derived plotting fields and a runnable public arithmetic checker.
Adva retains only original code, contracts, aggregate measurements and facts
under `experiments/japan_geostrophic_audit_v1/`; no raw arrays or dependencies.
After downloading and unpacking the reviewed public bundle:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 verify_summary.py --root .
```

An optional one-launch exact reconstruction contract and `reproduce_full.py`
are supplied for the complete frozen local cache:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 reproduce_full.py \
  --frozen /home/ubuntu/research-inputs/japan-geostrophic-audit-20260924-v1/frozen
```

The original numerical allowance is spent. The optional reader replay has
not been launched by this audit; it may not reset the original ledger,
retune parameters or substitute missing data. Missing full cache returns
Unavailable. Exact replay compares the complete metrics JSON byte-for-byte;
its dependencies are separately installed and version-recorded. See the
experiment README and public README for all commands and omissions.

## References

- [Research 0230](0230-native-background-forecast-and-display-interpolation.md).
- [NCEP/NCAR Reanalysis 1, NOAA PSL](https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html).
- [NOAA data-use statement](https://psl.noaa.gov/disclaimer/).
- [Geostrophic wind height/geopotential unit conventions](https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.geostrophic_wind.html).
- [DaCunha and Davis, periodic linear Floquet systems](https://arxiv.org/abs/0901.3841).

No external paper or source-page expression is imported. These finite physical
observations do not establish a native certificate or a completed Adva import.
