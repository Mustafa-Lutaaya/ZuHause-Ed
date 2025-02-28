from django.shortcuts import render, redirect
from .models import Word, Player
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json

def main(request):
    return render(request, 'main.html')

def whack(request):
    return render(request, 'whack.html')

MAX_WRONG_GUESSES = 12  # Number of wrong attempts before game over

def zhed(request):
    # Game Is Initially Inactive
    game_state = request.session.get("game_state", False)

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
            request.session["game_state"] = False  # ✅ Reset game state
            request.session['show_hint'] = False  # By default, don't show hint

            messages.success(request, f"Welcome, {player_name}!" if created else f"Welcome back, {player_name}!")

            game_state = request.session.get("game_state", False)

            return redirect("zhed")  # Refresh the page

    # Game Start
    if "start_game" in request.POST:
        request.session["game_state"] = True # Set Game State To Active

        word = Word.objects.first()
        if not word:
            return render(request, {'message': "No more words available!"})

        guessed_word = ""
        correct_guesses = request.session.get('correct_guesses', [])

        for letter in word.word:
            if letter in correct_guesses:
                guessed_word += letter
            else:
                guessed_word += " _ "
                
        request.session['guessed_word'] = guessed_word  # Store the guessed word in session 
        request.session['word'] = word.word.lower()
        request.session['get_hint'] = word.hint
        request.session['meaning'] = word.meaning
        request.session['translation'] = word.translation
        request.session['translated_definition'] = word.translated_definition
        request.session['correct_guesses'] = []
        request.session['wrong_guesses'] = 0
        request.session['game_active'] = True
        request.session['show_hint'] = False  # By default, don't show hint
        
        return redirect("zhed") # Reload page to reflect changes
    
     # Show hint request handling
    if "show_hint" in request.POST:
        request.session['show_hint'] = True  # Set flag to show the hint

    
    # Handling letter guesses
    if request.method == "POST" and "letter" in request.POST:
        if not game_state:  # Allows guesses only when the game is active
            return redirect("zhed")
        
        guessed_letter = request.POST.get("letter").lower()

        word = request.session.get('word', '')  # Retrieve the current word from session
        if word == '':  # If the word is not in session, fetch it again
            word = Word.objects.first()
        

        if guessed_letter.isalpha() and len(guessed_letter) == 1:  # Valid guess
            correct_guesses = request.session.get('correct_guesses', [])  # Fetch the current correct guesses list
            if guessed_letter in word:
                if guessed_letter not in correct_guesses:
                    correct_guesses.append(guessed_letter)
            else:
                request.session['wrong_guesses'] += 1

        # If the player has lost, end the game
        if request.session['wrong_guesses'] >= MAX_WRONG_GUESSES:
            return render(request, 'zhed.html', {'message': "Game Over! You've lost!"})

        # If the word is fully guessed, end the game
        if all(letter in correct_guesses for letter in word):
            player = Player.objects.get(name=request.session.get("player_name"))
            player.score += 10  # Or calculate based on word length or other factors
            player.save()
            request.session["player_score"] = player.score  # Update session score
            return render(request, 'whack.html', {
                'message': f"Well done! You guessed the word: {word.capitalize()}."
            })

        return redirect("zhed")  # Continue the game if guesses are incorrect or correct
    
    # Game Pause
    if "pause_game" in request.POST:
        request.session["game_state"] = False # Set Game State To Inactive
        request.session['show_hint'] = False  # By default, don't show hint
        return redirect("zhed") # Reload page to reflect changes

    # Ensure player is logged for updated diplays
    player_name = request.session.get("player_name")
    player = Player.objects.get(name=player_name)
    scores = list(Player.objects.order_by("-score").values("name", "score"))  # Convert to list
    word = Word.objects.first()
    
    # Ensure session data is up-to-date
    request.session["player_score"] = player.score
    request.session["player_level"] = player.level
    request.session["player_name"] = player.name  
    request.session['word'] = word.word.lower()
    request.session['get_hint'] = word.hint
 

    
    return render(request, 'Zhed.html', {
        'player_name': player_name,
        'player_score': request.session["player_score"],
        'player_level': request.session["player_level"],
        'scores': scores,
        'game_state': game_state,
        'word': word.word.lower(),
        'get_hint': request.session.get('get_hint', ''),
        'wrong_guesses': request.session.get('wrong_guesses',0),
        'show_hint': request.session.get('show_hint', False)

            })
    
    

        
    





































    
    
    
#     # Fetch a new word if one is not already in session
#     if 'target_word' not in request.session:
#         word = Word.objects.exclude(id__in=player.played_words.all()).first()
#         if not word:
#             return render(request, 'game_over.html', {'message': "No more words available!"})

#         request.session['target_word'] = word.word.lower()
#         request.session['hint_text'] = word.hint
#         request.session['meaning'] = word.meaning
#         request.session['translation'] = word.translation
#         request.session['translated_definition'] = word.translated_definition
#         request.session['correct_guesses'] = []
#         request.session['wrong_guesses'] = 0
#         request.session['game_active'] = True
    
#         # Handle button clicks
#     if request.method == "POST":
#         if "hint_button" in request.POST:
#             return render(request, 'Zhed.html', {
#                 'player_name': player_name,
#                 'player_score': request.session["player_score"],
#                 'player_level': request.session["player_level"],
#                 'hint': request.session.get('hint_text'),
#                 'target_word': request.session.get('target_word'),
#                 'guessed_letters': request.session.get('correct_guesses', []),
#                 'wrong_guesses': request.session.get('wrong_guesses', 0),
#                 'game_active': request.session.get('game_active', True),
#                 'show_hint': True
#             })

#         if "score_button" in request.POST:
#             scores = Player.objects.order_by("score").values("name", "score")
#             return render(request, 'Zhed.html', {
#                 'player_name': player_name,
#                 'player_score': request.session["player_score"],
#                 'player_level': request.session["player_level"],
#                 'target_word': request.session.get('target_word'),
#                 'guessed_letters': request.session.get('correct_guesses', []),
#                 'wrong_guesses': request.session.get('wrong_guesses', 0),
#                 'game_active': request.session.get('game_active', True),
#                 'scores': scores
#             })

#    # Handle guessing
#     if request.method == "POST" and "letter" in request.POST:
#         guessed_letter = request.POST.get("letter", "").lower()

#         if guessed_letter and guessed_letter.isalpha() and len(guessed_letter) == 1:
#             if guessed_letter in request.session['target_word']:
#                 if guessed_letter not in request.session['correct_guesses']:
#                     request.session['correct_guesses'].append(guessed_letter)
#             else:
#                 request.session['wrong_guesses'] += 1
#                 if request.session['wrong_guesses'] >= MAX_WRONG_GUESSES:
#                     request.session['game_active'] = False

#         # Check if the word is fully guessed
#         guessed_word = ''.join([letter if letter in request.session['correct_guesses'] else '_' for letter in request.session['target_word']])
#         if guessed_word == request.session['target_word']:
#             player.score += 10 if len(request.session['target_word']) < 15 else 15
#             player.played_words.add(Word.objects.get(word=request.session['target_word']))
#             player.save()
#             request.session["player_score"] = player.score  # Update score in session
#             request.session['game_active'] = False  # End game




# def mark_word(request, player_id, word_id):
#     player = Player.objects.get(id=player_id)
#     word = Word.objects.get(id=word_id)

#     # Add The Word To Player's Played Words
#     player.played_words.add(word)
#     player.correct_guesses_count += 1
#     player.save()

#     # ✅ Correctly handle leveling up
#     if player.correct_guesses_count >= 7:
#         player.level += 1
#         player.correct_guesses_count = 0  
#         player.save()

#     return JsonResponse({'message': f'Word "{word.word}" guessed correctly!', 'level': player.level})
