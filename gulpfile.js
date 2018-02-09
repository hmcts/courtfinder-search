var gulp = require('gulp'),
    rimraf=require('gulp-rimraf'),
    concat=require('gulp-concat'),
    jshint=require('gulp-jshint'),
    imagemin=require('gulp-imagemin'),
    rubySass=require('gulp-ruby-sass'),
    stylish = require('jshint-stylish'),
    runSequence = require('run-sequence');

var paths = {
  dest_dir: 'courtfinder/assets/',
  src_dir: 'courtfinder/assets-src/',
  styles: 'courtfinder/assets-src/stylesheets/**/*.scss',
  scripts: [
    // vendor scripts
    'courtfinder/assets-src/vendor/jquery-details/jquery.details.js',
    // Application
    'courtfinder/assets-src/javascripts/application.js',
    'courtfinder/assets-src/javascripts/analytics.js',
  ],
  vendor_scripts: 'courtfinder/assets-src/javascripts/vendor/**/*',
  images: ['courtfinder/assets-src/images/**/*', 'node_modules/govuk_frontend_toolkit/govuk_frontend_toolkit/images/**/*']
};

// clean out assets folder
gulp.task('clean', function() {
  return gulp
    .src(paths.dest_dir, {read: false})
    .pipe(rimraf());
});

// compile scss
gulp.task('sass', function() {
  gulp
    .src(paths.styles)
    .pipe(rubySass({
      loadPath: 'node_modules/govuk_frontend_toolkit/govuk_frontend_toolkit/stylesheets'
    }))
    .pipe(gulp.dest(paths.dest_dir + 'stylesheets'));
});

// default js task
gulp.task('js', function() {
  var prod = paths.scripts.slice(0);

  // ignore debug files
  prod.push('!' + paths.src_dir + '**/*debug*');
  // create concatinated js file
  gulp
    .src(prod)
    .pipe(concat('application.js'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts'));
  // copy static vendor files
  gulp
    .src(paths.vendor_scripts)
    .pipe(gulp.dest(paths.dest_dir + 'javascripts/vendor'));
  // create debug js file
  gulp
    .src(paths.src_dir + 'javascripts/**/*debug*')
    .pipe(concat('debug.js'))
    .pipe(gulp.dest(paths.dest_dir + 'javascripts/'));
});

// jshint js code
gulp.task('lint', function() {
  var files = paths.scripts.slice(0);

  // files to ignore from linting
  files.push('!courtfinder/assets-src/vendor/**');
  files.push('!courtfinder/assets-src/javascripts/vendor/**');

  gulp
    .src(files)
    .pipe(jshint())
    .pipe(jshint.reporter(stylish));
});

// optimise images
gulp.task('images', function() {
  gulp
    .src(paths.images)
    .pipe(imagemin({optimizationLevel: 5}))
    .pipe(gulp.dest(paths.dest_dir + 'images'));
});

// setup watches
gulp.task('watch', function() {
  gulp.watch(paths.styles, ['sass']);
  gulp.watch(paths.src_dir + 'javascripts/**/*', ['lint', 'js']);
  gulp.watch(paths.images, ['images']);
});

// setup default tasks
gulp.task('default', ['build']);
// run build
gulp.task('build', function() {
  runSequence('clean', ['lint', 'js', 'images', 'sass']);
});
