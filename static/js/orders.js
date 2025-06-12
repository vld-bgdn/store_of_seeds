document.addEventListener('DOMContentLoaded', function () {
    // Handle delivery method changes
    const deliveryMethodRadios = document.querySelectorAll('input[name="delivery_method"]');
    const deliveryFields = document.querySelectorAll('.delivery-fields');
    const deliveryCostDisplay = document.getElementById('deliveryCostDisplay');
    const totalCostDisplay = document.getElementById('totalCostDisplay');
    const cartTotal = parseFloat('{{ cart.get_total_price }}');

    function updateDeliveryCostDisplay(cost) {
        deliveryCostDisplay.textContent = cost + ' ₽';
        const total = cartTotal + cost;
        totalCostDisplay.textContent = total.toFixed(2) + ' ₽';
    }

    function showDeliveryFields(method) {
        deliveryFields.forEach(field => {
            field.style.display = 'none';
        });

        if (method === 'post') {
            document.getElementById('postFields').style.display = 'block';
            updateDeliveryCostDisplay(200);
        } else if (method === 'cdek') {
            document.getElementById('cdekFields').style.display = 'block';
            updateDeliveryCostDisplay(0);

            // Initialize CDEK city selection
            const cityInput = document.getElementById('cdekCity');
            cityInput.addEventListener('change', function () {
                const city = this.value;
                if (city) {
                    // Mock CDEK API call
                    fetch('/orders/cdek-calculate/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        },
                        body: `city=${encodeURIComponent(city)}&cart_total=${cartTotal}`
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                const pointSelect = document.getElementById('cdekPoint');
                                pointSelect.innerHTML = '';

                                // Add points to select
                                data.points.forEach(point => {
                                    const option = document.createElement('option');
                                    option.value = point.id;
                                    option.textContent = point.address;
                                    pointSelect.appendChild(option);
                                });

                                // Update cost display
                                document.getElementById('cdekCost').textContent =
                                    'Стоимость: ' + data.cost + ' ₽';
                                updateDeliveryCostDisplay(data.cost);
                            }
                        });
                }
            });
        } else if (method === 'pickup') {
            document.getElementById('pickupFields').style.display = 'block';
            updateDeliveryCostDisplay(0);
        }
    }

    // Show fields for initially selected method
    const initialMethod = document.querySelector('input[name="delivery_method"]:checked').value;
    showDeliveryFields(initialMethod);

    // Add change listeners
    deliveryMethodRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            showDeliveryFields(this.value);
        });
    });

    // Form submission handling
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', function (e) {
            const cdekMethod = document.querySelector('input[name="delivery_method"]:checked').value === 'cdek';
            const cdekPoint = document.getElementById('cdekPoint');

            if (cdekMethod && (!cdekPoint.value || cdekPoint.value === '')) {
                e.preventDefault();
                alert('Пожалуйста, выберите пункт выдачи СДЭК');
            }
        });
    }
});
