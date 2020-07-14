# python-log-analysis

Scripts to analyze logs and generate graphs with python.

## Setup

```
git clone https://github.com/arquivo/PwaLogsMiner.git
cd PwaLogsMiner
cd python-log-analysis
pip install --upgrade virtualenv
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

### Install spacy and download the model

```
pip install -U spacy
python -m spacy download pt_core_news_sm
```

### 1º Step

Run log_analyzer_pg.py

```
python log_analyzer_pg.py
```

### 2º Step

Run graphs.py

#### Parameters

<pre>
-k or --key        --> Private Key GeoLookup ipstack
</pre>

#### Run

```
python graphs.py
```

### Example

### Authors

- [Pedro Gomes](pedro.gomes.fccn@gmail.com)
