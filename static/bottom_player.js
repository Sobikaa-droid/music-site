const bottom_audio = document.getElementById('bottom_audio');
const bottom_audio_title = document.getElementById('bottom_audio_title');
const bottom_audio_artist = document.getElementById('bottom_audio_artist');
const bottom_audio_image = document.getElementById('bottom_audio_image');
const progressSlider = document.getElementById('progressSlider');
const volumeSlider = document.getElementById('volumeSlider');
const muteButton = document.getElementById('muteButton');

let currentAudio = null;
let previousButton = null;

function playPauseAudio(id, button) {
  const audio = document.getElementById(id);
  const audio_title = document.getElementById('title' + id);
  const audio_artist = document.getElementById('artist' + id);
  const audio_image = document.getElementById('image' + id);

  bottom_audio.style.visibility = "visible";
  bottom_audio_title.textContent = audio_title.textContent;
  bottom_audio_artist.textContent = audio_artist.textContent;
  bottom_audio_image.src = audio_image.src;

  if (audio.paused) {
    if (currentAudio !== null && !currentAudio.paused) {
      currentAudio.pause();
    }

    if (previousButton !== null) {
      previousButton.innerHTML = '<i class="fa-solid fa-play"></i>';
    }
    audio.play();
    currentAudio = audio;
    button.innerHTML = '<i class="fa-solid fa-pause"></i>';
  } else {
    audio.pause();
    button.innerHTML = '<i class="fa-solid fa-play"></i>';
  }

  previousButton = button;

  /* Progress */

  progressSlider.addEventListener('input', function() {

    audio.currentTime = (progressSlider.value / 100) * audio.duration;
  });

  audio.addEventListener('timeupdate', function() {
    progressSlider.value = (audio.currentTime / audio.duration) * 100;
  });

  /* Volume */

  volumeSlider.addEventListener('input', function() {
    audio.volume = volumeSlider.value;
  });

  muteButton.addEventListener('click', function() {
    if (audio.muted) {
      audio.muted = false;
      muteButton.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
    } else {
      audio.muted = true;
      muteButton.innerHTML = '<i class="fa-solid fa-volume-xmark"></i>';
    }
  });
}