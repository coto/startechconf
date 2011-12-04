var scrappyDo = require('../lib/scrappy-do');

var scrappy = scrappyDo.create({
    base: 'www.municipal.cl'
  , debug: true
});
  
/* Set up the jobs, will be execute secuencially */
scrappy.get('/', function(data, $) {

  var res = $('body table tr:eq(3) tr td table tr:eq(3) a');

  data.menu = [];
  res.each(function(idx, el) {
    data.menu.push({
        name: el.childNodes[0].innerHTML.toLowerCase()
      , link: el.href
    });
  });
});

scrappy.on('end', function(data) {
	console.log(data);
});

scrappy.do();
