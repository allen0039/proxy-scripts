// Runs after the bundled OpenCC t2cn.js library in Surge's response-script context.
(function () {
  var originalBody = $response && $response.body;
  if (typeof originalBody !== "string" || !originalBody) {
    $done({});
    return;
  }

  try {
    var subtitle = JSON.parse(originalBody);
    if (!subtitle || !Array.isArray(subtitle.body)) {
      $done({});
      return;
    }

    var convert = OpenCC.Converter({ from: "tw", to: "cn" });
    var changed = false;
    for (var i = 0; i < subtitle.body.length; i++) {
      var line = subtitle.body[i];
      if (!line || typeof line.content !== "string") continue;
      var simplified = convert(line.content);
      if (simplified !== line.content) {
        line.content = simplified;
        changed = true;
      }
    }
    $done(changed ? { body: JSON.stringify(subtitle) } : {});
  } catch (error) {
    // An error response or a changed subtitle format must pass through untouched.
    $done({});
  }
})();
