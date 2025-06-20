import './style.css';

async function ButtonClick() {
  const res = await fetch("http://localhost:8000/generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(
      {
        "text": "hello",
        "error_correction_level": "M",
        "format": "png",
        "size": 10
      }
    )
  });
  const data = await res.blob();
  const url = URL.createObjectURL(data);
  document.getElementById("qr_image").src = url;
}

let button = document.getElementById("button");
button.addEventListener("click", ButtonClick);
