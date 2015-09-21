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

gulp.task('ng-index', ['sass', 'ng-templates', 'js-ng-app'], function() {
    plugins.util.log('Rebuilding the angular index.html');

    return clean('/index.html', function(cb) {
        gulp.src(config.ngAppPath + '/index.html')
          .pipe(inject(config.staticOutputDir + '/css/knownly-*.css', 'app-style'))
          .pipe(inject(config.staticOutputDir + '/js/vendor-*.js', 'vendor'))
          .pipe(inject(config.staticOutputDir + '/js/app-*.js', 'app'))
          .pipe(inject(config.staticOutputDir +'/js/templates-*.js', 'templates'))
          .pipe(gulp.dest(config.staticOutputDir + '/'))
          .on('error', plugins.util.log)
          .pipe(plugins.livereload())
          .on('end', cb || function() {});
    });
});

gulp.task('ng-templates', function(cb) {
    plugins.util.log('Building angular templates');

    return clean('/js/templates-*.js', function() {
        gulp.src(config.ngAppPath + '/views/**/*.html')
          .pipe(plugins.angularTemplatecache({
            root:   'views/',
            module: 'knownlyApp'
          }))
          .pipe(plugins.streamify(plugins.rev()))
          .pipe(gulp.dest(config.staticOutputDir + '/js'))
          .on('error', plugins.util.log)
          .on('end', cb || function() {});
      });
});

gulp.task('icons-vendor', function(cb) {
    return clean('/fonts/*', function() {
        gulp.src([
            config.bowerDir + '/fontawesome/fonts/**.*',
            config.bowerDir + '/bootstrap-sass-official/assets/fonts/**/*.*'])
        .pipe(gulp.dest(config.staticOutputDir + '/fonts/'))
        .on('end', cb || function() {});
    });
});

gulp.task('js-vendor', function(cb) {
    return clean('/js/vendor.js', function() {
        gulp.src([
            config.bowerDir + '/jquery/dist/jquery.min.js',
            config.bowerDir + '/bootstrap-sass-official/assets/javascripts/bootstrap.min.js',
            config.bowerDir + '/jquery.easing/js/jquery.easing.min.js',
        ])
        .pipe(plugins.concat('knownly-vendor.js'))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .on('end', cb || function() {});
    });
});

gulp.task('js-ng-vendor', function(cb) {
    return clean('/js/vendor-*.js', function() {
        return gulp.src([
            config.bowerDir + '/underscore/*.js',
            config.bowerDir + '/requirejs/require.js',
            config.bowerDir + '/jquery/dist/jquery.js',
            config.bowerDir + '/angular/angular.js', 
            config.bowerDir + '/angular-cookies/angular-cookies.js',
            config.bowerDir + '/angular-animate/angular-animate.js', 
            config.bowerDir + '/angular-route/angular-route.js',
            config.bowerDir + '/angular-loader/angular-loader.js',
            config.bowerDir + '/angular-bootstrap/ui-bootstrap.js',
            config.bowerDir + '/jquery.easing/js/jquery.easing.min.js',
        ])
        .pipe(plugins.concat('vendor.js'))
        .pipe(plugins.uglify())
        .pipe(plugins.streamify(plugins.rev()))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .on('end', cb || function() {});
    });
});

gulp.task('js-ng-app', function(cb) {
    return clean('/js/app-*.js', function() {
        gulp.src([
            config.ngAppPath + '/scripts/services/**/*.js',
            config.ngAppPath + '/scripts/controllers/**/*.js',
            config.ngAppPath + '/scripts/app.js',
        ])
        .pipe(plugins.concat('app.js'))
        .pipe(plugins.uglify())
        .pipe(plugins.streamify(plugins.rev()))
        .pipe(plugins.size({ showFiles: true }))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .on('end', cb || function() {});
    });
});

gulp.task('js-app', function(cb) {
    return clean('/js/knownly-app.js', function() {
        gulp.src([
            config.jsDir + '/*.js',
        ])
        .pipe(plugins.concat('knownly-app.js'))
        .pipe(plugins.uglify())
        .pipe(gulp.dest(config.staticOutputDir + '/js/')) // Emit non-revision-tagged version for Django templated views
        .pipe(plugins.size({ showFiles: true }))
        .pipe(plugins.livereload())
        .on('end', cb || function() {});
    });
});

gulp.task('sass', function(cb) {
    return clean('/css/*.css', function() {
        gulp.src(config.sassPath + '/import.scss')
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
        .pipe(gulp.dest(config.staticOutputDir + '/css'))
        .pipe(plugins.livereload())
        .on('end', cb || function() {});
    });
});

gulp.task('static-error-pages', function(cb) {
    return clean('/error-pages/*', function() {
        gulp.src([config.errorPagesDir + '/*.html',])
        .pipe(gulp.dest(config.staticOutputDir + '/error-pages/'))
        .on('end', cb || function() {});
    });
});

gulp.task('static-misc', function(cb) {
    return clean(config.staticOutputDir + '/*', function() {
        gulp.src([config.miscDir + '/*',])
        .pipe(gulp.dest(config.staticOutputDir))
        .on('end', cb || function() {});
    });
});

gulp.task('static-images', function(cb) {
    return clean(config.staticOutputDir + '/img/', function() {
        gulp.src([config.imagesDir + '/**/*',])
        .pipe(gulp.dest(config.staticOutputDir + '/img/'))
        .on('end', cb || function() {});
    });
});

gulp.task('watch', function() {
    plugins.livereload.listen();

    gulp.watch(config.sassPath + '/**/*.scss', ['sass', 'ng-index']);
    gulp.watch(config.ngAppPath + '/**/*', ['ng-index']);
    gulp.watch(config.jsDir + '/**/*.js', ['js-app']);
});

function clean(relativePath, cb) {
  plugins.util.log('Cleaning: ' + plugins.util.colors.blue(relativePath));

  del([config.staticOutputDir + relativePath, ]).then(cb || function() {});
}

gulp.task('default');
gulp.task('build', ['js-app', 'ng-index', 'static-images', 'static-error-pages', 'static-misc']);
gulp.task('deploy', ['icons-vendor', 'js-ng-vendor', 'js-vendor', 'js-app', 'ng-index', 'static-images', 'static-error-pages', 'static-misc']);
