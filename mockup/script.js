const slider = document.getElementById("myRange")
const indicator = document.getElementById("slider-value-indicator")

slider.oninput = function () {
  updateIndicator()
}

function updateIndicator() {
  indicator.innerHTML = slider.value
  indicator.style.width = `${slider.value}%`
}

updateIndicator()