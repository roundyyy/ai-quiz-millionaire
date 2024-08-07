import tkinter as tk
from tkinter import ttk
import requests
import json
import pygame
import random
import os

LLAMA_API_URL = "http://localhost:11434/api/generate"
LLAMA_TAGS_URL = "http://localhost:11434/api/tags"
CACHED_QUESTIONS_FILE = "cached_questions.txt"


class QuizMillionaireChallenge:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz Millionaire Challenge")
        self.master.geometry("1200x1000")
        self.master.configure(bg="#0A0A23")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "TLabel",
            background="#0A0A23",
            foreground="white",
            font=("Arial", 15, "bold"),
        )
        self.style.configure(
            "TButton",
            background="#1C1C3C",
            foreground="white",
            font=("Arial", 12, "bold"),
            padding=10,
        )

        self.model_var = tk.StringVar(value="Select Model")
        self.model_menu = ttk.OptionMenu(master, self.model_var, "Select Model")
        self.model_menu.pack(pady=10)
        self.fetch_and_update_models()

        self.start_button = ttk.Button(
            master, text="Start Game", command=self.start_game
        )
        self.start_button.pack(pady=20)

        self.money_levels = [
            100,
            200,
            300,
            500,
            1000,
            2000,
            4000,
            8000,
            16000,
            32000,
            64000,
            125000,
            250000,
            500000,
            1000000,
        ]
        self.current_level = 0

        self.question_label = ttk.Label(master, text="", wraplength=750)
        self.question_label.pack(pady=20)

        self.answer_buttons = []
        for i in range(4):
            button = ttk.Button(
                master, text="", width=70, command=lambda x=i: self.check_answer(x)
            )
            button.pack(pady=5)
            self.answer_buttons.append(button)

        self.next_button = ttk.Button(
            master, text="Next Question", command=self.next_question
        )
        self.next_button.pack(pady=20)
        self.next_button.config(state=tk.DISABLED)

        self.money_label = ttk.Label(master, text="$0", font=("Arial", 24, "bold"))
        self.money_label.pack(pady=10)

        self.result_label = tk.Text(master, wrap=tk.WORD, height=10, width=80)
        self.result_label.pack(pady=10)
        self.result_label.config(state=tk.DISABLED)

        self.lifeline_frame = ttk.Frame(master)
        self.lifeline_frame.pack(pady=10)

        self.lifelines = {
            "50:50": ttk.Button(
                self.lifeline_frame, text="50:50", command=self.fifty_fifty
            ),
            "Phone a Friend": ttk.Button(
                self.lifeline_frame, text="Phone a Friend", command=self.phone_friend
            ),
            "Ask the Audience": ttk.Button(
                self.lifeline_frame, text="Ask the Audience", command=self.ask_audience
            ),
        }

        for lifeline in self.lifelines.values():
            lifeline.pack(side=tk.LEFT, padx=5)

        self.lifeline_used = {
            "50:50": False,
            "Phone a Friend": False,
            "Ask the Audience": False,
        }

        self.restart_button = ttk.Button(
            master, text="Restart Game", command=self.restart_game
        )
        self.restart_button.pack(pady=10)
        self.restart_button.config(state=tk.DISABLED)

        self.current_question = None
        self.cached_questions = self.load_cached_questions()  # Load cached questions
        pygame.mixer.init()

    def start_game(self):
        self.current_level = 0
        self.money_label.config(text="$0")
        self.next_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)
        self.lifeline_used = {key: False for key in self.lifeline_used}
        for lifeline in self.lifelines.values():
            lifeline.config(state=tk.NORMAL)
        self.next_question()

    def fetch_and_update_models(self):
        try:
            response = requests.get(LLAMA_TAGS_URL)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                if model_names:
                    self.model_menu["menu"].delete(0, "end")
                    for model_name in model_names:
                        self.model_menu["menu"].add_command(
                            label=model_name,
                            command=lambda value=model_name: self.model_var.set(value),
                        )
                    self.model_var.set(
                        model_names[0]
                    )  # Set the first fetched model as default
                return model_names
            else:
                print(
                    f"Failed to fetch Ollama models. Status code: {response.status_code}"
                )
                return []
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
            return []

    def load_cached_questions(self):
        if not os.path.exists(CACHED_QUESTIONS_FILE):
            return set()
        with open(CACHED_QUESTIONS_FILE, "r") as file:
            questions = file.readlines()
        return set(q.strip() for q in questions)

    def save_cached_question(self, question):
        with open(CACHED_QUESTIONS_FILE, "a") as file:
            file.write(question + "\n")

    def get_question_from_ollama(self):
        try:
            seed = random.randint(0, 1000000000)
            # print(f"Using seed: {seed}")
            difficulty = (self.current_level + 1) / len(self.money_levels)
            # print(f"Current difficulty: {difficulty}")
            temperature = random.uniform(0.1, 0.4)
            top_p = random.uniform(0.2, 0.5)
            frequency_penalty = random.uniform(0.8, 1.0)
            presence_penalty = random.uniform(0.7, 1.0)

            cached_questions_instruction = "Do not ask these questions: " + ", ".join(
                [f'"{q}"' for q in self.cached_questions]
            )

            instruction = f"""Generate a random question.
            The question must be from any area of knowledge you have been trained on.
            Ensure the question is unique and not a repeat.
            Use the seed {seed} for randomization and set the difficulty based on a scale from 1 to 15, where 1 is very easy and 15 is very difficult. Current difficulty: {difficulty * 15}.
            Provide the question, four possible answers, and the correct answer index (0-3) in JSON format.
            Use proper punctuation in the question and answers.
            {cached_questions_instruction}
            Example format:
            {{
                "question": "Which famous scientist developed the theory of general relativity?",
                "answers": ["Isaac Newton", "Albert Einstein", "Stephen Hawking", "Niels Bohr"],
                "correct_answer": 1
            }}"""

            payload = {
                "model": self.model_var.get(),
                "prompt": instruction,
                "format": "json",
                "stream": False,
                "option": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "seed": seed,
                    "repeat_penalty": 1.2,
                    "frequency_penalty": frequency_penalty,
                    "presence_penalty": presence_penalty,
                    "num_ctx": 128000,
                },
            }

            response = requests.post(LLAMA_API_URL, json=payload, stream=True)
            response_text = ""
            for line in response.iter_lines():
                if line:
                    response_text += line.decode("utf-8")

            if response.status_code == 200:
                response_json = json.loads(response_text)
                if "response" in response_json:
                    question_data = json.loads(response_json["response"])
                    self.cached_questions.add(
                        question_data["question"]
                    )  # Cache the new question
                    self.save_cached_question(question_data["question"])  # Save to file
                    return question_data
                else:
                    raise ValueError("Invalid response structure")
            else:
                raise ValueError(
                    f"Error from Ollama local model: {response.status_code} {response.text}"
                )
        except Exception as e:
            self.result_label.config(state=tk.NORMAL)
            self.result_label.delete("1.0", tk.END)
            self.result_label.insert(
                tk.END, f"Error: Failed to fetch question from Ollama API: {str(e)}"
            )
            self.result_label.config(state=tk.DISABLED)
            return None

    def next_question(self):
        if self.current_level < len(self.money_levels):
            self.result_label.config(state=tk.NORMAL)
            self.result_label.delete("1.0", tk.END)
            self.result_label.config(state=tk.DISABLED)
            question_data = self.get_question_from_ollama()
            if question_data:
                self.current_question = question_data
                self.question_label.config(text=question_data["question"])
                for i, button in enumerate(self.answer_buttons):
                    button.config(text=question_data["answers"][i], state=tk.NORMAL)
                self.next_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.DISABLED)
            else:
                self.question_label.config(
                    text="Failed to fetch question. Please try again."
                )
        else:
            self.result_label.config(state=tk.NORMAL)
            self.result_label.insert(tk.END, "Congratulations! You've won $1,000,000!")
            self.result_label.config(state=tk.DISABLED)
            self.money_label.config(text="$1,000,000")
            self.next_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)

    def check_answer(self, selected_index):
        if self.current_question:
            correct_index = self.current_question["correct_answer"]
            if selected_index == correct_index:
                pygame.mixer.music.load("Audio/good.mp3")
                pygame.mixer.music.play()
                self.current_level += 1
                if self.current_level == len(self.money_levels):
                    self.result_label.config(state=tk.NORMAL)
                    self.result_label.delete("1.0", tk.END)
                    self.result_label.insert(
                        tk.END, "Congratulations! You've won $1,000,000!"
                    )
                    self.result_label.config(state=tk.DISABLED)
                    self.money_label.config(text="$1,000,000")
                    self.next_button.config(state=tk.DISABLED)
                    self.restart_button.config(state=tk.NORMAL)
                else:
                    self.result_label.config(state=tk.NORMAL)
                    self.result_label.delete("1.0", tk.END)
                    self.result_label.insert(
                        tk.END,
                        f"Correct! You've won ${self.money_levels[self.current_level-1]}",
                    )
                    self.result_label.config(state=tk.DISABLED)
                    self.money_label.config(
                        text=f"${self.money_levels[self.current_level-1]}"
                    )
                    self.next_button.config(state=tk.NORMAL)
            else:
                pygame.mixer.music.load("Audio/bad.mp3")
                pygame.mixer.music.play()
                self.result_label.config(state=tk.NORMAL)
                self.result_label.delete("1.0", tk.END)
                self.result_label.insert(
                    tk.END,
                    f"I'm sorry, that's incorrect. You've lost everything. The correct answer was: {self.current_question['answers'][correct_index]}",
                )
                self.result_label.config(state=tk.DISABLED)
                self.current_level = 0
                self.money_label.config(text="$0")
                self.next_button.config(state=tk.DISABLED)
                self.restart_button.config(state=tk.NORMAL)

            for button in self.answer_buttons:
                button.config(state=tk.DISABLED)

    def fifty_fifty(self):
        pygame.mixer.music.load("Audio/5050.mp3")
        pygame.mixer.music.play()
        correct_index = self.current_question["correct_answer"]
        wrong_indices = [i for i in range(4) if i != correct_index]
        remove_indices = random.sample(wrong_indices, 2)
        for i in remove_indices:
            self.answer_buttons[i].config(state=tk.DISABLED)
        self.lifelines["50:50"].config(state=tk.DISABLED)
        self.lifeline_used["50:50"] = True

    def phone_friend(self):
        pygame.mixer.music.load("Audio/phone.mp3")
        pygame.mixer.music.play()
        self.get_lifeline_help(
            "Imagine you are a friend being called for help in Who Wants to Be a Millionaire?. Provide your best guess for the correct answer and a brief explanation why."
        )
        self.lifelines["Phone a Friend"].config(state=tk.DISABLED)
        self.lifeline_used["Phone a Friend"] = True

    def ask_audience(self):
        pygame.mixer.music.load("Audio/audience.mp3")
        pygame.mixer.music.play()
        self.get_lifeline_help(
            "Simulate an audience poll for this question like in Who Wants to Be a Millionaire? tv show. Provide percentage guesses for each answer, ensuring they add up to 100%. Return the result as a JSON object with keys A, B, C, D and their corresponding percentage values."
        )
        self.lifelines["Ask the Audience"].config(state=tk.DISABLED)
        self.lifeline_used["Ask the Audience"] = True

    def get_lifeline_help(self, instruction):
        try:
            payload = {
                "model": self.model_var.get(),
                "prompt": f"{instruction}\n\nQuestion: {self.current_question['question']}\nAnswers: {self.current_question['answers']}",
                "format": "json",
                "stream": False,
            }

            response = requests.post(LLAMA_API_URL, json=payload, stream=True)
            response_text = ""
            for line in response.iter_lines():
                if line:
                    response_text += line.decode("utf-8")

            if response.status_code == 200:
                response_json = json.loads(response_text)
                if "response" in response_json:
                    help_text = json.loads(response_json["response"])
                    if instruction.startswith("Simulate an audience poll"):
                        formatted_text = "Audience Poll Results:\n"
                        for key, value in help_text.items():
                            formatted_text += f"{key}: {value}%\n"
                        self.result_label.config(state=tk.NORMAL)
                        self.result_label.delete("1.0", tk.END)
                        self.result_label.insert(tk.END, formatted_text)
                    else:
                        self.result_label.config(state=tk.NORMAL)
                        self.result_label.delete("1.0", tk.END)
                        self.result_label.insert(tk.END, help_text)
                    self.result_label.config(state=tk.DISABLED)
                else:
                    raise ValueError("Invalid response structure")
            else:
                raise ValueError(
                    f"Error from Ollama local model: {response.status_code} {response.text}"
                )
        except Exception as e:
            self.result_label.config(state=tk.NORMAL)
            self.result_label.delete("1.0", tk.END)
            self.result_label.insert(
                tk.END, f"Error: Failed to get lifeline help: {str(e)}"
            )
            self.result_label.config(state=tk.DISABLED)

    def restart_game(self):
        self.current_level = 0
        self.money_label.config(text="$0")
        self.next_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)
        self.lifeline_used = {key: False for key in self.lifeline_used}
        for lifeline in self.lifelines.values():
            lifeline.config(state=tk.NORMAL)
        self.next_question()


if __name__ == "__main__":
    root = tk.Tk()
    game = QuizMillionaireChallenge(root)
    root.mainloop()
