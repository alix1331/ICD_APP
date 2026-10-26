// VIDEO

$(function() {
  // Auto play modal videoModal
  $(".video").click(function() {
    var theModal = $(this).data("target"),
    videoSRC = $(this).attr("data-video"),
    videoSRCauto = videoSRC + "?modestbranding=1&rel=0&controls=0&showinfo=0&html5=1&autoplay=1";
    $(theModal + ' iframe').attr('src', videoSRCauto);
    $(theModal + ' button.close').click(function() {
      $(theModal + ' iframe').attr('src', videoSRC);
    });
  });
});



// LIGHTBOX

$(document).on('click', '[data-toggle="lightbox"]', function(event) {
  event.preventDefault();
  $(this).ekkoLightbox();
});



// TESTIMONIALS
// Only runs when the slick plugin is loaded and the page has a slider.
// (Without this guard the page throws "slick is not a function" on every load.)

if ($.fn.slick && $('.slider').length) {
  $('.slider').slick({
    infinite: true,
    slidesToShow: 1,
    slidesToScroll: 1
  });
}

// Tooltip
$(function () {
  if ($.fn.tooltip) {
    $('[data-toggle="tooltip"]').tooltip();
  }
});



// Copy the text of a table cell to the clipboard.
// The cell id is "<record id> cp" (see index.html).
function CopyText2(el) {
  var cell = document.getElementById(el + " cp");
  if (!cell) {
    return;
  }
  // Visible text only: no <span class="highlight"> markup, no HTML entities,
  // no leading/trailing white space from the template.
  var text = cell.innerText.trim();

  function listener(e) {
    e.clipboardData.setData("text/plain", text);
    e.preventDefault();
  }
  document.addEventListener("copy", listener);
  document.execCommand("copy");
  document.removeEventListener("copy", listener);
}



// Page loading spinner (only on pages that have a .spinner-wrapper element)

var spinnerWrapperEl = document.querySelector('.spinner-wrapper');
if (spinnerWrapperEl) {
  window.addEventListener("load", function () {
    spinnerWrapperEl.style.opacity = '0';
    setTimeout(function () {
      spinnerWrapperEl.style.display = "none";
    }, 200);
  });
}



// Increase Fontsize
function toggleFontSize(tagName, newSize) {
  var elements = document.getElementsByTagName(tagName);
  for (var i = 0; i < elements.length; i++) {
    if (elements[i].style.fontSize === '') {
      elements[i].style.fontSize = newSize;
    } else {
      elements[i].style.fontSize = '';
    }
  }
}