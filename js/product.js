const id = new URLSearchParams(window.location.search).get('id') || '1';
const product = getProductById(id);

if (product) {
    document.getElementById('productTitle').textContent = product.name;
    document.getElementById('productCategory').textContent = product.category === 'hoodies' ? 'Худи' : product.category === 'tshirts' ? 'Футболки' : 'Рубашки';
    document.getElementById('productPrice').textContent = product.price + '₽';
    document.getElementById('productImage').src = product.image;
    document.getElementById('productImage').alt = product.name;
    document.getElementById('productDesc').textContent = product.description;
    document.getElementById('productBreadcrumb').textContent = product.name;

    const oldPriceEl = document.getElementById('productOldPrice');
    if (product.oldPrice) {
        oldPriceEl.textContent = product.oldPrice + '₽';
        oldPriceEl.style.display = 'inline';
    } else {
        oldPriceEl.style.display = 'none';
    }

    document.title = product.name + ' — Fashion Store';
}
