from django.db import models
from django.utils import timezone  # Import timezone to get current time

# Word Model
class Word(models.Model):
    word = models.CharField(max_length=50, unique=True) # Stores Word & Must Be Unique
    hint = models.TextField() # Stores Hint Related To The Word
    meaning = models.TextField() # Stores Meaning Of The Word
    translation = models.TextField() # Stores Translation Of The Word In English
    translated_definition = models.TextField() # Stores Word Definition
    created_at = models.DateTimeField(default=timezone.now)  # Automatically adds the timestamp when the word is created

    # How Player Object is displayed in The Admin Interface
    def __str__(self): # Defini
        return self.word
    
    class Meta:
        ordering = ['created_at']  # Ensure words are ordered by the time they were added (ascending order)
    
# Player Model
class Player(models.Model):
    name = models.CharField(max_length=50, unique=True) # Stores Player's Name & Must Be Unique
    score = models.IntegerField(default=0) # Stores Players Score & Its Default is 0
    level = models.IntegerField(default=1) # Stores Players Current Level & Its Default is 1
    played_words = models.ManyToManyField(Word,related_name='players', blank=True) # Played Words Store & Can Be Left Initially Empty At The Game Start

    # How Player Object is displayed in The Admin Interface
    def __str__(self):
        return self.name

# States Model
class States(models.Model):
    gamestate = models.BooleanField(default=True)
    halfgamestate = models.BooleanField(default=False)
    dormant = models.BooleanField(default=False)

    def set_gamestate(self):
        self.gamestate = True
        self.halfgamestate = False
        self.dormant = False
        self.save()
    
    def set_halfgamestate(self):
        self.gamestate = False
        self.halfgamestate = True
        self.dormant = False
        self.save()

    def set_dormantstate(self):
        self.gamestate = False
        self.halfgamestate = False
        self.dormant = True
        self.save()

        
    def __str__(self):
        return f"GameState: {self.gamestate}, HalfGameState: {self.halfgamestate}, Dormant: {self.dormant}"


# SHORT NOTES
# Django Models are Python Classes That Define The Structure Of The Database.