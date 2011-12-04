
// mini query :)

$ = function(id){
  var el = document.getElementById(id);
  if (!el) return;
  el.on = function(event, fn){
    el.addEventListener(event, fn, false);
  };
  return el;
};