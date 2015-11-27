/* jshint node: true */
'use strict';

var gulp    = require('gulp'),
    path    = require('path'),
    plugins = require('gulp-load-plugins')({
        lazy: false}),
    del     = require('del'),
    dotenv = require('dotenv');

dotenv.config();

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
          .pipe(plugins.size({title: '\t File size [index.html]',  showFiles: true }))
          .pipe(gulp.dest(config.staticOutputDir + '/'))
          .pipe(plugins.livereload())
          .on('end', cb || function() {});
    });
});

gulp.task('ng-templates', function(cb) {
    plugins.util.log('Building angular templates');

    return clean('/js/templates*+(.js|.map)', function() {
        gulp.src(config.ngAppPath + '/scripts/components/**/*.html')
          .pipe(plugins.plumber({errorHandler: onError}))
          .pipe(plugins.angularTemplatecache({
            root:   'components/',
            module: 'knownlyApp'
          }))
          .pipe(gulp.dest(config.staticOutputDir + '/js'))
          .pipe(plugins.sourcemaps.init())
          .pipe(plugins.streamify(plugins.rev()))
          .pipe(plugins.size({title: '\t File size [ng-templates]',  showFiles: true }))
          .pipe(plugins.sourcemaps.write('./'))
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
        .pipe(plugins.size({title: '\t File size [Icons]'}))
        .pipe(gulp.dest(config.staticOutputDir + '/fonts/'))
        .on('end', cb || function() {});
    });
});

gulp.task('js-vendor', function(cb) {
    return clean('/js/knownly-vendor*+(.js|.map)', function() {
        gulp.src([
            config.bowerDir + '/jquery/dist/jquery.min.js',
            config.bowerDir + '/bootstrap-sass-official/assets/javascripts/bootstrap.min.js',
            config.bowerDir + '/jquery.easing/js/jquery.easing.min.js',
        ])
        .pipe(plugins.plumber({errorHandler: onError}))
        .pipe(plugins.concat('knownly-vendor.js'))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .pipe(plugins.sourcemaps.init())
        .pipe(plugins.uglify())
        .pipe(plugins.rename({
          extname: '.min.js'
        }))
        .pipe(plugins.size({title: '\t File size [js-vendor]',  showFiles: true }))
        .pipe(plugins.sourcemaps.write('./'))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .on('end', cb || function() {});
    });
});

gulp.task('js-ng-vendor', function(cb) {
    return clean('/js/vendor-*+(.js|.map)', function() {
        return gulp.src([
            config.bowerDir + '/underscore/underscore.js',
            config.bowerDir + '/requirejs/require.js',
            config.bowerDir + '/jquery/dist/jquery.js',
            config.bowerDir + '/angular/angular.js', 
            config.bowerDir + '/angular-cookies/angular-cookies.js',
            config.bowerDir + '/angular-animate/angular-animate.js',
            config.bowerDir + '/angular-ui-router/release/angular-ui-router.js',
            config.bowerDir + '/angular-loader/angular-loader.js',
            config.bowerDir + '/angular-bootstrap/ui-bootstrap.js',
            config.bowerDir + '/angular-bootstrap/ui-bootstrap-tpls.js',
            config.bowerDir + '/jquery.easing/js/jquery.easing.js',
            config.bowerDir + '/mixpanel/mixpanel-jslib-snippet.js',
            config.bowerDir + '/angular-mixpanel/src/angular-mixpanel.js',
        ])
        .pipe(plugins.plumber({errorHandler: onError}))
        .pipe(plugins.concat('vendor.js'))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .pipe(plugins.sourcemaps.init())
        .pipe(plugins.uglify())
        .pipe(plugins.size({title: '\t File size [ng-vendor]:',  showFiles: true }))
        .pipe(plugins.streamify(plugins.rev()))
        .pipe(plugins.sourcemaps.write('./'))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .on('end', cb || function() {});
    });
});

gulp.task('js-ng-app', function(cb) {

    return clean('/js/app-*+(.js|.map)', function() {
        gulp.src([
            config.ngAppPath + '/scripts/directives/**/*.js',
            config.ngAppPath + '/scripts/services/**/*.js',
            config.ngAppPath + '/scripts/components/**/*.js',
            config.ngAppPath + '/scripts/app.js',
            config.jsDir + '/*.js',
        ])
        .pipe(plugins.plumber({errorHandler: onError}))
        .pipe(plugins.sourcemaps.init())
        .pipe(plugins.concat('app.js'))
        .pipe(plugins.preprocess({context: { MIXPANEL_TOKEN: process.env.MIXPANEL_TOKEN }}))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .pipe(plugins.uglify())
        .pipe(plugins.streamify(plugins.rev()))
        .pipe(plugins.sourcemaps.write('./'))
        .pipe(plugins.size({title: '\t File size [ng-app]:', showFiles: true }))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .on('end', cb || function() {});
    });
});

gulp.task('js-app', function(cb) {
    return clean('/js/knownly-app*+(.js|.map)', function() {
        gulp.src([
            config.jsDir + '/*.js',
        ])
        .pipe(plugins.plumber({errorHandler: onError}))
        .pipe(plugins.concat('knownly-app.js'))
        .pipe(gulp.dest(config.staticOutputDir + '/js/'))
        .pipe(plugins.sourcemaps.init())
        .pipe(plugins.uglify())
        .pipe(plugins.rename({
          extname: '.min.js'
        }))
        .pipe(plugins.size({title: '\t File size [js-app]:',  showFiles: true }))
        .pipe(plugins.sourcemaps.write('./'))
        .pipe(gulp.dest(config.staticOutputDir + '/js/')) // Emit non-revision-tagged version for Django templated views
        .pipe(plugins.livereload())
        .on('end', cb || function() {});
    });
});

gulp.task('sass', function(cb) {
    clean('/css/*.css', function() {
        gulp.src(config.sassPath + '/import.scss')
          .pipe(plugins.plumber({errorHandler: onError}))
          .pipe(plugins.sourcemaps.init())
          .pipe(plugins.sass({
              includePaths: [
                config.bowerDir + '/bootstrap-sass-official/assets/stylesheets',
                config.bowerDir + '/fontawesome/scss',
                config.bowerDir + '/hover/scss'],
              outputStyle: 'expanded'
           }))
          .pipe(plugins.rename('knownly.css'))
          .pipe(gulp.dest(config.staticOutputDir + '/css'))
          .pipe(plugins.minifyCss())
          .pipe(plugins.rename('knownly.min.css'))
          .pipe(gulp.dest(config.staticOutputDir + '/css')) // Emit non-revision-tagged version for Django templated views
          .pipe(plugins.streamify(plugins.rev()))
          .pipe(plugins.size({title: '\t File size [CSS]:',  showFiles: true }))
          .pipe(plugins.sourcemaps.write('./'))
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

gulp.task('watch', ['default'], function() {
    plugins.livereload.listen();

    gulp.watch(config.sassPath + '/**/*.scss', ['sass', 'ng-index']);
    gulp.watch(config.ngAppPath + '/**/*+(.js|.html)', ['ng-index']);
    gulp.watch(config.jsDir + '/**/*.js', ['js-app']);
});

function clean(relativePath, cb) {
  plugins.util.log('\t Cleaning: ' + plugins.util.colors.blue(relativePath));

  del([config.staticOutputDir + relativePath, ]).then(cb || function() {});
}

var onError = function (error) {  
  plugins.notify.onError(
    {
      title: "Error", 
      message: "Check your terminal", sound: "Sosumi"
    }
  )(error);
  console.log(error.toString());
  this.emit("end");
};

gulp.task('statics',['icons-vendor',
                          'static-images',
                          'static-error-pages',
                          'static-misc']);


gulp.task('regular-site', ['js-vendor', 'sass', 'js-app']);
gulp.task('angular-site', plugins.sequence('js-ng-vendor', 'ng-index'));
gulp.task('deploy', plugins.sequence(['regular-site', 'angular-site'], 'statics'));
gulp.task('default', ['deploy']);
