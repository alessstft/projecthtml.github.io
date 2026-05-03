let cartBonusPoints = 0;
let bonusEnabled = false;

function getCartSubtotal() {
    return cartState.items.reduce((sum, item) => {
        const product = typeof getProductById === 'function' ? getProductById(item.id) : null;
        const price = product ? product.price : 0;
        return sum + price * (item.quantity || 1);
    }, 0);
}

function getMaxBonus() {
    const subtotal = getCartSubtotal();
    return Math.floor(subtotal / 2);
}

function updateBonusUI() {
    const block = document.getElementById('bonusPaymentBlock');
    const sliderArea = document.getElementById('bonusSliderArea');
    const input = document.getElementById('bonusPointsInput');
    const maxEl = document.getElementById('bonusMaxPoints');
    const availableEl = document.getElementById('availableBonusPoints');
    const discountDisplay = document.getElementById('bonusDiscountDisplay');
    const discountLine = document.getElementById('discountLine');
    const discountEl = document.getElementById('cartDiscount');
    const totalEl = document.getElementById('cartTotal');
    const subtotalEl = document.getElementById('cartSubtotal');

    if (!block || !USER_IS_AUTH) return;

    const subtotal = getCartSubtotal();
    const maxBonus = getMaxBonus();
    const availableBonus = USER_BONUS_POINTS;

    block.style.display = 'block';
    availableEl.textContent = availableBonus.toLocaleString();
    maxEl.textContent = maxBonus.toLocaleString();

    if (input) {
        input.max = Math.min(availableBonus, maxBonus);
    }

    const discount = bonusEnabled ? cartBonusPoints : 0;
    const finalTotal = subtotal - discount;

    if (subtotalEl) subtotalEl.textContent = subtotal.toLocaleString() + ' ₽';
    if (totalEl) totalEl.textContent = finalTotal.toLocaleString() + ' ₽';

    if (discountLine) {
        discountLine.style.display = bonusEnabled && discount > 0 ? 'flex' : 'none';
    }
    if (discountEl) discountEl.textContent = '-' + discount.toLocaleString() + ' ₽';
    if (discountDisplay) discountDisplay.textContent = discount.toLocaleString() + ' ₽';
}

function renderCartPage() {
    const container = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    const subtotalEl = document.getElementById('cartSubtotal');
    if (!container || !totalEl) return;

    if (!cartState.items.length) {
        container.innerHTML = '<p class="cart-empty">Ваша корзина пуста</p><div class="cart-empty-actions"><a href="/catalog/" class="btn btn-outline">Перейти в каталог</a></div>';
        if (totalEl) totalEl.textContent = '0 ₽';
        if (subtotalEl) subtotalEl.textContent = '0 ₽';
        const block = document.getElementById('bonusPaymentBlock');
        if (block) block.style.display = 'none';
        return;
    }

    let subtotal = 0;
    container.innerHTML = cartState.items.map(item => {
        const product = typeof getProductById === 'function' ? getProductById(item.id) : null;
        const price = product ? product.price : 0;
        const name = product ? product.name : 'Товар';
        const image = product ? product.image : '';
        const quantity = item.quantity || 1;
        const sum = price * quantity;
        subtotal += sum;

        return `
            <div class="cart-item-page" data-id="${item.id}">
                <div class="cart-item-main">
                    ${image ? `<img src="${image}" alt="${name}" class="cart-item-image">` : ''}
                    <div>
                        <div class="cart-item-title">${name}</div>
                        <div class="cart-item-price">${price} ₽</div>
                    </div>
                </div>
                <div class="cart-item-controls">
                    <button class="cart-btn cart-minus">−</button>
                    <span class="cart-qty">${quantity}</span>
                    <button class="cart-btn cart-plus">+</button>
                    <button class="cart-btn cart-remove">Удалить</button>
                    <span class="cart-item-sum">${sum.toLocaleString()} ₽</span>
                </div>
            </div>
        `;
    }).join('');

    updateCartCount();
    updateBonusUI();
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
        renderCartPage();
    }
});

document.getElementById('useBonusToggle')?.addEventListener('change', (e) => {
    bonusEnabled = e.target.checked;
    const sliderArea = document.getElementById('bonusSliderArea');
    if (sliderArea) sliderArea.style.display = bonusEnabled ? 'block' : 'none';

    if (bonusEnabled) {
        const input = document.getElementById('bonusPointsInput');
        const maxBonus = getMaxBonus();
        const allowed = Math.min(USER_BONUS_POINTS, maxBonus);
        cartBonusPoints = allowed;
        if (input) input.value = cartBonusPoints;
    } else {
        cartBonusPoints = 0;
    }
    updateBonusUI();
});

document.getElementById('bonusPointsInput')?.addEventListener('input', (e) => {
    const maxBonus = getMaxBonus();
    const allowed = Math.min(USER_BONUS_POINTS, maxBonus);
    let val = parseInt(e.target.value) || 0;
    if (val < 0) val = 0;
    if (val > allowed) val = allowed;
    cartBonusPoints = val;
    updateBonusUI();
});

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

document.getElementById('checkoutBtn')?.addEventListener('click', async () => {
    if (!cartState.items.length) {
        alert('Корзина пуста');
        return;
    }
    if (typeof USER_AUTHENTICATED !== 'undefined' && !USER_AUTHENTICATED) {
        window.location.href = LOGIN_URL + '?next=' + encodeURIComponent('/cart/');
        return;
    }

    const payload = { items: cartState.items };
    if (bonusEnabled && cartBonusPoints > 0) {
        payload.bonus_points = cartBonusPoints;
    }

    try {
        const response = await fetch('/checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!data.success) {
            alert(data.message || 'Ошибка при оформлении заказа');
            return;
        }
        alert(data.message || 'Заказ оформлен');
        cartState.items = [];
        localStorage.setItem('fashionCart', JSON.stringify(cartState.items));
        renderCartPage();
    } catch (error) {
        alert('Ошибка сервера. Попробуйте позже.');
    }
});
