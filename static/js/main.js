(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Initiate the wowjs
    new WOW().init();


    // Fixed Navbar
    $(window).scroll(function () {
        if ($(window).width() < 992) {
            if ($(this).scrollTop() > 45) {
                $('.fixed-top').addClass('bg-white shadow');
            } else {
                $('.fixed-top').removeClass('bg-white shadow');
            }
        } else {
            if ($(this).scrollTop() > 45) {
                $('.fixed-top').addClass('bg-white shadow').css('top', -45);
            } else {
                $('.fixed-top').removeClass('bg-white shadow').css('top', 0);
            }
        }
    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


   // Testimonials carousel (compact + unique style)
$(".testimonial-carousel").owlCarousel({
    autoplay: true,
    autoplayTimeout: 5000,
    smartSpeed: 500,
    margin: 10,
    loop: true,
    center: false,          // ❌ no center highlighting
    dots: true,             // ✔ use dots instead of arrows
    nav: false,             // ❌ remove arrows to avoid looking like donor slider
    responsive: {
        0:{
            items:2
        },
        768:{
            items:2        // ❗ Always show one testimonial at a time
        },
        992:{
            items:2
        }
    }
});

    $(".news-carousel").owlCarousel({
    autoplay: true,
    autoplayTimeout: 3500,     // slower rotation
    smartSpeed: 600,           // smoother slide, not snappy like testimonials
    margin: 15,                // smaller gap
    loop: true,
    dots: true,
    nav: true,                 // add arrows to make it feel different
    navText: [
        '<i class="fa fa-chevron-left"></i>',
        '<i class="fa fa-chevron-right"></i>'
    ],
    responsive: {
        0: { items: 1 },
        576: { items: 1 },
        768: { items: 2 },
        992: { items: 3 }
    }
});

})(jQuery);

