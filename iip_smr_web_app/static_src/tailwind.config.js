/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  /**
   * Stylesheet generation mode.
   *
   * Set mode to "jit" if you want to generate your styles on-demand as you author your templates;
   * Set mode to "aot" if you want to generate the stylesheet in advance and purge later (aka legacy mode).
   */
  mode: "aot",

  purge: [
    /**
     * HTML. Paths to Django template files that will contain Tailwind CSS classes.
     */

    /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
    '../templates/**/*.twig',
    '../templates/**/*.html',

    /*
     * Main templates directory of the project (BASE_DIR/templates).
     * Adjust the following line to match your project structure.
     */
    '../../templates/**/*.twig',

    /*
     * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
     * Adjust the following line to match your project structure.
     */
    '../../**/templates/**/*.twig',

    /**
     * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
     * patterns match your project structure.
     */
    /* JS 1: Ignore any JavaScript in node_modules folder. */
    '!../../**/node_modules',
    /* JS 2: Process all JavaScript files in the project. */
    // '../../**/*.js',

    /**
     * Python: If you use Tailwind CSS classes in Python, uncomment the following line
     * and make sure the pattern below matches your project structure.
     */
    // '../../**/*.py'
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        transparent: 'transparent',
        primary: '#87806C',
        secondary: '#666256',
        light: '#F2EEEA',
        accent: '#959A92',
        'theme-100': '#F2EEEA',
        'theme-200': '#E4E1D9',
        'theme-gray': '#C7C7C7',
        'theme-500': '#87806C',
        'theme-700': '#666256',
        'theme-800': '#353431',
        'theme-900': '#1A1919',
      },
      fontFamily: {
        sans: ['Staff Light', ...defaultTheme.fontFamily.sans],
        sans_bold: ['Staff Medium ', ...defaultTheme.fontFamily.sans],
        serif: ['Silk Serif', ...defaultTheme.fontFamily.serif],
      },
      height: {
        '160': '40rem',
        '19/20': '95vh',
      },
      minWidth: {
        '96': '24rem',
      },
      minHeight: {
        '190': '50rem',
      },
      cursor: {
        'zoom-in': 'zoom-in',
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [
    /**
     * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
     * for forms. If you don't like it or have own styling for forms,
     * comment the line below to disable '@tailwindcss/forms'.
     */
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/line-clamp'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
