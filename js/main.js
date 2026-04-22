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
        if (id) {
            addToCart(id);
            sendAddToCartRequest(id);
        }
    }

    const productBtn = e.target.closest('.btn-add-cart-product');
    if (productBtn) {
        e.preventDefault();
        const fromDataset = productBtn.dataset?.id;
        const fromUrl = new URLSearchParams(window.location.search).get('id');
        const id = fromDataset || fromUrl || '1';
        addToCart(id);
        sendAddToCartRequest(id);
    }
});

function renderCart() {
    const container = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    if (!container || !totalEl) return;

    if (!cartState.items.length) {
        container.innerHTML = '<p>Ваша корзина пуста</p>';
        totalEl.textContent = '0₽';
        return;
    }

    let total = 0;
    container.innerHTML = cartState.items.map(item => {
        const product = typeof getProductById === 'function' ? getProductById(item.id) : null;
        const price = product ? product.price : 0;
        const name = product ? product.name : 'Товар';
        const image = product ? product.image : '';
        const quantity = item.quantity || 1;
        const sum = price * quantity;
        total += sum;

        return `
            <div class="cart-item" data-id="${item.id}">
                <div class="cart-item-main">
                    ${image ? `<img src="${image}" alt="${name}" class="cart-item-image">` : ''}
                    <div>
                        <div class="cart-item-title">${name}</div>
                        <div class="cart-item-price">${price}₽</div>
                    </div>
                </div>
                <div class="cart-item-controls">
                    <button class="cart-btn cart-minus">−</button>
                    <span class="cart-qty">${quantity}</span>
                    <button class="cart-btn cart-plus">+</button>
                    <button class="cart-btn cart-remove">Удалить</button>
                    <span class="cart-item-sum">${sum}₽</span>
                </div>
            </div>
        `;
    }).join('');

    totalEl.textContent = total + '₽';
}

function openCartModal() {
    const overlay = document.getElementById('cartModalOverlay');
    const modal = document.getElementById('cartModal');
    if (!overlay || !modal) return;
    renderCart();
    overlay.classList.add('is-open');
    modal.classList.add('is-open');
}

function closeCartModal() {
    const overlay = document.getElementById('cartModalOverlay');
    const modal = document.getElementById('cartModal');
    if (!overlay || !modal) return;
    overlay.classList.remove('is-open');
    modal.classList.remove('is-open');
}

document.addEventListener('click', (e) => {
    if (e.target.closest('.cart-link')) {
        e.preventDefault();
        openCartModal();
    }

    const minusBtn = e.target.closest('.cart-minus');
    const plusBtn = e.target.closest('.cart-plus');
    const removeBtn = e.target.closest('.cart-remove');

    if (minusBtn || plusBtn || removeBtn) {
        const itemEl = e.target.closest('.cart-item');
        if (!itemEl) return;
        const id = itemEl.dataset.id;
        const item = cartState.items.find(i => i.id === id);
        if (!item) return;

        if (minusBtn) {
            const currentQty = item.quantity || 1;
            const newQty = currentQty - 1;
            if (newQty <= 0) {
                cartState.items = cartState.items.filter(i => i.id !== id);
            } else {
                item.quantity = newQty;
            }
        } else if (plusBtn) {
            item.quantity = (item.quantity || 1) + 1;
        } else if (removeBtn) {
            cartState.items = cartState.items.filter(i => i.id !== id);
        }

        localStorage.setItem('fashionCart', JSON.stringify(cartState.items));
        updateCartCount();
        renderCart();
    }
});

document.getElementById('cartModalOverlay')?.addEventListener('click', closeCartModal);
document.getElementById('cartModalClose')?.addEventListener('click', closeCartModal);
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeCartModal();
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
