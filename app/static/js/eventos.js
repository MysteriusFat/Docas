function addPerson( _id, current_user ){

  console.log( current_user );

  button = document.getElementById( _id );
  button.classList.add('disabled');

  var x = {
    event_id : _id,
    user_id : current_user
  }

  $.ajax({
    url: '/addPeople',
    data: x,
    type: 'POST'
  });
}
