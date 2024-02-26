from datetime import datetime


def save_markdown(task_output):
    #get today's date in the format YYY-MM-DD
    today_date = datetime.now().strftime('%Y-%m-%d')
    # set the filename with today's date
    filename = f"{today_date}.md"
    #write the task output to the markdown file
    with open(filename,'w') as file:
        file.write(task_output.exported_output) #result)
    print(f"Newsletter saved as {filename}")
    