# Input Method Engine Using Neural Networks
This is our NLP capstone repo. Here is the detailed plan for our project:
http://very-natural.blogspot.com/2017/04/3-formal-proposal.html

## Dev Notes
### Dependencies
* Python 3, tensorflow 1.0 are used.
* To install all the dependecies (note, tensorflow is not included)
    * run **`pip3 install -r requirement.txt`**

### Data prep
* Download larger corpus to /data:
    * **Lancaster Corpus of Mandarin Chinese (LCMC)**, SQlite version:  Download [lcmc.db3](https://www.google.com/url?q=https://drive.google.com/open?id%3D0B6AoAA-0CimLTXMzRzNsdzltWVE&sa=D&ust=1492071674907000&usg=AFQjCNEVmzMXIkyobfENysdBt-02JAiUDw)
    * **Weibo corpus**: Download [weibo.txt](https://drive.google.com/file/d/0B6AoAA-0CimLXzBaSktfdFBfZXM/view?usp=sharing)
* Run `data_extractor.py` to generate datasets and samples.
    * **`data/lcmc_clean.data`** Pickle-dumped byte file, contains [context, pinyins, chars] triples without any added noise. In the current version, with `context_window=10, max_input_window=5`, the resulting file will be around 300MB. Change the `first_n` parameter to generate a smaller file.
    *  **`data/sms_clean.data`** SMS corpus triples, same format as above. 60 MB.
    *  **`data/weibo_clean.data`** Weibo corpus triple, same format as above. Large.

### Evaluation
* To run evaluatoin
    * run **`python3 eval.py --model [model] --k [k]`**
