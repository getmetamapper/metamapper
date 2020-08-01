// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

let shouldSkip = false;

module.exports = (on, config) => {
  // https://stackoverflow.com/questions/58657895/is-there-a-reliable-way-to-have-cypress-exit-as-soon-as-a-test-fails
  on('task', {
    resetShouldSkipFlag () {
      shouldSkip = false;
      return null;
    },
    shouldSkip ( value ) {
      if ( value != null ) shouldSkip = value;
      return shouldSkip;
    }
  });

  on('before:browser:launch', (browser = {}, args) => {
    if (browser.name === 'chrome') {
      args.push('--disable-dev-shm-usage')
      return args
    }

    return args
  })

  require('cypress-log-to-output').install(on, (type, event) => {
    if (event.level === 'error' || event.type === 'error') {
      return event.url.indexOf('https://www.gravatar.com/avatar') < 0
    }

    if (event.level === 'log' || event.type === 'log') {
      return true
    }

    return false
  })
}
