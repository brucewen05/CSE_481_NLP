from flask import Flask, jsonify, render_template, request

import sys
sys.path.append("..")

import pinyin_util as pu
import beam_search as bs

app = Flask(__name__)
 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tokenize/', methods=['GET'])
def tokenize():
    ret_data = {"value": pu.segment_with_hint(request.args.get('raw'))}
    return jsonify(ret_data)

@app.route('/predict/', methods=['GET'])
def getPrediction():
    print("prev_context:-------------", request.args.get('prev-chars'))
    print("pinyin_tokens:---------", request.args.get('pinyin-tokens'))
    predicted_result = bs.ngram_beam_search(request.args.get('prev-chars'), 
                                            request.args.get('pinyin-tokens'))
    ret_data = {"value": predicted_result }
    return jsonify(ret_data)
 
if __name__ == '__main__':
    app.run(port=8080, debug=True)