
var btn1   = document.getElementById('btn1'); 	// sentinel
var btn2   = document.getElementById('btn2'); 	// Lansat
var btn3   = document.getElementById('btn3');		// Modis
var cerrar = document.getElementById('cerrar');	// Ocultar
/* AMARILLO */
btn1.addEventListener('click' , function(){
	overlay.image_ = $("#data").data('url_1');
	overlay.onRemove();
	overlay.onAdd();
	overlay.draw();
});
/* AZUL */
btn2.addEventListener('click' , function(){
	overlay.image_ = $("#data").data('url_2');
	overlay.onRemove();
	overlay.onAdd();
	overlay.draw();
});
/* MORADO */
btn3.addEventListener('click' , function(){
	overlay.image_ = "https://media.azulejossola.com/product/azulejo-morado-brillo-20x20-100m2caja-25-piezascaja-800x800.jpeg"
	overlay.onRemove();
	overlay.onAdd();
	overlay.draw();
});
cerrar.addEventListener('click' , function(){
	overlay.toggle();
});
