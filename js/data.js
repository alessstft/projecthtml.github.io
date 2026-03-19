const PRODUCTS = [
    {
        id: '1',
        name: 'Худи Oversize Black',
        price: 3490,
        oldPrice: 4990,
        image: 'images/худи.jpg',
        sku: '4322231',
        category: 'hoodies',
        isNew: false,
        isPopular: true,
        description: 'Качественное худи оверсайз из плотного хлопка. Удобный крой, капюшон с верёвками. Идеально для повседневной носки.'
    },
    {
        id: '2',
        name: 'Худи Sport Grey',
        price: 3990,
        image: 'images/худи2.jpg',
        sku: '2452342',
        category: 'hoodies',
        isNew: true,
        isPopular: true,
        description: 'Спортивное худи из мягкого материала. Идеально для прогулок и тренировок.'
    },
    {
        id: '3',
        name: 'Худи Red',
        price: 4290,
        image: 'images/худи3.jpg',
        sku: '235203',
        category: 'hoodies',
        isNew: false,
        isPopular: true,
        description: 'Красное худи из качественного хлопка. Удобный крой, с капюшоном.'
    },
    {
        id: '4',
        name: 'Худи Urban Navy',
        price: 3670,
        oldPrice: 4590,
        image: 'images/худи4.jpg',
        sku: '4235304',
        category: 'hoodies',
        isNew: false,
        isPopular: true,
        description: 'Городское худи серого цвета. Стиль оверсайз.'
    },
    {
        id: '5',
        name: 'Футболка Grey',
        price: 1290,
        image: 'images/тишка.jpg',
        sku: '6324891',
        category: 'tshirts',
        isNew: false,
        isPopular: true,
        description: 'Футболка серого цвета. Хлопок премиум качества.'
    },
    {
        id: '6',
        name: 'Футболка Graphic Yellow',
        price: 1590,
        image: 'images/тишка2.jpg',
        sku: '34698232',
        category: 'tshirts',
        isNew: true,
        isPopular: true,
        description: 'Футболка с принтом. Хлопок премиум качества.'
    },
    {
        id: '7',
        name: 'Футболка с бабочкой',
        price: 1390,
        image: 'images/тишка3.jpg',
        sku: '4382973',
        category: 'tshirts',
        isNew: false,
        isPopular: true,
        description: 'Мягкая хлопковая футболка.'
    },
    {
        id: '8',
        name: 'Футболкас бабочкой на спине',
        price: 1490,
        image: 'images/тишка4.jpg',
        sku: '8491704',
        category: 'tshirts',
        isNew: false,
        isPopular: true,
        description: 'Оверсайз футболка с открытой спиной.'
    },
    {
        id: '9',
        name: 'Рубашка Casual Blue',
        price: 2790,
        image: 'images/рубашка.jpg',
        sku: '71498781',
        category: 'shirts',
        isNew: false,
        isPopular: true,
        description: 'Кэжуал рубашка белого цвета с муравьями. Лёгкая и удобная.'
    }
];

function getProductById(id) {
    return PRODUCTS.find(p => p.id === String(id));
}

