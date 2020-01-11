var abrir = document.getElementById('abrir');
var	over = document.getElementById('overlay');
var	popup = document.getElementById('popup');
var	cerrar = document.getElementById('cerrarpop');

abrir.addEventListener('click', function(){
	over.classList.add('active');
	popup.classList.add('active');
});

cerrar.addEventListener('click' , function(){
	over.classList.remove('active');
	popup.classList.remove('active');
});
