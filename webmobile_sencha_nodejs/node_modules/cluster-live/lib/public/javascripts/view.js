
/**
 * Create a `View` with the given template `id`,
 * bound to the given `obj`, and element `type`.
 *
 * @param {String} id
 * @param {Object} obj
 * @param {String} type
 * @api public
 */

function View(id, obj, type) {
  EventEmitter.call(this);
  this.id = id;
  this.html = $(id + '-template').innerHTML;
  this.tmpl = View.compile(this.html);
  this.el = document.createElement(type || 'div');
  this.obj = obj;
};

/**
 * Inherit from `EventEmitter.prototype`.
 */

View.prototype = Object.create(EventEmitter.prototype);

/**
 * Render the view.
 *
 * @return {DOMElement}
 * @api public
 */

View.prototype.render = function(){
  var locals = {};
  locals[this.id] = this.obj;
  this.el.innerHTML = this.tmpl(locals);
  this.emit('render', locals);
  return this.el;
};

/**
 * Apply overlay `msg`.
 *
 * @param {String} msg
 */

View.prototype.overlay = function(msg){
  var overlay = new View('overlay', { message: msg })
    , el = overlay.render();
  this.el.childNodes[0].appendChild(el);
};

/**
 * Remove overlay.
 */

View.prototype.removeOverlay = function(){
  var els = this.el.getElementsByClassName('overlay')
    , el = els[0];
  if (!el) return;
  el.parentNode.removeChild(el);
};

/**
 * Compile the given template `str` to a `Function`.
 *
 * @param {String} html
 * @return {Function}
 * @api public
 */

View.compile = function(str){
  var js = ['var __ = [];']
    , parts = str.split(/\{([^}]+)\}/)
    , len = parts.length;

  for (var i = 0; i < len; ++i) {
    // js
    if (i % 2) {
      js.push('__.push(locals.' + parts[i] + ');')
    // html
    } else {
      js.push("__.push('" + parts[i].replace(/'/g, '\\\'') + "');");
    }
  }

  js.push('return __.join("");');
  js = js.join('\n');
  return new Function('locals', js);
};