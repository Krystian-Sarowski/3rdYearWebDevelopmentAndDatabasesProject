from flask import Flask, render_template, session, request
import random
import pickle
import os
import datetime

FNAME = "data/results.pickle"

app = Flask(__name__)

@app.route("/game")
def start_page():
    num_to_guess = random.randint(1,1000) #The number is generated that the player needs to guess to win.
    session["numToGuess"] = num_to_guess #Assign the number the player needs to guess to session.
    session["startTime"] = datetime.datetime.now() #Assign the starting time to the session.
    session["numOfTries"] = 0   #Assign the number of attempts the player has made to session.
    return render_template(
        "game.html",
        the_num= "",
        the_title= "Simple guessing game"
    ) #Output the game template for the first time to the player.

@app.route("/game", methods=["POST"])
def refresh_page():
    if request.form["guessedNum"] != "":
        guessed_num = int(request.form["guessedNum"])
        if guessed_num >= 1 and guessed_num <= 1000:
            num_to_guess = session["numToGuess"]
            num_of_tries = session["numOfTries"]
            num_of_tries += 1
            session["numOfTries"] = num_of_tries 
            response = ""
            if num_to_guess == guessed_num:
                start_time = session["startTime"]
                now_time = datetime.datetime.now()
                #Calculates elapsed time by subtracting starting time from the current time and
                #converts it into seconds and sets it as an int so it can be saved to file.
                elapsed_time = int((now_time - start_time) / datetime.timedelta(seconds=1))
                session["TimeTaken"] = elapsed_time #Assigns the elapsed time to the session.
                return render_template(
                "win.html",
                num_of_tries = num_of_tries,
                the_title="Simple Guessing Game",
                system_response = "Congratulations, you guessed correctly!"
                ) #Output the win template as the player has guessed the number.
            elif num_to_guess < guessed_num:
                response = "Sorry, your guess is too high."
            else:
                response = "Sorry, your guess is too low."      
            return render_template(
                "game.html",
                the_num = guessed_num,
                the_title="Simple Guessing Game",
                system_response = response
            ) #Output the game template again as the player failed to guess the number.
        else:
            return render_template(
            "retry.html",
            the_title="Simple guessing game",
            system_response = "You need to enter a number between 1 and 1000"
        )  #Output the retry template as the player has not entered a number between 1 and 1000.
    else:
        return render_template(
            "retry.html",
            the_title="Simple guessing game",
            system_response = "You need to enter a number"
        ) #Output the retry template as the player has not entered a number.

@app.route("/record", methods=["POST"])
def record_score():
    player_name = request.form["name"]
    num_of_tries = session["numOfTries"]
    elapsed_time = session["TimeTaken"]
    if not os.path.exists(FNAME):
        data = []
    else:
        with open(FNAME, "rb") as pf: #Go and get data from the pickle file
            data = pickle.load(pf)
    data.append((num_of_tries, elapsed_time, player_name)) #Race Condition
    data=sorted(data, key = lambda i: (i[0], i[1])) #Sort the array based on the number of attempts then based on the time taken.
    finish_index = 0
    for sublist in data: #Serches for the position the user's entry is in.
        if sublist[0] == num_of_tries and sublist[1] == elapsed_time and sublist[2] == player_name:
            finish_index += 1
            break
        else:
            finish_index += 1
    with open(FNAME, "wb") as pf:
        pickle.dump(data, pf)         #Write the data to the pickle file, it overwrites the data in the pickle data
    return "Your time and number of attempts was recorded. You are number " + str(finish_index) + " in the list."

@app.route("/highscores")
def show_scores():
    with open(FNAME, "rb") as pf: #Go and get data from the pickle file
            data = pickle.load(pf)  
    return render_template(
        "results.html",
        the_title = "Results of all the player's",
        table_title_0 = "Player Name",
        table_title_1 = "Number Of Attempts",
        table_title_2 = "Time Taken(Seconds)",
        the_data = data 
    )

app.secret_key = "buffdvnfdidvinfdvn[fiodfsdmjfie[wnf[sodnf]]]"

app.run(debug=True)