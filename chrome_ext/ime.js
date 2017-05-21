var CHOICES_PER_PAGE = 2;
var MAX_CONTEXT_WINDOW = 10;
var SERVER_ADDR = "TODO";

$(document).ready(function() {

    var choices = []
    var curPageStart = 0

    // unfocus
    $('textarea').blur()
    $('input').blur()
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
        
        if (imeInput.text() !== "") {
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
                var str = imeInput.text();
                imeInput.text(str.substring(0, str.length - 1));
            }
        }
        if (imeInput.text() !== "") {
            imeBox.show();
        } else {
            imeBox.fadeOut(200);
        }
    }

    function choose(inputElement, index) {
        output(inputElement, choices[curPageStart + index - 1])
    }

    function buffer(txt, inputElement) {
        imeInput.text(imeInput.text() + txt);
        reloadPredictions(getContextWindow(inputElement), imeInput.text());
        setChoiceElemsInPage();
    }

    function output(inputElement, txt) {
        index = inputElement[0].selectionStart;
        inputElement.val(inputElement.val().substring(0, index) + txt +
            inputElement.val().substring(index));

        setCaretPosition(inputElement[0], index + txt.length)

        imeBox.fadeOut(200);
        imeInput.text("");
    }
    
    function nextPage() {
        if (curPageStart + CHOICES_PER_PAGE < choices.length) {
            curPageStart += CHOICES_PER_PAGE;
        }
        setChoiceElemsInPage()
    }

    function prevPage() {
        if (curPageStart - CHOICES_PER_PAGE >= 0) {
            curPageStart -= CHOICES_PER_PAGE;
        }
        setChoiceElemsInPage()
    }

    function reloadPredictions(context, pinyin) {
        console.log("query " + context + "|" + pinyin);
        // TODO: query backend; handle data race
        choices = ["自然", "孜然", "自燃", "字", "子"];
    }

    function getContextWindow(inputElement) {
        index = inputElement[0].selectionStart;
        lines = inputElement.val().split("\n");
        prev_txt = "^" + lines[lines.length - 1];  // last line
        context = prev_txt.substring(Math.max(0, index - MAX_CONTEXT_WINDOW), index);
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
