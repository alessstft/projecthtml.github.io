(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const catParam = urlParams.get('cat');

    if (catParam) {
        const select = document.getElementById('categoryFilter');
        const links = document.querySelectorAll('.sidebar-categories a');
        if (select) select.value = catParam;
        links.forEach(link => {
            if (link.dataset.cat === catParam) {
                link.style.color = 'var(--color-accent)';
            }
        });
    }

    const categoryFilter = document.getElementById('categoryFilter');
    categoryFilter?.addEventListener('change', filterProducts);

    const sortFilter = document.getElementById('sortFilter');
    sortFilter?.addEventListener('change', filterProducts);

    document.getElementById('applyPrice')?.addEventListener('click', filterProducts);

    function filterProducts() {
        const cat = categoryFilter?.value || '';
        const sort = sortFilter?.value || 'popular';
        const priceMin = parseInt(document.getElementById('priceMin')?.value) || 0;
        const priceMax = parseInt(document.getElementById('priceMax')?.value) || Infinity;

        const cards = document.querySelectorAll('.catalog-products .card');
        let visible = [];

        cards.forEach(card => {
            const cardCat = card.dataset.category || '';
            const price = parseInt(card.dataset.price) || 0;

            const catMatch = !cat || cardCat === cat;
            const priceMatch = price >= priceMin && price <= priceMax;

            if (catMatch && priceMatch) {
                card.style.display = '';
                visible.push({ el: card, price, new: card.dataset.new === '1' });
            } else {
                card.style.display = 'none';
            }
        });

        const container = document.querySelector('.catalog-products');
        if (container && sort !== 'popular') {
            visible.sort((a, b) => {
                if (sort === 'price-asc') return a.price - b.price;
                if (sort === 'price-desc') return b.price - a.price;
                if (sort === 'new') return (b.new ? 1 : 0) - (a.new ? 1 : 0);
                return 0;
            });
            visible.forEach(({ el }) => container.appendChild(el));
        }
    }

    if (catParam) filterProducts();
})();
