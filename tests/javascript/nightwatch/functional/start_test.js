module.exports = {
  "Start page" : function (browser) {
    browser
      .url(browser.launch_url)
      .assert.containsText('h2', 'Congratulations on your first Django-powered page')
  },
};
