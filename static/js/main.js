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

$('.slider').slick({
  infinite:true,
  slideToShow: 1,
  slidesToScroll: 1
});

// Tooltip
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

//  // Copy to ClipBoard
// function CopyText(el) {
// // concat the id to our string `${el} cp`  or el + ' cp'
//  var copyText = document.getElementById(`${el} cp`)
//  console.log(copyText)
//    // Select the text field
//  copyText.select();
//  copyText.setSelectionRange(0, 99999); // For mobile devices
//
//   // Copy the text inside the text field
//  navigator.clipboard.writeText(copyText.value);
//};
//
//    // Copy to ClipBoard
 function CopyText2(el) {
 // concat the id to our string `${el} cp`  or el + ' cp'
  var copyText = document.getElementById(`${el} cp`)
  var str = copyText.innerHTML
   function listener(e) {
    e.clipboardData.setData("text/html", str);
    e.clipboardData.setData("text/plain", str);
    e.preventDefault();
  }
  document.addEventListener("copy", listener);
  document.execCommand("copy");
  document.removeEventListener("copy", listener);
};
//
//// none: Hide
//function ToggleText(el){
//    var x = document.getElementById(el);
//          if (x.style.display === "none") {
//            x.style.display = "block";
//          } else {
//            x.style.display = "none";
//          }
//}

// Hide and Show Element on Click


const spinnerWrapperEl = document.querySelector('.spinner-wrapper');
    window.addEventListener("load", ()=>{
    spinnerWrapperEl.style.opacity = '0';
    setTimeout(()=>{
    spinnerWrapperEl.style.display = "none";
     },200);
});

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

