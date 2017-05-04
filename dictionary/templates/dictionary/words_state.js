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