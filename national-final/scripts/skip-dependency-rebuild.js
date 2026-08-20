'use strict';

// Runtime browser assets are vendored under renderer/vendor. The application
// has no native Node dependencies, so electron-builder must not install or
// rebuild node_modules while creating the portable package.
module.exports = async () => false;
