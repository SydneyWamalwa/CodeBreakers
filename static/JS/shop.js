
// load the paystack api outside the DOM to ensure their scope is global and can be accessed from anywhere in the code.
function openPaymentModal() {
var modal = document.getElementById('paymentModal');
modal.style.display = 'block';
}
                                                                            /*this two functions are responsible for the email popup display*/
function closePaymentModal() {
var modal = document.getElementById('paymentModal');
modal.style.display = 'none';
}
function getUserEmail() {
    const userEmailInput = document.getElementById('email');
    return userEmailInput.value;
}

function processPayment() {
// Get the email entered by the user
const userEmail = getUserEmail()

// Close the payment modal
closePaymentModal()
// Make an AJAX request to Flask to generate a unique reference
fetch('/generate-reference', {                                                              //this is used to create a unique id for each transaction
    method: 'POST'
})
.then(response => response.json())
.then(data => {
    // Use the fetched reference number to make the payment through the Paystack API
    var reference = data.reference;

    // Perform payment processing logic using Paystack API and the total amount
    // var totalAmount = parseFloat(document.querySelector('.cart-total-price').innerText.replace('Ksh.', '').trim());
    // console.log(totalAmount)

    // Now you can use the userEmail, totalAmount, and reference to make the payment through the Paystack API
    var paystackPayload = {
        key: 'pk_test_72adfba481a29bf8d587280ca7d96002ac4210c4', // Your test public key
        email: userEmail,
        amount: total * 100, // Amount must be in kobo. the total variable is calculated when we calculated cart-item-total
        currency: 'KES',
        ref: reference, // Use the fetched reference number
        metadata: {
            custom_fields: [
                {
                    display_name: 'Cart Total',
                    variable_name: 'cart_total',
                    value: total
                }
            ]
        },
        callback: function(response) {
            console.log(response);
            var reference = response.reference
                purchaseComplete()
                closePaymentModal()

                alert('Payment Successful!!!' + reference);

            // handle further actions here, such as updating order status
        },
        onClose: function () {
            alert('Payment window closed without completion');
        }
    };

    // Initialize Paystack with the payload
    var handler = PaystackPop.setup(paystackPayload);
    handler.openIframe();
})
.catch(error => console.error('Error:', error));
}


// Validate email function
// function validateEmail(email) {
// var regex = /\S+@\S+\.\S+/;
// return regex.test(email);
// }


// DomContentLoaded ensure pages isloaded before JavaScript can Execute
document.addEventListener('DOMContentLoaded', function() {


// event listner to process paymentonce proceed to purchase button is clicked
    document.getElementById('purchaseBtn').addEventListener('click', function () {
        // Display the payment modal when the button is clicked
        openPaymentModal();
    });



    //function toggle cart when shopping cart icon is clicked
    let iconCart = document.querySelector('.shop-cart-container');
    let body = document.querySelector('body');
    iconCart.addEventListener('click', addCartToBody)

    // removing items from cart event listener
    var removeCartItemButtons = document.getElementsByClassName('remove-btn') // loop over all buttons in the cart and add an event listner for whatever index the button is currently on
    for (i = 0; i < removeCartItemButtons.length; i++) {
        var button = removeCartItemButtons[i]
        button.addEventListener('click', removeCartItem) //call the function on a click event
}

// quantity change event listener
// update total when quantity value changes by listening for change event
    var quantityInputs = document.getElementsByClassName('cart-quantity-input')
    for (i = 0; i < quantityInputs.length; i++) {
        var input = quantityInputs[i]
        input.addEventListener('change', quantityChanged) //call a change function on cart-quantity-input class
    }

    // This function uses the quantity input variable in line 113 to get quantityInputs
    // function to update the number inside the shopping cart with total number of products everytime the quanity changes.
    function updateCartCount(){
        var totalCount= 0
        for (var i = 0; i < quantityInputs.length; i++ ){             // loop over all the quantity rows in quantity and increase total with whatever the current quantity for the row is
            totalCount += parseInt(quantityInputs[i].value)
        }
        document.querySelector('.shop-items-count').innerText = totalCount
    }


// add to cart event listener
    var addToCartButtons = document.getElementsByClassName('shop-item-button')
    for (i = 0; i < addToCartButtons.length; i++) {
        var cartButton = addToCartButtons[i]
        cartButton.addEventListener('click', addToCart)
    }
// alert user when purchase button is clicked and clear the cart
    document.getElementsByClassName('btn-purchase')[0].addEventListener('click', purchaseComplete)
    // updateCartTotal()   //update total once everything is removed from cart
    // updateCartCount()
    // openPaymentModal();



function purchaseComplete(){
    // alert('Thank you for your purchase')
    openPaymentModal();
    var cartItems = document.getElementsByClassName('cart-items')[0]  //get all rows from our cart-items class
    while (cartItems.hasChildNodes()){                                 //if the cart still has any children 'rows' keep running until they are all removed
        cartItems.removeChild(cartItems.firstChild)

    }
    // updateCartTotal()   //update total once everything is removed from cart
    // updateCartCount()
    //update cart count

}
//function toggle cart when shopping cart icon is clicked
function addCartToBody(){
    body.classList.toggle('showCart');     //use this class in css to style
}


    // function to add items to cart
    function addToCart(event){
        var button = event.target
        // get parent element of our items. Top level in our nested elements
        var shopItem = button.parentElement.parentElement
        // extract necessary columns using their class names
        var title = shopItem.getElementsByClassName('shop-item-description')[0].innerText.replace('Description:', '')
        var price = shopItem.getElementsByClassName('shop-item-price')[0].innerText.replace('Price:', '')
        var imageSrc = shopItem.getElementsByClassName('shop-item-image')[0].src //get the omage source for our images
        addItemToCart(title, price, imageSrc)
        updateCartTotal()
    }

// add items for purchase to cart
    function addItemToCart(title, price, imageSrc){
        var cartRow = document.createElement('div') //create new element to hold our items
        cartRow.classList.add('cart-row') //add this class to enable same formatting in css

        var cartItems = document.getElementsByClassName('cart-items')[0]  //get the class holding all rows
        var cartItemNames = cartItems.getElementsByClassName('cart-item-title')
        for(var i = 0; i < cartItemNames.length; i++) {
            if (cartItemNames[i].innerText.trim().toLowerCase() === title.trim().toLowerCase()) { //trim whitespaces and convert to lower case for comparision
                alert('This item is already added to the cart')
                return
            }
        }
        // create a new row for every new element added and pass variable names
        var cartRowContents = `
            <div class="cart-item cart-column">
                <img class="cart-item-image" src="${imageSrc}" width="100" height="100" alt="product">
                <span class="cart-item-title">${title}</span>
            </div>
            <div class="cart-item cart-column">
                <span class="cart-item-color">black</span>
            </div>
            <div class="cart-quantity cart-column">
                <input class="cart-quantity-input" type="number" value="1">
            </div>

            <div class="cart-item-price-button cart-item cart-column">
                <span class="cart-column cart-price-details" >${price}</span><!--cart-price removed -->
                <button class=" remove-btn btn-danger" type="button">REMOVE</button>
            </div>`
        cartRow.innerHTML = cartRowContents  // call innerHTML method since we are passing actual HTML tags
        cartItems.appendChild(cartRow) //add the new row to cart-items element
        // our DOMContentLoaded only recognize events that were there when page was first loaded. any buttons added after that wont work. we add another click event to remove the newly added rows from our cart
        updateCartCount()

        cartRow.getElementsByClassName('remove-btn')[0].addEventListener('click', removeCartItem)
        // change quantity when new row's quantity changes
        cartRow.getElementsByClassName('cart-quantity-input')[0].addEventListener('change', quantityChanged)
    }
    // quantity change function
    function quantityChanged(event){
        var input = event.target
        if (isNaN(input.value) || input.value <= 0) { //number must be a valid integer and not < 1
            input.value = 1
        }
        updateCartTotal() //change the total cost depending on quantity change
        updateCartCount() //call the update cart function when the quantity changes.
    }
// function to remove item from the cart
    function removeCartItem(event) {
        var buttonClicked = event.target
            buttonClicked.parentElement.parentElement.remove()
            updateCartTotal()
            updateCartCount()
    }
// function to update the cart total
    function updateCartTotal() {
    // cart-items is the container class for all our rows. access it and get the very first element from the list[0]
        var cartItemContainer = document.getElementsByClassName('cart-items')[0]

        // inside items class get all the rows
        var cartRows = cartItemContainer.getElementsByClassName('cart-row')
        total = 0
        // loop over cart-rows. we only need quantity and price columns
        for (i = 0; i < cartRows.length; i++) {
            var cartRow = cartRows[i] //get a single row from the item rows

            // get the price and quantity elements from the row using their class names. get the very first one.
            var priceElement = cartRow.getElementsByClassName('cart-price-details')[0]
            var quantityElement = cartRow.getElementsByClassName('cart-quantity-input')[0]

            // extract the text from an element using innertext. use replace to get rid of currency and float to convert to number
            var price = parseFloat(priceElement.innerText.replace('Ksh.', ''))
            var quantity = quantityElement.value
            total = total + (price * quantity)
        }
        total = Math.round(total * 100) / 100
        // get the cart total using its class name and change its text to above total using innertext
        document.getElementsByClassName('cart-total-price')[0].innerText = 'Ksh.' + total
    }
updateCartCount()   //initialize our shopping count function


});




