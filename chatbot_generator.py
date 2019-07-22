from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from chatterbot import ChatBot

YAML_CORPUS = "reddit_data/all.yml"


chatbot = ChatBot("Doc")

trainer = ChatterBotCorpusTrainer(chatbot)

trainer.train(YAML_CORPUS)

# TODO change that line in chatbot sourcecode for text interpretation Pull Request.

while True:
    try:
        question = input("You:")
        bot_input = chatbot.get_response(question)
        print(f"{chatbot.name}:{bot_input}")

    except (KeyboardInterrupt, EOFError, SystemExit):
        break
