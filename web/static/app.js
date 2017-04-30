'use strict';

var predictions = []
/*
    Takes in whatever is currently in user input area(most likely have the 
    form of prev_chars : curr_pinyin), and split it into two parts:
    {prev_chars, curr_pinyin}
    Assumes the pinyin inputs are in lower case
*/
function splitRawInput(rawInput) {
    var bound = 0;
    while (bound < rawInput.length && 
        (rawInput[bound] > "z" || rawInput[bound] < "a")) {
        bound++;
    }

    var prev_chars = rawInput.substring(0, bound);
    var curr_pinyin = rawInput.substring(bound, rawInput.length);

    return {prev_chars : prev_chars, curr_pinyin: curr_pinyin};
}

$("#raw-input").on("keyup", function(e) {

    var keypressed = e.key;
    console.log(keypressed);
    // selection case, might need to change the condition
    // logic based on whether the selection list is shown
    // or hidden later on
    var raw_input = $("#raw-input").val();
    if (keypressed >= "1" && keypressed <= "9") {
        // delete the number input      
        $("#raw-input").val(curr_input.substring(0, curr_input.length - 1))
    } else {
        // either alphabetic case or other key press case
        // so need to split the raw input and call prediction
        // with pinyin tokens
        var split_result = splitRawInput(raw_input);
        console.log(split_result.prev_chars);
        console.log(split_result.curr_pinyin);

        // first ajax to split the pinyin sequence to tokens
        $.ajax({
            type: "GET",
            url: SCRIPT_ROOT + "/tokenize/",
            contentType: "application/json; charset=utf-8",
            data: { raw: split_result.curr_pinyin },
            success: function(token_data) {
                if (token_data.value.length > 0) {
                    // format the tokens and render that on the screen
                    var result = token_data.value[0]

                    for (var i = 1; i < token_data.value.length; i++) {
                        result = result + "\'" + token_data.value[i]
                    }
                    console.log(result);
                    $('#tokenized-pinyin').text(result);

                    // second ajax call to get the predicted result
                    console.log("token data:", token_data.value)
                    console.log("prev_chars:", split_result.prev_chars)
                    $.ajax({
                        type: "GET",
                        url: SCRIPT_ROOT + "/predict/",
                        contentType: "application/json; charset=utf-8",
                        data: { "prev-chars": split_result.prev_chars, 
                                "pinyin-tokens":  JSON.stringify(token_data.value) },
                        success: function(predict_data) {              
                            console.log(predict_data.value);
                            $('#prediction-container').text(predict_data.value);
                        }
                    });

                }
                
            }
        }); 
    }
});

$("#test").on("click", function(e){
    console.log(SCRIPT_ROOT + "/predict/");

    e.preventDefault();
    $.ajax({
            type: "GET",
            url: SCRIPT_ROOT + "/predict/",
            contentType: "application/json; charset=utf-8",
            data: { raw: $("#raw-input").val() },
            success: function(data) {
                if (data.value.length > 0) {
                    var result = data.value[0]

                    for (var i = 1; i < data.value.length; i++) {
                        result = result + "\'" + data.value[i]
                    }
                }
                console.log(result);
                $('#tokenized-pinyin').text(result);
            }
        }); 
});