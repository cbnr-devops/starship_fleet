console.log('We are inside app-controller.js');

/* on page load */
window.onload = function() {
    const starship_id = document.getElementById("starshipID").value;
    console.log("onLoad - Request Starship ID - " + starship_id);

    fetch("os", { method: "GET" })
        .then(function(res) {
            if (res.ok) return res.json();
            throw new Error('Request failed');
        })
        .catch(function(error) {
            console.log(error);
        })
        .then(function(data) {
            document.getElementById('hostname').innerHTML = `Pod - ${data.os}`;
        });
};

const btn = document.getElementById('submit');
if (btn) {
    btn.addEventListener('click', func);
}

function func() {
    const starship_id = document.getElementById("starshipID").value;
    console.log("onClick Submit - Request Starship ID - " + starship_id);

    fetch("starship", {
            method: "POST",
            body: JSON.stringify({ id: parseInt(document.getElementById("starshipID").value) }),
            headers: { "Content-type": "application/json; charset=UTF-8" }
        })
        .then(function(res) {
            if (res.ok) return res.json();
            throw new Error('Request failed.');
        })
        .catch(function(error) {
            alert("Ooops, We have 8 starships.\nSelect a number from 1 - 8");
            console.log(error);
        })
        .then(function(data) {
            if (!data) {
                alert("Starship not found. Select a number from 1 - 8");
                return;
            }
            document.getElementById('starshipName').innerHTML = data.name;

            const element = document.getElementById("starshipImage");
            element.style.backgroundImage = "url(" + data.image + ")";

            document.getElementById('starshipDescription').innerHTML =
                data.description.replace(/(.{80})/g, "$1<br>");
        });
}
