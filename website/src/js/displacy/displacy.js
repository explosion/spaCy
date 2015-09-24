var container = document.getElementById("displacy");
var dp = [];

var displaCy = function(mode, api, query, call) {
    if(mode == "manual" && !call) call = query + "/"; 
    var request = call || query;
    if(mode == "steps") call = 0;

    dp.loadingIndicator();

    var xhr = new XMLHttpRequest();
    xhr.open( "POST", api, true);
    xhr.setRequestHeader("Content-type", "text/plain");
    xhr.onreadystatechange = function(data) {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var result = JSON.parse(xhr.responseText);
                dp.setDisplay(mode, api, query, call, result);
                dp.loadingIndicator(false);
            }
        }
    }
    xhr.send(JSON.stringify({ text: request}));
}

dp.setDisplay = function(mode, api, query, call, result) {
    var state = (typeof call === "number") ? call : 0;
    var wordlist = result.words;
    var arrowlist = result.states[state].arrows;
    var stacklist = result.states[state].stack;
    var focus = result.states[state].focus;
    var is_final = result.states[state].is_final;
    var actionlist = result.actions;

    var classnames = { 
        words: { "NO_TAG" : "w-notag", "ADJ" : "w-adj", "ADV" : "w-adv", "ADP" : "w-adp", "DET" : "w-det", "NOUN" : "w-noun", "PRON" : "w-pron", "PRT" : "w-prt", "VERB" : "w-verb", "X" : "w-x", "PUNCT" : "w-punct", "EOL" : "w-eol", "SPACE" : "w-space", "on_stack" : "stack", "is_entity" : "w-ent", "low_prob" : "w-low", "in_focus" : "in-focus"
        },
        arrows : { "correct_arc" : "correct", "incorrect_arc" : "incorrect" }
    }

    container.scrollLeft = 0;
    dp.clearDisplay();
    dp.addCss(arrowlist, wordlist);
    dp.addArrows(arrowlist);
    dp.addWords(wordlist, classnames.words, focus, stacklist);
    dp.setFocus(focus, arrowlist, wordlist, stacklist);

    if(mode == "steps") dp.addActions(actionlist, is_final, mode, api, query, call, result);
    if(mode == "manual") dp.addActions(actionlist, is_final, mode, api, query, call);
}

dp.clearDisplay = function() {
    document.getElementById("displacy").innerHTML = "";
}

dp.clearActions = function() {
    var actions = document.getElementById("actions");
    if(actions != null) actions.innerHTML = "";
}

dp.loadingIndicator = function(loading) {
    var spinner = dp.element("div", "spinner", "spinner", false);
    container.appendChild(spinner);

    if(!loading) {
        document.getElementById("spinner").style.visibility = "hidden";
    }
}

dp.calcSize = function(arrowlist) {
    var size = { height: "350", width: "175", spacing: "10", unit: "px" }
    if(arrowlist.length <= 3) size.height /= 2.75;
    if(arrowlist.length > 12) {
        size.width *= 1.15; 
        size.height *=1.25;
    }
    if(arrowlist.length > 20) {
        size.width *=1.25;
        size.height *=1.5;
    }
    return size;
}

dp.addCss = function(arrowlist, wordlist) {
    var size = dp.calcSize(arrowlist);

    var css = { 
        height: size.height + size.unit, 
        width: size.width + size.unit, 
        spacing: size.spacing + size.unit
    }

    var stylesheet = dp.element("style", false, false, ["scoped", "true"]);
    var styles = ["#displacy *,#displacy *:before,#displacy *:after{box-sizing:border-box}#displacy{position:relative;overflow:scroll}#displacy .focus{position:absolute;top:0;height:100%;z-index:-1;background:rgba(0,0,0,.25)}#displacy .current-stack{margin:6em 1.5em;font-size:.75em;opacity:.25}#displacy .actions{position:fixed;}#displacy .words{display:flex;display:-webkit-flex;display:-ms-flexbox;display:-webkit-box;flex-flow:row nowrap;overflow:hidden;text-align:center}#displacy .words .word:after{content:attr(title);display:block}#displacy .arrows{width:100%;position:relative}.level{position:absolute;bottom:0;width:100%}#displacy .arrow{height:100%;position:absolute;overflow:hidden}#displacy .arrow:before{content:attr(title);text-align:center;display:block;height:200%;border-radius:50%;border:2px solid;margin:0 auto}#displacy .arrow:after{content:'';width:0;height:0;position:absolute;bottom:-1px;border-top:12px solid;border-left:6px solid transparent;border-right:6px solid transparent}#displacy .arrow.null{display:none}"];

    for(var i = 1; i <= arrowlist.length; i++) {
        var level = ".level" + i;

        styles.push("#displacy " + level + "{height:" + parseInt(100/arrowlist.length * i) + "%}#displacy " + level + " .arrow{width:calc(" + css.width + " * " + i + ")}#displacy " + level + " .arrow:before{width:calc(100% - " + css.spacing + " * " + parseInt(arrowlist.length - i) + " - 10px)}#displacy " + level + " .arrow.left:after{left:calc(" + css.spacing + " * " + (arrowlist.length - i)/2 + ")}#displacy " + level + " .arrow.right:after{right:calc(" + css.spacing + " * " + (arrowlist.length - i)/2 + ")}");
    }

    for(i = 1; i < wordlist.length; i++) {
        styles.push("#displacy .level .arrow:nth-child(" + i + "){left:calc(" + css.width + " * " + parseInt(i - 1) + ")}#displacy .arrows{height:" + css.height + "}#displacy .level{left:calc(" + css.width + "/2)}");
    }

    styles.push("#displacy .words{min-width:calc(" + css.width + " * " + wordlist.length + ")}.words .word{width:" + css.width + "}")

    stylesheet.appendChild(document.createTextNode(styles.join(' ')));
    container.appendChild(stylesheet);
}

dp.addArrows = function(arrowlist) {
    var arrowContainer = dp.element("div", "arrows");

    for(var i = 0; i < arrowlist.length; i++) {
        var level = dp.element("div", "level level" + (i + 1));
        
        for(var j = 0; j < arrowlist[i].length; j++) {
            var arrow = dp.element("span");

            if(arrowlist[i][j] !== null) {
                arrow.setAttribute("title", arrowlist[i][j].label);
                arrow.className = "arrow " + arrowlist[i][j].dir;
            }
            else {
                arrow.className = "arrow null";
            }
            level.appendChild(arrow);
        }
        arrowContainer.appendChild(level);
    }
    container.appendChild(arrowContainer);
}

dp.addWords = function(wordlist, classnames, focus, stacklist) {
    var wordContainer = dp.element("div", "words");

    for(i = 0; i < wordlist.length; i++) {
        var classes = [ "word" ];
        var current = wordlist[i];
        var tag = current.tag;

        var word = dp.element("div", false, false, ["title", tag]);
        classes.push(classnames[tag]);

        if(i === focus) classes.push(classnames["in_focus"]);
        if(stacklist[i]) classes.push(classnames["on_stack"]);
        if(current.is_entity) classes.push(classnames["is_entity"]);
        if(!current.is_entity && current.prob <= -17) classes.push(classnames["low_prob"]);

        word.className = classes.join(" ");
        var wordtext = dp.element("span", false, false, false, wordlist[i].word);
        word.appendChild(wordtext);
        wordContainer.appendChild(word);
    }
    container.appendChild(wordContainer);
}

dp.setFocus = function(focus, arrowlist, wordlist, stacklist) {
    var size = dp.calcSize(arrowlist);

    var focusContainer = dp.element("div", "focus", "focus");
    focusContainer.style.width = size.width + size.unit;
    focusContainer.style.left = size.width * focus + size.unit;

    focusContainer.appendChild(dp.compileStack(wordlist, stacklist));
    container.appendChild(focusContainer);

    if(size.width * focus - container.scrollLeft > container.clientWidth/2) container.scrollLeft = size.width * focus - container.clientWidth/2 + size.width/2;
}

dp.compileStack = function(wordlist, stacklist) {
    var stack = dp.element("div", "current-stack", false, ["title", "Stack"]);

    for(var i in wordlist) {
        if(stacklist[i]) {
            var word = dp.element("div", false, false, false, wordlist[i].word);
            stack.appendChild(word);
        }
    }
    return stack;
}

dp.addActions = function(actionlist, is_final, mode, api, query, call, result) {
    dp.clearActions();
    var bindings = [];
    var actionContainer = dp.element("div", "actions", "actions");

    for(var i in actionlist) {
        var button = dp.element("button", actionlist[i].label, false, false, actionlist[i].label);
        button.onclick = dp.performAction(mode, api, query, call, actionlist[i].key, result);

        if(actionlist[i].is_valid && !is_final) bindings.push({ 
            key: actionlist[i].key,
            code: actionlist[i].binding,
            action: button.onclick
        });
        else button.disabled = true;

        actionContainer.appendChild(button);
    }
    container.appendChild(actionContainer);

    document.onkeydown = function(event) {
        if ('input' != event.target.tagName.toLowerCase()) {
            var codes = [];
            for(i in bindings) {
                if(event.keyCode == bindings[i].code) {
                    bindings[i].action();
                }
                codes.push(bindings[i].code);
            }

            if(codes.indexOf(event.keyCode)!=-1) return false;
        }  
    }

    if(is_final) container.scrollLeft = 0;
}

dp.performAction = function(mode, api, query, call, action, result) {
    if(mode == "parse" || mode == "manual") {
        return function() {
            call += action + ",";
            displaCy(mode, api, query, call);
        }
    }

    if(mode == "steps") {
        return function() {
            if(action == "N") call++;
            else if(action == "P" && call > 0) call--;
            else call = 0;
            dp.setDisplay(mode, api, query, call, result);
        }
    }
}

dp.element = function(tag, classname, id, attribute, content) {
    var element = document.createElement(tag);
    element.className = classname || "";
    if(id) element.id = id;
    if(attribute) element.setAttribute(attribute[0], attribute[1]);
    if(content) element.appendChild(document.createTextNode(content));
    return element;
}
