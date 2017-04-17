# Input Method Engine Using Neural Networks
This is our NLP capstone repo. Here is the detailed plan for our project:
http://very-natural.blogspot.com/2017/04/3-formal-proposal.html

## Dev Notes
* Python 3 is used.

## Dependencies
* To install all the dependecies (note, tensorflow is not included)
    * run **`pip3 install -r requirement.txt`**

### Data prep
* **Lancaster Corpus of Mandarin Chinese (LCMC)**, SQlite version:  Download [lcmc.db3](https://www.google.com/url?q=https://drive.google.com/open?id%3D0B6AoAA-0CimLTXMzRzNsdzltWVE&sa=D&ust=1492071674907000&usg=AFQjCNEVmzMXIkyobfENysdBt-02JAiUDw) and put it in the `/data` directory.
* Run `data_extractor.py` to generate datasets.
    * **`data/data_lcmc_clean.json`** contains mappings without any added noise. In the current version, with `context_window=10, max_input_window=5`, the resulting file will be around 700MB. Change the `first_n` parameter to generate a smaller file.