$entities_query = @"
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT distinct ?sub WHERE {
  ?sub ?pred ?obj .
  FILTER(REGEX(STR(?sub), "ww1lod"))
} 
"@

$SPARQL_URL = "http://ldf.fi/ww1lod/sparql?query=" + [System.Web.HttpUtility]::UrlEncode($entities_query)
$headers = @{"Accept" = "application/json" }
$payload = @{"query" = $entities_query }
$res = Invoke-WebRequest -Uri $SPARQL_URL -Headers $headers

$entities = @()
$res = ConvertFrom-Json $res
foreach ($s in $res.results.bindings) {
  $entities += $s.sub.value
}


$paths = @(1, 2, 3, 4, 5)
$results = @{ }

foreach ($path in $paths) {
  Write-Host "Path: " $path
  $average = @()
  foreach ($entity in $entities) {
    Write-Host "Entity: " $entity
    $path_minus_one = $path - 1
    $query = @"
  PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
  prefix crm: <http://www.cidoc-crm.org/cidoc-crm/>
  
  select (count(*) as ?count)
  where {
    {
    <$entity> (crm:|!crm:){,$path_minus_one} ?s .
    ?s ?p ?o .
    FILTER(REGEX(STR(?p), "^http://www.cidoc-crm.org/cidoc-crm")) .
    }
    UNION {
    <$entity> (crm:|!crm:){,$path} ?s .
    ?s ?p ?o .
    FILTER(REGEX(STR(?p), "^http://www.w3.org/2004/02/skos/core#prefLabel")) .
    }
  }  
"@
    $SPARQL_URL = "http://ldf.fi/ww1lod/sparql?query=" + [System.Web.HttpUtility]::UrlEncode($query)
    $headers = @{"Accept" = "application/json" }
    $payload = @{"query" = $entities_query }
    $res = Invoke-WebRequest -Uri $SPARQL_URL -Headers $headers
    $res = ConvertFrom-Json $res
    $average += $res.results.bindings[0].count.value
    # if ($average.Count -gt 50) { break }
  }

  Write-Host $average
  $average = ($average | Measure-Object -Average).Average

  Write-Host "Entity Expansion Path: " $path " average nodes + edges : " $average
  $results["path" + $path] = $average

}

Out-File -InputObject ($results | ConvertTo-Json) -FilePath "./evaluation/entity_path_statistics.json" -Encoding "utf8"