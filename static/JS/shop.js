//function toggle cart when shopping cart icon is clicked
// DomContentLoaded ensure pages isloaded before JavaScript can Execute
document.addEventListener('DOMContentLoaded', function() {
    let iconCart = document.querySelector('.shop-cart-container');
    let body = document.querySelector('body');

    iconCart.addEventListener('click', () => {
        body.classList.toggle('showCart');
    });

    // removing items from cart
    var removeCartItemButtons = document.getElementsByClassName('remove-btn') // loop over all buttons in the cart and add an event listner for whatever index the button is currently on
    for (i = 0; i < removeCartItemButtons.length; i++) {
        var button = removeCartItemButtons[i]
        button.addEventListener('click', removeCartItem) //call the function on a click event
}
// update total when quantity value changes by listening for change event
    var quantityInputs = document.getElementsByClassName('cart-quantity-input')
    for (i = 0; i < quantityInputs.length; i++) {
        var input = quantityInputs[i]
        input.addEventListener('change', quantityChanged) //call a change function on cart-quantity-input class
    }
    var addToCartButtons = document.getElementsByClassName('shop-item-button')
    for (i = 0; i < addToCartButtons.length; i++) {
        var cartButton = addToCartButtons[i]
        cartButton.addEventListener('click', addToCart)
    }
// alert user when purchase button is clicked and clear the cart
    document.getElementsByClassName('btn-purchase')[0].addEventListener('click', purchaseComplete)

function purchaseComplete(){
    alert('Thank you for your purchase')
    var cartItems = document.getElementsByClassName('cart-items')[0]  //get all rows from our cart-items class
    while (cartItems.hasChildNodes()){                                 //if the cart still has any children 'rows' keep running until they are all removed
        cartItems.removeChild(cartItems.firstChild)
    }
    updateCartTotal()   //update total once everything is removed from cart

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
    }
// function to remove item from the cart
    function removeCartItem(event) {
        var buttonClicked = event.target
            buttonClicked.parentElement.parentElement.remove()
            updateCartTotal()
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



});




