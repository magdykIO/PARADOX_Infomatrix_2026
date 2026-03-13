from AI import TODO


def start():
    quest = TODO()

    # Interaction with app
    big_task = input("Яку велику ціль ти хочеш досягти? ")
    print("\nГейм-Майстер аналізує складність завдання... 🔮")

    # Викликаємо декомпозицію
    sub_tasks = quest.decompose_task(big_task)

    print("\nТвій план битви розгорнуто:")
    print(sub_tasks)

    print("\n---")
    print("Виконай перший пункт, щоб отримати досвід (XP)!")


if __name__ == "__main__":
    start()
