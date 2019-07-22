from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from chatterbot import ChatBot

chatbot = ChatBot("Doc")

trainer = ChatterBotCorpusTrainer(chatbot)

#trainer.train("chatterbot.corpus.english.greetings")
trainer.train("reddit_data/all.yml")

# TODO change that line in code for text interpretation Pull Request.

while True:
    try:
        question = input("You:")
        bot_input = chatbot.get_response(question)
        print(f"{chatbot.name}:{bot_input}")

    except (KeyboardInterrupt, EOFError, SystemExit):
        break
