const cartState = {
    items: JSON.parse(localStorage.getItem('fashionCart')) || []
};

function updateCartCount() {
    const count = cartState.items.reduce((sum, item) => sum + (item.quantity || 1), 0);
    document.querySelectorAll('.cart-count').forEach(el => {
        el.textContent = count;
    });
}

function addToCart(id) {
    const existing = cartState.items.find(item => item.id === String(id));
    if (existing) {
        existing.quantity = (existing.quantity || 1) + 1;
    } else {
        cartState.items.push({ id: String(id), quantity: 1 });
    }
    localStorage.setItem('fashionCart', JSON.stringify(cartState.items));
    updateCartCount();
    showToast('Товар добавлен в корзину');
}

function sendAddToCartRequest(id) {
    try {
        fetch('https://httpbin.org/post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ productId: id })
        }).catch(() => {});
    } catch (e) {}
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
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
        if (!USER_AUTHENTICATED) {
            showToast('Войдите или зарегистрируйтесь, чтобы добавить товар в корзину');
            window.location.href = LOGIN_URL + '?next=' + encodeURIComponent(window.location.pathname + window.location.search);
            return;
        }
        const id = btn.dataset.id;
        if (id) {
            addToCart(id);
            sendAddToCartRequest(id);
        }
    }

    const productBtn = e.target.closest('.btn-add-cart-product');
    if (productBtn) {
        e.preventDefault();
        if (!USER_AUTHENTICATED) {
            showToast('Войдите или зарегистрируйтесь, чтобы добавить товар в корзину');
            window.location.href = LOGIN_URL + '?next=' + encodeURIComponent(window.location.pathname + window.location.search);
            return;
        }
        const fromDataset = productBtn.dataset?.id;
        const fromUrl = new URLSearchParams(window.location.search).get('id');
        const fromPath = window.location.pathname.split('/').filter(Boolean).pop();
        const id = fromDataset || fromUrl || fromPath || '1';
        addToCart(id);
        sendAddToCartRequest(id);
    }
});

document.querySelectorAll('.search-form').forEach(form => {
    form?.addEventListener('submit', (e) => {
        e.preventDefault();
        const input = form.querySelector('input');
        const query = input?.value?.trim();
        if (query) {
            window.location.href = '/catalog/?search=' + encodeURIComponent(query);
        }
    });
});
