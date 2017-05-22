/**
 * Created by sokalauvalery on 01/05/2017.
 */
var save_word = function (word, meaning, status) {
   jQuery.ajax({
       url: "/dictionary/save_word/",
       type: "POST",
       data: {"word": word, "meaning": meaning, "status": status},
       cache: false
   })
};

var get_server_word_info = function(method, word, displayMethod, elementId) {
    jQuery.ajax({
       url: "/dictionary/" + method + "/",
       type: "POST",
       data: "word=" + word,
       cache: false,
       timeout: 5000,
       success: function (res) {
           displayMethod(res, elementId)
       },
       error: function (res) {
           console.log('Error' + toString(res));
           document.getElementById(elementId).innerHTML='Failed to get data from server.'
       }
    });
};

var display_speech_part = function(name, res, output_element_id){
    if (name in res) {
        var container_div = document.createElement('div');
        container_div.className = 'row';
        document.getElementById(output_element_id).appendChild(container_div)
        var header_div = document.createElement('div');
        header_div.innerHTML = name + ':';
        header_div.id = name + '_header';
        header_div.className = 'col-md-4';
        container_div.appendChild(header_div);
        var content_div = document.createElement('div');
        content_div.className = 'col-md-4';
        container_div.appendChild(content_div);
        for (var line in res[name]) {
            var noun_div = document.createElement('div');
            noun_div.innerHTML = res[name][line];
            noun_div.className = 'row';
            content_div.appendChild(noun_div)
        }
    }
};

var display_word_definition = function (meaning, elementId) {
    var el = document.getElementById(elementId);
    while (el.firstChild) el.removeChild(el.firstChild);
    console.log(meaning);
    if (meaning) {
        display_speech_part('Noun', meaning, elementId);
        display_speech_part('Verb', meaning, elementId);
        display_speech_part('Adjective', meaning, elementId);
        display_speech_part('Adverb', meaning, elementId);
        display_speech_part('Preposition', meaning, elementId);
        display_speech_part('Conjunctions', meaning, elementId);
        display_speech_part('Interjections', meaning, elementId);
    } else {
        document.getElementById(elementId).innerHTML='Failed to get definition.'
    }
    return meaning;
};

var display_word_usage = function (usages, elementId) {
    var el = document.getElementById(elementId);
    while (el.firstChild) el.removeChild(el.firstChild);
    // var usages = get_server_word_info('get_usage', word);
    if (usages) {
        for (var source in usages){
            var header_div = document.createElement('div');
            header_div.innerHTML = source;
            for (var usage in usages[source]) {
                var usage_div = document.createElement('div');
                usage_div.innerHTML = usages[source][usage]
                header_div.appendChild(usage_div)
        }
        }
        el.appendChild(header_div)
    } else {
        document.getElementById(elementId).innerHTML='Failed to get usage from server.'
    }
    return usages
};

var display_word_translation = function (translate, elementId) {
    var el = document.getElementById(elementId)
    while (el.firstChild) el.removeChild(el.firstChild);
    if (translate) {
        for (var source in translate){
            var header_div = document.createElement('div');
            header_div.innerHTML = source;
            for (var usage in translate[source]) {
                var usage_div = document.createElement('div');
                usage_div.innerHTML = translate[source][usage]
                header_div.appendChild(usage_div)
            }
            el.appendChild(header_div)
        }
    } else {
        document.getElementById(elementId).innerHTML='Failed to get definition.'
    }

}