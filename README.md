# TeleBot-Residential-Complex

Welcome to TeleBot-Residential-Complex! This Telegram bot allows residents to submit various requests related to access control and security within the residential complex.

## Features
- **Request Submission**: Users can submit requests such as passing a pedestrian, passing a car, or calling security directly through the bot.
- **Admin Panel**: Administrators have access to an admin panel where they can manage requests, view statistics, and perform administrative tasks.
- **Web Interface**: Requests submitted through the bot are displayed on a local webpage for easy review by security personnel.

## Bot Abilities
- **Pass a Pedestrian**: Residents can request permission for pedestrians to enter the residential complex.
- **Pass a Car**: Residents can request permission for vehicles to enter the residential complex.
- **Call Security**: Residents can call for security assistance directly through the bot.

## Integration with FastAPI
The bot is integrated with a FastAPI-based web interface, providing additional functionality and ease of use. The web interface allows security personnel to view and manage requests submitted through the bot in real-time.

To run the web interface:
1. Install FastAPI and Uvicorn by running `pip install fastapi uvicorn`.
2. Navigate to the `Kursova_Telegram_Bot` directory.
3. Run the following command: `uvicorn TeleBot.server.server:app --log-level debug --port=8001`.
4. Access the web interface at the specified URL.

## Screenshots
![Request Submission](https://github.com/romchhh/TeleBot-Residential-Complex/assets/123520267/a7e25f4c-d33b-4933-8bce-8507aa1a160f)

![Web Interface](https://github.com/romchhh/TeleBot-Residential-Complex/assets/123520267/58ff8412-ed9f-471d-8b25-d2f32bd322de)

![image](https://github.com/romchhh/TeleBot-Residential-Complex/assets/123520267/fd1174d9-e4f9-4821-b159-1b2c92fd94ac)


## Usage
1. **Start the Bot**: Users can start using the bot by sending a `/start` command.
2. **Submit Requests**: Users can submit requests by selecting appropriate options from the bot's menu.
3. **Admin Functions**: Administrators can access the admin panel by sending an `/admin` command. From there, they can manage requests and perform administrative tasks.

## Installation

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Set up your Telegram bot token, group ID, admin IDs, session name, API hash, API ID, and other configurations in the `config.py` file.

```python

token = "YOUR BOT TOKEN"
admins = (ADMIN IDS,)
group_id = GROUP ID FOR REQUEST
db_data_name = "PATH TO YOUR DB FILE"
URL_SITE = f'http://127.0.0.1:8001' # in index.html, app.js

```

5. Run the bot using `python main.py`.

## Contributing
Contributions are welcome! If you'd like to contribute to the project, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
