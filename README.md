# Input Method Engine Using Neural Networks

Input Method Engine (IME) is a program that facilitates the input of non-english languages into digital devices. This work improves upon traditional n-gram based Chinese Pinyin IMEs by incorporating previous context and using a Seq2Seq neural network model with end-to-end training. Our model simplifies the NLP pipeline, while maintaining some tolerance for Pinyin abbreviations and typos.
Our evaluation shows that it significantly outperforms the baseline bigram model in terms of prediction accuracies. We also
built a Chrome extension frontend to help users type Chinese in any web pages.


See our full [project report](https://github.com/brucewen05/CSE_481_NLP/blob/master/poster_and_report/final_report.pdf) for more details.



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

