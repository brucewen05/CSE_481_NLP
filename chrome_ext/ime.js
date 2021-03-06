var CHOICES_PER_PAGE = 5;
var MAX_CONTEXT_WINDOW = 10;
var SERVER_ADDR = "http://13.85.8.128:7000";

$(document).ready(function() {

    var choices = [];
    var numPinyinsUsed = [];
    var curPageStart = 0;
    var preselectionStack = [["", ""]];  // [[chars, additional pinyins used]]
    var curPinyinInput = "";
    var loading = false;
    // invariant: imeInput.text() == preselectionStack.top[0] + curPinyinInput

    // unfocus
    $('textarea').blur();
    $('input').blur();
    // IME floating widget
    imeBox = $("<div id='ime_box'></div>");
    // For simplicity, only edit at the right end
    var imeInput = $("<span id='ime_input'></span>");
    imeBox.append($("<div id='ime_input_box'></div>").append(imeInput));
    imeBox.append("<div id='ime_list'></div><div id='ime_ops'><span id='ime_prev'><</span><span id='ime_next'>></span></div>");
    $("body").append(imeBox);
    imeBox.hide();

    function handleInput(inputElement, event) {
        // a-z -> always add to buffer
        // space -> choose top, or "space" if buffer empty
        // enter -> input as english, or "enter" if buffer empty
        // 1-9 -> choose index, or "number" if buffer empty
        // [+>] [-<] -> paging control, or input directly if buffer empty
        // Backspace -> del buffer, or del directly if buffer empty
        // any other -> always input directly
        if (event.shiftKey || event.ctrlKey || event.altKey || event.metaKey) {
            return;
        }

        key = event.key;
        if (/^[a-z]$/.test(key)) {
            event.preventDefault();
            buffer(key, inputElement);
            imeBox.show();
            return;
        }
        
        if (curPinyinInput !== "") {
            event.preventDefault();

            if (key == " ") {
                choose(inputElement, 1);
            } else if (event.keyCode == 13) {  // enter
                output(inputElement, imeInput.text());
            } else if (/^[1-9]$/.test(key)) {
                choose(inputElement, parseInt(key));
            } else if (key == "=" || key == ".") {
                nextPage();
            } else if (key == "-" || key == ",") {
                prevPage();
            } else if (event.keyCode == 8) {  // backspace
                if (preselectionStack.length > 1) {
                    curPinyinInput = preselectionStack.pop()[1] + curPinyinInput;
                } else if (curPinyinInput != "") {
                    curPinyinInput = curPinyinInput.substring(0, curPinyinInput.length - 1);
                }
                var preselected = preselectionStack[preselectionStack.length - 1];
                imeInput.text(preselected[0] + curPinyinInput);
                if (curPinyinInput !== "") {
                    reloadPredictions(getContextWindow(inputElement) + preselected[0], curPinyinInput);
                }
            }
        }
        if (imeInput.text() !== "") {
            imeBox.show();
        } else {
            imeBox.fadeOut(200);
        }
    }

    function choose(inputElement, index) {
        if (loading) return;
        var num = curPageStart + index - 1;
        var preselected = preselectionStack[preselectionStack.length - 1]
        if (numPinyinsUsed[num] == curPinyinInput.length) {
            output(inputElement, preselected[0] + choices[num])
        } else {
            var pinyinUsed = curPinyinInput.substring(0, numPinyinsUsed[num])
            curPinyinInput = curPinyinInput.substring(numPinyinsUsed[num])
            preselectionStack.push([preselected[0] + choices[num], pinyinUsed])
            preselected = preselectionStack[preselectionStack.length - 1]
            imeInput.text(preselected[0] + curPinyinInput)
            reloadPredictions(getContextWindow(inputElement) + preselected[0], curPinyinInput);
        }
    }

    function buffer(txt, inputElement) {
        curPinyinInput += txt;
        var preselected = preselectionStack[preselectionStack.length - 1];
        imeInput.text(preselected[0] + curPinyinInput);
        reloadPredictions(getContextWindow(inputElement) + preselected[0], curPinyinInput);
    }

    function output(inputElement, txt) {
        index = inputElement[0].selectionStart;
        inputElement.val(inputElement.val().substring(0, index) + txt +
            inputElement.val().substring(index));
        setCaretPosition(inputElement[0], index + txt.length)
        imeBox.fadeOut(200);
        imeInput.text("");
        curPinyinInput = "";
        preselectionStack = [["", ""]];
    }
    
    function nextPage() {
        if (curPageStart + CHOICES_PER_PAGE < choices.length) {
            curPageStart += CHOICES_PER_PAGE;
        }
        setChoiceElemsInPage();
    }

    function prevPage() {
        if (curPageStart - CHOICES_PER_PAGE >= 0) {
            curPageStart -= CHOICES_PER_PAGE;
        }
        setChoiceElemsInPage();
    }

    function reloadPredictions(context, pinyin) {
        loading = true;
        var oldInput = imeInput.text();
        console.log("query " + context + "|" + pinyin);
        $(".ime_choice").css("opacity", 0.5);

        $.ajax({
            type: "GET",
            url: SERVER_ADDR + "/predict/",
            contentType: "application/json; charset=utf-8",
            data: { "prev-chars": context, 
                    "pinyin-tokens":  pinyin },
            success: function(predict_data) {
                if (imeInput.text() !== oldInput) {
                    return;  // result outdated
                }
                // console.log(predict_data.value);
                choices = []
                numPinyinsUsed = []
                predict_data.value.forEach(function(tup) {
                    choices.push(tup[0]);
                    numPinyinsUsed.push(tup[1]);
                });
                curPageStart = 0;
                setChoiceElemsInPage();
                loading = false;
                $(".ime_choice").css("opacity", 1);
            }
        });
        // choices = ["自然", "孜然", "自燃", "字", "子"];
        // numPinyinsUsed = [5, 5, 5, 2, 2];
        // curPageStart = 0;
        // setChoiceElemsInPage();
    }

    function getContextWindow(inputElement) {
        var index = inputElement[0].selectionStart;
        var lines = inputElement.val().split("\n");
        var prev_txt = "^" + lines[lines.length - 1];  // last line
        var context = prev_txt.substring(Math.max(0, index - MAX_CONTEXT_WINDOW), index + 1);
        return context;
    }

    function setChoiceElemsInPage(inputElement) {
        var imeList = $("#ime_list").empty();
        for (var i = curPageStart; i < choices.length && i < curPageStart + CHOICES_PER_PAGE; i++) {
            var choice = $("<span class='ime_choice'>" + (i - curPageStart + 1) + ". " + choices[i] + "</span>");
            choice.click(function() {
                output(inputElement, choices[i]);
            });
            imeList.append(choice);
        }
    }

    document.addEventListener("focusin", function(e) {
        var src = $(e.srcElement);
        if (src.is("textarea") || src.is("input")) {
            src.keydown(function(event) {
                handleInput(src, event);

                // moves the ime box
                var cursorPos = getCaretPosition(src.val(),
                    src.css("font-family"),
                    src.css("font-size"),
                    src.css("line-height"));
                var inputPos = src.offset();
                // console.log(cursorPos)
                // console.log(inputPos)
                imeBox.css("left", cursorPos.left + inputPos.left + 15 + "px")
                imeBox.css("top", cursorPos.top + inputPos.top + 10 + "px")
            })
        }
        e.stopPropagation();
    });

    document.addEventListener("focusout", function(e) {
        var src = $(e.srcElement);
        if (src.is("textarea") || src.is("input")) {
            src.off("keydown");
            imeBox.fadeOut(200);
            imeInput.text("");
        }
        e.stopPropagation();
    })
});


function setCaretPosition(elem, caretPos) {
    if (elem != null) {
        if (elem.createTextRange) {
            var range = elem.createTextRange();
            range.move('character', caretPos);
            range.select();
        } else {
            if(elem.selectionStart) {
                elem.focus();
                elem.setSelectionRange(caretPos, caretPos);
            } else {
                elem.focus();
            }
        }
    }
}

// units: px, relative to upper left of input area
function getCaretPosition(txt, fontname, fontsize, lineheight){
    fontname = fontname.split(/[, ]+/)[0]
    var c = document.createElement('canvas');
    var ctx = c.getContext('2d');
    ctx.font = fontsize + " " + fontname;

    var lines = txt.split("\n");
    var lastLine = lines[lines.length - 1];
    width = ctx.measureText(lastLine).width;

    if (lineheight != parseInt(lineheight) + "px") {  // e.g. lineheight: normal
        lineheight = parseInt(fontsize) * 1.2
    }
    height = parseInt(lineheight) * lines.length;

    return { left: width, top: height };
}
