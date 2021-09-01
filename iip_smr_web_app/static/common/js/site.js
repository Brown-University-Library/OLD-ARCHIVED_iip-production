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


(function($) {
  $("body").addClass("loading");
  $(window).load(function() {
    $("body").addClass("is-loaded");
    $("body").removeClass("loading");

    // init headroom
    var headerEl = document.querySelector("header");
    if (headerEl) {
      var headroom = new Headroom(headerEl);
      headroom.init();
    }

    // initial page scroll state
    if (window.pageYOffset > 0) {
      headerEl.classList.add('headroom--not-top');
    }

    $('.showMenuButton').on('click', function(e) {
      $('header').addClass('-menuVisible');
    });

    $('.hideMenuButton').on('click', function(e) {
      $('header').removeClass('-menuVisible');
    });

    $('.headerExternalButtonSearchFocusInput').on('click', function(e) {
      $('#search_form input').focus();
    });

    $('.toggleDescriptionButton').on('click', function(e) {
      $('.shortDescription').hide();
      $('.longDescription').show();
    });

    $(document).keyup(function(e) {
      if (e.key === "Escape") {
        $('header').removeClass('-menuVisible');
      }
    });

    $('#search_form').submit(function(e) {
      e.preventDefault();
      var input = $('#header_external_search').val()
      window.location.replace(`/search/?s=${input.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;')}`);
    });

    var textSearchVal = getQueryVariable('s');
    if (textSearchVal && textSearchVal.length) {
      $('#header_external_search').val(textSearchVal);
    }

    $(".-categoriesMenu a").on("click", function(e) {
      var $target = $(e.target);
      var $parent = $target.closest('li');
      e.preventDefault();

      if (!$parent || $target.hasClass('active')) {
        return null;
      }

      var categoryClass = $parent[0].className.split('_')[1];
      $(".-horizontalList-category").addClass('-hidden');
      $(`.-horizontalList-category.-horizontalList_${categoryClass}`).removeClass('-hidden');
      $(".-categoriesMenu .active").removeClass('active');
      $parent.addClass('active');
    });

    $(".-volumesMenu a").on("click", function(e) {
      var $target = $(e.target);
      var $parent = $target.closest('li');
      e.preventDefault();

      if (!$parent) {
        return null;
      }

      var volumeClass = $parent[0].className.split('-')[2];
      $(".-horizontalList-volume").addClass('-hidden');
      $(`.-horizontalList-volume.-horizontalList_${volumeClass}`).removeClass('-hidden');
      $(".-volumesMenu .active").removeClass('active');
      $parent.addClass('active');
    });

    // initial volumes state (make not static in the future)
    if ($(".-volumesMenu").length) {
      $(".-horizontalList-volume.-horizontalList_volume_8").removeClass('-hidden');
      $(".-menuItem-volume_8").addClass('active');
    }

    const initSidebarStick = () => {
      if ($("#main_sidebar").length) {
        const sidebar1 = new StickySidebar('#main_sidebar', {
          topSpacing: 0,
          bottomSpacing: 0,
          resizeSensor: true,
        });
      }
      if ($("#main_sidebar_secondary").length) {
        const sidebar2 = new StickySidebar('#main_sidebar_secondary', {
          topSpacing: 0,
          bottomSpacing: 0,
          resizeSensor: true,
        });
      }
    };

    const removeSidebarStick = () => {
      // TODO: reimplement this with new sticky sidebar package
      // $("#sidebar").unstick();
    };

    if (window.innerWidth > 990) {
      setTimeout(() => {
        initSidebarStick();
      }, 300);
    }

    $(window).resize(() => {
      if (window.innerWidth > 990) {
        initSidebarStick();
      } else {
        removeSidebarStick();
      }
    });

    window.downloadPDF = () => {
      $(".lazyload")
        .removeClass("lazyload")
        .addClass("lazyloaded");
      // window.scrollTo(0,document.body.scrollHeight);
      setTimeout(() => {
        // window.scrollTo(0,0);
        window.print();
      }, 1000);
    };
    if (window.location.hash === "#download") {
      window.downloadPDF();
    }

    setTimeout(() => {
      if ($('body').hasClass('home')) {
        $('.background').plaxify({
          "xRange": 20,
          "yRange": 20
        });
        $('.middle').plaxify({
          "xRange": 10,
          "yRange": 10,
          invert: true
        });
        $('.foreground').plaxify({
          "xRange": 5,
          "yRange": 5,
          invert: true
        });
        $.plax.enable();
      } else if ($('body').hasClass('error404')) {
        $('.left').plaxify({
          "xRange": 40,
          "yRange": 40,
          invert: true
        });
        $('.middle').plaxify({
          "xRange": 0,
          "yRange": 0,
          invert: true
        });
        $('.right').plaxify({
          "xRange": 20,
          "yRange": 20,
        });
        $.plax.enable();
      }
    }, 300);

  });


  $('.redesignDismiss').on('click', (e) => {
    e.preventDefault();
    setCookie('redesignFeedbackDismissed', true, 365);
    $('.redesignFeedback').addClass('-hidden');
    $('.crisp-client').addClass('-hidden');
  });

  if (getCookie('redesignFeedbackDismissed') !== "true") {
    $('.redesignFeedback').removeClass('-hidden');
    $('.crisp-client').removeClass('-hidden');
  } else {

    // use crisp api in the future
    setTimeout(() => {
      $('.crisp-client').addClass('-hidden');
    }, 500)
    setTimeout(() => {
      $('.crisp-client').addClass('-hidden');
    }, 1000)
    setTimeout(() => {
      $('.crisp-client').addClass('-hidden');
    }, 2000)
    setTimeout(() => {
      $('.crisp-client').addClass('-hidden');
    }, 4000)
    setTimeout(() => {
      $('.crisp-client').addClass('-hidden');
    }, 10000)
    setTimeout(() => {
      $('.crisp-client').addClass('-hidden');
    }, 20000)
  }


  $(document).on("click", ".accordionMenuToggle", (e) => {
    let $target = $(e.target);
    let parent;


    e.preventDefault();

    if (!$target.hasClass('accordionMenuToggle')) {
      $target = $target.parent('.accordionMenuToggle');
    }

    $parent = $target.parent('.accordionMenuItem');
    $parent.find('.accordionMenu').toggleClass('-hidden');
    $parent.toggleClass('-toggled');
  });

  $(document).on("click", ".tab", (e) => {
    let $target = $(e.target);
    const tabData = $target.data('tabname');

    e.preventDefault();

    $('.tab').removeClass('-active');
    $target.addClass('-active');

    if (tabData) {
      $(".homepageContentFeed").addClass('-hidden');
      $(`.homepageContentFeed.-feed-${tabData}`).removeClass('-hidden');
    }
  });


  $(".showMoreClassicsAtIssues").on("click", (e) => {
    e.preventDefault();
    $(".olderIssues").removeClass("-hidden");
  });

  $("#accordion-section-custom_css").hide();

  /*
   * Open and close the share dropdown menu
   */
  $(".-shareButton").on("click", (e) => {
    e.preventDefault();
    $("#book_share_links").show();
  });
  $(document).on("click", (e) => {
    const $target = $(e.target);
    if (!$target.hasClass("-shareButton") && !$target.parents('.-shareButton').length) {
      $("#book_share_links").hide();
    }
  });

  /*
   * Add or remove a book from the Saved Bookshelf
   */
  $(".-saveButton").on("click", (e) => {
    e.preventDefault();
    if ($('.-saveButton').hasClass('-bookIsSaved')) {
      $(".saveButtonText").text('Save');
    } else {
      $(".saveButtonText").text('Saved');
    }
    $(".-saveButton").toggleClass('-bookIsSaved');

    const bookID = $("#bookID").data().id;

    $.post('/wp-json/chs/v1/bookshelf', {
      bookID,
      _wpnonce: chsScriptVars.nonce,
    }, (res) => {
      console.log(res);
    });
  });

  /*
   * Show more posts on homepage
   */
  $(".moreFrom a").on("click", (e) => {
    e.preventDefault();
    $('.-teaseHidden').removeClass('-teaseHidden');
    $('.moreFrom').hide();
  });

  /*
   * workaround for saving a nonce for react
   */
  window.__iip__.nonce = chsScriptVars.nonce;
})(jQuery);
