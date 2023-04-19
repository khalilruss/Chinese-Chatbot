 # FYP-Chinese-Chatbot
A protype chatbot system that, through conversation in the form of messages, determines a
user’s proficiency in Mandarin Chinese in an attempt to address the
Language Learning Plateau.

**See [here](FYP_Chinese_Chatbot_Demo.mp4?raw=true) for explanation video.** <br />
**See [here](Using%20Natural%20Language%20Processing%20and%20Machine%20Learning%20to%20address%20the%20Language%20Learning%20Plateau.pdf) for full project report.**

# System Architecture 
The prototype system uses a micro-service architecture comprising of 7 micro-services: User interface (UI) for displaying the user interface, 
User Authentication for authentication, Chatbot for chatbot functionality, Classifier for proficiency classification of user responses, 
Grammar Extractor for grammar pattern extraction, coreNLP for tokenization and POS tagging, and Database for information storage.
![Screenshot from 2023-04-18 18-12-52](https://user-images.githubusercontent.com/47543130/232853584-69999ec0-2aa8-4416-9192-adfee66034ba.png)

# Deploy the system locally
Ensure that docker and docker-compose are installed on the target computer and ports 3000,8000,8001,8002,8005,9001 and 5432 don't have any services running on them. 
Clone this repo and run the command ***‘docker-compose --env-file ./.env.dev up -d’*** from the main directory
