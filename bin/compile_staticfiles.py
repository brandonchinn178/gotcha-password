import sass

sass.compile(
    dirname=('gotcha_password/static/sass', 'gotcha_password/static/css'),
    output_style='compressed',
)
