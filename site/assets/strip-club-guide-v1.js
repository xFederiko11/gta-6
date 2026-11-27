(function () {
  "use strict";
  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-strip-video-load]");
    if (!button) return;
    var videoId = button.getAttribute("data-video-id") || "";
    if (!/^[A-Za-z0-9_-]{11}$/.test(videoId)) return;
    var frame = document.createElement("iframe");
    frame.src = "https://www.youtube-nocookie.com/embed/" + videoId + "?autoplay=1&rel=0";
    frame.title = "GTA 6: le tre location — video GTAAccess";
    frame.loading = "lazy";
    frame.referrerPolicy = "strict-origin-when-cross-origin";
    frame.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    frame.allowFullscreen = true;
    button.replaceWith(frame);
  });
})();
