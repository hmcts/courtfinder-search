/*
  3 stage process
  gulp is watching asset-src and putting them into assets
  then when we develop they get sereved from /assets
  when we deploy we do ./manage.py collectstatic
  which makes /static
*/

var gulp = require('gulp'),
    sass = require('gulp-ruby-sass');

var src_base = 'courtfinder/assets-src',
    dest_base = 'courtfinder/assets';

var scss_path = src_base + '/stylesheets/**/*.scss';

gulp.task('sass', function (){
  return gulp.src( scss_path )
    .pipe(sass({ 
      style: 'expanded', 
      lineNumbers: true,
      noCache: true
    }))
    .on('error', function (err) { console.log(err.message); })
    .pipe(gulp.dest( dest_base + '/stylesheets/css/'));
});

gulp.task('default', ['sass']);


gulp.task('watch', ['sass'], function() {
  // sass
  gulp.watch(scss_path, ['sass']);
});