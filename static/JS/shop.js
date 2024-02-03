// console.log("I am come!!")
// document.addEventListener("DOMContentLoaded", function(){
//     // const cartSection = document.getElementsByClassName('.cart-section');
//     const shopCartLink = document.querySelector('.shop-cart-link');

//     shopCartLink = document.addEventListener('click', function(){
//         console.log('here')
//     })
// });

// var element = document.getElementsByClassName('.shop-cart-link');
// function toggleDisplay() {
//     var display = element.style.display;
//     if (display == 'none') {
//         element.style.display = 'block'
//     } else {
//         element.style.display = 'none'
//     }
// }
// element.addEventListener('click', toggleDisplay);
var elements = document.getElementsByClassName('shop-cart-link');

function toggleDisplay() {
    // Assuming there is only one element, use [0] to access it
    var element = elements[0];

    var display = element.style.display;
    if (display == 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

// Loop through the elements and add an event listener to each one
for (var i = 0; i < elements.length; i++) {
    elements[i].addEventListener('click', toggleDisplay);
}