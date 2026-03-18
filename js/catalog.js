document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const catParam = params.get('cat') || '';
    const searchParam = (params.get('search') || '').toLowerCase();

    const categoryFilter = document.getElementById('categoryFilter');
    const sortFilter = document.getElementById('sortFilter');
    const priceMinInput = document.getElementById('priceMin');
    const priceMaxInput = document.getElementById('priceMax');
    const container = document.getElementById('catalogProducts');

    if (categoryFilter && catParam) {
        categoryFilter.value = catParam;
    }

    function applyFilters() {
        const cat = categoryFilter ? categoryFilter.value : '';
        const sort = sortFilter ? sortFilter.value : 'popular';
        const priceMin = parseInt(priceMinInput?.value) || 0;
        const priceMax = parseInt(priceMaxInput?.value) || Infinity;

        let list = PRODUCTS.slice();

        if (searchParam) {
            list = list.filter(p => p.name.toLowerCase().includes(searchParam));
        }
        if (cat) {
            list = list.filter(p => p.category === cat);
        }

        list = list.filter(p => p.price >= priceMin && p.price <= priceMax);

        if (sort === 'price-asc') {
            list.sort((a, b) => a.price - b.price);
        } else if (sort === 'price-desc') {
            list.sort((a, b) => b.price - a.price);
        } else if (sort === 'new') {
            list.sort((a, b) => (b.isNew === true) - (a.isNew === true));
        }

        renderProductList(container, list);
    }

    categoryFilter?.addEventListener('change', applyFilters);
    sortFilter?.addEventListener('change', applyFilters);
    document.getElementById('applyPrice')?.addEventListener('click', applyFilters);

    applyFilters();
});

