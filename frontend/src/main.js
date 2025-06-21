async function ButtonClick() {
  let generate_button = document.getElementById("generate_button");
  generate_button.classList.add("cannot_generate");
  generate_button.classList.remove("can_generate");
  const text = document.getElementById("input_text").value;
  if (text == "") {
    return;
  }
  const error_correction_level = document.getElementById("error_level_select").value;
  const format = document.getElementById("format_select").value;
  const size = document.getElementById("size_input").value;
  const res = await fetch("http://localhost:8000/generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(
      {
        "text": text,
        "error_correction_level": error_correction_level,
        "format": format,
        "size": size
      }
    )
  });
  const data = await res.blob();
  const url = URL.createObjectURL(data);
  document.getElementById("qr_image").src = url;
  let a = document.getElementById("download_a");
  a.href = url;
  const d = new Date();
  a.download = `qr_code_${d.getTime()}.${format}`;
  a.classList.add("can_download");
  a.classList.remove("cannot_download");
  generate_button.classList.add("can_generate");
  generate_button.classList.remove("cannot_generate");
}

function CanGenerateCheck() {
  const text = document.getElementById("input_text").value;
  const size_input = document.getElementById("size_input");
  let generate_button = document.getElementById("generate_button");
  if (
    text != "" &&
    !size_input.validity.rangeOverflow &&
    !size_input.validity.rangeUnderflow
  ) {
    generate_button.classList.add("can_generate");
    generate_button.classList.remove("cannot_generate");
  } else {
    generate_button.classList.add("cannot_generate");
    generate_button.classList.remove("can_generate");
  }
}

function AdjustPopover() {
  let popover = document.getElementById("ecl_hint");
  const pop_button = document.getElementById("pop_button");
}

let button = document.getElementById("generate_button");
button.addEventListener("click", ButtonClick);

let textarea = document.getElementById("input_text");
textarea.addEventListener("input", CanGenerateCheck);

let size_input = document.getElementById("size_input");
size_input.addEventListener("input", CanGenerateCheck);
