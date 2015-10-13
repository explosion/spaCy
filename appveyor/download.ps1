# Wordnet download Windows script

$WORDNET_URL = "http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz"
$WORDNET_RELATIVE_PATH = "corpora\en"

function Download ($filename, $url) {
    $webclient = New-Object System.Net.WebClient

    $basedir = $pwd.Path + "\"
    $filepath = $basedir + $filename
    if (Test-Path $filename) {
        Write-Host "Reusing" $filepath
        return $filepath
    }
                                                                               
    # Download and retry up to 3 times in case of network transient errors.
    Write-Host "Downloading" $filename "from" $url
    $retry_attempts = 2
    for ($i = 0; $i -lt $retry_attempts; $i++) {
        try {
            $webclient.DownloadFile($url, $filepath)
            break
        }
        Catch [Exception]{
            Start-Sleep 1
        }
    }
    if (Test-Path $filepath) {
        Write-Host "File saved at" $filepath
    } else {
        # Retry once to get the error message if any at the last try
        $webclient.DownloadFile($url, $filepath)
    }
    return $filepath
}

function InstallWordNet () {
   if((Test-Path $WORDNET_RELATIVE_PATH) -eq 0)
   {
       mkdir $WORDNET_RELATIVE_PATH;
   }
   $wordnet_fname = $WORDNET_RELATIVE_PATH + "\wordnet.tar.gz" 
   Download  $wordnet_fname $WORDNET_URL
}


function main () {
    InstallWordNet
}

main