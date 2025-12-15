// Cart functionality with AJAX
document.addEventListener('DOMContentLoaded', function() {
    // Add to cart buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('href');
            const originalText = this.textContent;
            
            // Show loading state
            this.textContent = 'Adding...';
            this.disabled = true;
            
            // Make AJAX request
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => {
                if (response.ok) {
                    // Show success state
                    this.textContent = 'Added!';
                    this.classList.add('bg-green-600', 'hover:bg-green-700');
                    this.classList.remove('from-fuchsia-600', 'to-pink-600', 'hover:from-fuchsia-700', 'hover:to-pink-700');
                    
                    // Reset after 2 seconds
                    setTimeout(() => {
                        this.textContent = originalText;
                        this.disabled = false;
                        this.classList.remove('bg-green-600', 'hover:bg-green-700');
                        this.classList.add('from-fuchsia-600', 'to-pink-600', 'hover:from-fuchsia-700', 'hover:to-pink-700');
                    }, 2000);
                } else {
                    throw new Error('Failed to add to cart');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.textContent = 'Error';
                this.classList.add('bg-red-600', 'hover:bg-red-700');
                this.classList.remove('from-fuchsia-600', 'to-pink-600', 'hover:from-fuchsia-700', 'hover:to-pink-700');
                
                // Reset after 2 seconds
                setTimeout(() => {
                    this.textContent = originalText;
                    this.disabled = false;
                    this.classList.remove('bg-red-600', 'hover:bg-red-700');
                    this.classList.add('from-fuchsia-600', 'to-pink-600', 'hover:from-fuchsia-700', 'hover:to-pink-700');
                }, 2000);
            });
        });
    });
});
