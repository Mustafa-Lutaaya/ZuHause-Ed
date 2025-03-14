from django.shortcuts import render, redirect
from .models import Word, Player, States
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json

def main(request):
    return render(request, 'main.html')



def zhed(request):
    # Fetch or create the game state
    zone, _ = States.objects.get_or_create(id=1)

   # Ensure session variables are properly initialized
    if "gamestate" not in request.session:
        request.session["gamestate"] = zone.gamestate
    if "halfgamestate" not in request.session: 
        request.session["halfgamestate"] = zone.halfgamestate
    if "dormant" not in request.session:
        request.session["dormant"] = zone.dormant
   
    # Login
    if request.method == "POST":
        if "name" in request.POST:
            player_name = request.POST.get("name").strip()
            if not player_name:
                messages.error(request, "Please enter a valid name.")
                return redirect('/')
            
            player, created = Player.objects.get_or_create(name=player_name)
            request.session["player_name"] = player.name  # Store player in session
            request.session["player_score"] = player.score
            request.session["player_level"] = player.level
            request.session["played_words"] = list(player.played_words.values_list("id", flat=True))  # Stores list of word IDs
            request.session['show_hint'] = False  # By default, don't show hint

            messages.success(request, f"Welcome, {player_name}!" if created else f"Welcome back, {player_name}!")
            
            
            # Game is inactive after login
            zone.gamestate = False
            zone.halfgamestate = False
            zone.dormant = False
            zone.save()
            
            return redirect("zhed")  # Refresh the page
    
    MAX_WRONG_GUESSES = 13  # Number of wrong attempts before game over

    player_name = request.session.get("player_name")
    player = Player.objects.get(name=player_name)
    played_words = player.played_words.all()
    word = Word.objects.exclude(id__in=played_words.values_list("id", flat=True)).first()
    scores = list(Player.objects.order_by("-score").values("name", "score"))  # Convert to list
    
    # Game Start
    if "start_game" in request.POST:
        zone.gamestate = True
        zone.halfgamestate = False
        zone.dormant = False
        zone.save()
        
        
        if word:
            request.session["word"] = word.word.lower()
            request.session["get_hint"] = word.hint
            request.session["meaning"] = word.meaning
            request.session["translation"] = word.translation
            request.session["translated_definition"] = word.translated_definition
            correct_guesses = request.session.get("correct_guesses", [])
            correct_guesses_count = request.session.get("correct_guesses", [])
            wrong_guesses = request.session.get ("wrong_guesses", []) # Wrong Guesses stored as an Intenger Count
        else:
            request.session["word"] = ""  
            request.session["get_hint"] = ""
            messages.warning(request, "No new words available!")
            return redirect("zhed") # Reload page to reflect changes
    
    # Guess Letter
    if "letter" in request.POST:
        cgw = ""
        # played_words = request.session.get("played_words",[])
        word = request.session.get("word", "")
        correct_guesses = request.session.get("correct_guesses", [])
        correct_guesses_count = request.session.get("correct_guesses", [])
        wrong_guesses = request.session.get ("wrong_guesses", []) # Wrong Guesses stored as an Intenger Count
        player_name  = request.session["player_name"] # Store player in session

        letter = request.POST.get("letter", "").lower()

        if letter.isalpha() and len(letter) == 1:
            if letter in word:
                if letter not in correct_guesses:
                    correct_guesses.append(letter)
                    # cgw += letter
                    messages.success(request, f"Great Guess, {player_name}!")

            else:
                wrong_guesses.append(letter)
                # cgw += "_"
                messages.success(request, f"Wrong Guess, {player_name}!")

                if len(wrong_guesses) == (MAX_WRONG_GUESSES -5):
                    messages.success(request, f"Time's Almost Up, {player_name}!")

            # Save updates to session
            request.session["correct_guesses"] = correct_guesses
            request.session["wrong_guesses"] = wrong_guesses   # Store as an integer
            
            # Check for Win Condition
            if all(l in correct_guesses for l in word):
                correct_guesses_count.append(word)
                zone.gamestate = False  # End game if word is fully guessed
                zone.dormant = True
                zone.save()

                word_obj = Word.objects.get(word=word)  # Get the actual word object
                player.played_words.add(word_obj)  # **✅ Store the word as played**
                request.session["played_words"] = list(player.played_words.values_list("id", flat=True))

                # messages.success(request, f"Congratulations {player_name}, you guessed the word!")
            
            # Check if the game is over due to too many wrong guesses
            if len(wrong_guesses) >  MAX_WRONG_GUESSES:
                zone.gamestate = False
                zone.dormant = True
                zone.save()

                # messages.error(request, f"Game Over, {player_name}. The word was '{word.upper()}'.")

            return redirect("zhed")

    # Show hint request handling
    if "show_hint" in request.POST:
        request.session['show_hint'] = True  # Set flag to show the hint
    
    # Game Pause
    if "pause_game" in request.POST:
        zone.gamestate = False
        zone.halfgamestate = True
        zone.save()
        request.session['show_hint'] = False  # By default, don't show hint
        return redirect("zhed") # Reload page to reflect changes
    
    # messages.error(request, f"Game Over, {player_name}. The word was '{word.upper()}'.")

    # **Ensure session data is updated**
    request.session["player_score"] = player.score
    request.session["player_level"] = player.level

    # Ensure player is logged for updated diplays
    player_name = request.session.get("player_name")
    player = Player.objects.get(name=player_name)
    
    # Ensure session data is up-to-date
    request.session["player_score"] = player.score
    request.session["player_level"] = player.level
    request.session["player_name"] = player.name  

    
    return render(request, 'Zhed.html', {
        "gamestate": zone.gamestate,
        "halfgamestate": zone.halfgamestate,
        "dormant": zone.dormant,
        'player_name': player_name,
        'player_score': request.session["player_score"],
        'player_level': request.session["player_level"],
        'scores': scores,
        'cgw': cgw,
        'word': word.word.lower(),
        'get_hint': request.session.get('get_hint', ''),
        'wrong_guesses': request.session.get('wrong_guesses',[]),
        'correct_guesses': request.session.get('correct_guesses',[]),
        'show_hint': request.session.get('show_hint', False)
            })


