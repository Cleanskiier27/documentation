function Get-SatGpuConfig {
    . "$PSScriptRoot\porty-manager.ps1"

    $manager = Get-PortyConfig
    $hostBase = $manager.Host
    $apiPort = $manager.ApiPort
    $webPort = $manager.WebPort
    $workerPort = $manager.MeshPort
    $mapPort = $manager.MapPort
    $satellitePort = $manager.SatellitePort
    $analyticsPort = $manager.AnalyticsPort
    $telemetryPort = $manager.TelemetryPort
    $universalBase = if ([string]::IsNullOrWhiteSpace($env:UNIVERSAL_API_BASE_URL)) { $hostBase } else { $env:UNIVERSAL_API_BASE_URL.TrimEnd('/') }
    $meshMode = if ([string]::IsNullOrWhiteSpace($env:WIFI7_MESH_MODE)) { 'overlay' } else { $env:WIFI7_MESH_MODE }
    $meshInterface = if ([string]::IsNullOrWhiteSpace($env:WIFI7_MESH_INTERFACE)) { 'mesh0' } else { $env:WIFI7_MESH_INTERFACE }
    $universalApiPort = $manager.UniversalApiPort

    $config = [ordered]@{
        AppName = if ([string]::IsNullOrWhiteSpace($env:APP_NAME)) { 'AI World - NetworkBuster' } else { $env:APP_NAME }
        Host = $hostBase
        ApiPort = $apiPort
        WebPort = $webPort
        WorkerPort = $workerPort
        MapPort = $mapPort
        SatellitePort = $satellitePort
        AnalyticsPort = $analyticsPort
        TelemetryPort = $telemetryPort
        UniversalApiBaseUrl = $universalBase
        UniversalApiPort = $universalApiPort
        Wifi7MeshMode = $meshMode
        Wifi7MeshInterface = $meshInterface
        Endpoints = @(
            @{ Name = 'aiworld-api'; Url = "$hostBase:$apiPort" },
            @{ Name = 'aiworld-web'; Url = "$hostBase:$webPort" },
            @{ Name = 'aiworld-mesh'; Url = "$hostBase:$workerPort" },
            @{ Name = 'aiworld-map'; Url = "$hostBase:$mapPort" },
            @{ Name = 'aiworld-satellite'; Url = "$hostBase:$satellitePort" },
            @{ Name = 'aiworld-analytics'; Url = "$hostBase:$analyticsPort" },
            @{ Name = 'aiworld-telemetry'; Url = "$hostBase:$telemetryPort" },
            @{ Name = 'universal-api'; Url = "$universalBase:$universalApiPort" }
        )
    }

    return [pscustomobject]$config
}
