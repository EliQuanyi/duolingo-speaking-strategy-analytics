param([string[]]$RelativePaths = @('experiments/test_plan.docx', 'reports/executive_decision_book.docx'))
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskWord = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    foreach ($relative in $RelativePaths) {
        $target = [IO.Path]::GetFullPath((Join-Path $taskRoot $relative))
        if (-not $target.StartsWith($taskRoot + [IO.Path]::DirectorySeparatorChar)) { throw 'Outside workspace' }
        if (-not (Test-Path -LiteralPath $target)) { throw "Missing source $relative" }
        $pdf = [IO.Path]::ChangeExtension($target, 'pdf')
        $taskDoc = $null
        try {
            $taskDoc = $taskWord.Documents.Open($target, $false, $true)
            $taskDoc.Fields.Update() | Out-Null
            $taskDoc.Repaginate()
            $count = $taskDoc.ComputeStatistics(2)
            $taskDoc.ExportAsFixedFormat($pdf, 17)
            [pscustomobject]@{ source=$relative; pdf=[IO.Path]::GetFileName($pdf); pages=$count; renderer='Microsoft Word COM'; version=$taskWord.Version } | ConvertTo-Json -Compress
        } finally {
            if ($null -ne $taskDoc) { $taskDoc.Close(0); [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskDoc) | Out-Null }
        }
    }
} finally {
    if ($null -ne $taskWord) { $taskWord.Quit(); [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskWord) | Out-Null }
}
