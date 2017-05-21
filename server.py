from flask import Flask, jsonify, render_template, request, json

import pinyin_util as pu
# import beam_search as bs
# import inference_handler as ih

app = Flask(__name__, static_folder = "web/static", template_folder = "web/templates")
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tokenize/', methods=['GET'])
def tokenize():
    ret_data = { "value": pu.segment_with_hint(request.args.get('raw')) }
    return jsonify(ret_data)

@app.route('/predict/', methods=['GET'])
def getPrediction():
    # need to convert pinyin-tokens to array, but prev-chars is fine
    # since it is a string already
    # TODO: figure out a way to swap model easily
    predicted_result = ih.query(request.args.get('prev-chars'), 
                                            json.loads(request.args.get('pinyin-tokens')))
    ret_data = { "value": predicted_result }
    return jsonify(ret_data)

@app.route('/fake-predict/', methods=['GET'])
def getFakePrediction():
    ret_data = {"value": ["a", "b", "c", "d", "e"]}
    return jsonify(ret_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
