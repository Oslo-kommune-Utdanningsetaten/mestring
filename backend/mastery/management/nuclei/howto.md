# Up and running with Nuclei

Source: https://docs.projectdiscovery.io/quickstart#getting-started-with-cli

## Install nuclei CLI (needs go)

`go install -v github.com/projectdiscovery/pdtm/cmd/pdtm@latest`

## Install discovery tools

`pdtm -ia`

## Discover assets

`subfinder -d example.com`

## Vulnerability scanning:

- Create a list of urls (use swagger if you like) and store in urls.txt
- `nuclei -l urls.txt -stats -json-export results.json` this might take an hour
- `python make_report.py` to generate html from json
- `open report.html` to view the results
