let keyboard;

        document.getElementById("startButton").addEventListener("click", function() {
            if (/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)) {
                let keyboardContainer = document.getElementById("keyboardContainer");
                
                // Create keyboard div if not exists
                if (!keyboard) {
                    keyboard = new SimpleKeyboard.default({
                        onChange: input => console.log("Typed:", input),
                        layout: {
                            default: ["1 2 3 4 5 6 7 8 9 0", "q w e r t y u i o p", "a s d f g h j k l", "z x c v b n m {bksp}", "{space}"]
                        }
                    });
                } 

                // Toggle visibility by modifying inline styles
                keyboardContainer.style.display = keyboardContainer.style.display === "none" ? "block" : "none";
            } else {
                alert("This feature is only available on mobile devices.");
            }
        });
