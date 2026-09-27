$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$python = Join-Path $env:USERPROFILE '.platformio/penv/Scripts/python.exe'
$pio = Join-Path $env:USERPROFILE '.platformio/penv/Scripts/pio.exe'
if (!(Test-Path $pio)) { throw 'Install PlatformIO first.' }
Push-Location $projectRoot
$previousBuildDir = $env:PLATFORMIO_BUILD_DIR
try {
    & $python tools/generate_bench_ini.py
    if ($LASTEXITCODE -ne 0) { throw 'INI generation failed' }
    # Work around the legacy toolchain's handling of spaces in build paths.
    $env:PLATFORMIO_BUILD_DIR = Join-Path $env:TEMP 'levin-current-bench-pio-build'
    & $pio run -e levin_F407VE_bench
    if ($LASTEXITCODE -ne 0) { throw 'Firmware build failed' }
    $destination = Join-Path $projectRoot '.build/levin-bench'
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    foreach ($name in @('firmware.bin','firmware.elf')) {
        Copy-Item -LiteralPath (Join-Path $env:PLATFORMIO_BUILD_DIR "levin_F407VE_bench/$name") -Destination $destination
    }
    Copy-Item -LiteralPath reference/levin-bench.ini -Destination $destination
    Copy-Item -LiteralPath docs/INJECTOR_BENCH.md -Destination $destination
    $hashes = @('firmware.bin','firmware.elf','levin-bench.ini') | ForEach-Object {
        $hash = Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $destination $_)
        "$($hash.Hash.ToLower())  $_"
    }
    [IO.File]::WriteAllLines((Join-Path $destination 'SHA256SUMS.txt'), $hashes)
    Write-Output "Build files: $destination"
} finally {
    $env:PLATFORMIO_BUILD_DIR = $previousBuildDir
    Pop-Location
}
