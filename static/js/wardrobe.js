function switchCategory(type, element) {
    if (element.classList.contains('disable')) return;

    document.querySelectorAll('.cat-icon').forEach(i => i.classList.remove('active'));
    element.classList.add('active');
    console.log("Category switched to: " + type);
}

function selectItem(category, itemId) {
    console.log("Equipping " + itemId);
    // Тут робимо fetch('/api/equip', ...)
}

function buyItem(itemId, price) {
    alert("Бажаєте купити цей скін за " + price + " 🌰?");
}