document.addEventListener("DOMContentLoaded", function() {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];  // Get the cart from localStorage

    const cartItemsContainer = document.getElementById("cart-items");
    const totalItemsSpan = document.getElementById("total-items");
    const totalPriceSpan = document.getElementById("total-price");
    const grandTotalSpan = document.getElementById("grand-total");

    // Function to update the cart display
    function updateCartDisplay() {
        cartItemsContainer.innerHTML = '';  // Clear the container before rendering
        let totalPrice = 0;

        cart.forEach((item, index) => {
            const itemElement = document.createElement('div');
            itemElement.classList.add('cart-item');
            itemElement.innerHTML = `
                <img src="${item.image}" alt="${item.title}" class="cart-item-image">
                <div class="cart-item-details">
                    <h3>${item.title}</h3>
                    <p><strong>By:</strong> ${item.author}</p>
                    <p><strong>Price:</strong> ₹${item.price}</p>
                </div>
                <div class="cart-item-actions">
                    <button class="remove-btn" data-index="${index}">Remove</button>
                </div>
            `;

            // Add to the total price
            totalPrice += item.price;

            cartItemsContainer.appendChild(itemElement);
        });

        // Update cart summary
        totalItemsSpan.textContent = cart.length;
        totalPriceSpan.textContent = totalPrice;
        const shipping = totalPrice > 500 ? 0 : 50;
        grandTotalSpan.textContent = totalPrice + shipping;
    }

    

    // Event listener for removing items from the cart
    cartItemsContainer.addEventListener('click', function(event) {
        const target = event.target;

        if (target.classList.contains('remove-btn')) {
            const index = target.getAttribute('data-index');
            cart.splice(index, 1);  // Remove the item from the cart
            localStorage.setItem("cart", JSON.stringify(cart));  // Update the cart in localStorage
            updateCartDisplay();  // Re-render the cart
        }
    });

    updateCartDisplay();  // Initial display of cart items
});
