param([switch]$SkipBuild)
$ErrorActionPreference = 'Stop'
$monitorRoot = Split-Path -Parent $PSScriptRoot
$monitorDeps = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies'
$monitorNode = Join-Path $monitorDeps 'node/bin/node.exe'
$monitorQa = Join-Path $monitorRoot 'reports/generated/monitoring_build'
New-Item -ItemType Directory -Path $monitorQa -Force | Out-Null
$monitorJunction = Join-Path $monitorQa 'node_modules'
if (-not (Test-Path -LiteralPath $monitorJunction)) {
    New-Item -ItemType Junction -Path $monitorJunction -Target (Join-Path $monitorDeps 'node/node_modules') | Out-Null
}
if (-not $SkipBuild) {
    & $monitorNode (Join-Path $PSScriptRoot 'build_monitoring_dashboard.mjs')
    if ($LASTEXITCODE -ne 0) { throw 'Artifact workbook builder failed.' }
}
$monitorXlsx = Join-Path $monitorRoot 'reports/strategy_dashboard.xlsx'
$monitorPdf = Join-Path $monitorRoot 'reports/strategy_dashboard.pdf'
$monitorCompanion = "$monitorXlsx.inspect.ndjson"
if (Test-Path -LiteralPath $monitorCompanion) {
    Move-Item -LiteralPath $monitorCompanion -Destination (Join-Path $monitorQa 'monitoring_saved_inspect.ndjson') -Force
}
$monitorSource = Get-Content -Raw -LiteralPath (Join-Path $monitorQa 'monitoring_artifact_qa.json') | ConvertFrom-Json
$monitorExcel = $null; $monitorBook = $null
$monitorNativeCases = [System.Collections.Generic.List[object]]::new()
try {
    $monitorExcel = New-Object -ComObject Excel.Application
    $monitorExcel.Visible = $false
    $monitorExcel.DisplayAlerts = $false
    $monitorBook = $monitorExcel.Workbooks.Open($monitorXlsx, 0, $false)
    if ($monitorBook.Worksheets.Count -ne 2) { throw 'Expected exactly two sheets.' }
    $monitorEvidence = $monitorBook.Worksheets.Item('证据与就绪')
    $monitorInputs = $monitorBook.Worksheets.Item('未来KPI')
    $monitorDauCell = $monitorEvidence.Range('C24')
    $monitorOldDau = [double]$monitorDauCell.Value2
    if ($monitorOldDau -ne 37.2) { throw 'First saved DAU actual did not match source.' }
    $monitorMandatory = @('D8','H8','D9','H9','D10','H10','D11','H11','D12','H12','D13','H13','D14','H14','D15','H15')
    $monitorFixture = [ordered]@{ D8=0; H8=4; D9=1; H9=30; D10=2; H10='TEST'; D11=0; H11='QA fixture only'; D12='通过'; H12='通过'; D13='通过'; H13='通过'; D14='QA frozen'; H14='QA scope'; D15=60; H15='QA power' }
    function Set-MonitorValue([string]$Address, $Value) {
        $monitorCell = $monitorInputs.Range($Address)
        if ($Value -is [string]) { $monitorCell.Value2 = [string]$Value }
        else { $monitorCell.Value2 = [double]$Value }
    }
    function Assert-MonitorStatus([string]$CaseName, [string]$Expected) {
        $monitorExcel.CalculateFullRebuild()
        $monitorActual = [string]$monitorInputs.Range('B5').Value2
        if ($monitorActual -ne $Expected) { throw "$CaseName returned $monitorActual instead of $Expected" }
        if ([string]$monitorEvidence.Range('B5').Value2 -ne $Expected) { throw "Overview link failed for $CaseName" }
        $monitorColor = $monitorInputs.Range('B5').DisplayFormat.Interior.Color
        $monitorExpectedColor = if ($Expected.StartsWith('黄色')) { 13562111 } elseif ($Expected.StartsWith('绿色')) { 15200739 } else { 14606843 }
        if ($monitorColor -ne $monitorExpectedColor) { throw "$CaseName conditional color $monitorColor differs from $monitorExpectedColor" }
        $monitorNativeCases.Add([pscustomobject]@{name=$CaseName; expected=$Expected; actual=$monitorActual; color=$monitorColor; expected_color=$monitorExpectedColor})
    }
    Assert-MonitorStatus 'saved_blank_inputs' '黄色：未就绪'
    foreach ($monitorKey in $monitorFixture.Keys) {
        Set-MonitorValue ([string]$monitorKey) $monitorFixture[$monitorKey]
    }
    Assert-MonitorStatus 'all_prerequisites_zero_baseline_zero_approved_budget' '绿色：可提交受限验证审批'
    foreach ($monitorKey in $monitorMandatory) {
        $monitorInputs.Range([string]$monitorKey).Value2 = $null
        Assert-MonitorStatus "missing_$monitorKey" '黄色：未就绪'
        Set-MonitorValue ([string]$monitorKey) $monitorFixture[$monitorKey]
    }
    Set-MonitorValue 'H10' ' '
    Assert-MonitorStatus 'whitespace_currency' '黄色：未就绪'
    Set-MonitorValue 'H10' 0
    Assert-MonitorStatus 'numeric_currency' '红色：输入口径无效'
    Set-MonitorValue 'H10' 'TEST'
    Set-MonitorValue 'D9' 0
    Assert-MonitorStatus 'zero_mde' '红色：输入口径无效'
    Set-MonitorValue 'D9' 1
    Set-MonitorValue 'D10' -1
    Assert-MonitorStatus 'negative_cap' '红色：输入口径无效'
    Set-MonitorValue 'D10' 0
    Assert-MonitorStatus 'zero_cap_preserved' '绿色：可提交受限验证审批'
    Set-MonitorValue 'H13' '不通过'
    $monitorInputs.Range('D8').Value2 = $null
    Assert-MonitorStatus 'known_permission_failure_with_missing_baseline' '红色：停止当前方案'
    foreach ($monitorKey in $monitorMandatory) { $monitorInputs.Range([string]$monitorKey).Value2 = $null }
    Assert-MonitorStatus 'restore_delivered_unknowns' '黄色：未就绪'
    if ($monitorEvidence.ChartObjects().Count -ne 1) { throw 'Editable native chart missing.' }
    $monitorSeries = $monitorEvidence.ChartObjects().Item(1).Chart.SeriesCollection().Item(1)
    $monitorChartFormula = [string]$monitorSeries.Formula
    $monitorEditedDau = [double]$monitorOldDau + 1
    $monitorDauCell.Value2 = [double]$monitorEditedDau
    $monitorExcel.CalculateFullRebuild()
    $monitorSeriesValues = $monitorSeries.Values
    $monitorUpdatedChart = @($monitorSeriesValues)[0]
    if ([double]$monitorUpdatedChart -ne ([double]$monitorOldDau + 1)) { throw ('Native chart did not follow source edit. Cell=' + $monitorEvidence.Range('C24').Value2 + ', chart=' + $monitorUpdatedChart + ', formula=' + $monitorChartFormula) }
    $monitorDauCell.Value2 = [double]$monitorOldDau
    foreach ($monitorSourceRow in $monitorSource.provenance) {
        $monitorEvidence.Hyperlinks.Add($monitorEvidence.Range($monitorSourceRow.cell), $monitorSourceRow.source_url, '', '原始SEC来源', $monitorSourceRow.source_id) | Out-Null
    }
    foreach ($monitorSheet in @($monitorEvidence, $monitorInputs)) {
        $monitorPage = $monitorSheet.PageSetup
        $monitorPage.Orientation = 2
        $monitorPage.PaperSize = 9
        $monitorPage.Zoom = $false
        $monitorPage.FitToPagesWide = 1
        $monitorPage.FitToPagesTall = 1
        $monitorPage.LeftMargin = $monitorExcel.InchesToPoints(0.25)
        $monitorPage.RightMargin = $monitorExcel.InchesToPoints(0.25)
        $monitorPage.TopMargin = $monitorExcel.InchesToPoints(0.22)
        $monitorPage.BottomMargin = $monitorExcel.InchesToPoints(0.28)
        $monitorPage.CenterHorizontally = $true
        $monitorPage.PrintGridlines = $false
        $monitorPage.PrintHeadings = $false
        $monitorPage.RightFooter = '&P / &N'
    }
    $monitorEvidence.PageSetup.PrintArea = '$B$2:$I$40'
    $monitorInputs.PageSetup.PrintArea = '$B$2:$I$30'
    $monitorExcel.CalculateFullRebuild()
    $monitorNativeSave = $false; $monitorNativePdf = $false; $monitorNativeError = @()
    try { $monitorBook.Save(); $monitorNativeSave = $true } catch { $monitorNativeError += ('Save: ' + $_.Exception.Message) }
    try { $monitorBook.ExportAsFixedFormat(0, $monitorPdf, 0, $true, $false); $monitorNativePdf = $true } catch { $monitorNativeError += ('ExportAsFixedFormat: ' + $_.Exception.Message) }
    $monitorNativeReceipt = [ordered]@{
        engine='Microsoft Excel COM'; version=$monitorExcel.Version; worksheet_count=2; native_chart_count=1;
        native_boundary_tests=@($monitorNativeCases); chart_source_formula=$monitorChartFormula;
        chart_edit_value_observed=$monitorUpdatedChart; chart_edit_restored=$true;
        all_planning_inputs_restored_blank=$true; final_status=$monitorInputs.Range('B5').Value2;
        native_save_succeeded=$monitorNativeSave; native_pdf_succeeded=$monitorNativePdf; native_errors=$monitorNativeError;
        pdf_export='Attempted Workbook.ExportAsFixedFormat from artifact-authored XLSX; see success flags';
        print_areas=@('B2:I40','B2:I30'); format='A4 landscape, one page per worksheet';
        limitations=@('No live data, experiment execution or automatic refresh.', 'Human review must verify source authenticity, contracts, eligibility and budget.', 'Native conditional formatting and chart recalculation checked; KPI result states are design rules, not measured results.')
    }
    $monitorNativeReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $monitorQa 'monitoring_native_qa.json') -Encoding UTF8
    Write-Output ('Excel ' + $monitorExcel.Version + '. Native boundary cases: ' + $monitorNativeCases.Count + '. Save=' + $monitorNativeSave + ', PDF=' + $monitorNativePdf)
    if (-not $monitorNativeSave -or -not $monitorNativePdf) { Write-Output ($monitorNativeError -join "`n") }
} finally {
    if ($null -ne $monitorBook) { $monitorBook.Close($false); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($monitorBook) }
    if ($null -ne $monitorExcel) { $monitorExcel.Quit(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($monitorExcel) }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
$monitorPython = Join-Path $monitorDeps 'python/python.exe'
if (-not $monitorNativeSave -or -not $monitorNativePdf) {
    & $monitorPython -B (Join-Path $PSScriptRoot 'build_monitoring_dashboard.py') --prepare
    if ($LASTEXITCODE -ne 0) { throw 'Print/link packaging failed.' }
}
& $monitorNode (Join-Path $PSScriptRoot 'build_monitoring_dashboard.mjs') --render-saved
if ($LASTEXITCODE -ne 0) { throw 'Final workbook rendering failed.' }
if (-not $monitorNativePdf) {
    & $monitorPython -B (Join-Path $PSScriptRoot 'build_monitoring_dashboard.py') --pdf
    if ($LASTEXITCODE -ne 0) { throw 'Same-view PDF packaging/validation failed.' }
}
& $monitorNode (Join-Path $PSScriptRoot 'build_monitoring_dashboard.mjs') --render-pdf
if ($LASTEXITCODE -ne 0) { throw 'Actual PDF page rendering failed.' }
