// var popup1 = document.getElementById("popup-1")
// var openPopup1 = document.getElementById("open-popup-1")
// var closePopup1 = document.getElementById('close-popup-1')

// openPopup1.addEventListener('click', () => {
// 	popup1.style.display = "block";
// })

// closePopup1.addEventListener('click', () => {
// 	popup1.style.display = "none";
// })
$(document).ready(function () {
    $('#price').on('change click keyup input paste',(function (event) {
    $(this).val(function (index, value) {
        return '$' + value.replace(/(?!\.)\D/g, "").replace(/(?<=\..*)\./g, "").replace(/(?<=\.\d\d).*/g, "").replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    });
}));
})
