# infinitas_export_to_kamaitachi

This is a python script/module intended to convert the newly released infinitas IIDX CSV export to kamaitachi's score format.

This is manully cobbled together from [other stuff I wrote that did this](https://github.com/everybodyeverybody/inf_score_analyzer)

## Usage

This should run on any modern release of python 3.

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

# At this point, make an API token in Tachi, in Profile -> Service Integrations
# and export it to the environment

export TACHI_API_TOKEN="<your token>"

# Download the CSV from infinitas's export https://p.eagate.573.jp/game/infinitas/2/djdata/score_download.html
# ONLY SP IS WRITTEN NOW I WILL ADD DP SOON
python3 -m src.infinitas_export_to_kamaitachi <path to your csv>
```

## Notes

I am pretty sure I've played every song in infinitas and have all the normalized titles necessary, but if it throws an error for you saying it can't find a song, raise a bug and let me know.
