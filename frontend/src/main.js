var can_generate = false;

async function ButtonClick() {
  // 生成中の生成ボタンのクリックを禁止する
  if (!can_generate) return;
  can_generate = false;
  // エラーメッセージがある場合は削除
  let error_message = document.getElementById("error_message");
  const clone = error_message.cloneNode(false);
  error_message.parentNode.replaceChild(clone, error_message);
  // ローディングのアニメーションを再生
  let loading_animation = document.getElementById("spinner");
  loading_animation.hidden = false;
  // ダウンロードリンクの無効化
  let a = document.getElementById("download_a");
  a.removeAttribute("href");
  a.tabIndex = "-1";
  a.classList.add("cannot_download");
  a.classList.remove("can_download");
  // 現在のQRコードを削除
  let qr_image = document.getElementById("qr_image");
  qr_image.removeAttribute("src");
  // 生成が完了するまで生成ボタンの無効化
  let generate_button = document.getElementById("generate_button");
  generate_button.classList.add("cannot_generate");
  generate_button.classList.remove("can_generate");
  const text = document.getElementById("input_text").value;
  const error_correction_level = document.getElementById("error_level_select").value;
  const format = document.getElementById("format_select").value;
  const size = document.getElementById("size_input").value;
  const dpi = document.getElementById("dpi").value;
  const res = await fetch("http://localhost:8000/generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(
      {
        "text": text,
        "error_correction_level": error_correction_level,
        "format": format,
        "size": size,
        "dpi": dpi
      }
    )
  });
  if (res.ok) {
    // プレビュー・ダウンロードリンクの追加
    const data = await res.blob();
    const url = URL.createObjectURL(data);
    qr_image.src = url;
    a.href = url;
    const d = new Date();
    a.download = `qr_code_${d.getTime()}.${format}`;
    a.classList.add("can_download");
    a.classList.remove("cannot_download");
  } else {
    if (
      res.status == 422
    ) {
      let error_message = document.getElementById("error_message");
      let message0 = document.createElement("span");
      message0.innerHTML = "入力されたテキストが長すぎます。";
      let message1 = document.createElement("span");
      message1.innerHTML = "短くしたうえでやり直してください。";
      error_message.appendChild(message0);
      error_message.appendChild(message1);
    } else {
      let error_message = document.getElementById("error_message");
      let message0 = document.createElement("span");
      message0.innerHTML = "サーバーにエラーが生じました。"
      let message1 = document.createElement("span");
      message1.innerHTML = "やり直してください。";
      error_message.appendChild(message0);
      error_message.appendChild(message1);
    }
  }
  // ローディングアニメーション消す
  loading_animation.hidden = true;
  // 生成を再び可能に
  generate_button.classList.add("can_generate");
  generate_button.classList.remove("cannot_generate");
  can_generate = true;
}

function CanGenerateCheck() {
  const text = document.getElementById("input_text").value;
  let generate_button = document.getElementById("generate_button");
  if ( text != "") {
    generate_button.classList.add("can_generate");
    generate_button.classList.remove("cannot_generate");
    can_generate = true;
  } else {
    generate_button.classList.add("cannot_generate");
    generate_button.classList.remove("can_generate");
    can_generate = false;
  }
}

function AdjustPopover() {
  let popover = document.getElementById("ecl_hint");
  const target = document.getElementById("error_level_label");
  const target_rect = target.getBoundingClientRect();
  const popover_height = Number(window.getComputedStyle(popover).getPropertyValue("height").split("p")[0]);
  popover.style.left = target_rect.left + "px";
  popover.style.top = target_rect.top - popover_height - 5 + "px";
}

let button = document.getElementById("generate_button");
button.addEventListener("click", ButtonClick);

let textarea = document.getElementById("input_text");
textarea.addEventListener("input", CanGenerateCheck);

let size_input = document.getElementById("size_input");
size_input.addEventListener("input", CanGenerateCheck);

addEventListener("scroll", AdjustPopover);

let pop_button = document.getElementById("pop_button");
pop_button.addEventListener("click", AdjustPopover);
