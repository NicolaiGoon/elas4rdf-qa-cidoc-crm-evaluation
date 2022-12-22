param(
    $mode = "eval",
    $outfile = "",
    $inputfile = "",
    $consider_Answers = 10
)
if ($mode -eq "get-output") {
    & python .\evaluation\get_system_output.py $outfile
}
elseif ($mode -eq "build") {
    & python .\evaluation\buildEval.py
}
elseif ($mode -eq "eval") {
   
    $thres = @(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
    $types = @("ALL", "BeginsAt", "tookPlaceAt", "carriedOutBy", "showsFeatures", "fallsWithin", "hadParticipant","hadParticipantBegins","falltookPlace","fallhasTimeSpan")  
    $output = @()
    foreach ($threshold in $thres) {
        foreach ($type in $types) {
            Write-Host "Using threshold: " $threshold " and type: " $type
            & python .\evaluation\filter_system_output.py $threshold $type $inputfile
            $results = & python .\evaluation\evaluate.py .\evaluation\system_output_filtered.json $consider_Answers | ConvertFrom-Json
            $results | Add-Member -Name "type" -Value $type -MemberType NoteProperty
            $results | Add-Member -Name "threshold" -Value $threshold -MemberType NoteProperty
            $output = $output + $results
        }
    }
    $outpath = ".\evaluation\results.json"
    $outpath_csv = ".\evaluation\results.csv"
    $output | ConvertTo-Json | Out-file -FilePath $outpath
    $output | ConvertTo-Csv -Delimiter ';' | Out-file -FilePath $outpath_csv
    Write-Host "Output in: " $outpath ", " $outpath_csv
}
elseif ($mode -eq "graphs"){
    & python .\evaluation\graphs.py .\evaluation\results.json
}