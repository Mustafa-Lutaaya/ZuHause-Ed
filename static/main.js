document.addEventListener("DOMContentLoaded", function () {
    let keyboard;

    document.getElementById("startButton").addEventListener("click", function () {
        console.log("Start Button Clicked!"); // For debugging
        
        // Only show the virtual keyboard on mobile devices
        if (/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)) {
            let keyboardInput = document.getElementById("keyboardInput");

            // Show the input field (previously hidden)
            keyboardInput.style.display = "block";

            // Initialize the virtual keyboard
            $(keyboardInput).keyboard({
                layout: 'qwerty',
                alwaysOpen: true,
                customLayout: {
                    'normal': [
                        '1 2 3 4 5 6 7 8 9 0',
                        'q w e r t y u i o p',
                        'a s d f g h j k l',
                        'z x c v b n m',
                        '{space} {bksp}'
                    ]
                },
                // Optional: Set up events (e.g., for typing)
                change: function(e, keyboard, el) {
                    console.log("Current input: ", el.value);
                }
            });

            // Focus on the input to start typing
            keyboardInput.focus();
        } else {
            alert("This feature is only available on mobile devices.");
        }
    });
});
