<!DOCTYPE html>
<html>
<head>
  <title>Create Handwriting Font</title>
  <style>
    canvas {
      border: 1px solid black;
      touch-action: none;
    }
    #chars {
      display: flex;
      flex-wrap: wrap;
      max-width: 600px;
      margin-top: 10px;
    }
    .char-box {
      border: 1px solid gray;
      padding: 5px;
      margin: 3px;
      text-align: center;
      cursor: pointer;
      user-select: none;
    }
    .char-box.selected {
      background-color: lightblue;
    }
  </style>
</head>
<body>
  <h2>Draw Characters for Your Handwriting Font</h2>

  <div>
    <label>Select Character to Draw:</label>
    <div id="chars"></div>
  </div>

  <canvas id="drawCanvas" width="200" height="200"></canvas>
  <br>
  <button onclick="clearCanvas()">Clear</button>
  <button onclick="saveChar()">Save Character</button>
  <p id="status"></p>

<script>
const charsToDraw = "abcdefghijklmnopqrstuvwxyz0123456789";
const charsDiv = document.getElementById('chars');
const canvas = document.getElementById('drawCanvas');
const ctx = canvas.getContext('2d');
let drawing = false;
let currentChar = charsToDraw[0];

// Create char selection boxes
charsToDraw.split('').forEach(ch => {
  const div = document.createElement('div');
  div.textContent = ch;
  div.className = 'char-box';
  if (ch === currentChar) div.classList.add('selected');
  div.onclick = () => {
    document.querySelectorAll('.char-box').forEach(el => el.classList.remove('selected'));
    div.classList.add('selected');
    currentChar = ch;
    clearCanvas();
  };
  charsDiv.appendChild(div);
});

// Drawing logic
canvas.addEventListener('pointerdown', e => {
  drawing = true;
  ctx.beginPath();
  ctx.moveTo(e.offsetX, e.offsetY);
});

canvas.addEventListener('pointermove', e => {
  if (!drawing) return;
  ctx.lineTo(e.offsetX, e.offsetY);
  ctx.stroke();
});

canvas.addEventListener('pointerup', e => {
  drawing = false;
});

canvas.addEventListener('pointerleave', e => {
  drawing = false;
});

function clearCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function saveChar() {
  const dataURL = canvas.toDataURL("image/png");
  fetch('/save_char', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({char: currentChar, image: dataURL})
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('status').innerText = `Saved character '${currentChar}'`;
    clearCanvas();
  })
  .catch(err => {
    document.getElementById('status').innerText = 'Error saving character';
  });
}
</script>
</body>
</html>
