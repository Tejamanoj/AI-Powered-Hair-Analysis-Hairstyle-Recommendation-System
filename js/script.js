let arStarted = false; // Only set true after Start button/counter

// Start camera on page load so video is always visible
window.onload = () => {
  startCamera();
};

// ===== LOAD HAIRSTYLE IMAGE =====
const hairImg = new Image();
hairImg.src = "../hairstyles/style1.png";
hairImg.onerror = () => {
  console.warn("Hairstyle image failed to load:", hairImg.src);
};

// ===== ELEMENTS =====
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

// ===== SMOOTHING VARIABLES =====
let smoothX = 0;
let smoothY = 0;
let smoothScale = 0;
let smoothAngle = 0;

// ===== START CAMERA =====
async function startCamera() {

  try { // ✅ FIX 2: Added try/catch — handles case where user denies camera permission

    const stream = await navigator.mediaDevices.getUserMedia({
      video: true
    });

    video.srcObject = stream;

    video.onloadedmetadata = () => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      arStarted = true; // ✅ FIX 3: Set arStarted to true only after camera is ready
      startFaceMesh();
    };

  } catch (err) {
    console.error("Camera access denied or failed:", err);
    alert("Could not access camera. Please allow camera permission and try again.");
  }
}

// ===== FACE MESH =====
function startFaceMesh() {

  const faceMesh = new FaceMesh({
    locateFile: (file) =>
      `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
  });

  faceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
  });

  faceMesh.onResults(results => {

    // CLEAR CANVAS EACH FRAME
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) { // ✅ FIX 4: Added length check to avoid empty array errors

      for (const landmarks of results.multiFaceLandmarks) {

        // ===== KEY LANDMARKS =====
        const forehead = landmarks[10];
        const leftFace = landmarks[234];
        const rightFace = landmarks[454];

        // ===== FACE WIDTH =====
        const faceWidth =
          (rightFace.x - leftFace.x) * canvas.width;

        // ===== AUTO SCALE =====
        const scale = faceWidth * 1.45;

        // ===== TARGET POSITION =====
        const targetX =
          (leftFace.x * canvas.width) - (scale * 0.25);

        const targetY =
          (forehead.y * canvas.height) - (scale * 0.45);

        // ===== HEAD ROTATION =====
        const targetAngle = Math.atan2(
          rightFace.y - leftFace.y,
          rightFace.x - leftFace.x
        );

        // ===== SMOOTHING =====
        smoothX += (targetX - smoothX) * 0.2;
        smoothY += (targetY - smoothY) * 0.2;
        smoothScale += (scale - smoothScale) * 0.2;
        smoothAngle += (targetAngle - smoothAngle) * 0.2;

        // ===== PIVOT POINT =====
        const pivotX = smoothX + smoothScale * 0.5;
        const pivotY = smoothY + smoothScale * 0.25;

        ctx.save();
        ctx.translate(pivotX, pivotY);
        ctx.rotate(smoothAngle);

        // ===== DRAW HAIR =====
        if (arStarted && hairImg.complete) { // ✅ FIX 5: Added hairImg.complete check — ensures image is loaded before drawing

          ctx.drawImage(
            hairImg,
            smoothX - smoothScale * 0.25,
            smoothY - smoothScale * 0.25,
            scale,
            scale * 0.7
          );

        }

        ctx.restore();
      }
    }

  });

  // ===== CAMERA LOOP =====
  const camera = new Camera(video, {
    onFrame: async () => {
      await faceMesh.send({ image: video });
    },
    width: 640,
    height: 480
  });

  camera.start();
}

// ===== CHANGE HAIRSTYLE =====
function changeHair(fileName) {
  hairImg.src = "../hairstyles/" + fileName;
  hairImg.onerror = () => { // ✅ FIX 6: Re-attach onerror on every style change
    console.warn("Hairstyle image failed to load:", hairImg.src);
  };
}

// ===== CAPTURE IMAGE & PREDICT HAIR TYPE =====
async function captureImage() {
  const tempCanvas = document.createElement("canvas");
  tempCanvas.width = video.videoWidth;
  tempCanvas.height = video.videoHeight;
  tempCanvas.getContext("2d").drawImage(video, 0, 0);

  tempCanvas.toBlob(async (blob) => {
    try { // ✅ FIX 7: Added try/catch — handles backend being offline

      const formData = new FormData();
      formData.append("image", blob, "capture.jpg");

      const res = await fetch("../backend/predict", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Server error: " + res.status); // ✅ FIX 8: Check for HTTP errors

      const data = await res.json();
      alert(`Hair Type: ${data.hair_type} (${data.confidence}% confidence)`);

    } catch (err) {
      console.error("Prediction failed:", err);
      alert("Could not connect to the AI backend. Make sure app.py is running.");
    }
  }, "image/jpeg");
}

// ===== SAVE STYLE =====
async function saveStyle() {
  const link = document.createElement("a");
  link.download = "my_hairstyle.png";
  link.href = canvas.toDataURL();
  link.click();
}