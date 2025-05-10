document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables to store selections
    let selectedSize = document.getElementById('size-select').value;
    let selectedFrame = null;
    let selectedMaterial = null;
    
    // Get base price
    const basePrice = parseFloat(document.getElementById('base-price').textContent.replace('$', ''));
    
    // Select the first frame and material by default
    if (document.querySelector('.frame-option')) {
        document.querySelector('.frame-option').classList.add('selected');
        selectedFrame = document.querySelector('.frame-option').getAttribute('data-frame-id');
    }
    
    if (document.querySelector('.material-option')) {
        document.querySelector('.material-option').classList.add('selected');
        selectedMaterial = document.querySelector('.material-option').getAttribute('data-material-id');
    }
    
    // Update price calculation
    updatePriceCalculation();
    
    // Size Selection Change
    document.getElementById('size-select').addEventListener('change', function() {
        selectedSize = this.value;
        const multiplier = this.options[this.selectedIndex].getAttribute('data-multiplier');
        document.getElementById('size-adjustment').textContent = 'x' + multiplier;
        updatePriceCalculation();
    });
    
    // Frame Selection
    document.querySelectorAll('.frame-option').forEach(frame => {
        frame.addEventListener('click', function() {
            // Remove selected class from all frames
            document.querySelectorAll('.frame-option').forEach(f => {
                f.classList.remove('selected');
            });
            
            // Add selected class to clicked frame
            this.classList.add('selected');
            selectedFrame = this.getAttribute('data-frame-id');
            
            // Update frame price display
            const framePrice = this.getAttribute('data-price');
            document.getElementById('frame-price').textContent = '$' + framePrice;
            
            // Update frame overlay
            updateFrameOverlay(this);
            
            // Update total price
            updatePriceCalculation();
        });
    });
    
    // Material Selection
    document.querySelectorAll('.material-option').forEach(material => {
        material.addEventListener('click', function() {
            // Remove selected class from all materials
            document.querySelectorAll('.material-option').forEach(m => {
                m.classList.remove('selected');
            });
            
            // Add selected class to clicked material
            this.classList.add('selected');
            selectedMaterial = this.getAttribute('data-material-id');
            
            // Update material multiplier display
            const materialMultiplier = this.getAttribute('data-multiplier');
            document.getElementById('material-multiplier').textContent = 'x' + materialMultiplier;
            
            // Update total price
            updatePriceCalculation();
        });
    });
    
    // Initialize price calculation and preview
    if (document.querySelector('.frame-option')) {
        updateFrameOverlay(document.querySelector('.frame-option'));
    }
    
    // Update frame overlay on the artwork preview
    function updateFrameOverlay(frameElement) {
        const frameOverlay = document.getElementById('frame-overlay');
        const frameBorderStyle = getComputedStyle(frameElement.querySelector('img')).borderColor;
        
        // Set the frame overlay style
        frameOverlay.style.borderColor = frameBorderStyle || '#8B4513'; // Default to a wood color if not available
        frameOverlay.style.borderWidth = '20px'; // Default frame width
        frameOverlay.style.borderStyle = 'solid';
    }
    
    // Calculate and update the total price
    function updatePriceCalculation() {
        if (!selectedSize || !selectedFrame || !selectedMaterial) {
            return; // Exit if any selection is missing
        }
        
        // Get current values
        const sizeSelect = document.getElementById('size-select');
        const sizeMultiplier = parseFloat(sizeSelect.options[sizeSelect.selectedIndex].getAttribute('data-multiplier'));
        
        const selectedFrameElement = document.querySelector(`.frame-option[data-frame-id="${selectedFrame}"]`);
        const framePrice = parseFloat(selectedFrameElement.getAttribute('data-price'));
        
        const selectedMaterialElement = document.querySelector(`.material-option[data-material-id="${selectedMaterial}"]`);
        const materialMultiplier = parseFloat(selectedMaterialElement.getAttribute('data-multiplier'));
        
        // Calculate prices
        const sizeAdjustedPrice = basePrice * sizeMultiplier;
        const materialAdjustedPrice = sizeAdjustedPrice * materialMultiplier;
        const totalPrice = materialAdjustedPrice + framePrice;
        
        // Update UI
        document.getElementById('frame-price').textContent = '$' + framePrice.toFixed(2);
        document.getElementById('size-adjustment').textContent = 'x' + sizeMultiplier.toFixed(1);
        document.getElementById('material-multiplier').textContent = 'x' + materialMultiplier.toFixed(1);
        document.getElementById('total-price').textContent = '$' + totalPrice.toFixed(2);
        
        // You can also update a hidden field if you need to submit this value in a form
    }
    
    // Form submission
    document.getElementById('customization-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        const requiredFields = ['first_name', 'last_name', 'email', 'address', 'city', 'postal_code', 'country'];
        let isValid = true;
        
        requiredFields.forEach(field => {
            const input = document.getElementById(field);
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        if (!isValid) {
            alert('Please fill in all required fields.');
            return;
        }
        
        // Here you would typically submit the form data to the server
        // For this example, we'll just show a success message
        alert('Thank you for your order! We will process it shortly.');
    });
    
    // Calculate price via API - Advanced functionality
    function calculatePriceViaAPI() {
        const artworkId = document.getElementById('artwork_id').value;
        const sizeId = selectedSize;
        const frameId = selectedFrame;
        const materialId = selectedMaterial;
        
        // Only calculate if all selections are made
        if (!artworkId || !sizeId || !frameId || !materialId) {
            return;
        }
        
        // Prepare data for API call
        const data = {
            artwork_id: artworkId,
            size_id: sizeId,
            frame_id: frameId,
            material_id: materialId
        };
        
        // Make API call
        fetch('/api/calculate_price/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update UI with returned price data
            document.getElementById('base-price').textContent = '$' + data.base_price.toFixed(2);
            document.getElementById('total-price').textContent = '$' + data.total_price.toFixed(2);
        })
        .catch(error => {
            console.error('Error calculating price:', error);
        });
    }
    
    // Call API-based price calculation when all selections change (optional enhancement)
    // Uncomment this if you want to use server-side calculation instead of client-side
    /*
    const selectionElements = [
        document.getElementById('size-select'),
        ...document.querySelectorAll('.frame-option'),
        ...document.querySelectorAll('.material-option')
    ];
    
    selectionElements.forEach(element => {
        if (element.tagName === 'SELECT') {
            element.addEventListener('change', calculatePriceViaAPI);
        } else {
            element.addEventListener('click', calculatePriceViaAPI);
        }
    });
    */
});
