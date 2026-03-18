<<<<<<< HEAD
const products = {
    '1': { title: 'Худи Oversize Black', category: 'Худи', price: '3490', oldPrice: '4990', image: 'images/худи.jpg', desc: 'Качественное худи оверсайз из плотного хлопка. Удобный крой, капюшон с верёвками.' },
    '2': { title: 'Худи Sport Grey', category: 'Худи', price: '3990', image: 'images/худи2.jpg', desc: 'Спортивное худи из мягкого материала. Идеально для прогулок и тренировок.' },
    '3': { title: 'Худи Minimal White', category: 'Худи', price: '4290', image: 'images/худи3.jpg', desc: 'Минималистичное худи белого цвета. Лаконичный дизайн для повседневной носки.' },
    '4': { title: 'Худи Urban Navy', category: 'Худи', price: '3670', oldPrice: '4590', image: 'images/худи4.jpg', desc: 'Городское худи тёмно-синего цвета. Стиль оверсайз.' },
    '5': { title: 'Футболка Basic Black', category: 'Футболки', price: '1290', image: 'images/тишка.jpg', desc: 'Классическая базовая футболка чёрного цвета. 100% хлопок.' },
    '6': { title: 'Футболка Graphic White', category: 'Футболки', price: '1590', image: 'images/тишка2.jpg', desc: 'Футболка с принтом. Хлопок премиум качества.' },
    '7': { title: 'Футболка Cotton Grey', category: 'Футболки', price: '1390', image: 'images/тишка3.jpg', desc: 'Мягкая хлопковая футболка серого цвета.' },
    '8': { title: 'Футболка Oversize Cream', category: 'Футболки', price: '1490', image: 'images/тишка4.jpg', desc: 'Оверсайз футболка бежевого оттенка.' },
    '9': { title: 'Рубашка Casual Blue', category: 'Рубашки', price: '2790', image: 'images/рубашка.jpg', desc: 'Кэжуал рубашка голубого цвета. Идеально для офиса и отдыха.' }
};

const id = new URLSearchParams(window.location.search).get('id');
const product = products[id || '1'];

if (product) {
    document.getElementById('productTitle').textContent = product.title;
    document.getElementById('productCategory').textContent = product.category;
    document.getElementById('productPrice').textContent = product.price + '₽';
    document.getElementById('productImage').src = product.image;
    document.getElementById('productImage').alt = product.title;
    document.getElementById('productDesc').textContent = product.desc;
    document.getElementById('productBreadcrumb').textContent = product.title;
=======
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
>>>>>>> b6d3d89 (Мои локальные изменения)

    const oldPriceEl = document.getElementById('productOldPrice');
    if (product.oldPrice) {
        oldPriceEl.textContent = product.oldPrice + '₽';
        oldPriceEl.style.display = 'inline';
    } else {
        oldPriceEl.style.display = 'none';
    }

<<<<<<< HEAD
    document.title = product.title + ' — Fashion Store';
=======
    document.title = product.name + ' — Fashion Store';
>>>>>>> b6d3d89 (Мои локальные изменения)
}
