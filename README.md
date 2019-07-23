# Reddit Chatterbot

A script that turns reddit dumps into a chatbot. Made with [chatterbot](https://github.com/gunthercox/ChatterBot). 

## Instructions

Preferebly use python 3.6

1. Download a comment dumpt from pushshift's [incredible archive](https://files.pushshift.io/reddit/comments/) in `bz2` format.
2. Tweak variables on top of `database_builder.py` and run it.
3. Build a corpus of Q and As by tweaking the variables in `corpus_builder.py` and then running it. 
4. Tweak variables in `chatbot_generator.py` and run it. 
5. You should now be able to talk to your bot in the command line. 
