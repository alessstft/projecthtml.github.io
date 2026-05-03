// Fashion Store - Main JavaScript

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateCartCount(count) {
    if (count !== undefined) {
        document.querySelectorAll('.cart-count').forEach(el => {
            el.textContent = count || 0;
        });
    }
}

function showToast(message) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

async function loadCartCount() {
    try {
        const response = await fetch('/api/cart/');
        const items = await response.json();
        const count = items.reduce((sum, item) => sum + item.quantity, 0);
        updateCartCount(count);
    } catch (err) {
        console.error('Error loading cart count:', err);
    }
}

async function addToCart(productId, size = 'M') {
    try {
        const response = await fetch('/api/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ product_id: productId, quantity: 1, size: size })
        });
        const data = await response.json();
        if (data.success) {
            updateCartCount(data.cart_count);
            showToast('Товар добавлен в корзину');
        }
    } catch (err) {
        showToast('Ошибка добавления товара');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadCartCount();
});

document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-add-cart');
    if (btn) {
        e.preventDefault();
        const id = btn.dataset.id;
        if (id) {
            addToCart(id);
        }
    }

    const productBtn = e.target.closest('.btn-add-cart-product');
    if (productBtn) {
        e.preventDefault();
        const id = productBtn.dataset.id;
        if (id) {
            const sizeSelect = document.getElementById('productSize');
            const size = sizeSelect ? sizeSelect.value : 'M';
            addToCart(id, size);
        }
    }
});