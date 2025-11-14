MESSAGES = {
    "start_prompt": "Choose an option:",
    "button_open_app": "Open AM Driving Exams",
    "button_about": "About the app",
    "button_feedback": "Feedback / report an issue",
    "about_text": (
        "This bot is the entry point to AM Driving Exams, a Telegram mini app for preparing for "
        "Armenia’s driving theory exams.\n\n"
        "<b>How it works</b>\n"
        "The app is based on the spaced repetition method, specifically the system designed by "
        "Sebastian Leitner in 1972. <a href='https://en.wikipedia.org/wiki/Leitner_system'>Learn more on Wikipedia.</a>\n\n"
        "Imagine you have a flashcard for every question and several boxes. Initially, all "
        "flashcards are in Box 1, which has the highest priority. When you answer a card correctly, "
        "it moves to Box 2, then to Box 3. If you later answer it incorrectly, it goes back to Box 1.\n\n"
        "Box 1 always has the highest priority—questions from it are always available for review. "
        "Cards in higher-numbered boxes become available after certain time intervals that follow "
        "the Fibonacci sequence (1, 2, 3, 5, 8, 13, 21, etc.). For example, a card in Box 2 becomes "
        "available in 1 day; in Box 3, in 2 days; and so on. This pushes well-remembered questions "
        "farther out while focusing your time on the harder ones.\n\n"
        "<b>How to use the app</b>\n\n"
        "If you’re new or want to quickly assess your readiness, start with the default "
        "“Quick revision → All questions” flow. You can also select specific topics by tapping the "
        "icon in the top right of the Select revision mode screen. Batch size is configured using the slider below.\n\n"
        "If you want to review only new questions or only those you answered incorrectly, choose "
        "the “New only” or “Only incorrect” modes. The “New” and “Mistakes” shortcuts on the home "
        "screen use default settings (batch size of 30; all topics included).\n\n"
        "<b>Where do the questions come from?</b>\n\n"
        "All questions are sourced from the Armenian Police’s official website and are based on "
        "the latest revision published in April 2022. <a href='https://www.police.am/%D5%BE%D5%A1%D6%80%D5%B8%D6%80%D5%A4%D5%A1%D5%AF%D5%A1%D5%B6-%D5%A5%D5%BE-%D5%A5%D6%80%D5%A9%D5%A5%D5%BE%D5%A5%D5%AF%D5%B8%D6%82%D5%A9%D5%B5%D5%A1%D5%B6-%D5%BF%D5%A5%D5%B2%D5%A5%D5%AF%D5%A1%D5%BF%D5%B8%D6%82/the-list-of-driving-theory-test-questions.html'>View questions here.</a>\n"
        "In their original form, the questions are organized into 10 topic-based groups. In the "
        "mini app, each group’s PDF is parsed into individual questions.\n\n"
        "The app currently supports Armenian, English, and Russian. Arabic and Farsi are planned.\n\n"
        "<b>What data does the app collect?</b>\n\n"
        "The app does not collect personal or sensitive data. From Telegram, it receives Telegram "
        "ID, username, first name, and last name.\n\n"
        "It also stores your settings (UI and exam language, daily goal, etc.) and your "
        "spaced-repetition progress.\n\n"
        "<b>How you can help</b>\n\n"
        "The app is in beta, so feedback is especially welcome. If you notice any issues with the "
        "questions (they're parsed automatically, i.e. orthography or style can't be judged,"
         "but a wrong answer or image can be) or the UI, or if you have any suggestions "
        "regarding the app's features and experience, please reach out via the /feedback command. "
        "Any help with Armenian localization is welcome, too — in the current version, the app's "
        "Armenian interface (and this bot's messages) are translated automatically.\n\n"
        "© Vlad Fediushin, 2025"
    ),
    "feedback_prompt": "Write a feedback message and send it here.",
    "feedback_thanks": "Thanks, your feedback was delivered.",
    "admin_feedback": "\U0001F4E9 Feedback from {profile}\nID: {user_id}\n\n{message}",
    "command_about": "About the app",
    "command_feedback": "Send feedback",
    "reminder_text": "Hi! Today's plan is {goal} questions. You've completed {done}. Keep pushing!"
}
