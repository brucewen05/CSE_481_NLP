'use strict';

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

function displayPredictions(prediction_list) {
    var container = $("#prediction-container");
    container.text("")

    console.log("length is:", prediction_list.length)

    for (var i = 0; i < prediction_list.length; i++) {
        console.log(prediction_list[i])
        // this adds an element as well as adding an event
        // listener such that when this element is click,
        // the handleSelect function is called.
        $("<a class=\"collection-item\" data-index=\"" + i + 
            "\"><span class=\"badge\">" + prediction_list[i] + 
            "</span>" + (i + 1) + "</a>").on("click", 
            function(){
                handleSelect($(this).data("index"));
            }).appendTo(container)
    }

    container.show();
}

function handleSelect(num) {
    var container = $("#prediction-container");
    console.log(num)
    if (container.is(":visible")) {
        var element_clicked = container.find("[data-index='" + num + "']")
        console.log(element_clicked.children().text());

        var input_area = $("#raw-input");
        var token_area = $("#tokenized-pinyin");
        var split_result = splitRawInput(input_area.val());
        var updated_input = split_result.prev_chars + element_clicked.children().text();
        input_area.val(updated_input);
        token_area.text("");
        container.hide();
    }
}

$("#raw-input").on("keyup", function(e) {

    var keypressed = e.key;
    var prediction_container = $("#prediction-container");
    console.log(keypressed);
    // selection case, might need to change the condition
    // logic based on whether the selection list is shown
    // or hidden later on
    var raw_input = $("#raw-input").val();
    if (keypressed >= "1" && keypressed <= "9") {
        // user want to select a choice from the prediction list
        if (prediction_container.is(":visible")) {
            // delete the number input
            var curr_input = $("#raw-input").val();
            $("#raw-input").val(curr_input.substring(0, curr_input.length - 1));
            handleSelect(parseInt(keypressed) - 1);
        }
        // otherwise, let the user type a number!!
        // TODO:need to call predict here as well
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
		    split_result.prev_chars = "^" + split_result.prev_chars;
		    
		    $.ajax({
                        type: "GET",
                        url: SCRIPT_ROOT + "/predict/",
                        contentType: "application/json; charset=utf-8",
                        data: { "prev-chars": split_result.prev_chars, 
                                "pinyin-tokens":  JSON.stringify(token_data.value) },
                        success: function(predict_data) {              
                            console.log(predict_data.value);
                            displayPredictions(predict_data.value)
                            //$('#prediction-container').text(predict_data.value);
                        }
                    });

                }
                
            }
        }); 
    }
});
