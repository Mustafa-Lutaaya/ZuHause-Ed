from django.shortcuts import render, redirect
from .models import Word, Player, States
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json


zone, _ = States.objects.get_or_create(id=1)

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
            request.session['show_hint'] = False  # By default, don't show hint

            # Game is inactive after login
            zone.gamestate = False
            zone.halfgamestate = False
            zone.dormant = False
            zone.save()

            messages.success(request, f"Welcome, {player_name}!" if created else f"Welcome back, {player_name}!")
            
            return redirect("zhed")  # Refresh the page
    
    MAX_WRONG_GUESSES = 12  # Number of wrong attempts before game over
    player_name = request.session.get("player_name")
    player = Player.objects.get(name=player_name)
    played_words = player.played_words.all()
    scores = list(Player.objects.order_by("-score").values("name", "score"))  # Convert to list

    # Game Start
    if "start_game" in request.POST:
        request.session["played_words"] = list(player.played_words.values_list("id", flat=True))  # Stores list of word IDs
        zone.gamestate = True
        zone.halfgamestate = False
        zone.dormant = False
        zone.save()
        
        word = Word.objects.exclude(id__in=played_words.values_list("id", flat=True)).first()
        if word:
            request.session["cgw"] = [("__" if char != " " else "__") for char in word.word]  # Create a list with underscores for each letter in the word
            request.session['word'] = word.word.lower()
            request.session["get_hint"] = word.hint
            request.session["meaning"] = word.meaning
            request.session["translation"] = word.translation
            request.session["translated_definition"] = word.translated_definition
            correct_guesses = request.session.get("correct_guesses", [])
            correct_guesses_count = request.session.get("correct_guesses", [])
            wrong_guesses = request.session.get ("wrong_guesses", []) # Wrong Guesses stored as an Intenger Count
        else:
            messages.warning(request, "No new words available!")
            zone.gamestate = False  # End game if word is fully guessed
            zone.dormant = True
            zone.save()
        
        request.session["wrong_guesses"] = []
        request.session["correct_guesses"] = []
        request.session["show_hint"] = False
        
        return redirect("zhed") # Reload page to reflect changes

    # Guess Letter
    if zone.gamestate:
        if "letter" in request.POST:
            word = request.session.get("word", "")
            cgw = request.session.get("cgw", ["__" for _ in word])  # Retrieve existing cgw
            correct_guesses = request.session.get("correct_guesses", [])
            correct_guesses_count = request.session.get("correct_guesses", [])
            wrong_guesses = request.session.get ("wrong_guesses", []) # Wrong Guesses stored as an Intenger Count
            player_name  = request.session["player_name"] # Store player in session

            letter = request.POST.get("letter", "").lower()

            if letter.isalpha() and len(letter) == 1:
                if letter in word:
                    if letter not in correct_guesses:
                        correct_guesses.append(letter)

                    for index, char in enumerate(word):
                        if char == letter and cgw[index] == "__":
                            cgw[index] = letter  # Show only one occurrence
                            break  # Stop after revealing one letter

                        if char == " ":
                            cgw[index] = " "
        
                    request.session["cgw"] = cgw  # Store the updated cgw in the session
                    request.session["correct_guesses"] = correct_guesses  
                    messages.success(request, f"Great Guess, {player_name}!")

                else:
                    wrong_guesses.append(letter)
                    messages.success(request, f"Wrong Guess, {player_name}!")

                    if len(wrong_guesses) == (MAX_WRONG_GUESSES -5):
                        messages.success(request, f"Time's Almost Up, {player_name}!")

                # Save updates to session
                request.session["correct_guesses"] = correct_guesses
                request.session["wrong_guesses"] = wrong_guesses   # Store as an integer
                
                # Check for Win Condition
                if all(cgw[i] != "__" for i in range(len(word))):
                    correct_guesses_count.append(word)
                    player.score += 10  # Increment the player's score
                    player.save()  # Save the updated player score

                    zone.gamestate = False  # End game if word is fully guessed
                    zone.dormant = True
                    zone.save()

                    word_obj = Word.objects.get(word=word)  # Get the actual word object
                    player.played_words.add(word_obj)  # Store the word as played**

                    total_played = player.played_words.count()

                    if total_played % 10 == 0:
                        player.level += 1
                        player.save()
                        messages.success(request, f"We Just Levelled Up! {player_name}!")
                        request.session["player_level"] = player.level
                    request.session["played_words"] = list(player.played_words.values_list("id", flat=True))
                
                # Check if the game is over due to too many wrong guesses
                if len(wrong_guesses) >=  MAX_WRONG_GUESSES:
                    zone.gamestate = False
                    zone.dormant = True
                    zone.save()
                


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

    # Ensure player is logged for updated diplays
    player_name = request.session.get("player_name")
    player = Player.objects.get(name=player_name)
    scores = list(Player.objects.order_by("-score").values("name", "score"))  # Convert to list
    
    # Ensure session data is up-to-date
    request.session["player_score"] = player.score
    request.session["player_level"] = player.level
    request.session["player_name"] = player.name
    

    return render(request, 'Zhed.html', {
        
        "gamestate": zone.gamestate,
        "halfgamestate": zone.halfgamestate,
        "dormant": zone.dormant,
        'word': request.session.get("word", ""),
        'cgw': request.session.get("cgw", ["__" for _ in request.session.get("word", "")]),
        'player_name': player_name,
        'player_score': request.session["player_score"],
        'player_level': request.session["player_level"],
        'scores': scores,
        'get_hint': request.session.get('get_hint', ''),
        'wrong_guesses': request.session.get('wrong_guesses',[]),
        'correct_guesses': request.session.get('correct_guesses',[]),
        'show_hint': request.session.get('show_hint', False),
        'meaning': request.session.get("meaning", ""),
        'translation': request.session.get("translation", ""),
        'translated_definition': request.session.get("translated_definition", ""),
            })
