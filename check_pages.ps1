try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $docPath = "d:\Engineering Subjects\FDS Fundamentels of data science\Healthcare Management\MediAnalytics_Project_Report.docx"
    $doc = $word.Documents.Open($docPath)
    $pages = $doc.ComputeStatistics(2) # 2 = wdStatisticPages
    $words = $doc.ComputeStatistics(0) # 0 = wdStatisticWords
    $doc.Close([ref]$false)
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    Write-Output "PAGE_COUNT: $pages"
    Write-Output "WORD_COUNT: $words"
} catch {
    Write-Output "ERROR: $($_.Exception.Message)"
}
