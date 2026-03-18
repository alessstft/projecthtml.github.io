
let cart = JSON.parse(localStorage.getItem('fashionCart')) || [];

function updateCartCount() {
    const count = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
    document.querySelectorAll('.cart-count').forEach(el => {
        el.textContent = count;
    });
}

function addToCart(id) {
    const existing = cart.find(item => item.id === String(id));
    if (existing) {
        existing.quantity = (existing.quantity || 1) + 1;
    } else {
        cart.push({ id: String(id), quantity: 1 });
    }
    localStorage.setItem('fashionCart', JSON.stringify(cart));
    updateCartCount();
    showToast('Товар добавлен в корзину');
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

updateCartCount();

document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-add-cart');
    if (btn) {
        e.preventDefault();
        const id = btn.dataset.id;
        if (id) addToCart(id);
    }

    const productBtn = e.target.closest('.btn-add-cart-product');
    if (productBtn) {
        e.preventDefault();
        const id = new URLSearchParams(window.location.search).get('id') || '1';
        addToCart(id);
    }
});

document.querySelectorAll('.search-form').forEach(form => {
    form?.addEventListener('submit', (e) => {
        e.preventDefault();
        const input = form.querySelector('input');
        const query = input?.value?.trim();
        if (query) {
            window.location.href = 'catalog.html?search=' + encodeURIComponent(query);
        }
    });
});
