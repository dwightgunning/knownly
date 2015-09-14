/* jshint node: true */
'use strict';

var gulp    = require('gulp'),
    path    = require('path'),
    plugins = require('gulp-load-plugins')({
        lazy: false}),
    del     = require('del');

var config = {
    errorPagesDir: './static-src/error-pages',
    imagesDir: './static-src/img',
    miscDir: './static-src/misc',
    jsDir: './static-src/js',
    sassPath: './static-src/sass',
    bowerDir: './bower_components',
    staticOutputDir: './static'
};

gulp.task('icons', function() {
    return gulp.src([
        config.bowerDir + '/fontawesome/fonts/**.*',
        config.bowerDir + '/bootstrap-sass-official/assets/fonts/**/*.*'])
    .pipe(gulp.dest(config.staticOutputDir + '/fonts/'));
});

gulp.task('js', function() {
    return gulp.src([
        config.bowerDir + '/jquery/dist/jquery.min.js',
        config.bowerDir + '/bootstrap-sass-official/assets/javascripts/bootstrap.min.js',
        config.bowerDir + '/jquery.easing/js/jquery.easing.min.js',
        config.jsDir + '/scrolling.js',
        config.jsDir + '/scrolling.js',
        config.jsDir + '/twitter_widgets.js',
    ])
    .pipe(plugins.concat('knownly-app.js'))
    .pipe(gulp.dest(config.staticOutputDir + '/js/'));
});

gulp.task('sass', function() {
    gulp.src(config.sassPath + '/import.scss')
    .pipe(plugins.sass({ 
            includePaths: [
                config.bowerDir + '/bootstrap-sass-official/assets/stylesheets',
                config.bowerDir + '/fontawesome/scss',
                config.bowerDir + '/hover/scss'],
            outputStyle: 'compressed'
        }).on('error', plugins.sass.logError))
    .pipe(plugins.rename('knownly.css'))
    .pipe(gulp.dest(config.staticOutputDir + '/css'));
});

gulp.task('static-error-pages', function() {
return gulp.src([config.errorPagesDir + '/*.html',])
    .pipe(gulp.dest(config.staticOutputDir + '/error-pages/'));
});

gulp.task('static-misc', function() {
return gulp.src([config.miscDir + '/*',])
    .pipe(gulp.dest(config.staticOutputDir));
});

gulp.task('static-images', function() {
return gulp.src([config.imagesDir + '/**/*',])
    .pipe(gulp.dest(config.staticOutputDir + '/img/'));
});

// Rerun the task when a file changes
gulp.task('watch', function() {
    gulp.watch(config.sassPath + '/**/*.scss', ['css']);
});

gulp.task('clean', function() {
    return del([config.staticOutputDir + '/*', ]);
});

gulp.task('default');
gulp.task('build', ['icons', 'sass', 'js', 'static-images', 'static-error-pages', 'static-misc']);
