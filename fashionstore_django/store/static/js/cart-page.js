function renderCartPage() {
    const container = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    if (!container || !totalEl) return;

    if (!cartState.items.length) {
        container.innerHTML = '<p class="cart-empty">Ваша корзина пуста</p>';
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
            <div class="cart-item-page" data-id="${item.id}">
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

renderCartPage();

document.addEventListener('click', (e) => {
    const minusBtn = e.target.closest('.cart-minus');
    const plusBtn = e.target.closest('.cart-plus');
    const removeBtn = e.target.closest('.cart-remove');

    if (minusBtn || plusBtn || removeBtn) {
        const itemEl = e.target.closest('.cart-item-page');
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
        renderCartPage();
    }
});

document.getElementById('checkoutBtn')?.addEventListener('click', async () => {
    if (!cartState.items.length) {
        alert('Корзина пуста');
        return;
    }
    if (typeof USER_AUTHENTICATED !== 'undefined' && !USER_AUTHENTICATED) {
        window.location.href = LOGIN_URL + '?next=' + encodeURIComponent('/cart/');
        return;
    }

    try {
        const response = await fetch('/checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ items: cartState.items }),
        });
        const data = await response.json();
        if (!data.success) {
            alert(data.message || 'Ошибка при оформлении заказа');
            return;
        }
        alert(data.message || 'Заказ оформлен');
        cartState.items = [];
        localStorage.setItem('fashionCart', JSON.stringify(cartState.items));
        updateCartCount();
        renderCartPage();
    } catch (error) {
        alert('Ошибка сервера. Попробуйте позже.');
    }
});
