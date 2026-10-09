# Run from the repository root after installing the pinned environment.
$ErrorActionPreference = 'Stop'
$env:OMP_NUM_THREADS='2'
$env:OPENBLAS_NUM_THREADS='2'
$output = 'experiments/outputs/ert-numerical-validation-rerun'
if (Test-Path -LiteralPath $output) { throw 'Use a fresh output directory to preserve prior results.' }
.venv/Scripts/python.exe -m opensubsurface.validation census --output $output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label baseline-tree --solver simpeg --cell-size 0.5 --extent 64.0 --mesh-type tree --grading 1.5
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label independent-pygimli-h15 --solver pygimli --cell-size 1.5 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 64 --source-ball-radius-ratio 8.0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label tensor-h025-e64-g15 --solver simpeg --cell-size 0.25 --extent 64.0 --mesh-type tensor --grading 1.5 --central-extent 12.0 --source-batch-size 8
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label tensor-h05-e128-g15 --solver simpeg --cell-size 0.5 --extent 128.0 --mesh-type tensor --grading 1.5
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label tensor-h05-e64-g12 --solver simpeg --cell-size 0.5 --extent 64.0 --mesh-type tensor --grading 1.2
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label tensor-h05-e64-g15 --solver simpeg --cell-size 0.5 --extent 64.0 --mesh-type tensor --grading 1.5
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label tensor-h05-e64-g15-c24 --solver simpeg --cell-size 0.5 --extent 64.0 --mesh-type tensor --grading 1.5 --central-extent 24.0 --source-batch-size 8
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label tree-balls003125-r16-remote2 --solver simpeg --cell-size 0.5 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 1 --source-ball-cell-size 0.03125 --source-ball-radius-ratio 16.0 --intermediate-cell-size 2.0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label tree-balls003125-remote2 --solver simpeg --cell-size 0.5 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 8 --source-ball-cell-size 0.03125 --intermediate-cell-size 2.0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label tree-balls00625-r16-remote2 --solver simpeg --cell-size 0.5 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 4 --source-ball-cell-size 0.0625 --source-ball-radius-ratio 16.0 --intermediate-cell-size 2.0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation worker --output $output --label tree-remote2 --solver simpeg --cell-size 0.5 --extent 64.0 --mesh-type tree --grading 1.5 --intermediate-cell-size 2.0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation conforming --output $output --label fitted-s24-r12-v005 --solver pygimli --cell-size 0.75 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 64 --source-ball-radius-ratio 8.0 --fem-core-extent 12.0 --segments 24 --rings 12 --target-volume 0.05
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation conforming --output $output --label fitted-s48-r24-v001 --solver pygimli --cell-size 0.5 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 64 --source-ball-radius-ratio 8.0 --fem-core-extent 12.0 --segments 48 --rings 24 --target-volume 0.01
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation conforming --output $output --label fitted-s48-r24-v0025 --solver pygimli --cell-size 0.5 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 64 --source-ball-radius-ratio 8.0 --fem-core-extent 12.0 --segments 48 --rings 24 --target-volume 0.025
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation conforming --output $output --label fitted-s64-r32-v0025 --solver pygimli --cell-size 0.5 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 64 --source-ball-radius-ratio 8.0 --fem-core-extent 12.0 --segments 64 --rings 32 --target-volume 0.025
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation inclusions --output $output --label pygimli-inclusions-h05-core6 --solver pygimli --cell-size 0.5 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 64 --source-ball-radius-ratio 8.0 --fem-core-extent 6.0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation inclusions --output $output --label pygimli-inclusions-h075 --solver pygimli --cell-size 0.75 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 64 --source-ball-radius-ratio 8.0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation inclusions --output $output --label pygimli-inclusions-h075-core6 --solver pygimli --cell-size 0.75 --extent 64.0 --mesh-type tree --grading 1.5 --central-extent 12.0 --source-batch-size 64 --source-ball-radius-ratio 8.0 --fem-core-extent 6.0
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation replay-homogeneous --output $output
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.venv/Scripts/python.exe -m opensubsurface.validation_report $output
exit $LASTEXITCODE
