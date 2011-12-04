var scrappyDo = require('../lib/scrappy-do');

var scrappy = scrappyDo.create({
    base: 'sofsis.cl'
  , cache: true
  , cacheExpire: 24
  , debug: true
});
  
/* Set up the jobs, will be execute secuencially */
//scrappy.get('/', 'body table tr:eq(3) tr td table tr:eq(3) a', function(res, data, $) {
scrappy.get('/', function(data, $) {
  data.title = $('h1').html();
  data.slogan = $('h2').html();
  data.descrition = $('h3').html();
  data.contact = $('a').attr('href').split(':')[1];
});

/*
scrappy.get('/otro', function(res, data) {
  console.log('length: ', res.length);
});
*/

scrappy.on('end', function(data) {
	console.log(data);
});

scrappy.do();
