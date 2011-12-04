
/**
 * Initialize a new `Master`.
 */

function Master() {
  var self = this;
  EventEmitter.call(this);
  this.view = new MasterView(this);
  this.on('change', function(data){
    self.update(data);
    self.view.render();
  });
};

/**
 * Inherit from `EventEmitter.prototype`.
 */

Master.prototype = Object.create(EventEmitter.prototype);

/**
 * Update properties with the given `obj`.
 *
 * @param {Object} obj
 */

Master.prototype.update = function(obj){
  var keys = Object.keys(obj)
    , len = keys.length;

  for (var i = 0; i < len; ++i) {
    this[keys[i]] = obj[keys[i]];
  }
};

/**
 * Initialize a new `MasterView` with the given `master`.
 *
 * @param {Master} master
 */

function MasterView(master) {
  View.call(this, 'master', master);
  var el = $('master');
  el.appendChild(this.el);
}

/**
 * Inherit from `View.prototype`.
 */

MasterView.prototype = Object.create(View.prototype);
