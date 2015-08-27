var gulp = require('gulp')
var bower = require('gulp-bower')
var concat = require('gulp-concat')
var notify = require('gulp-notify') 
var sass = require('gulp-ruby-sass')
var rename = require('gulp-rename');

var config = {
    jsDir: './static/js/',
    sassPath: './static/sass/import.scss',
     bowerDir: './bower_components' 
}

gulp.task('bower', function() { 
    return bower().pipe(gulp.dest(config.bowerDir)) 
});

gulp.task('icons', function() { 
    return gulp.src([
        config.bowerDir + '/fontawesome/fonts/**.*',
        config.bowerDir + '/bootstrap-sass-official/assets/fonts/**/*.*']) 
    .pipe(gulp.dest('static/fonts/')); 
});

gulp.task('js', function() {
    return gulp.src([
        config.bowerDir + '/jquery/dist/jquery.min.js',
        config.bowerDir + '/bootstrap-sass-official/assets/javascripts/bootstrap.min.js',
        config.bowerDir + '/jquery.easing/js/jquery.easing.min.js',
        config.jsDir + '/**/*.js',
        '!' + config.jsDir + '/app.js',
    ])
    .pipe(concat('app.js'))
    .pipe(gulp.dest('static/js/')); 
});

gulp.task('css', function() { 
    return sass(config.sassPath, {
        style: 'compressed',
        loadPath: [
              config.bowerDir + '/bootstrap-sass-official/assets/stylesheets',
             config.bowerDir + '/fontawesome/scss',
            config.bowerDir + '/hover/scss',
        ]
    }) 
    .on('error', notify.onError(function(error) {
        return 'Error: ' + error.message;
    }))
    .pipe(rename('knownly.css'))
    .pipe(gulp.dest('static/css'));
});

// Rerun the task when a file changes
 gulp.task('watch', function() {
    gulp.watch(config.sassPath + '/**/*.scss', ['css']); 
});

  gulp.task('default', ['bower', 'icons', 'css', 'js']);
