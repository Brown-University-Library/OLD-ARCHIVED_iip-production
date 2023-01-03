function getQueryVariable(variable) {
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i = 0; i < vars.length; i++) {
    var pair = vars[i].split("=");
    if (pair[0] == variable) {
      return pair[1];
    }
  }
  return (false);
}

function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

function eraseCookie(name) {
  document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

const initSite = () => {
  $(document).on("click", ".accordionMenuToggle", (e) => {
    let $target = $(e.target);
    let parent;
    e.preventDefault();

    if (!$target.hasClass('accordionMenuToggle')) {
      $target = $target.parent('.accordionMenuToggle');
    }

    $parent = $target.parent('.accordionMenuItem');
    $parent.find('.accordionMenu').toggleClass('hidden');
    $parent.toggleClass('-toggled');
  });
};

(function($) {
  $("body").addClass("loading");
  $(window).load(function() {
    $("body").addClass("is-loaded");
    $("body").removeClass("loading");
    initSite();
  });
})(jQuery);
