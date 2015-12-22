param (
    [string]$python = $(throw "-python is required."),
    [string]$install_mode = $(throw "-install_mode is required."),
    [string]$pip_date,
    [string]$compiler
)

$ErrorActionPreference = "Stop"

if(!(Test-Path -Path ".build"))
{
    if($compiler -eq "mingw32")
    {
        virtualenv .build --system-site-packages --python $python
    }
    else
    {
        virtualenv .build --python $python
    }

    if($compiler)
    {
        "[build]`r`ncompiler=$compiler" | Out-File -Encoding ascii .\.build\Lib\distutils\distutils.cfg
    }
}

.build\Scripts\activate.ps1

python build.py prepare $pip_date
python build.py $install_mode
python build.py test
exit $LASTEXITCODE
