// ---------- Prediction Form Handler ----------
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form data
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());

        // Convert numeric fields
        data.minimum_nights = parseInt(data.minimum_nights);
        data.number_of_reviews = parseInt(data.number_of_reviews);
        data.reviews_per_month = parseFloat(data.reviews_per_month);
        data.calculated_host_listings_count = parseInt(data.calculated_host_listings_count);
        data.availability_365 = parseInt(data.availability_365);

        // UI elements
        const resultContainer = document.getElementById('resultContainer');
        const loadingState = document.getElementById('loadingState');
        const predictBtn = document.getElementById('predictBtn');
        const errorMsg = document.getElementById('errorMessage');
        const priceDisplay = document.getElementById('predictedPrice');
        const rangeDisplay = document.getElementById('priceRange');

        // Show loading, hide result
        loadingState.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        errorMsg.classList.add('hidden');
        predictBtn.disabled = true;
        predictBtn.querySelector('span').textContent = 'Predicting...';

        try {
            // ✅ FIXED: Use live Render backend
            const API_URL = 'https://revnest-5vik.onrender.com/predict';

            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                // Display result
                priceDisplay.textContent = `$${result.predicted_price.toFixed(2)}`;
                rangeDisplay.textContent = result.price_range || 'Standard';
                resultContainer.classList.remove('hidden');
            } else {
                errorMsg.textContent = `Error: ${result.detail || 'Something went wrong'}`;
                errorMsg.classList.remove('hidden');
            }
        } catch (error) {
            errorMsg.textContent = `Error: Cannot connect to the server. Make sure the API is running.`;
            errorMsg.classList.remove('hidden');
            console.error('API Error:', error);
        } finally {
            loadingState.classList.add('hidden');
            predictBtn.disabled = false;
            predictBtn.querySelector('span').textContent = 'Predict Price';
        }
    });
});