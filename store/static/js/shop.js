function createProductCardHTML(product) {
    const hasOld = !!product.oldPrice;
    const isNew = !!product.isNew;
    const badges = [];
    if (hasOld) badges.push('<span class="badge sale">-30%</span>');
    if (isNew) badges.push('<span class="badge new">NEW</span>');

    return `
        <article class="card" data-id="${product.id}" data-category="${product.category}" data-price="${product.price}" data-new="${product.isNew ? '1' : '0'}">
            <a href="/product/${product.id}/" class="card-link">
                <div class="card-image">
                    <img src="${product.image}" alt="${product.name}">
                    ${badges.join('')}
                </div>
                <div class="card-info">
                    <h3 class="card-title">${product.name}</h3>
                    <p class="card-category">${product.category === 'hoodies' ? 'Худи' : product.category === 'tshirts' ? 'Футболки' : 'Рубашки'}</p>
                    <p class="card-price">
                        ${hasOld ? `<span class="old-price">${product.oldPrice}₽</span>` : ''}
                        <span class="price">${product.price}₽</span>
                    </p>
                    <p class="card-sku">Артикул: ${product.sku}</p>
                </div>
            </a>
            <button class="btn-add-cart" data-id="${product.id}">В корзину</button>
        </article>
    `;
}

function renderProductList(container, products) {
    const el = typeof container === 'string' ? document.querySelector(container) : container;
    if (!el) return;
    el.innerHTML = products.map(createProductCardHTML).join('');
}

function setupProductModal() {
    const overlay = document.getElementById('productModalOverlay');
    const modal = document.getElementById('productModal');
    if (!overlay || !modal) return;

    const imgEl = document.getElementById('modalProductImage');
    const titleEl = document.getElementById('modalProductTitle');
    const categoryEl = document.getElementById('modalProductCategory');
    const skuEl = document.getElementById('modalProductSku');
    const priceEl = document.getElementById('modalProductPrice');
    const descEl = document.getElementById('modalProductDesc');
    const closeBtn = document.getElementById('productModalClose');
    const addBtn = document.getElementById('modalAddToCart');

    function openModal(product) {
        imgEl.src = product.image;
        imgEl.alt = product.name;
        titleEl.textContent = product.name;
        categoryEl.textContent = product.category === 'hoodies' ? 'Худи' : product.category === 'tshirts' ? 'Футболки' : 'Рубашки';
        skuEl.textContent = product.sku;
        priceEl.textContent = product.price + '₽';
        descEl.textContent = product.description;
        if (addBtn) addBtn.dataset.id = product.id;
        overlay.classList.add('is-open');
        modal.classList.add('is-open');
    }

    function closeModal() {
        overlay.classList.remove('is-open');
        modal.classList.remove('is-open');
    }

    document.addEventListener('click', (e) => {
        const link = e.target.closest('.card-link');
        if (link && link.closest('.card')) {
            const card = link.closest('.card');
            const id = card.dataset.id;
            const product = getProductById(id);
            if (product) {
                e.preventDefault();
                openModal(product);
            }
        }
    });

    overlay.addEventListener('click', closeModal);
    closeBtn?.addEventListener('click', closeModal);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setupProductModal();
});

