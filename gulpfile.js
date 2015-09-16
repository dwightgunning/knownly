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
    ngAppPath: './ng-app',
    bowerDir: './bower_components',
    staticOutputDir: './static'
};

function inject(glob, tag) {
    return plugins.inject(
      gulp.src(glob, {
        read: false,
      }), {
        starttag: '<!-- inject:' + tag + ':{{ext}} -->'
      }
    );
}

gulp.task('ng-index', ['sass', 'js-vendor', 'ng-templates', 'js-ng-app'], function() {
    plugins.util.log('Rebuilding the angular index.html');

    return gulp.src(config.ngAppPath + '/index.html')
      .pipe(inject(config.staticOutputDir + '/css/knownly-*.css', 'app-style'))
      .pipe(inject(config.staticOutputDir + '/js/vendor-*.js', 'vendor'))
      .pipe(inject(config.staticOutputDir + '/js/app-*.js', 'app'))
      .pipe(inject(config.staticOutputDir +'/js/templates-*.js', 'templates'))
      .pipe(gulp.dest(config.staticOutputDir + '/'))
      .on('error', plugins.util.log);
});

gulp.task('ng-templates', function() {
    plugins.util.log('Building angular templates');

    return gulp.src(config.ngAppPath + '/views/**/*.html')
      .pipe(plugins.angularTemplatecache({
        root:   'views/',
        module: 'clientApp'
      }))
      .pipe(plugins.streamify(plugins.rev()))
      .pipe(gulp.dest(config.staticOutputDir + '/js'))
      .on('error', plugins.util.log);
});

gulp.task('icons', function() {
    return gulp.src([
        config.bowerDir + '/fontawesome/fonts/**.*',
        config.bowerDir + '/bootstrap-sass-official/assets/fonts/**/*.*'])
    .pipe(gulp.dest(config.staticOutputDir + '/fonts/'));
});

gulp.task('js-vendor', function() {
    return gulp.src([
        config.bowerDir + '/jquery/dist/jquery.min.js',
        config.bowerDir + '/bootstrap-sass-official/assets/javascripts/bootstrap.min.js',
        config.bowerDir + '/jquery.easing/js/jquery.easing.min.js',
    ])
    .pipe(plugins.concat('vendor.js'))
    .pipe(gulp.dest(config.staticOutputDir + '/js/')) // Emit non-revision-tagged version for Django templated views
    .pipe(plugins.streamify(plugins.rev()))
    .pipe(gulp.dest(config.staticOutputDir + '/js/'));
});

gulp.task('js-ng-app', function() {
    return gulp.src([
        config.ngAppPath + '/scripts/**/*.js',
    ])
    .pipe(plugins.concat('app.js'))
    .pipe(plugins.uglify())
    .pipe(plugins.streamify(plugins.rev()))
    .pipe(plugins.size({ showFiles: true }))
    .pipe(gulp.dest(config.staticOutputDir + '/js/'));
});

gulp.task('js-app', function() {
    return gulp.src([
        config.jsDir + '/scrolling.js',
        config.jsDir + '/twitter_widgets.js',
    ])
    .pipe(plugins.concat('knownly-app.js'))
    .pipe(plugins.uglify())
    .pipe(gulp.dest(config.staticOutputDir + '/js/')) // Emit non-revision-tagged version for Django templated views
    .pipe(plugins.streamify(plugins.rev()))
    .pipe(plugins.size({ showFiles: true }))
    .pipe(gulp.dest(config.staticOutputDir + '/js/'));
});

gulp.task('sass', function() {
    return gulp.src(config.sassPath + '/import.scss')
    .pipe(plugins.sass({ 
            includePaths: [
                config.bowerDir + '/bootstrap-sass-official/assets/stylesheets',
                config.bowerDir + '/fontawesome/scss',
                config.bowerDir + '/hover/scss'],
            outputStyle: 'compressed'
        }).on('error', plugins.sass.logError))
    .pipe(plugins.minifyCss())
    .pipe(plugins.rename('knownly.css'))
    .pipe(gulp.dest(config.staticOutputDir + '/css')) // Emit non-revision-tagged version for Django templated views
    .pipe(plugins.streamify(plugins.rev()))
    .pipe(plugins.size({ showFiles: true }))
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
gulp.task('build', ['icons', 'js-app', 'ng-index', 'static-images', 'static-error-pages', 'static-misc']);
