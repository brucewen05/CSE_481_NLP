from flask import Flask, jsonify, render_template, request, json

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
    # need to convert pinyin-tokens to array, but prev-chars is fine
    # since it is a string already
    print("prev_context:-------------", request.args.get('prev-chars'))
    print("pinyin_tokens:---------", request.args.get('pinyin-tokens'))
    predicted_result = bs.ngram_beam_search(request.args.get('prev-chars'), 
                                            json.loads(request.args.get('pinyin-tokens')))
    ret_data = {"value": sort_and_merge_predictions(predicted_result) }
    return jsonify(ret_data)

def sort_and_merge_predictions(predictions_list, max_items=9):
    flat_list = [item for sublist in predictions_list for item in sublist]
    #print(flat_list)
    ranked = sorted(flat_list, key=lambda x: x[1] / len(x[0]), reverse=True)[:max_items]
    return [x[0] for x in ranked]
 
if __name__ == '__main__':
    app.run(port=8080, debug=True)