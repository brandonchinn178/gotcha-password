module.exports = function (grunt) {
    grunt.loadNpmTasks("grunt-contrib-sass");
    grunt.loadNpmTasks("grunt-contrib-watch");

    grunt.initConfig({
        sass: {
            dist: {
                options: {
                    style: "compressed",
                },
                files: [{
                    expand: true,
                    cwd: "gotcha_password/static/sass",
                    src: "**/*.scss",
                    dest: "gotcha_password/static/css",
                    ext: ".css",
                }]
            }
        },
        watch: {
            sass: {
                files: "gotcha_password/static/sass/**/*.scss",
                tasks: "sass",
            }
        }
    });

    grunt.registerTask("build", ["sass"]);
    grunt.registerTask("default", ["build", "watch"]);
};