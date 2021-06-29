const audio = document.getElementsByTagName("audio")[0]
const playButton = document.getElementById("play")

playButton.addEventListener('click', () => {
  audio.play()
})

// for (let i = 1; i < 78; i++){
//     const audio = document.getElementsByTagName("audio")[0]
//     const playButton = document.getElementById("play")
    
//     playButton.addEventListener('click', () => {
//     audio.play()
//     })
//     console.log(audio)
//     }