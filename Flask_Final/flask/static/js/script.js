const dropdown = document.getElementById('dropdown');
dropdown.addEventListener('change', function () {
    const selectedPage = this.value;
    window.location.href = selectedPage;
});

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector(".search-input");
    const categoryDropdown = document.querySelector(".category-dropdown");
    const authorDropdown = document.querySelector(".author-dropdown");
    const findBookBtn = document.querySelector(".find-book-btn");
    const books = document.querySelectorAll(".book-item");

    function filterBooks() {
        const searchText = searchInput.value.toLowerCase();
        const selectedCategory = categoryDropdown.value.toLowerCase();
        const selectedAuthor = authorDropdown.value.toLowerCase();

        books.forEach(book => {
            const title = book.querySelector("h3").innerText.toLowerCase();
            const author = book.querySelector("p b").innerText.toLowerCase();
            const category = book.getAttribute("data-category")?.toLowerCase() || "";

            let matchTitle = searchText === "" || title.includes(searchText);
            let matchCategory = selectedCategory === "" || category.includes(selectedCategory);
            let matchAuthor = selectedAuthor === "" || author.includes(selectedAuthor);

            if (matchTitle && matchCategory && matchAuthor) {
                book.style.display = "block";
            } else {
                book.style.display = "none";
            }
        });
    }

    findBookBtn.addEventListener("click", filterBooks);
    searchInput.addEventListener("input", filterBooks);
    categoryDropdown.addEventListener("change", filterBooks);
    authorDropdown.addEventListener("change", filterBooks);
    
});
document.addEventListener('DOMContentLoaded', function() {
    // Update cart display on page load
    updateCartDisplay();

    // Add event listeners to all buy buttons
    const buyButtons = document.querySelectorAll('.buy-btn');
    buyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const bookItem = this.closest('.book-item');
            const bookData = {
                id: Date.now(), // Use timestamp as a unique ID
                image: bookItem.querySelector('img').src,
                title: bookItem.querySelector('h3').textContent,
                author: bookItem.querySelector('p b').textContent.replace('By ', ''),
                price: bookItem.querySelector('.price').textContent,
                quantity: 1
            };
            
            // Send the data to server
            fetch('/add-to-cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(bookData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show notification
                    showNotification(bookData.title);
                    
                    // Update cart count and total in navbar
                    updateCartDisplay(data.cart_count, data.cart_total);
                }
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
            });
        });
    });

    // Function to show notification
    function showNotification(bookTitle) {
        // Create notification element
        const notification = document.createElement('div');
        notification.classList.add('cart-notification');
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-check-circle"></i>
                <span>${bookTitle} added to cart!</span>
            </div>
        `;
        
        // Add notification to body
        document.body.appendChild(notification);
        
        // Show notification with animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Function to update cart display
    function updateCartDisplay(count = null, total = null) {
        if (count === null || total === null) {
            // Fetch cart data if not provided
            fetch('/get-cart-data')
            .then(response => response.json())
            .then(data => {
                document.querySelector('.cart-count').textContent = data.cart_count;
                document.querySelector('.cart-total').textContent = data.cart_total;
            })
            .catch(error => {
                console.error('Error fetching cart data:', error);
            });
        } else {
            // Update with provided data
            document.querySelector('.cart-count').textContent = count;
            document.querySelector('.cart-total').textContent = total;
        }
    }

    // Book descriptions database
    const bookDescriptions = {
        'Prayers to GANESHA': 'A deeply spiritual collection that explores the various prayers and mantras dedicated to Lord Ganesha, the remover of obstacles. This book delves into the symbolism, tradition, and cultural significance of Ganesha worship across different regions of India.',
        'IMMORTAL LOVE': 'A touching romance that spans centuries, following two souls destined to find each other in every lifetime. Set against the backdrop of historical events, this epic love story explores themes of destiny, sacrifice, and the enduring power of true love.',
        'BY-WAYS OF BOMBAY': 'A fascinating historical account of old Bombay (now Mumbai), detailing its hidden streets, forgotten communities, and secret traditions. This richly researched work provides readers with a glimpse into the city\'s colonial past and vibrant cultural heritage.',
        'Pasayadan': 'A profound philosophical text that translates and explains the famous Marathi prayer composed by Sant Dnyaneshwar. The book explores themes of peace, universal brotherhood, and spiritual enlightenment through detailed commentary and historical context.',
        'Mystery in the Hills': 'An exciting adventure thriller set in the misty hills of a remote Indian hill station. When a series of mysterious events disrupt the peaceful town, a young detective must solve the puzzle before time runs out, uncovering long-buried secrets along the way.',
        'Tales of Wisdom': 'A collection of short morality tales drawn from various cultural traditions, each story conveying timeless wisdom and life lessons. Perfect for readers of all ages, this book combines entertainment with profound insights into human nature.',
        'Legends of the Forests': 'A magical journey through mystical forests and their ancient guardians. Blending folklore with fantasy, this book introduces readers to enchanted creatures and the deep wisdom of nature, encouraging environmental consciousness.',
        'Whispers of the Wind': 'A lyrical poetry collection that captures the ephemeral beauty of nature and the human experience. Through vivid imagery and melodic verses, the poet explores themes of love, loss, hope, and the passage of time.',
        'Journey to the Stars': 'A captivating science fiction novel that follows humanity\'s first interstellar expedition. As the crew navigates unknown territories and encounters alien civilizations, they must confront fundamental questions about human existence and purpose.',
        'Dance of the Mind': 'A thought-provoking exploration of consciousness and creativity. Through a blend of philosophy, neuroscience, and personal anecdotes, the author examines how our minds perceive reality and generate original thought.',
        'Echoes from the Past': 'A sweeping historical novel that follows multiple generations of a family through pivotal moments in history. From partition to independence and beyond, this emotional saga explores identity, belonging, and the impact of historical events on ordinary lives.',
        'Tales of the Unknown': 'A collection of supernatural short stories that will send chills down your spine. Drawing from urban legends and folk horror, these tales explore the thin veil between our world and the unexplained.',
        'The Alchemist': 'A philosophical novel about following your dreams. It tells the story of Santiago, an Andalusian shepherd boy who yearns to travel in search of treasure. His quest leads him to riches far different—and far more satisfying—than he ever imagined.',
        'To Kill a Mockingbird': 'A powerful examination of racial injustice in America through the innocent eyes of a child. Set in the Depression-era South, this Pulitzer Prize-winning novel explores moral growth, compassion, and the irrationality of prejudice.',
        '1984': 'A dystopian social science fiction novel that explores themes of totalitarianism, mass surveillance, and repressive government control. Orwell\'s vision of a future world has had profound impact on our understanding of politics and truth.',
        'The Great Gatsby': 'A tragic love story set in the Jazz Age, this novel explores themes of decadence, idealism, social upheaval, and resistance to change. Through the mysterious millionaire Jay Gatsby, Fitzgerald examines the hollowness of the American Dream.'
    };

    // Book details modal functionality
    const modal = document.getElementById('bookDetailsModal');
    const closeButton = document.querySelector('.close-modal');
    const detailButtons = document.querySelectorAll('.detail-btn');
    
    // Handle detail button clicks
    detailButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookItem = this.closest('.book-item');
            
            // Get book information
            const bookImage = bookItem.querySelector('img').src;
            const bookTitle = bookItem.querySelector('h3').textContent;
            const bookAuthor = bookItem.querySelector('p b').textContent;
            const bookPrice = bookItem.querySelector('.price').textContent;
            
            // Get book description (or use default if not found)
            const bookDescription = bookDescriptions[bookTitle] || 
                "This captivating book takes readers on an unforgettable journey through its pages. With rich character development, engaging storytelling, and thoughtful themes, it offers readers a truly immersive experience.";
            
            // Populate modal
            document.getElementById('modalBookImage').src = bookImage;
            document.getElementById('modalBookTitle').textContent = bookTitle;
            document.getElementById('modalBookAuthor').textContent = bookAuthor;
            document.getElementById('modalBookPrice').textContent = bookPrice;
            document.getElementById('modalBookDescription').textContent = bookDescription;
            
            // Create a "buy" function for the modal button
            document.getElementById('modalBuyButton').onclick = function() {
                // Simulate clicking the buy button on the original book item
                bookItem.querySelector('.buy-btn').click();
                
                // Add a confirmation message inside the modal
                const confirmation = document.createElement('p');
                confirmation.textContent = 'Added to cart!';
                confirmation.classList.add('added-confirmation');
                confirmation.style.color = '#4caf50';
                confirmation.style.fontWeight = 'bold';
                confirmation.style.marginTop = '10px';
                
                const modalBuyButton = document.getElementById('modalBuyButton');
                modalBuyButton.insertAdjacentElement('afterend', confirmation);
                
                // Remove confirmation after 2 seconds
                setTimeout(() => {
                    confirmation.remove();
                }, 2000);
            };
            
            // Show modal with animation
            modal.style.display = 'block';
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
        });
    });
    
    // Close modal when X button is clicked
    closeButton.addEventListener('click', closeModal);
    
    // Close modal when clicking outside modal content
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });
    
    // Close modal function
    function closeModal() {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }

    // Category dropdown functionality
    const dropdown = document.getElementById('dropdown'); 
    dropdown.addEventListener('change', function() {
        const selectedPage = this.value;
        window.location.href = selectedPage; 
    });
    
    // Search functionality
    const searchInput = document.querySelector(".search-input");
    const categoryDropdown = document.querySelector(".category-dropdown");
    const authorDropdown = document.querySelector(".author-dropdown");
    const findBookBtn = document.querySelector(".find-book-btn");
    const books = document.querySelectorAll(".book-item");
    
    function filterBooks() {
        const searchText = searchInput.value.toLowerCase();
        const selectedCategory = categoryDropdown.value.toLowerCase();
        const selectedAuthor = authorDropdown.value.toLowerCase();
        
        books.forEach(book => {
            const title = book.querySelector("h3").innerText.toLowerCase();
            const author = book.querySelector("p b").innerText.toLowerCase();
            const category = book.getAttribute("data-category")?.toLowerCase() || "";
            
            let matchTitle = searchText === "" || title.includes(searchText);
            let matchCategory = selectedCategory === "" || category.includes(selectedCategory);
            let matchAuthor = selectedAuthor === "" || author.includes(selectedAuthor);
            
            if (matchTitle && matchCategory && matchAuthor) {
                book.style.display = "block";
            } else {
                book.style.display = "none";
            }
        });
    }
    
    findBookBtn.addEventListener("click", filterBooks);
    searchInput.addEventListener("input", filterBooks);
    categoryDropdown.addEventListener("change", filterBooks);
    authorDropdown.addEventListener("change", filterBooks);
});