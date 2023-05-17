const button = document.querySelector(".menu-button");
const dashboard = document.querySelector(".dashboard-1");
const changePassword = document.querySelector(".change-password");
const myOrders = document.querySelector(".my-orders");
const editPro = document.querySelector(".edit-pro");

button.addEventListener("click" , page);

function page(event) {
    const classN = event.target.className;
    if ( classN === "one") {
        dashboard.style.display = "block";
        myOrders.style.display = "none";
        editPro.style.display = "none";
        changePassword.style.display = "none";
    } else if (classN === "2") {
        myOrders.style.display = "block";
        dashboard.style.display = "none";
        changePassword.style.display = "none";
        editPro.style.display = "none";
    } else if (classN === "3") {
        myOrders.style.display = "none";
        dashboard.style.display = "none";
        changePassword.style.display = "none";
        editPro.style.display = "block";
    } else if (classN === "4") {
        myOrders.style.display = "none";
        dashboard.style.display = "none";
        changePassword.style.display = "block";
        editPro.style.display = "none";
    }
} 