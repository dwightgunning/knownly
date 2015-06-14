var gulp = require('gulp'),
    sass = require('gulp-ruby-sass') 
    notify = require('gulp-notify') 
    bower = require('gulp-bower');

var config = {
     sassPath: './static/sass',
     bowerDir: './bower_components' 
}

gulp.task('bower', function() { 
    return bower()
         .pipe(gulp.dest(config.bowerDir)) 
});

gulp.task('icons', function() { 
    return gulp.src(config.bowerDir + '/fontawesome/fonts/**.*') 
        .pipe(gulp.dest('static/fonts')); 
});

gulp.task('css', function() { 
    return sass(config.sassPath, {
             style: 'compressed',
             loadPath: [
                 './resources/sass',
                 config.bowerDir + '/bootstrap-sass-official/assets/stylesheets',
                 config.bowerDir + '/fontawesome/scss',
             ]
         }) 
        .on('error', notify.onError(function (error) {
            return 'Error: ' + error.message;
            })
        )
    .pipe(gulp.dest('static/css'));
});

// Rerun the task when a file changes
 gulp.task('watch', function() {
     gulp.watch(config.sassPath + '/**/*.scss', ['css']); 
});

  gulp.task('default', ['bower', 'icons', 'css']);
