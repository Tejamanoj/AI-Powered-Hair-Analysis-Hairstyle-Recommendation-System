async function startAR() {
  const cameraBox = document.querySelector(".camera-box");
  const loader = document.getElementById("arLoader");
  const count = document.getElementById("count");

  if (cameraBox.requestFullscreen) {
    await cameraBox.requestFullscreen();
  }

  loader.style.display = "flex";
  let num = 3;

  const interval = setInterval(() => {
    count.innerText = num;
    num--;
    if (num < 0) {
      clearInterval(interval);
      loader.style.display = "none";
      arStarted = true;
      startCamera();
    }
  }, 700);
}

function exitAR() {
  if (document.fullscreenElement) {
    document.exitFullscreen();
  }
}

// ===== DRAG AND DROP SETUP =====
window.addEventListener("DOMContentLoaded", () => {
  const uploadBox = document.querySelector(".upload-box");
  const fileInput = document.getElementById("upload");
  const preview = document.getElementById("imagePreview");

  if (!uploadBox) return;

  // Drag over
  uploadBox.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadBox.classList.add("drag-over");
  });

  // Drag leave
  uploadBox.addEventListener("dragleave", () => {
    uploadBox.classList.remove("drag-over");
  });

  // Drop
  uploadBox.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadBox.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      // Set file to input
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      fileInput.files = dataTransfer.files;
      showPreview(file);
    }
  });

  // Normal file input change
  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) {
      showPreview(fileInput.files[0]);
    }
  });

  function showPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (preview) {
        preview.src = e.target.result;
        preview.style.display = "block";
        uploadBox.querySelector("span").textContent = "✅ " + file.name;
      }
    };
    reader.readAsDataURL(file);
  }
});

// ===== ANALYZE HAIR =====
async function analyzeHair() {
  const fileInput = document.getElementById("upload");
  const resultEl = document.getElementById("result");

  if (!fileInput.files[0]) {
    alert("Please upload an image first!");
    return;
  }

  resultEl.textContent = "⏳ Analyzing...";

  const formData = new FormData();
  formData.append("image", fileInput.files[0]);

  try {
    const res = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Server error");

    const data = await res.json();

    // ✅ Get image as base64 to pass to results page
    const reader = new FileReader();
    // ✅ Fix — store image in sessionStorage instead
reader.onload = (e) => {
  sessionStorage.setItem("hairImage", e.target.result);
  sessionStorage.setItem("hairType", data.hair_type);
  sessionStorage.setItem("hairConfidence", data.confidence);
  window.location.href = "../frontend/results.html";
};
reader.readAsDataURL(fileInput.files[0]);
    reader.readAsDataURL(fileInput.files[0]);

  } catch (err) {
    console.error(err);
    resultEl.textContent = "❌ Could not connect to backend. Make sure app.py is running.";
  }
}