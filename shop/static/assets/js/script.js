const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () => {
    history.pushState({},null,'/register');
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    history.pushState({},null,'/login');
    container.classList.remove("active");
});

window.onload=function(){
var path=window.location.pathname;
if(path=='/register'){
    registerBtn.click();
}
else{
    loginBtn.click();
}
}





function submitForm() {
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    var message = document.getElementById('message').value;

    // Simple form validation
    if (name.trim() === '' || email.trim() === '' || message.trim() === '') {
        alert('Please fill in all fields');
        return;
    }

    // You can add further form submission logic here
    alert('Form submitted successfully!');
    document.getElementById('contactForm').reset();
}