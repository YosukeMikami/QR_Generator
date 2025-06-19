import './style.css';

async function ButtonClick() {
  const res = await fetch("http://localhost:8000/generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({"text": "hello"})
  })
  const data = await res.json();
  let div = document.getElementById("res")
  div.innerHTML = data.message
}

let button = document.getElementById("button")
button.addEventListener("click", ButtonClick)
